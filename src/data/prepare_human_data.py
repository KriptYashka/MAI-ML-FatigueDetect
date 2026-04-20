import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

DATASET_PATH = r"C:\Users\kript\.cache\kagglehub\datasets\sonalshinde123\human-decision-fatigue-behavioral-dataset\versions\1\human_decision_fatigue_dataset.csv"
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_data(path: str = DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def prepare_data(df: pd.DataFrame = None) -> tuple:
    if df is None:
        df = load_data()

    feature_cols = [
        'Hours_Awake', 'Decisions_Made', 'Task_Switches', 
        'Avg_Decision_Time_sec', 'Sleep_Hours_Last_Night',
        'Caffeine_Intake_Cups', 'Stress_Level_1_10', 
        'Error_Rate', 'Cognitive_Load_Score'
    ]

    X = df[feature_cols].values
    
    le = LabelEncoder()
    y = le.fit_transform(df['Fatigue_Level'])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    np.save(os.path.join(PROCESSED_DATA_DIR, "X_train_human.npy"), X_train_scaled)
    np.save(os.path.join(PROCESSED_DATA_DIR, "X_test_human.npy"), X_test_scaled)
    np.save(os.path.join(PROCESSED_DATA_DIR, "y_train_human.npy"), y_train)
    np.save(os.path.join(PROCESSED_DATA_DIR, "y_test_human.npy"), y_test)
    joblib.dump(scaler, os.path.join(PROCESSED_DATA_DIR, "scaler_human.pkl"))
    joblib.dump(feature_cols, os.path.join(PROCESSED_DATA_DIR, "feature_cols_human.pkl"))
    joblib.dump(le, os.path.join(PROCESSED_DATA_DIR, "label_encoder.pkl"))

    print(f"Human fatigue data prepared: {len(X_train)} train, {len(X_test)} test samples")
    print(f"Features: {feature_cols}")
    print(f"Classes: {le.classes_}")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, feature_cols, scaler, le


if __name__ == "__main__":
    prepare_data()
