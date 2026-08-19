import aiosqlite
import json
import time
import os

DB_PATH = os.getenv("SQLITE_PATH", "/home/claude/aegisagent-ai/services/gateway/audit_log.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    client_ip TEXT NOT NULL,
    status TEXT NOT NULL,
    classification TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    language TEXT NOT NULL,
    technique_id TEXT,
    severity TEXT,
    action_executed TEXT,
    payload_snippet TEXT,
    raw_json TEXT NOT NULL
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(SCHEMA)
        await db.commit()


async def log_incident(record: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO incidents
               (timestamp, client_ip, status, classification, confidence_score,
                language, technique_id, severity, action_executed, payload_snippet, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                time.time(),
                record.get("client_ip", ""),
                record.get("status", ""),
                record.get("classification", ""),
                record.get("confidence_score", 0.0),
                record.get("language", "en"),
                (record.get("mitre_analysis") or {}).get("technique_id"),
                (record.get("mitre_analysis") or {}).get("severity"),
                (record.get("mitre_analysis") or {}).get("action_executed"),
                record.get("payload_snippet", "")[:200],
                json.dumps(record),
            ),
        )
        await db.commit()


async def recent_incidents(limit: int = 50):
    """Returns full incident objects (with nested mitre_analysis) reconstructed
    from raw_json, so REST-loaded history matches the shape the WebSocket
    stream sends live -- the dashboard renders both the same way."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT timestamp, raw_json FROM incidents ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        out = []
        for r in rows:
            record = json.loads(r["raw_json"])
            record["receivedAt"] = int(r["timestamp"] * 1000)
            out.append(record)
        return out


async def incident_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT classification, COUNT(*) as count FROM incidents GROUP BY classification"
        )
        rows = await cursor.fetchall()
        return {r["classification"]: r["count"] for r in rows}
