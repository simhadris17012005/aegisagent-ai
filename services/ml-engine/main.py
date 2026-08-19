"""
AegisAgent-AI :: ML Engine Service
Serves the real trained threat-text classifier and network anomaly detector.
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from pipeline.inference_engine import get_threat_evaluator, get_anomaly_evaluator

app = FastAPI(title="AegisAgent ML Inference Engine", version="1.0.0")


class TextPredictRequest(BaseModel):
    text: str
    language: str = "en"


class NetworkFlowRequest(BaseModel):
    packets_per_sec: float = 0.0
    bytes_per_sec: float = 0.0
    duration_sec: float = 1.0
    unique_dst_ports: float = 1.0
    syn_ratio: float = 0.0
    avg_packet_size: float = 500.0
    failed_conn_ratio: float = 0.0


@app.on_event("startup")
def warm_models():
    # Load models once at startup rather than per-request
    get_threat_evaluator()
    get_anomaly_evaluator()


@app.get("/health")
def health():
    return {"status": "ok", "service": "ml-engine"}


@app.post("/predict")
def predict_text(req: TextPredictRequest):
    evaluator = get_threat_evaluator()
    result = evaluator.evaluate(req.text)
    result["language"] = req.language
    return result


@app.post("/predict/network")
def predict_network(req: NetworkFlowRequest):
    evaluator = get_anomaly_evaluator()
    return evaluator.evaluate(req.dict())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
