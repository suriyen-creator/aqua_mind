from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from backend.dataset_builder import MODEL_FEATURES
from backend.sentinel2 import parse_utc


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts" / "operational"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"
CALIBRATED_MODEL_PATH = ARTIFACT_DIR / "calibrated_model.joblib"
RAW_MODEL_PATH = ARTIFACT_DIR / "xgboost_model.json"
VALIDATION_REPORT_PATH = ARTIFACT_DIR / "validation_report.json"


def get_operational_model_status() -> dict[str, Any]:
    required = [METADATA_PATH, CALIBRATED_MODEL_PATH, RAW_MODEL_PATH]
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        validation = (
            json.loads(VALIDATION_REPORT_PATH.read_text(encoding="utf-8"))
            if VALIDATION_REPORT_PATH.is_file()
            else None
        )
        return {
            "available": False,
            "operational_approved": False,
            "reason": (
                validation.get("reason")
                if validation
                else f"missing validated artifacts: {', '.join(missing)}"
            ),
            "validation": validation,
        }
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    approved = metadata.get("operational_approved") is True
    return {
        "available": approved,
        "operational_approved": approved,
        "reason": None if approved else "model metadata is not operationally approved",
        "metadata": metadata,
    }


def build_live_feature_vector(snapshot: dict[str, Any]) -> dict[str, float]:
    sentinel = snapshot["sentinel"]["summary"]
    environment = snapshot["environment"]["features"]
    issue_time = parse_utc(snapshot["environment"]["issue_time"])
    observed_at = parse_utc(sentinel["observed_at"])
    values: dict[str, Any] = {
        "ndci_latest": sentinel["ndci_latest"],
        "ndci_mean_30d": sentinel["ndci_mean_30d"],
        "ndci_slope_30d": sentinel["ndci_slope_30d"],
        "ndwi_latest": sentinel["ndwi_latest"],
        "valid_pixel_ratio": sentinel["valid_pixel_ratio"],
        "satellite_age_days": max(
            0.0, (issue_time - observed_at).total_seconds() / 86400
        ),
        **environment,
    }
    missing = [
        name
        for name in MODEL_FEATURES
        if values.get(name) is None or not np.isfinite(float(values[name]))
    ]
    if missing:
        raise ValueError(f"live feature vector is incomplete: {', '.join(missing)}")
    return {name: float(values[name]) for name in MODEL_FEATURES}


@lru_cache(maxsize=1)
def _load_models() -> tuple[Any, xgb.Booster, dict[str, Any]]:
    status = get_operational_model_status()
    if not status["available"]:
        raise RuntimeError(status["reason"])
    calibrated = joblib.load(CALIBRATED_MODEL_PATH)
    raw = xgb.Booster()
    raw.load_model(RAW_MODEL_PATH)
    return calibrated, raw, status["metadata"]


def predict_operational(snapshot: dict[str, Any]) -> dict[str, Any]:
    calibrated, raw, metadata = _load_models()
    vector = build_live_feature_vector(snapshot)
    frame = pd.DataFrame([vector], columns=MODEL_FEATURES)
    probability = float(calibrated.predict_proba(frame)[0, 1])
    matrix = xgb.DMatrix(frame, feature_names=MODEL_FEATURES)
    contributions = raw.predict(matrix, pred_contribs=True)[0]
    shap_values = contributions[:-1]
    base_value = float(contributions[-1])
    factors = [
        {
            "name": name,
            "value": vector[name],
            "shap_value": float(shap_value),
            "impact": "increase" if shap_value > 0 else "decrease",
        }
        for name, shap_value in zip(MODEL_FEATURES, shap_values, strict=True)
    ]
    threshold = float(metadata["decision_threshold"])
    return {
        "probability": probability,
        "risk_score": round(probability * 100, 1),
        "decision_threshold": threshold,
        "predicted_positive": probability >= threshold,
        "factors": factors,
        "top_factors": sorted(
            factors, key=lambda factor: abs(factor["shap_value"]), reverse=True
        )[:3],
        "raw_base_value": base_value,
        "model_metadata": metadata,
        "warning": (
            "SHAP explains the raw XGBoost margin. Displayed probability is "
            "post-calibration, so SHAP values are not probability-point changes."
        ),
    }
