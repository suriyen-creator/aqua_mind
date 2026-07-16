from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "xgboost_model.json"
FEATURES = [
    "B2", "B3", "B4", "B5", "B8", "NDWI", "NDCI",
    "Temperature", "WindSpeed", "Humidity", "Rainfall", "DO", "Chlorophyll",
]

sample = {
    "B2": 0.10,
    "B3": 0.12,
    "B4": 0.08,
    "B5": 0.20,
    "B8": 0.18,
    "Temperature": 31.0,
    "WindSpeed": 2.0,
    "Humidity": 85.0,
    "Rainfall": 1.0,
    "DO": 5.4,
    "Chlorophyll": 24.0,
}
sample["NDWI"] = (sample["B3"] - sample["B8"]) / (sample["B3"] + sample["B8"] + 1e-6)
sample["NDCI"] = (sample["B5"] - sample["B4"]) / (sample["B5"] + sample["B4"] + 1e-6)

frame = pd.DataFrame([[sample[name] for name in FEATURES]], columns=FEATURES)
model = xgb.Booster()
model.load_model(MODEL_PATH)
matrix = xgb.DMatrix(frame, feature_names=FEATURES)
probability = float(model.predict(matrix)[0])
contributions = model.predict(matrix, pred_contribs=True)[0]

top_factors = sorted(
    zip(FEATURES, contributions[:-1], strict=True),
    key=lambda item: abs(item[1]),
    reverse=True,
)[:3]

print("=" * 48)
print("SYNTHETIC TECHNICAL DEMO - NOT LIVE RISK")
print(f"XGBoost probability: {probability:.2%}")
print("Top SHAP factors (raw margin):")
for name, value in top_factors:
    print(f"- {name}: {float(value):+.4f}")
margin = float(model.predict(matrix, output_margin=True)[0])
print(f"SHAP additivity error: {abs(float(np.sum(contributions)) - margin):.8f}")
print("=" * 48)
