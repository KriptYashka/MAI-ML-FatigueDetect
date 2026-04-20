import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

DATASET_PATH = r"C:\Users\kript\.cache\kagglehub\datasets\konghuanqing\fatigue-dataset-for-steel\versions\1\Fatigue Dataset for Steel.xlsx"
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_data(path: str = DATASET_PATH) -> pd.DataFrame:
    df = pd.read_excel(path)
    return df


def prepare_data(df: pd.DataFrame = None) -> tuple:
    if df is None:
        df = load_data()
    feature_cols = [col for col in df.columns if col not in ['Sl. No.', 'Fatigue']]
    X = df[feature_cols].values
    y = df['Fatigue'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    np.save(os.path.join(PROCESSED_DATA_DIR, "X_train.npy"), X_train_scaled)
    np.save(os.path.join(PROCESSED_DATA_DIR, "X_test.npy"), X_test_scaled)
    np.save(os.path.join(PROCESSED_DATA_DIR, "y_train.npy"), y_train)
    np.save(os.path.join(PROCESSED_DATA_DIR, "y_test.npy"), y_test)
    joblib.dump(scaler, os.path.join(PROCESSED_DATA_DIR, "scaler.pkl"))
    joblib.dump(feature_cols, os.path.join(PROCESSED_DATA_DIR, "feature_cols.pkl"))

    print(f"Data prepared: {len(X_train)} train, {len(X_test)} test samples")
    print(f"Features: {len(feature_cols)}")
    print(f"Feature names: {feature_cols}")
    return X_train_scaled, X_test_scaled, y_train, y_test, feature_cols, scaler


if __name__ == "__main__":
    df = load_data()
    prepare_data(df)
