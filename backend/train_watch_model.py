from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb


BACKEND_DIR = Path(__file__).resolve().parent
MODEL_PATH = BACKEND_DIR / "environmental_watch_model.json"
METADATA_PATH = BACKEND_DIR / "environmental_watch_model.metadata.json"

FEATURE_NAMES = [
    "air_temperature_mean_d0_3",
    "precipitation_sum_d0_3",
    "wind_speed_mean_d0_3",
    "wind_gust_max_d0_3",
    "air_temperature_mean_d3_5",
    "precipitation_sum_d3_5",
    "wind_speed_mean_d3_5",
    "sst_at_issue",
    "wave_height_at_issue",
    "current_velocity_at_issue",
    "ndci_latest",
    "ndci_slope_30d",
    "satellite_age_days",
    "valid_pixel_ratio",
]


def _clip(value: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.clip((value - low) / (high - low), 0.0, 1.0)


def expert_watch_score(rows: np.ndarray) -> np.ndarray:
    """Transparent suitability rules used only to teach the SHAP surrogate.

    Weather/Ocean contributes up to 75 points, the base is 5 points, and
    quality-gated Sentinel-2 evidence contributes no more than 20 points.
    This target is an environmental watch index, never an event probability.
    """
    by_name = {name: rows[:, index] for index, name in enumerate(FEATURE_NAMES)}
    score = np.full(rows.shape[0], 5.0)
    score += 7.0 * _clip(by_name["air_temperature_mean_d0_3"], 26.0, 33.0)
    score += 4.0 * _clip(by_name["precipitation_sum_d0_3"], 0.0, 35.0)
    score += 13.0 * (1.0 - _clip(by_name["wind_speed_mean_d0_3"], 1.0, 9.0))
    score += 7.0 * (1.0 - _clip(by_name["wind_speed_mean_d3_5"], 1.0, 9.0))
    score += 7.0 * _clip(by_name["air_temperature_mean_d3_5"], 26.0, 33.0)
    score += 4.0 * _clip(by_name["precipitation_sum_d3_5"], 0.0, 45.0)
    score += 16.0 * _clip(by_name["sst_at_issue"], 26.0, 32.0)
    score += 9.0 * (1.0 - _clip(by_name["wave_height_at_issue"], 0.2, 1.8))
    score += 8.0 * (1.0 - _clip(by_name["current_velocity_at_issue"], 0.1, 1.2))

    satellite_ok = (
        np.isfinite(by_name["ndci_latest"])
        & np.isfinite(by_name["satellite_age_days"])
        & np.isfinite(by_name["valid_pixel_ratio"])
        & (by_name["satellite_age_days"] <= 10.0)
        & (by_name["valid_pixel_ratio"] >= 0.05)
    )
    ndci = np.nan_to_num(by_name["ndci_latest"], nan=-0.02)
    ndci_slope = np.nan_to_num(by_name["ndci_slope_30d"], nan=-0.002)
    score += satellite_ok * 15.0 * _clip(ndci, -0.02, 0.10)
    score += satellite_ok * 5.0 * _clip(ndci_slope, -0.002, 0.004)
    return np.clip(score, 0.0, 100.0)


def build_training_rows(count: int = 30000, seed: int = 28) -> np.ndarray:
    rng = np.random.default_rng(seed)
    rows = np.column_stack(
        [
            rng.uniform(23.0, 36.0, count),
            rng.uniform(0.0, 80.0, count),
            rng.uniform(0.0, 15.0, count),
            rng.uniform(0.0, 25.0, count),
            rng.uniform(23.0, 36.0, count),
            rng.uniform(0.0, 100.0, count),
            rng.uniform(0.0, 15.0, count),
            rng.uniform(24.0, 34.0, count),
            rng.uniform(0.0, 3.0, count),
            rng.uniform(0.0, 2.0, count),
            rng.uniform(-0.05, 0.20, count),
            rng.uniform(-0.01, 0.01, count),
            rng.uniform(0.0, 25.0, count),
            rng.uniform(0.0, 1.0, count),
        ]
    )
    missing_satellite = rng.random(count) < 0.45
    rows[missing_satellite, 10:14] = np.nan
    return rows


def train() -> None:
    rows = build_training_rows()
    target = expert_watch_score(rows)
    model = xgb.XGBRegressor(
        n_estimators=180,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=28,
        n_jobs=4,
    )
    frame = pd.DataFrame(rows, columns=FEATURE_NAMES)
    model.fit(frame, target)
    model.save_model(MODEL_PATH)

    prediction = model.predict(frame)
    metadata = {
        "model_version": "weather-first-rule-surrogate-v1",
        "output": "environmental_watch_index_0_100_not_probability",
        "training_target": "transparent expert-rule score",
        "training_rows": int(rows.shape[0]),
        "weather_ocean_max_points": 75,
        "base_points": 5,
        "satellite_max_points": 20,
        "satellite_gate": "age <= 10 days and valid_pixel_ratio >= 0.05",
        "mean_absolute_surrogate_error": round(float(np.mean(np.abs(prediction - target))), 4),
        "limitations": [
            "No field ground truth was used to create the target.",
            "The output is a watch index, not bloom probability or field accuracy.",
            "SHAP explains the XGBoost rule surrogate, not biological causality.",
        ],
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    train()
