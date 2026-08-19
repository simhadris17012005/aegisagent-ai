export type Classification =
  | "BENIGN" | "PHISHING" | "SQL_INJECTION" | "XSS" | "COMMAND_INJECTION"
  | "DDOS" | "PORT_SCAN" | "DATA_EXFILTRATION";

export interface MitreAnalysis {
  technique_id: string;
  technique_name: string;
  tactic: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  action_executed: string;
  firewall_rule: string;
  remediation_notes: string;
  localized_incident_summary: string;
}

export interface Incident {
  status: "THREAT_DETECTED" | "CLEAN";
  client_ip: string;
  confidence_score: number;
  classification: Classification;
  language: string;
  payload_snippet: string;
  mitre_analysis?: MitreAnalysis;
  receivedAt?: number;
}
