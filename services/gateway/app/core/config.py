import os

ML_ENGINE_URL = os.getenv("ML_ENGINE_URL", "http://localhost:8001/predict")
AGENT_CORE_URL = os.getenv("AGENT_CORE_URL", "http://localhost:8002/investigate")
THREAT_SCORE_THRESHOLD = float(os.getenv("THREAT_SCORE_THRESHOLD", "0.80"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aegis_admin:CHANGE_ME@localhost:5432/aegis_telemetry",
)
