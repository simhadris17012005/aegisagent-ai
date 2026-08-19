"""
AegisAgent-AI :: Autonomous Agent Core
Receives confirmed threats from the gateway, maps to MITRE ATT&CK, synthesizes
remediation, and produces a localized incident summary.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from app.mitre.knowledge_graph import map_to_mitre
from app.agents.remediation_expert import synthesize_remediation
from app.agents.localizer import localize_summary

app = FastAPI(title="AegisAgent Autonomous Agent Core", version="1.0.0")


class InvestigateRequest(BaseModel):
    client_ip: str
    threat_type: str
    payload: str = ""
    language: str = "en"


@app.get("/health")
def health():
    return {"status": "ok", "service": "agent-core"}


@app.post("/investigate")
def investigate(req: InvestigateRequest):
    mitre = map_to_mitre(req.threat_type)
    remediation = synthesize_remediation(req.threat_type, req.client_ip)
    summary = localize_summary(
        language=req.language,
        ip=req.client_ip,
        threat_type=req.threat_type,
        technique_id=mitre["technique_id"],
        technique_name=mitre["technique_name"],
        severity=mitre["severity"],
        action=remediation["action"],
    )
    return {
        "technique_id": mitre["technique_id"],
        "technique_name": mitre["technique_name"],
        "tactic": mitre["tactic"],
        "severity": mitre["severity"],
        "action_executed": remediation["action"],
        "firewall_rule": remediation["firewall_rule"],
        "remediation_notes": remediation["extra"],
        "localized_incident_summary": summary,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
