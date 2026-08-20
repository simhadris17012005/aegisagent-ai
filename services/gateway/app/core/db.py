import json
import time
import os
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    timestamp DOUBLE PRECISION NOT NULL,
    client_ip TEXT NOT NULL,
    status TEXT NOT NULL,
    classification TEXT NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL,
    language TEXT NOT NULL,
    technique_id TEXT,
    severity TEXT,
    action_executed TEXT,
    payload_snippet TEXT,
    raw_json TEXT NOT NULL
);
"""

_pool = None


async def get_pool():
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)

    return _pool


async def init_db():
    pool = await get_pool()

    async with pool.acquire() as db:
        await db.execute(SCHEMA)


async def log_incident(record: dict):
    pool = await get_pool()

    mitre = record.get("mitre_analysis") or {}

    async with pool.acquire() as db:
        await db.execute(
            """
            INSERT INTO incidents
            (
                timestamp,
                client_ip,
                status,
                classification,
                confidence_score,
                language,
                technique_id,
                severity,
                action_executed,
                payload_snippet,
                raw_json
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            """,
            time.time(),
            record.get("client_ip", ""),
            record.get("status", ""),
            record.get("classification", ""),
            record.get("confidence_score", 0.0),
            record.get("language", "en"),
            mitre.get("technique_id"),
            mitre.get("severity"),
            mitre.get("action_executed"),
            record.get("payload_snippet", "")[:200],
            json.dumps(record),
        )


async def recent_incidents(limit: int = 50):
    pool = await get_pool()

    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT timestamp, raw_json
            FROM incidents
            ORDER BY id DESC
            LIMIT $1
            """,
            limit,
        )

    out = []

    for row in rows:
        record = json.loads(row["raw_json"])
        record["receivedAt"] = int(row["timestamp"] * 1000)
        out.append(record)

    return out


async def incident_stats():
    pool = await get_pool()

    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT classification, COUNT(*) AS count
            FROM incidents
            GROUP BY classification
            """
        )

    return {
        row["classification"]: row["count"]
        for row in rows
    }

