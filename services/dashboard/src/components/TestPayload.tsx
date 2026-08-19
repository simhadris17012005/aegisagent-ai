import { useState } from "react";
import { useI18n, type LangCode } from "../lib/i18n";
import { inspectPayload } from "../lib/api";

const SAMPLES: Record<LangCode, string> = {
  en: "Your bank account has been suspended. Click here to verify: http://fraud-verify.com",
  te: "మీ బ్యాంక్ ఖాతా రద్దు చేయబడింది. వెంటనే ఇక్కడ క్లిక్ చేసి పాస్‌వర్డ్ మార్చండి: http://fraud-verify.com",
  hi: "आपका बैंक खाता निलंबित कर दिया गया है। यहां क्लिक करके सत्यापित करें: http://fraud-verify.com",
  ta: "உங்கள் வங்கிக் கணக்கு முடக்கப்பட்டுள்ளது. இங்கே கிளிக் செய்யவும்: http://fraud-verify.com",
};

export default function TestPayload() {
  const { t, lang } = useI18n();
  const [text, setText] = useState(SAMPLES[lang]);
  const [sending, setSending] = useState(false);

  async function send() {
    setSending(true);
    try {
      await inspectPayload({
        client_ip: `103.21.244.${Math.floor(Math.random() * 250)}`,
        language: lang,
        payload: text,
      });
    } catch {
      // gateway offline — WebSocket panel will simply stay quiet
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="bg-(--color-steel) border border-(--color-line) rounded-xl p-4 flex flex-col gap-2">
      <h2 className="font-(family-name:--font-display) text-sm text-(--color-mist) tracking-wide uppercase">
        {t("testPayload")}
      </h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        className="bg-(--color-void) border border-(--color-line) rounded-lg p-2 text-xs text-(--color-bone) font-(family-name:--font-mono) resize-none focus:outline-none focus:border-(--color-cyan)"
      />
      <button
        onClick={send}
        disabled={sending}
        className="self-end bg-(--color-cyan) text-(--color-void) text-xs font-semibold px-4 py-1.5 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
      >
        {sending ? "…" : t("send")}
      </button>
    </div>
  );
}
