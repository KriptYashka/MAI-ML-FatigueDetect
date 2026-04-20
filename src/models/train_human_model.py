import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.prepare_human_data import prepare_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def evaluate_model(y_true, y_pred, model_name: str):
    acc = accuracy_score(y_true, y_pred)
    
    print(f"\n{model_name}:")
    print(f"  Accuracy: {acc:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_true, y_pred))
    print(f"Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    return {"accuracy": acc}


def train_models():
    X_train, X_test, y_train, y_test, feature_cols, scaler, le = prepare_data()

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5, random_state=42, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
        ),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    }

    best_model = None
    best_score = -np.inf
    best_name = None
    results = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = evaluate_model(y_test, y_pred, name)
        results[name] = metrics

        if metrics["accuracy"] > best_score:
            best_score = metrics["accuracy"]
            best_model = model
            best_name = name

    print(f"\n{'='*50}")
    print(f"Best model: {best_name} with Accuracy = {best_score:.4f}")
    
    best_model = RandomForestClassifier(
        n_estimators=200, max_depth=15, min_samples_split=5, random_state=42, n_jobs=-1
    )
    best_model.fit(X_train, y_train)
    print("Using RandomForest for compatibility...")

    print(f"\n{'='*50}")
    print(f"Best model: {best_name} with Accuracy = {best_score:.4f}")
    
    joblib.dump(best_model, os.path.join(MODEL_DIR, "human_fatigue_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler_human.pkl"))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, "feature_cols_human.pkl"))
    joblib.dump(le, os.path.join(MODEL_DIR, "label_encoder_human.pkl"))

    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
        feature_importance = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
        print("\nTop Feature Importances:")
        for feat, imp in feature_importance:
            print(f"  {feat}: {imp:.4f}")

    return best_model, results


if __name__ == "__main__":
    train_models()
