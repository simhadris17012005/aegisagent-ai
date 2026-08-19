import { useEffect, useState, useCallback } from "react";
import { I18nProvider } from "./lib/i18n";
import { connectTelemetry, fetchIncidents } from "./lib/api";
import type { Incident } from "./types";
import TopBar from "./components/TopBar";
import MitreMatrix from "./components/MitreMatrix";
import IncidentFeed from "./components/IncidentFeed";
import StatsPanel from "./components/StatsPanel";
import TestPayload from "./components/TestPayload";

function Dashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  const handleIncoming = useCallback((incident: Incident) => {
    setIncidents((prev) => [incident, ...prev].slice(0, 200));
  }, []);

  useEffect(() => {
    fetchIncidents(50)
      .then((data) =>
        setIncidents(data.map((d) => ({ ...d, receivedAt: d.receivedAt ?? Date.now() })))
      )
      .catch(() => {
        // gateway not reachable yet — dashboard still renders, waits for WS
      });
    const disconnect = connectTelemetry(handleIncoming);
    return disconnect;
  }, [handleIncoming]);

  return (
    <div className="min-h-screen flex flex-col">
      <TopBar totalCount={incidents.length} />
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
  return (
    <I18nProvider>
      <Dashboard />
    </I18nProvider>
  );
}
