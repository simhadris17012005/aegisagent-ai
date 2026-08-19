"""
AegisAgent-AI :: ML Inference Engine
Loads the REAL trained models (not stubs) and serves predictions.
"""
import json
import os
import joblib

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


class ThreatTextEvaluator:
    """Multilingual threat text classifier: char n-gram TF-IDF + Logistic Regression."""

    def __init__(self):
        path = os.path.join(MODEL_DIR, "threat_classifier.joblib")
        meta_path = os.path.join(MODEL_DIR, "model_meta.json")
        self.pipeline = joblib.load(path)
        with open(meta_path) as f:
            self.meta = json.load(f)

    def evaluate(self, text: str) -> dict:
        proba = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.named_steps["clf"].classes_
        idx = proba.argmax()
        predicted_class = classes[idx]
        confidence = float(proba[idx])
        return {
            "is_threat": predicted_class != "BENIGN",
            "threat_type": predicted_class,
            "confidence": round(confidence, 4),
            "class_probabilities": {c: round(float(p), 4) for c, p in zip(classes, proba)},
        }


class NetworkAnomalyEvaluator:
    """IsolationForest-based network flow anomaly detector."""

    FEATURES = ["packets_per_sec", "bytes_per_sec", "duration_sec", "unique_dst_ports",
                "syn_ratio", "avg_packet_size", "failed_conn_ratio"]

    def __init__(self):
        path = os.path.join(MODEL_DIR, "anomaly_detector.joblib")
        bundle = joblib.load(path)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]

    def evaluate(self, flow: dict) -> dict:
        import numpy as np
        x = np.array([[flow.get(f, 0.0) for f in self.FEATURES]])
        x_s = self.scaler.transform(x)
        pred = self.model.predict(x_s)[0]  # 1 = normal, -1 = anomaly
        score = float(self.model.decision_function(x_s)[0])  # higher = more normal
        anomaly_type = self._classify_anomaly(flow) if pred == -1 else "NONE"
        return {
            "is_anomaly": bool(pred == -1),
            "anomaly_score": round(score, 4),
            "anomaly_type": anomaly_type,
        }

    @staticmethod
    def _classify_anomaly(flow: dict) -> str:
        if flow.get("unique_dst_ports", 0) > 30:
            return "PORT_SCAN"
        if flow.get("packets_per_sec", 0) > 1000 or flow.get("syn_ratio", 0) > 0.7:
            return "DDOS"
        if flow.get("bytes_per_sec", 0) > 500000 and flow.get("avg_packet_size", 0) > 1000:
            return "DATA_EXFILTRATION"
        return "UNKNOWN_ANOMALY"


# Singletons loaded once at service startup
_threat_evaluator = None
_anomaly_evaluator = None


def get_threat_evaluator() -> ThreatTextEvaluator:
    global _threat_evaluator
    if _threat_evaluator is None:
        _threat_evaluator = ThreatTextEvaluator()
    return _threat_evaluator


def get_anomaly_evaluator() -> NetworkAnomalyEvaluator:
    global _anomaly_evaluator
    if _anomaly_evaluator is None:
        _anomaly_evaluator = NetworkAnomalyEvaluator()
    return _anomaly_evaluator
