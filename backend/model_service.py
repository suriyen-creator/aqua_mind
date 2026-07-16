from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Literal

import xgboost as xgb


BACKEND_DIR = Path(__file__).resolve().parent
MODEL_PATH = BACKEND_DIR / "xgboost_model.json"

FEATURE_NAMES = [
    "ndci_mean_7d",
    "ndci_slope_7d",
    "sst_anomaly",
    "wind_speed_3d",
    "ndci_x_wind",
]

FEATURE_METADATA = {
    "ndci_mean_7d": ("NDCI mean 7d", "index"),
    "ndci_slope_7d": ("NDCI slope 7d", "index/day"),
    "sst_anomaly": ("SST anomaly", "°C"),
    "wind_speed_3d": ("Wind speed 3d", "m/s"),
    "ndci_x_wind": ("NDCI × wind interaction", "index·m/s"),
}

# Representative rows selected from backend/mock_data.csv. These are synthetic
# technical scenarios and are not observations from Chonburi.
MODEL_DEMO_SCENARIOS = {
    "low": {
        "ndci_mean_7d": 0.6991183324,
        "ndci_slope_7d": -0.0158411160,
        "sst_anomaly": 2.5977676706,
        "wind_speed_3d": 13.2965131104,
        "ndci_x_wind": 9.2958360727,
    },
    "medium": {
        "ndci_mean_7d": 0.7030204106,
        "ndci_slope_7d": 0.0443250822,
        "sst_anomaly": 4.8489848667,
        "wind_speed_3d": 17.0630024025,
        "ndci_x_wind": 11.9956389558,
    },
    "high": {
        "ndci_mean_7d": 0.8648788853,
        "ndci_slope_7d": 0.0113464088,
        "sst_anomaly": 1.0535954907,
        "wind_speed_3d": 19.6299292809,
        "ndci_x_wind": 16.9775113543,
    },
}


@lru_cache(maxsize=1)
def load_booster() -> xgb.Booster:
    booster = xgb.Booster()
    booster.load_model(MODEL_PATH)
    return booster


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def predict_model_demo(
    scenario: Literal["low", "medium", "high"] = "medium",
) -> dict:
    feature_values = MODEL_DEMO_SCENARIOS[scenario]
    values = [feature_values[name] for name in FEATURE_NAMES]
    matrix = xgb.DMatrix([values], feature_names=FEATURE_NAMES)
    booster = load_booster()

    probability = float(booster.predict(matrix)[0])
    contributions = booster.predict(matrix, pred_contribs=True)[0].tolist()
    shap_values = contributions[:-1]
    base_value = float(contributions[-1])
    raw_margin = base_value + sum(shap_values)

    factors = []
    for name, value, shap_value in zip(
        FEATURE_NAMES, values, shap_values, strict=True
    ):
        label, unit = FEATURE_METADATA[name]
        factors.append(
            {
                "name": label,
                "feature_key": name,
                "value": round(float(value), 4),
                "unit": unit,
                "impact": (
                    "increase"
                    if shap_value > 0.001
                    else "decrease"
                    if shap_value < -0.001
                    else "none"
                ),
                "shap_value": round(float(shap_value), 4),
            }
        )

    top_factors = sorted(
        factors, key=lambda factor: abs(factor["shap_value"]), reverse=True
    )[:3]
    return {
        "scenario": scenario,
        "probability": probability,
        "risk_score": round(probability * 100, 1),
        "raw_margin": raw_margin,
        "base_value": base_value,
        "factors": factors,
        "top_factors": top_factors,
        "shap_sum_matches_probability": math.isclose(
            sigmoid(raw_margin), probability, rel_tol=1e-5, abs_tol=1e-6
        ),
    }
