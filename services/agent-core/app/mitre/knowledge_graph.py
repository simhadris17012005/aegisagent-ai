"""
AegisAgent-AI :: MITRE ATT&CK Knowledge Graph Mapper
Deterministic mapping from threat_type -> real MITRE ATT&CK technique IDs.
Sourced from the public MITRE ATT&CK framework technique catalog.
"""

MITRE_MAP = {
    "PHISHING": {
        "technique_id": "T1566.002",
        "technique_name": "Phishing: Spearphishing Link",
        "tactic": "Initial Access",
        "severity": "CRITICAL",
    },
    "SQL_INJECTION": {
        "technique_id": "T1190",
        "technique_name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "severity": "HIGH",
    },
    "XSS": {
        "technique_id": "T1059.007",
        "technique_name": "Command and Scripting Interpreter: JavaScript",
        "tactic": "Execution",
        "severity": "MEDIUM",
    },
    "COMMAND_INJECTION": {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "severity": "CRITICAL",
    },
    "DDOS": {
        "technique_id": "T1498",
        "technique_name": "Network Denial of Service",
        "tactic": "Impact",
        "severity": "HIGH",
    },
    "PORT_SCAN": {
        "technique_id": "T1046",
        "technique_name": "Network Service Discovery",
        "tactic": "Discovery",
        "severity": "MEDIUM",
    },
    "DATA_EXFILTRATION": {
        "technique_id": "T1041",
        "technique_name": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration",
        "severity": "CRITICAL",
    },
}

DEFAULT_ENTRY = {
    "technique_id": "T1000",
    "technique_name": "Unclassified Suspicious Activity",
    "tactic": "Unknown",
    "severity": "LOW",
}


def map_to_mitre(threat_type: str) -> dict:
    return MITRE_MAP.get(threat_type, DEFAULT_ENTRY)
