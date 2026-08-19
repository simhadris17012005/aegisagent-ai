"""
AegisAgent-AI :: Ingestion Gateway
Receives traffic/text, dispatches to the ML engine, escalates confirmed
threats to the agent core, persists an audit trail, and streams live
telemetry to the SOC dashboard over WebSocket.
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import uvicorn

from app.core.config import ML_ENGINE_URL, AGENT_CORE_URL, THREAT_SCORE_THRESHOLD
from app.core import db

app = FastAPI(title="AegisAgent Ingestion Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.on_event("startup")
async def startup():
    await db.init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.websocket("/ws/telemetry")
async def telemetry_ws(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep-alive; dashboard doesn't need to send data
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.get("/api/v1/incidents")
async def get_incidents(limit: int = 50):
    return await db.recent_incidents(limit)


@app.get("/api/v1/stats")
async def get_stats():
    return await db.incident_stats()


@app.post("/api/v1/inspect")
async def inspect_payload(data: IngestionPayload):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            ml_response = await client.post(
                ML_ENGINE_URL, json={"text": data.payload, "language": data.language}
            )
            ml_response.raise_for_status()
            ml_result = ml_response.json()
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"ML Engine unreachable: {exc}")

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
                response_data["mitre_analysis"] = {"error": f"agent-core unreachable: {exc}"}

    await db.log_incident(response_data)
    await manager.broadcast(response_data)

    return response_data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
