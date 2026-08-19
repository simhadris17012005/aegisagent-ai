#!/usr/bin/env bash
# AegisAgent-AI :: Seeds the ml-engine with freshly trained models.
# Run this once before first launch (or whenever you want to retrain).
set -e

cd "$(dirname "$0")/../services/ml-engine/training"

echo "==> Installing training dependencies"
pip install --break-system-packages -q scikit-learn pandas numpy joblib skl2onnx onnx onnxruntime

echo "==> Building multilingual threat-text dataset"
python3 build_dataset.py

echo "==> Training threat text classifier (TF-IDF + Logistic Regression)"
python3 train_threat_classifier.py

echo "==> Training network anomaly detector (Isolation Forest)"
python3 train_anomaly_detector.py

echo "==> Done. Models saved to services/ml-engine/models/"
