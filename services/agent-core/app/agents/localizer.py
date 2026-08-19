"""
AegisAgent-AI :: Localized Incident Summary Translator
Template-based localization for en/te/hi/ta so the platform works fully
offline with zero external API dependency. In production this slot is where
the multi-provider proxy (proxy/router.py) can instead route to an LLM for
free-form localized narrative summaries.
"""

TEMPLATES = {
    "en": "{severity} {threat_type} attack detected from {ip}. MITRE technique {technique_id} ({technique_name}). Action taken: {action}.",
    "te": "{ip} నుండి {severity_te} {threat_type_te} దాడి గుర్తించబడింది. MITRE టెక్నిక్ {technique_id} ({technique_name}). తీసుకున్న చర్య: {action_te}.",
    "hi": "{ip} से {severity_hi} {threat_type_hi} हमला पाया गया। MITRE तकनीक {technique_id} ({technique_name})। की गई कार्रवाई: {action_hi}।",
    "ta": "{ip} இலிருந்து {severity_ta} {threat_type_ta} தாக்குதல் கண்டறியப்பட்டது। MITRE நுட்பம் {technique_id} ({technique_name})। மேற்கொள்ளப்பட்ட நடவடிக்கை: {action_ta}.",
}

THREAT_TYPE_I18N = {
    "PHISHING": {"te": "ఫిషింగ్", "hi": "फ़िशिंग", "ta": "ஃபிஷிங்"},
    "SQL_INJECTION": {"te": "SQL ఇంజెక్షన్", "hi": "SQL इंजेक्शन", "ta": "SQL ஊசி"},
    "XSS": {"te": "XSS", "hi": "XSS", "ta": "XSS"},
    "COMMAND_INJECTION": {"te": "కమాండ్ ఇంజెక్షన్", "hi": "कमांड इंजेक्शन", "ta": "கட்டளை ஊசி"},
    "DDOS": {"te": "DDoS", "hi": "DDoS", "ta": "DDoS"},
    "PORT_SCAN": {"te": "పోర్ట్ స్కాన్", "hi": "पोर्ट स्कैन", "ta": "போர்ட் ஸ்கேன்"},
    "DATA_EXFILTRATION": {"te": "డేటా చౌర్యం", "hi": "डेटा चोरी", "ta": "தரவு திருட்டு"},
}

SEVERITY_I18N = {
    "CRITICAL": {"te": "తీవ్రమైన", "hi": "गंभीर", "ta": "கடுமையான"},
    "HIGH": {"te": "అధిక", "hi": "उच्च", "ta": "உயர்"},
    "MEDIUM": {"te": "మధ్యస్థ", "hi": "मध्यम", "ta": "நடுத்தர"},
    "LOW": {"te": "తక్కువ", "hi": "निम्न", "ta": "குறைந்த"},
}

ACTION_I18N = {
    "IP_ISOLATED": {"te": "IP నిర్బంధించబడింది", "hi": "IP अलग किया गया", "ta": "IP தனிமைப்படுத்தப்பட்டது"},
    "WAF_RULE_APPLIED": {"te": "WAF నియమం వర్తింపజేయబడింది", "hi": "WAF नियम लागू किया गया", "ta": "WAF விதி பயன்படுத்தப்பட்டது"},
    "PARAM_SANITIZED": {"te": "పారామీటర్ శుద్ధి చేయబడింది", "hi": "पैरामीटर स्वच्छ किया गया", "ta": "அளவுரு சுத்தம் செய்யப்பட்டது"},
    "RATE_LIMITED": {"te": "రేట్ పరిమితం చేయబడింది", "hi": "दर सीमित की गई", "ta": "வீதம் வரம்பிடப்பட்டது"},
    "IP_WATCHLISTED": {"te": "IP నిఘాలో ఉంచబడింది", "hi": "IP निगरानी सूची में डाला गया", "ta": "IP கண்காணிப்பில் வைக்கப்பட்டது"},
    "LOGGED_ONLY": {"te": "లాగ్ మాత్రమే చేయబడింది", "hi": "केवल लॉग किया गया", "ta": "பதிவு மட்டும் செய்யப்பட்டது"},
}


def localize_summary(language: str, ip: str, threat_type: str, technique_id: str,
                      technique_name: str, severity: str, action: str) -> str:
    lang = language if language in TEMPLATES else "en"
    if lang == "en":
        return TEMPLATES["en"].format(
            severity=severity, threat_type=threat_type, ip=ip,
            technique_id=technique_id, technique_name=technique_name, action=action,
        )
    return TEMPLATES[lang].format(
        ip=ip, technique_id=technique_id, technique_name=technique_name,
        **{f"severity_{lang}": SEVERITY_I18N.get(severity, {}).get(lang, severity)},
        **{f"threat_type_{lang}": THREAT_TYPE_I18N.get(threat_type, {}).get(lang, threat_type)},
        **{f"action_{lang}": ACTION_I18N.get(action, {}).get(lang, action)},
    )
