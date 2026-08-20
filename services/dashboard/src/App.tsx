import { useCallback, useEffect, useState } from "react";
import { I18nProvider } from "./lib/i18n";
import {
  clearToken,
  connectTelemetry,
  fetchIncidents,
  isAuthenticated,
  logout,
} from "./lib/api";
import type { Incident } from "./types";
import TopBar from "./components/TopBar";
import Login from "./components/Login";
import MitreMatrix from "./components/MitreMatrix";
import IncidentFeed from "./components/IncidentFeed";
import StatsPanel from "./components/StatsPanel";
import TestPayload from "./components/TestPayload";

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  const handleIncoming = useCallback((incident: Incident) => {
    setIncidents((prev) => [incident, ...prev].slice(0, 200));
  }, []);

  useEffect(() => {
    fetchIncidents(50)
      .then((data) =>
        setIncidents(
          data.map((d) => ({
            ...d,
            receivedAt: d.receivedAt ?? Date.now(),
          }))
        )
      )
      .catch((err) => {
        console.error("[dashboard] failed to fetch incidents", err);
      });

    const disconnect = connectTelemetry(handleIncoming);

    return disconnect;
  }, [handleIncoming]);

  useEffect(() => {
    const handleExpired = () => {
      clearToken();
      onLogout();
    };

    window.addEventListener("aegis-auth-expired", handleExpired);

    return () => {
      window.removeEventListener("aegis-auth-expired", handleExpired);
    };
  }, [onLogout]);

  async function handleLogout() {
    await logout();
    onLogout();
  }

  return (
    <div className="min-h-screen flex flex-col">
      <TopBar totalCount={incidents.length} onLogout={handleLogout} />

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-[280px_1fr_300px] gap-4 p-4">
        <MitreMatrix incidents={incidents} />

        <div className="min-h-[60vh]">
          <IncidentFeed incidents={incidents} />
        </div>

        <div className="flex flex-col gap-4">
          <StatsPanel incidents={incidents} />
          <TestPayload />
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated);

  const handleLogin = useCallback(() => {
    setAuthenticated(true);
  }, []);

  const handleLogout = useCallback(() => {
    setAuthenticated(false);
  }, []);

  return (
    <I18nProvider>
      {authenticated ? (
        <Dashboard onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </I18nProvider>
  );
}
