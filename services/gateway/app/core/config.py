import os

ML_ENGINE_URL = os.getenv("ML_ENGINE_URL", "http://localhost:8001/predict")
AGENT_CORE_URL = os.getenv("AGENT_CORE_URL", "http://localhost:8002/investigate")

THREAT_SCORE_THRESHOLD = float(
    os.getenv("THREAT_SCORE_THRESHOLD", "0.80")
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aegis_admin:CHANGE_ME@localhost:5432/aegis_telemetry",
)

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173"
    ).split(",")
    if origin.strip()
]
