import type { Incident } from "../types";

const GATEWAY_HTTP =
  import.meta.env.VITE_GATEWAY_HTTP || "http://localhost:8000";
const GATEWAY_WS =
  import.meta.env.VITE_GATEWAY_WS || "ws://localhost:8000";

const TOKEN_KEY = "aegis_access_token";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  username: string;
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}

export async function login(
  username: string,
  password: string
): Promise<LoginResponse> {
  const res = await fetch(`${GATEWAY_HTTP}/api/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    let message = "Login failed";

    try {
      const data = await res.json();
      message = data.detail || message;
    } catch {
      // ignore invalid error response
    }

    throw new Error(message);
  }

  const data = (await res.json()) as LoginResponse;
  setToken(data.access_token);

  return data;
}

export async function logout(): Promise<void> {
  const token = getToken();

  try {
    if (token) {
      await fetch(`${GATEWAY_HTTP}/api/v1/auth/logout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    }
  } finally {
    clearToken();
  }
}

async function authenticatedFetch(
  input: RequestInfo | URL,
  init: RequestInit = {}
): Promise<Response> {
  const token = getToken();

  if (!token) {
    throw new Error("Authentication required");
  }

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(input, {
    ...init,
    headers,
  });

  if (res.status === 401) {
    clearToken();
    window.dispatchEvent(new Event("aegis-auth-expired"));
    throw new Error("Authentication expired");
  }

  return res;
}

export async function fetchIncidents(limit = 50): Promise<Incident[]> {
  const res = await authenticatedFetch(
    `${GATEWAY_HTTP}/api/v1/incidents?limit=${limit}`
  );

  if (!res.ok) throw new Error("Failed to fetch incidents");

  return res.json();
}

export async function fetchStats(): Promise<Record<string, number>> {
  const res = await authenticatedFetch(`${GATEWAY_HTTP}/api/v1/stats`);

  if (!res.ok) throw new Error("Failed to fetch stats");

  return res.json();
}

export async function inspectPayload(payload: {
  client_ip: string;
  language: string;
  payload: string;
}): Promise<Incident> {
  const res = await authenticatedFetch(`${GATEWAY_HTTP}/api/v1/inspect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error("Inspect request failed");

  return res.json();
}

export function connectTelemetry(
  onMessage: (incident: Incident) => void
): () => void {
  let ws: WebSocket | null = null;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;
  let closed = false;

  function connect() {
    if (closed) return;

    const token = getToken();

    if (!token) {
      return;
    }

    const url = `${GATEWAY_WS}/ws/telemetry?token=${encodeURIComponent(token)}`;

    ws = new WebSocket(url);

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
      // onclose handles reconnect
    };

    ws.onclose = () => {
      if (!closed && getToken()) {
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

    if (
      ws &&
      (ws.readyState === WebSocket.CONNECTING ||
        ws.readyState === WebSocket.OPEN)
    ) {
      ws.close();
    }

    ws = null;
  };
}
