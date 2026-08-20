import { useI18n, LANG_LABELS, type LangCode } from "../lib/i18n";

interface TopBarProps {
  totalCount: number;
  onLogout: () => void;
}

export default function TopBar({ totalCount, onLogout }: TopBarProps) {
  const { t, lang, setLang } = useI18n();
  const langs: LangCode[] = ["en", "te", "hi", "ta"];

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-(--color-line) bg-(--color-steel)">
      <div className="flex items-center gap-3">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 2L3 6v6c0 5 3.8 8.7 9 10 5.2-1.3 9-5 9-10V6l-9-4z"
            fill="none"
            stroke="#38E1C6"
            strokeWidth="1.6"
          />
          <path
            d="M8.5 12l2.3 2.3L15.5 9"
            stroke="#38E1C6"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        <h1 className="font-(family-name:--font-display) text-(--color-bone) text-lg tracking-wide">
          {t("brand")}
        </h1>
      </div>

      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-(--color-cyan) live-dot" />
          <span className="font-(family-name:--font-mono) text-xs text-(--color-cyan) tracking-widest">
            {t("live")}
          </span>
        </div>

        <div className="flex items-center gap-1 bg-(--color-void) rounded-lg p-1 border border-(--color-line)">
          {langs.map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={`px-2.5 py-1 rounded-md text-xs font-(family-name:--font-mono) transition-colors ${
                lang === l
                  ? "bg-(--color-cyan) text-(--color-void) font-semibold"
                  : "text-(--color-mist) hover:text-(--color-bone)"
              }`}
            >
              {LANG_LABELS[l]}
            </button>
          ))}
        </div>

        <div className="font-(family-name:--font-mono) text-(--color-bone) text-sm tabular-nums">
          {totalCount.toLocaleString()}
        </div>

        <button
          onClick={onLogout}
          className="rounded-lg border border-(--color-line) px-3 py-1.5 text-xs font-(family-name:--font-mono) text-(--color-mist) hover:border-red-400 hover:text-red-300 transition-colors"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
