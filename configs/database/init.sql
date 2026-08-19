CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    timestamp DOUBLE PRECISION NOT NULL DEFAULT EXTRACT(EPOCH FROM now()),
    client_ip TEXT NOT NULL,
    status TEXT NOT NULL,
    classification TEXT NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL,
    language TEXT NOT NULL,
    technique_id TEXT,
    severity TEXT,
    action_executed TEXT,
    payload_snippet TEXT,
    raw_json JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_classification ON incidents (classification);
CREATE INDEX IF NOT EXISTS idx_incidents_client_ip ON incidents (client_ip);
