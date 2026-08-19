import { useEffect, useState } from "react";
import { MITRE_TECHNIQUES } from "../lib/severity";
import { useI18n } from "../lib/i18n";
import type { Incident } from "../types";

export default function MitreMatrix({ incidents }: { incidents: Incident[] }) {
  const { t } = useI18n();
  const [flashed, setFlashed] = useState<Record<string, number>>({});

  const counts: Record<string, number> = {};
  for (const inc of incidents) {
    if (inc.mitre_analysis) {
      const id = inc.mitre_analysis.technique_id;
      counts[id] = (counts[id] || 0) + 1;
    }
  }
  const maxCount = Math.max(1, ...Object.values(counts));

  useEffect(() => {
    const latest = incidents[0];
    if (latest?.mitre_analysis) {
      const id = latest.mitre_analysis.technique_id;
      setFlashed((prev) => ({ ...prev, [id]: (prev[id] || 0) + 1 }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidents[0]?.receivedAt]);

  return (
    <div className="bg-(--color-steel) border border-(--color-line) rounded-xl p-4">
      <h2 className="font-(family-name:--font-display) text-sm text-(--color-mist) tracking-wide mb-4 uppercase">
        {t("mitreMatrix")}
      </h2>
      <div className="flex flex-col gap-2">
        {MITRE_TECHNIQUES.map((tech) => {
          const count = counts[tech.id] || 0;
          const intensity = count / maxCount;
          const bg = count === 0
            ? "rgba(139,149,167,0.08)"
            : `rgba(255, ${Math.round(176 - intensity * 100)}, ${Math.round(32 + (1 - intensity) * 40)}, ${0.15 + intensity * 0.55})`;

          return (
            <div
              key={tech.id}
              className={`rounded-lg px-3 py-2 border border-(--color-line) transition-all duration-500 ${flashed[tech.id] ? "tile-flash" : ""}`}
              style={{ background: bg }}
            >
              <div className="flex items-center justify-between">
                <span className="font-(family-name:--font-mono) text-xs text-(--color-bone) font-medium">
                  {tech.id}
                </span>
                <span className="font-(family-name:--font-mono) text-[10px] text-(--color-mist)">
                  {count > 0 ? `${count} ${t("hits")}` : t("noHits")}
                </span>
              </div>
              <div className="text-[11px] text-(--color-mist) mt-0.5">{tech.name}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
