import joblib
import numpy as np
import os
from typing import Dict, List, Optional


class HumanFatigueClassifier:
    def __init__(
        self,
        model_path: str = None,
        scaler_path: str = None,
        feature_cols_path: str = None,
        label_encoder_path: str = None
    ):
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
        
        self.model_path = model_path or os.path.join(base_dir, "human_fatigue_model.pkl")
        self.scaler_path = scaler_path or os.path.join(base_dir, "scaler_human.pkl")
        self.feature_cols_path = feature_cols_path or os.path.join(base_dir, "feature_cols_human.pkl")
        self.label_encoder_path = label_encoder_path or os.path.join(base_dir, "label_encoder_human.pkl")
        
        self.model: Optional = None
        self.scaler: Optional = None
        self.feature_cols: Optional[List[str]] = None
        self.label_encoder: Optional = None

    def load(self) -> None:
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.feature_cols = joblib.load(self.feature_cols_path)
        self.label_encoder = joblib.load(self.label_encoder_path)
        print(f"Human fatigue model loaded: {self.model.__class__.__name__}")

    def predict(self, features: Dict[str, float]) -> tuple:
        if self.model is None:
            self.load()
        
        feature_vector = np.array([[features.get(col, 0.0) for col in self.feature_cols]])
        feature_scaled = self.scaler.transform(feature_vector)
        prediction = self.model.predict(feature_scaled)
        
        label = self.label_encoder.inverse_transform(prediction)[0]
        probabilities = self.model.predict_proba(feature_scaled)[0]
        
        return label, probabilities.tolist()

    def predict_batch(self, features_list: List[Dict[str, float]]) -> List[Dict]:
        if self.model is None:
            self.load()
        
        feature_matrix = np.array([
            [f.get(col, 0.0) for col in self.feature_cols]
            for f in features_list
        ])
        feature_scaled = self.scaler.transform(feature_matrix)
        predictions = self.model.predict(feature_scaled)
        probabilities = self.model.predict_proba(feature_scaled)
        
        results = []
        for pred, probs in zip(predictions, probabilities):
            label = self.label_encoder.inverse_transform([pred])[0]
            results.append({
                "label": label,
                "probabilities": probs.tolist()
            })
        
        return results


if __name__ == "__main__":
    classifier = HumanFatigueClassifier()
    try:
        classifier.load()
        
        sample = {
            "Hours_Awake": 12,
            "Decisions_Made": 50,
            "Task_Switches": 10,
            "Avg_Decision_Time_sec": 3.5,
            "Sleep_Hours_Last_Night": 5.0,
            "Caffeine_Intake_Cups": 3,
            "Stress_Level_1_10": 7.0,
            "Error_Rate": 0.15,
            "Cognitive_Load_Score": 0.8,
        }
        
        label, probs = classifier.predict(sample)
        print(f"Predicted Fatigue Level: {label}")
        print(f"Probabilities: Low={probs[0]:.2%}, Moderate={probs[1]:.2%}, High={probs[2]:.2%}")
    except Exception as e:
        print(f"Error: {e}")
        print("Please run train_human_model.py first to train the model.")
