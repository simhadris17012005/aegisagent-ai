import { useI18n } from "../lib/i18n";
import { CLASSIFICATION_LABEL, SEVERITY_COLOR } from "../lib/severity";
import type { Incident } from "../types";

const CLASS_COLOR: Record<string, string> = {
  PHISHING: SEVERITY_COLOR.CRITICAL,
  SQL_INJECTION: SEVERITY_COLOR.HIGH,
  XSS: "#F2D93B",
  COMMAND_INJECTION: SEVERITY_COLOR.CRITICAL,
  DDOS: SEVERITY_COLOR.HIGH,
  PORT_SCAN: "#F2D93B",
  DATA_EXFILTRATION: SEVERITY_COLOR.CRITICAL,
  BENIGN: "#38E1C6",
};

export default function StatsPanel({ incidents }: { incidents: Incident[] }) {
  const { t } = useI18n();
  const total = incidents.length;
  const threats = incidents.filter((i) => i.status === "THREAT_DETECTED").length;
  const threatRate = total > 0 ? Math.round((threats / total) * 100) : 0;

  const counts: Record<string, number> = {};
  for (const inc of incidents) {
    counts[inc.classification] = (counts[inc.classification] || 0) + 1;
  }
  const maxCount = Math.max(1, ...Object.values(counts));

  return (
    <div className="bg-(--color-steel) border border-(--color-line) rounded-xl p-4 flex flex-col gap-5">
      <h2 className="font-(family-name:--font-display) text-sm text-(--color-mist) tracking-wide uppercase">
        {t("threatStats")}
      </h2>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="font-(family-name:--font-display) text-2xl text-(--color-bone) tabular-nums">
            {total}
          </div>
          <div className="text-[11px] text-(--color-mist) uppercase tracking-wide">
            {t("totalIncidents")}
          </div>
        </div>
        <div>
          <div
            className="font-(family-name:--font-display) text-2xl tabular-nums"
            style={{ color: threatRate > 50 ? SEVERITY_COLOR.CRITICAL : "#38E1C6" }}
          >
            {threatRate}%
          </div>
          <div className="text-[11px] text-(--color-mist) uppercase tracking-wide">
            {t("threatRate")}
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {Object.entries(counts)
          .sort((a, b) => b[1] - a[1])
          .map(([cls, count]) => (
            <div key={cls}>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-(--color-mist)">
                  {CLASSIFICATION_LABEL[cls] || cls}
                </span>
                <span className="font-(family-name:--font-mono) text-(--color-bone)">{count}</span>
              </div>
              <div className="h-1.5 rounded-full bg-(--color-void) overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${(count / maxCount) * 100}%`,
                    background: CLASS_COLOR[cls] || "#8B95A7",
                  }}
                />
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
