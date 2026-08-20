"""
AegisAgent-AI :: Ingestion Gateway
Receives traffic/text, dispatches to the ML engine, escalates confirmed
threats to the agent core, persists an audit trail, and streams live
telemetry to the SOC dashboard over WebSocket.
"""

from datetime import datetime, timedelta, timezone

import httpx
import json
import uvicorn

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core import db
from app.core.config import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    AGENT_CORE_URL,
    CORS_ORIGINS,
    JWT_EXPIRE_MINUTES,
    JWT_SECRET,
    ML_ENGINE_URL,
    THREAT_SCORE_THRESHOLD,
)


JWT_ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(title="AegisAgent Ingestion Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginPayload(BaseModel):
    username: str
    password: str


class IngestionPayload(BaseModel):
    client_ip: str
    endpoint: str = "/api"
    payload: str
    language: str = "en"


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        dead = []

        for ws in self.active:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


def create_access_token(username: str) -> str:
    if not JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET is not configured",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> str:
    if not JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET is not configured",
        )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token",
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token",
        )


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    return verify_token(credentials.credentials)


@app.on_event("startup")
async def startup():
    await db.init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.post("/api/v1/auth/login")
async def login(data: LoginPayload):
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=500,
            detail="Admin credentials are not configured",
        )

    if data.username != ADMIN_USERNAME or data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    token = create_access_token(data.username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_MINUTES * 60,
        "username": data.username,
    }


@app.post("/api/v1/auth/logout")
async def logout(username: str = Depends(require_auth)):
    # JWT is stateless. The dashboard should delete its stored token.
    return {
        "status": "ok",
        "message": "Logged out successfully",
    }


@app.get("/api/v1/auth/me")
async def current_user(username: str = Depends(require_auth)):
    return {
        "authenticated": True,
        "username": username,
    }


@app.websocket("/ws/telemetry")
async def telemetry_ws(ws: WebSocket):
    token = ws.query_params.get("token")

    if not token:
        await ws.close(code=1008, reason="Authentication required")
        return

    try:
        verify_token(token)
    except HTTPException:
        await ws.close(code=1008, reason="Invalid or expired token")
        return

    await manager.connect(ws)

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.get("/api/v1/incidents")
async def get_incidents(
    limit: int = 50,
    username: str = Depends(require_auth),
):
    return await db.recent_incidents(limit)


@app.get("/api/v1/stats")
async def get_stats(
    username: str = Depends(require_auth),
):
    return await db.incident_stats()


@app.post("/api/v1/inspect")
async def inspect_payload(
    data: IngestionPayload,
    username: str = Depends(require_auth),
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            ml_response = await client.post(
                ML_ENGINE_URL,
                json={
                    "text": data.payload,
                    "language": data.language,
                },
            )
            ml_response.raise_for_status()
            ml_result = ml_response.json()

        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"ML Engine unreachable: {exc}",
            )

    is_threat = ml_result.get("is_threat", False)
    confidence = ml_result.get("confidence", 0.0)

    response_data = {
        "status": "THREAT_DETECTED" if is_threat else "CLEAN",
        "client_ip": data.client_ip,
        "confidence_score": confidence,
        "classification": ml_result.get("threat_type", "BENIGN"),
        "language": data.language,
        "payload_snippet": data.payload,
    }

    if is_threat and confidence >= THREAT_SCORE_THRESHOLD:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                agent_response = await client.post(
                    AGENT_CORE_URL,
                    json={
                        "client_ip": data.client_ip,
                        "threat_type": ml_result.get("threat_type"),
                        "payload": data.payload,
                        "language": data.language,
                    },
                )

                agent_response.raise_for_status()
                response_data["mitre_analysis"] = agent_response.json()

            except Exception as exc:
                response_data["mitre_analysis"] = {
                    "error": f"agent-core unreachable: {exc}"
                }

    await db.log_incident(response_data)
    await manager.broadcast(response_data)

    return response_data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
