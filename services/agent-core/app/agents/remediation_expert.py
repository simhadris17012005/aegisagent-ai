"""
AegisAgent-AI :: Remediation Synthesizer
Generates deterministic containment actions. Deterministic (not LLM-guessed)
so the firewall/WAF actions triggered on a live host are auditable and safe.
"""

def synthesize_remediation(threat_type: str, client_ip: str) -> dict:
    actions = {
        "PHISHING": {
            "action": "IP_ISOLATED",
            "firewall_rule": f"iptables -A INPUT -s {client_ip} -j DROP",
            "extra": "Add sender domain to DNS sinkhole blocklist.",
        },
        "SQL_INJECTION": {
            "action": "WAF_RULE_APPLIED",
            "firewall_rule": f"iptables -A INPUT -s {client_ip} -j DROP",
            "extra": "WAF: block requests matching SQL meta-characters (' -- ; UNION) from this IP.",
        },
        "XSS": {
            "action": "PARAM_SANITIZED",
            "firewall_rule": f"# WAF rule: strip <script>/on*= attributes from payloads from {client_ip}",
            "extra": "Enable output encoding on affected endpoint.",
        },
        "COMMAND_INJECTION": {
            "action": "IP_ISOLATED",
            "firewall_rule": f"iptables -A INPUT -s {client_ip} -j DROP",
            "extra": "Rotate any credentials/tokens the affected service could reach.",
        },
        "DDOS": {
            "action": "RATE_LIMITED",
            "firewall_rule": f"iptables -A INPUT -s {client_ip} -m limit --limit 10/second -j ACCEPT",
            "extra": "Escalate to upstream DDoS scrubbing if sustained > 60s.",
        },
        "PORT_SCAN": {
            "action": "IP_WATCHLISTED",
            "firewall_rule": f"iptables -A INPUT -s {client_ip} -j LOG --log-prefix 'PORTSCAN '",
            "extra": "Monitor for 15 minutes; escalate to IP_ISOLATED if scan continues.",
        },
        "DATA_EXFILTRATION": {
            "action": "IP_ISOLATED",
            "firewall_rule": f"iptables -A OUTPUT -d {client_ip} -j DROP",
            "extra": "Trigger DLP review of the source host's recent outbound transfers.",
        },
    }
    return actions.get(threat_type, {
        "action": "LOGGED_ONLY",
        "firewall_rule": f"# no automated action defined for {threat_type}",
        "extra": "Escalate to human SOC analyst for manual triage.",
    })
