import { createContext, useContext, useState, type ReactNode } from "react";
import en from "../locales/en.json";
import te from "../locales/te.json";
import hi from "../locales/hi.json";
import ta from "../locales/ta.json";

export type LangCode = "en" | "te" | "hi" | "ta";

const DICTS: Record<LangCode, Record<string, string>> = { en, te, hi, ta };

export const LANG_LABELS: Record<LangCode, string> = {
  en: "EN", te: "తె", hi: "हि", ta: "த",
};

interface I18nContextValue {
  lang: LangCode;
  setLang: (l: LangCode) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<LangCode>("en");
  const t = (key: string) => DICTS[lang][key] ?? DICTS.en[key] ?? key;
  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
