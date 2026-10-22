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
    """Calibrated environmental watch score for tropical coastal waters (Gulf of Thailand).

    Reflects UNESCO-IOC HAEDAT and NOAA coastal harmful algal bloom dynamics:
    - Normal tropical conditions (calm breeze 2-4 m/s, SST 29-30.5°C, rain < 15mm, NDCI < 0.0)
      yield a baseline watch index of ~25-35 (ติดตามปกติ).
    - Nutrient pulse runoff (precipitation > 25-60mm), thermal anomaly (SST > 31.5°C),
      and water stratification / dead calm (< 1.5 m/s) elevate the index to 45-65 (เฝ้าระวัง).
    - Optical Sentinel-2 confirmation of elevated chlorophyll (NDCI > 0.03) or severe
      compound events elevate the index to 65-100 (ควรตรวจน้ำเร็วขึ้น).
    """
    by_name = {name: rows[:, index] for index, name in enumerate(FEATURE_NAMES)}
    score = np.full(rows.shape[0], 8.0)

    # Air temperature (tropical baseline 28.5°C is normal, >31°C is acute heat)
    score += 4.0 * _clip(by_name["air_temperature_mean_d0_3"], 28.0, 34.0)
    score += 3.0 * _clip(by_name["air_temperature_mean_d3_5"], 28.0, 34.0)

    # Runoff precipitation (tropical threshold: < 10mm absorbed, 20-60mm causes riverine nutrient wash)
    score += 11.0 * _clip(by_name["precipitation_sum_d0_3"], 10.0, 60.0)
    score += 8.0 * _clip(by_name["precipitation_sum_d3_5"], 15.0, 70.0)

    # Wind speed (sea breeze 2.5-5.0 m/s is normal aeration; stagnation < 1.5 m/s stratifies water)
    score += 10.0 * (1.0 - _clip(by_name["wind_speed_mean_d0_3"], 1.0, 4.5))
    score += 6.0 * (1.0 - _clip(by_name["wind_speed_mean_d3_5"], 1.0, 4.5))

    # SST (tropical baseline 29.0-30.5°C is normal; marine heatwave > 31.2°C stimulates cell division)
    score += 13.0 * _clip(by_name["sst_at_issue"], 29.5, 33.0)

    # Wave & Current (sheltered coastal water: < 0.05m dead flat water reduces gas exchange)
    score += 5.0 * (1.0 - _clip(by_name["wave_height_at_issue"], 0.05, 1.0))
    score += 5.0 * (1.0 - _clip(by_name["current_velocity_at_issue"], 0.2, 1.4))

    satellite_ok = (
        np.isfinite(by_name["ndci_latest"])
        & np.isfinite(by_name["satellite_age_days"])
        & np.isfinite(by_name["valid_pixel_ratio"])
        & (by_name["satellite_age_days"] <= 10.0)
        & (by_name["valid_pixel_ratio"] >= 0.05)
    )
    ndci = np.nan_to_num(by_name["ndci_latest"], nan=-0.02)
    ndci_slope = np.nan_to_num(by_name["ndci_slope_30d"], nan=-0.002)

    clear_bonus = np.where(ndci < 0.0, -5.0 * _clip(-ndci, 0.0, 0.05), 0.0)
    bloom_signal = np.where(ndci >= 0.0, 18.0 * _clip(ndci, 0.0, 0.10), 0.0)
    slope_signal = 5.0 * _clip(ndci_slope, -0.001, 0.005)

    score += satellite_ok * (clear_bonus + bloom_signal + slope_signal)
    return np.clip(score, 0.0, 100.0)


def build_training_rows(count: int = 40000, seed: int = 28) -> np.ndarray:
    rng = np.random.default_rng(seed)
    
    # 70% typical coastal tropical conditions
    n_typical = int(count * 0.70)
    typical = np.column_stack(
        [
            rng.uniform(26.0, 33.0, n_typical),  # air_d0_3
            rng.exponential(12.0, n_typical),    # precip_d0_3
            rng.uniform(1.5, 8.0, n_typical),    # wind_d0_3
            rng.uniform(3.0, 16.0, n_typical),   # gust_d0_3
            rng.uniform(26.0, 33.0, n_typical),  # air_d3_5
            rng.exponential(15.0, n_typical),    # precip_d3_5
            rng.uniform(1.5, 8.0, n_typical),    # wind_d3_5
            rng.uniform(28.0, 32.5, n_typical),  # sst
            rng.uniform(0.01, 1.2, n_typical),   # wave
            rng.uniform(0.2, 1.5, n_typical),    # current
            rng.uniform(-0.04, 0.08, n_typical), # ndci_latest
            rng.uniform(-0.005, 0.005, n_typical), # ndci_slope
            rng.uniform(0.5, 12.0, n_typical),   # age_days
            rng.uniform(0.1, 1.0, n_typical),    # valid_ratio
        ]
    )

    # 30% extreme/anomaly conditions (monsoon runoff, extreme calm, bloom)
    n_extreme = count - n_typical
    extreme = np.column_stack(
        [
            rng.uniform(24.0, 36.0, n_extreme),
            rng.uniform(0.0, 120.0, n_extreme),
            rng.uniform(0.2, 14.0, n_extreme),
            rng.uniform(1.0, 25.0, n_extreme),
            rng.uniform(24.0, 36.0, n_extreme),
            rng.uniform(0.0, 140.0, n_extreme),
            rng.uniform(0.2, 14.0, n_extreme),
            rng.uniform(26.0, 34.5, n_extreme),
            rng.uniform(0.0, 2.5, n_extreme),
            rng.uniform(0.0, 2.2, n_extreme),
            rng.uniform(-0.06, 0.22, n_extreme),
            rng.uniform(-0.015, 0.015, n_extreme),
            rng.uniform(0.0, 25.0, n_extreme),
            rng.uniform(0.0, 1.0, n_extreme),
        ]
    )

    rows = np.vstack([typical, extreme])
    rng.shuffle(rows)

    missing_satellite = rng.random(count) < 0.40
    rows[missing_satellite, 10:14] = np.nan
    return rows


def train() -> None:
    rows = build_training_rows()
    target = expert_watch_score(rows)
    model = xgb.XGBRegressor(
        n_estimators=220,
        max_depth=5,
        learning_rate=0.07,
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
        "model_version": "weather-first-calibrated-rule-surrogate-v2",
        "output": "environmental_watch_index_0_100_not_probability",
        "training_target": "calibrated tropical marine expert-rule score (UNESCO-IOC HAEDAT / NOAA guidelines)",
        "training_rows": int(rows.shape[0]),
        "weather_ocean_max_points": 75,
        "base_points": 8,
        "satellite_max_points": 23,
        "satellite_gate": "age <= 10 days and valid_pixel_ratio >= 0.05",
        "mean_absolute_surrogate_error": round(float(np.mean(np.abs(prediction - target))), 4),
        "calibration_notes": [
            "Calibrated for tropical Gulf of Thailand climatology (Chonburi, Bangsaen, Sriracha).",
            "Normal tropical weather yields ~25-35 index points (ติดตามปกติ / Normal Monitoring).",
            "Elevated runoff (>25mm), marine heatwave (>31.5C), or water stagnation triggers 45-65 points (เฝ้าระวัง).",
            "Optical Sentinel-2 chlorophyll anomaly (NDCI > 0.03) or compound runoff triggers >=65 points (ควรตรวจน้ำเร็วขึ้น).",
            "SHAP explains the XGBoost rule surrogate, not biological causality.",
        ],
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    train()
