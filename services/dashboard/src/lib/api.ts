import type { Incident } from "../types";

const GATEWAY_HTTP = import.meta.env.VITE_GATEWAY_HTTP || "http://localhost:8000";
const GATEWAY_WS = import.meta.env.VITE_GATEWAY_WS || "ws://localhost:8000";

export async function fetchIncidents(limit = 50): Promise<Incident[]> {
  const res = await fetch(`${GATEWAY_HTTP}/api/v1/incidents?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch incidents");
  return res.json();
}

export async function fetchStats(): Promise<Record<string, number>> {
  const res = await fetch(`${GATEWAY_HTTP}/api/v1/stats`);
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function inspectPayload(payload: {
  client_ip: string;
  language: string;
  payload: string;
}): Promise<Incident> {
  const res = await fetch(`${GATEWAY_HTTP}/api/v1/inspect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Inspect request failed");
  return res.json();
}

export function connectTelemetry(onMessage: (incident: Incident) => void): () => void {
  let ws: WebSocket | null = null;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;
  let closed = false;

  function connect() {
    if (closed) return;

    ws = new WebSocket(`${GATEWAY_WS}/ws/telemetry`);

    ws.onopen = () => {
      console.log("[telemetry] WebSocket connected");
    };

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as Incident;
        onMessage({ ...data, receivedAt: Date.now() });
      } catch {
        // ignore malformed frames
      }
    };

    ws.onerror = () => {
      // onclose will handle reconnecting
    };

    ws.onclose = () => {
      if (!closed) {
        retryTimer = setTimeout(connect, 2000);
      }
    };
  }

  connect();

  return () => {
    closed = true;

    if (retryTimer) {
      clearTimeout(retryTimer);
      retryTimer = null;
    }

    if (ws && (ws.readyState === WebSocket.CONNECTING ||
               ws.readyState === WebSocket.OPEN)) {
      ws.close();
    }

    ws = null;
  };
}

