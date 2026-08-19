export const SEVERITY_COLOR: Record<string, string> = {
  CRITICAL: "#FF3B4E",
  HIGH: "#FFB020",
  MEDIUM: "#F2D93B",
  LOW: "#8B95A7",
};

export const CLASSIFICATION_LABEL: Record<string, string> = {
  BENIGN: "Clean",
  PHISHING: "Phishing",
  SQL_INJECTION: "SQL Injection",
  XSS: "XSS",
  COMMAND_INJECTION: "Command Injection",
  DDOS: "DDoS",
  PORT_SCAN: "Port Scan",
  DATA_EXFILTRATION: "Data Exfiltration",
};

export const MITRE_TECHNIQUES = [
  { id: "T1566.002", name: "Spearphishing Link", classification: "PHISHING" },
  { id: "T1190", name: "Exploit Public-Facing App", classification: "SQL_INJECTION" },
  { id: "T1059.007", name: "JavaScript Execution", classification: "XSS" },
  { id: "T1059", name: "Command Interpreter", classification: "COMMAND_INJECTION" },
  { id: "T1498", name: "Network DoS", classification: "DDOS" },
  { id: "T1046", name: "Service Discovery", classification: "PORT_SCAN" },
  { id: "T1041", name: "Exfiltration Over C2", classification: "DATA_EXFILTRATION" },
] as const;
