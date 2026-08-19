import os
"""
AegisAgent-AI :: Threat Text Classifier Training
Real trained model (not a stub): char n-gram TF-IDF + Logistic Regression.
Char n-grams are used deliberately -- they generalize across Telugu/Tamil/
Hindi/English scripts and catch obfuscated payloads (encoded quotes, mixed
case, comment-padding) that word tokenizers miss.
"""
import json
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

DATA_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

def main():
    df = pd.read_csv(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb", ngram_range=(2, 4), min_df=1, sublinear_tf=True
        )),
        ("clf", LogisticRegression(max_iter=2000, C=5.0, class_weight="balanced")),
    ])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds)
    print(f"Test accuracy: {acc:.4f}\n")
    print(report)

    joblib.dump(pipeline, f"{MODEL_DIR}/threat_classifier.joblib")

    classes = list(pipeline.named_steps["clf"].classes_)
    with open(f"{MODEL_DIR}/model_meta.json", "w") as f:
        json.dump({
            "classes": classes,
            "test_accuracy": round(float(acc), 4),
            "vectorizer": "tfidf_char_wb_2_4",
            "model": "logistic_regression",
            "n_train": len(X_train),
            "n_test": len(X_test),
        }, f, indent=2)

    # --- ONNX export (offline, no external model downloads needed) ---
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import StringTensorType
        onnx_model = convert_sklearn(
            pipeline,
            initial_types=[("input", StringTensorType([None, 1]))],
            target_opset=12,
        )
        with open(f"{MODEL_DIR}/xlm_threat_classifier.onnx", "wb") as f:
            f.write(onnx_model.SerializeToString())
        print("ONNX export: OK -> models/xlm_threat_classifier.onnx")
    except Exception as e:
        print(f"ONNX export skipped ({e}); joblib model is still fully functional.")

if __name__ == "__main__":
    main()
