import { useI18n } from "../lib/i18n";
import { SEVERITY_COLOR, CLASSIFICATION_LABEL } from "../lib/severity";
import type { Incident } from "../types";

function timeLabel(ts?: number) {
  const d = ts ? new Date(ts) : new Date();
  return d.toLocaleTimeString("en-GB", { hour12: false });
}

function Row({ incident }: { incident: Incident }) {
  const isThreat = incident.status === "THREAT_DETECTED";
  const severity = incident.mitre_analysis?.severity;
  const color = isThreat ? SEVERITY_COLOR[severity || "MEDIUM"] : "#38E1C6";

  return (
    <div className="row-in flex items-start gap-3 py-2.5 px-3 border-b border-(--color-line)/60 hover:bg-(--color-steel-light) transition-colors">
      <div className="w-1 self-stretch rounded-full" style={{ background: color }} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-(family-name:--font-mono) text-[11px] text-(--color-mist)">
            {timeLabel(incident.receivedAt)}
          </span>
          <span className="font-(family-name:--font-mono) text-xs text-(--color-bone)">
            {incident.client_ip}
          </span>
          <span
            className="text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase tracking-wide"
            style={{ background: `${color}22`, color }}
          >
            {CLASSIFICATION_LABEL[incident.classification] || incident.classification}
          </span>
          <span className="font-(family-name:--font-mono) text-[10px] text-(--color-mist)">
            {(incident.confidence_score * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-(--color-mist) uppercase">{incident.language}</span>
        </div>
        {incident.mitre_analysis && (
          <div className="mt-1 text-[12px] text-(--color-mist) leading-relaxed break-words">
            {incident.mitre_analysis.localized_incident_summary}
          </div>
        )}
        {incident.mitre_analysis && (
          <div className="mt-1 flex items-center gap-2">
            <span className="font-(family-name:--font-mono) text-[10px] text-(--color-cyan)">
              → {incident.mitre_analysis.action_executed}
            </span>
            <span className="font-(family-name:--font-mono) text-[10px] text-(--color-mist)">
              {incident.mitre_analysis.technique_id}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function IncidentFeed({ incidents }: { incidents: Incident[] }) {
  const { t } = useI18n();
  return (
    <div className="bg-(--color-steel) border border-(--color-line) rounded-xl overflow-hidden flex flex-col h-full">
      <h2 className="font-(family-name:--font-display) text-sm text-(--color-mist) tracking-wide uppercase px-4 py-3 border-b border-(--color-line)">
        {t("incidentStream")}
      </h2>
      <div className="overflow-y-auto flex-1">
        {incidents.length === 0 ? (
          <div className="px-4 py-8 text-center text-(--color-mist) text-sm font-(family-name:--font-mono)">
            {t("waiting")}
          </div>
        ) : (
          incidents.map((inc, i) => <Row key={`${inc.receivedAt}-${i}`} incident={inc} />)
        )}
      </div>
    </div>
  );
}
