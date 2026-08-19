import os
"""
AegisAgent-AI :: Network Anomaly Detector Training
Real trained IsolationForest on synthetic-but-realistic network flow features:
  [packets_per_sec, bytes_per_sec, duration_sec, unique_dst_ports, syn_ratio,
   avg_packet_size, failed_conn_ratio]

Normal traffic clusters tightly; DDoS/portscan/exfil patterns are injected as
distinct realistic distributions so the forest genuinely learns separable
structure (verified below with a held-out contamination check).
"""
import numpy as np
import joblib
import json

rng = np.random.default_rng(42)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

def gen_normal(n):
    return np.column_stack([
        rng.normal(50, 15, n).clip(1),          # packets/sec
        rng.normal(6000, 2000, n).clip(100),     # bytes/sec
        rng.normal(30, 10, n).clip(1),           # duration sec
        rng.integers(1, 4, n),                   # unique dst ports
        rng.normal(0.1, 0.05, n).clip(0, 1),     # syn ratio
        rng.normal(500, 100, n).clip(40),        # avg packet size
        rng.normal(0.02, 0.02, n).clip(0, 1),    # failed conn ratio
    ])

def gen_ddos(n):
    return np.column_stack([
        rng.normal(5000, 1500, n).clip(500),
        rng.normal(400000, 100000, n).clip(10000),
        rng.normal(2, 1, n).clip(0.1),
        rng.integers(1, 3, n),
        rng.normal(0.9, 0.05, n).clip(0, 1),
        rng.normal(60, 20, n).clip(40),
        rng.normal(0.6, 0.15, n).clip(0, 1),
    ])

def gen_portscan(n):
    return np.column_stack([
        rng.normal(200, 60, n).clip(10),
        rng.normal(8000, 2000, n).clip(500),
        rng.normal(5, 2, n).clip(0.5),
        rng.integers(50, 500, n),
        rng.normal(0.7, 0.1, n).clip(0, 1),
        rng.normal(60, 10, n).clip(40),
        rng.normal(0.8, 0.1, n).clip(0, 1),
    ])

def gen_exfil(n):
    return np.column_stack([
        rng.normal(30, 10, n).clip(1),
        rng.normal(2_000_000, 500000, n).clip(100000),
        rng.normal(600, 200, n).clip(30),
        rng.integers(1, 3, n),
        rng.normal(0.05, 0.03, n).clip(0, 1),
        rng.normal(1400, 100, n).clip(500),
        rng.normal(0.01, 0.01, n).clip(0, 1),
    ])

FEATURES = ["packets_per_sec", "bytes_per_sec", "duration_sec", "unique_dst_ports",
            "syn_ratio", "avg_packet_size", "failed_conn_ratio"]

def main():
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    normal = gen_normal(1200)
    anomalies = np.vstack([gen_ddos(60), gen_portscan(60), gen_exfil(60)])

    X_train = normal  # train only on normal traffic (unsupervised, realistic SOC setup)
    scaler = StandardScaler().fit(X_train)
    X_train_s = scaler.transform(X_train)

    model = IsolationForest(
        n_estimators=200, contamination=0.05, random_state=42, max_samples="auto"
    )
    model.fit(X_train_s)

    # Validate on held-out normal + injected anomalies
    X_val = np.vstack([gen_normal(200), anomalies])
    y_val = np.array([1] * 200 + [-1] * len(anomalies))  # 1=normal, -1=anomaly
    X_val_s = scaler.transform(X_val)
    preds = model.predict(X_val_s)

    from sklearn.metrics import classification_report
    report = classification_report(y_val, preds, target_names=["ANOMALY", "NORMAL"])
    print(report)

    joblib.dump({"model": model, "scaler": scaler, "features": FEATURES},
                f"{MODEL_DIR}/anomaly_detector.joblib")

    acc = (preds == y_val).mean()
    with open(f"{MODEL_DIR}/anomaly_model_meta.json", "w") as f:
        json.dump({
            "algorithm": "IsolationForest",
            "features": FEATURES,
            "validation_accuracy": round(float(acc), 4),
            "n_estimators": 200,
            "contamination": 0.05,
        }, f, indent=2)
    print(f"\nSaved model. Validation accuracy: {acc:.4f}")

if __name__ == "__main__":
    main()
