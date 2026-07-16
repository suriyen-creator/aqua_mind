from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from backend.dataset_builder import (
    MODEL_FEATURES,
    SATELLITE_FEATURES,
    WEATHER_FEATURES,
)


@dataclass(frozen=True)
class ValidationPolicy:
    minimum_total_rows: int = 100
    minimum_test_positive_events: int = 10
    minimum_recall: float = 0.70
    minimum_precision: float = 0.50
    maximum_brier_score: float = 0.25


def expected_calibration_error(
    y_true: np.ndarray, probability: np.ndarray, bins: int = 10
) -> float:
    edges = np.linspace(0, 1, bins + 1)
    total = len(y_true)
    error = 0.0
    for lower, upper in zip(edges[:-1], edges[1:], strict=True):
        mask = (probability >= lower) & (
            probability <= upper if upper == 1 else probability < upper
        )
        if not np.any(mask):
            continue
        error += (np.count_nonzero(mask) / total) * abs(
            float(np.mean(probability[mask])) - float(np.mean(y_true[mask]))
        )
    return float(error)


def choose_threshold(y_true: np.ndarray, probability: np.ndarray) -> float:
    candidates = np.linspace(0.1, 0.9, 81)
    scores = [f1_score(y_true, probability >= value, zero_division=0) for value in candidates]
    return float(candidates[int(np.argmax(scores))])


def calculate_metrics(
    y_true: np.ndarray,
    probability: np.ndarray,
    threshold: float,
) -> dict[str, float | int | None]:
    predicted = probability >= threshold
    has_both_classes = len(np.unique(y_true)) == 2
    return {
        "rows": len(y_true),
        "positive_events": int(np.sum(y_true)),
        "threshold": round(threshold, 4),
        "precision": round(float(precision_score(y_true, predicted, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predicted, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, predicted, zero_division=0)), 4),
        "pr_auc": (
            round(float(average_precision_score(y_true, probability)), 4)
            if has_both_classes
            else None
        ),
        "roc_auc": (
            round(float(roc_auc_score(y_true, probability)), 4)
            if has_both_classes
            else None
        ),
        "brier_score": round(float(brier_score_loss(y_true, probability)), 4),
        "log_loss": (
            round(float(log_loss(y_true, probability, labels=[0, 1])), 4)
            if len(y_true)
            else None
        ),
        "ece_10_bins": round(expected_calibration_error(y_true, probability), 4),
    }


def _chronological_split(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ordered = frame.sort_values("issue_time").reset_index(drop=True)
    train_end = max(1, int(len(ordered) * 0.6))
    calibration_end = max(train_end + 1, int(len(ordered) * 0.8))
    if calibration_end >= len(ordered):
        raise ValueError("Dataset is too small for train/calibration/test separation")
    return (
        ordered.iloc[:train_end],
        ordered.iloc[train_end:calibration_end],
        ordered.iloc[calibration_end:],
    )


def _fit_xgboost(
    train: pd.DataFrame,
    features: list[str],
    seed: int = 42,
) -> xgb.XGBClassifier:
    positive = int(train["is_bloom_t3_t5"].sum())
    negative = len(train) - positive
    scale_pos_weight = negative / positive if positive else 1.0
    model = xgb.XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.04,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_lambda=2.0,
        objective="binary:logistic",
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
        random_state=seed,
        n_jobs=1,
    )
    model.fit(train[features], train["is_bloom_t3_t5"])
    return model


def _evaluate_group(
    name: str,
    features: list[str],
    train: pd.DataFrame,
    calibration: pd.DataFrame,
    test: pd.DataFrame,
) -> tuple[dict[str, Any], Any, xgb.XGBClassifier]:
    raw_model = _fit_xgboost(train, features)
    calibrated = CalibratedClassifierCV(FrozenEstimator(raw_model), method="sigmoid")
    calibrated.fit(calibration[features], calibration["is_bloom_t3_t5"])
    calibration_probability = calibrated.predict_proba(calibration[features])[:, 1]
    threshold = choose_threshold(
        calibration["is_bloom_t3_t5"].to_numpy(), calibration_probability
    )
    probability = calibrated.predict_proba(test[features])[:, 1]
    return (
        {
            "name": name,
            "features": features,
            "metrics": calculate_metrics(
                test["is_bloom_t3_t5"].to_numpy(), probability, threshold
            ),
        },
        calibrated,
        raw_model,
    )


def train_and_validate(
    dataset_csv: str | Path,
    output_dir: str | Path,
    *,
    policy: ValidationPolicy = ValidationPolicy(),
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    def blocked(reason: str, rows: int) -> dict[str, Any]:
        report = {
            "status": "blocked_missing_validation_evidence",
            "operational_approved": False,
            "reason": reason,
            "verified_dataset_rows": rows,
            "policy": asdict(policy),
            "artifacts_created": ["validation_report.json"],
        }
        (output_dir / "validation_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return report

    frame = pd.read_csv(dataset_csv)
    required = ["station_id", "issue_time", "is_bloom_t3_t5", *MODEL_FEATURES]
    missing = [column for column in required if column not in frame]
    if missing:
        raise ValueError(f"dataset missing columns: {', '.join(missing)}")
    frame["issue_time"] = pd.to_datetime(
        frame["issue_time"], utc=True, errors="coerce", format="mixed"
    )
    frame = frame.dropna(subset=["issue_time", "is_bloom_t3_t5"]).copy()
    for feature in MODEL_FEATURES:
        frame[feature] = pd.to_numeric(frame[feature], errors="coerce")
    if len(frame) < policy.minimum_total_rows:
        return blocked(
            f"Need at least {policy.minimum_total_rows} verified rows; found {len(frame)}",
            len(frame),
        )
    train, calibration, test = _chronological_split(frame)
    for split_name, split in (
        ("train", train),
        ("calibration", calibration),
        ("test", test),
    ):
        if split["is_bloom_t3_t5"].nunique() < 2:
            return blocked(
                f"{split_name} split must contain bloom and non-bloom rows",
                len(frame),
            )

    prevalence = float(train["is_bloom_t3_t5"].mean())
    baseline_probability = np.full(len(test), prevalence)
    evaluations: dict[str, Any] = {
        "prevalence_baseline": {
            "features": [],
            "metrics": calculate_metrics(
                test["is_bloom_t3_t5"].to_numpy(), baseline_probability, 0.5
            ),
        }
    }

    logistic = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=2000, class_weight="balanced"),
    )
    logistic.fit(train[MODEL_FEATURES], train["is_bloom_t3_t5"])
    logistic_probability = logistic.predict_proba(test[MODEL_FEATURES])[:, 1]
    evaluations["logistic_baseline"] = {
        "features": MODEL_FEATURES,
        "metrics": calculate_metrics(
            test["is_bloom_t3_t5"].to_numpy(), logistic_probability, 0.5
        ),
    }

    fitted: dict[str, tuple[Any, xgb.XGBClassifier]] = {}
    for name, features in (
        ("satellite_only_xgboost", SATELLITE_FEATURES),
        ("weather_only_xgboost", WEATHER_FEATURES),
        ("full_xgboost", MODEL_FEATURES),
    ):
        evaluation, calibrated, raw_model = _evaluate_group(
            name, features, train, calibration, test
        )
        evaluations[name] = evaluation
        fitted[name] = (calibrated, raw_model)

    spatial_holdouts: dict[str, Any] = {}
    if frame["station_id"].nunique() >= 2:
        for station_id in sorted(frame["station_id"].unique()):
            spatial_train = frame[frame["station_id"] != station_id]
            spatial_test = frame[frame["station_id"] == station_id]
            if (
                spatial_train["is_bloom_t3_t5"].nunique() == 2
                and spatial_test["is_bloom_t3_t5"].nunique() == 2
            ):
                model = _fit_xgboost(spatial_train, MODEL_FEATURES)
                probability = model.predict_proba(spatial_test[MODEL_FEATURES])[:, 1]
                spatial_holdouts[station_id] = calculate_metrics(
                    spatial_test["is_bloom_t3_t5"].to_numpy(), probability, 0.5
                )

    full_metrics = evaluations["full_xgboost"]["metrics"]
    operational_approved = bool(
        len(frame) >= policy.minimum_total_rows
        and full_metrics["positive_events"] >= policy.minimum_test_positive_events
        and full_metrics["recall"] >= policy.minimum_recall
        and full_metrics["precision"] >= policy.minimum_precision
        and full_metrics["brier_score"] <= policy.maximum_brier_score
    )
    report = {
        "status": "approved" if operational_approved else "validation_failed",
        "operational_approved": operational_approved,
        "warning": (
            "Thresholds are a preliminary governance policy and require domain-owner "
            "approval before field use. Passing them does not remove the need for review."
        ),
        "policy": asdict(policy),
        "split": {
            "method": "chronological 60% train / 20% calibration / 20% test",
            "train_rows": len(train),
            "calibration_rows": len(calibration),
            "test_rows": len(test),
            "train_end": str(train["issue_time"].max()),
            "calibration_end": str(calibration["issue_time"].max()),
            "test_end": str(test["issue_time"].max()),
        },
        "evaluations": evaluations,
        "spatial_holdouts": spatial_holdouts,
    }
    (output_dir / "validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if operational_approved:
        calibrated, raw_model = fitted["full_xgboost"]
        joblib.dump(calibrated, output_dir / "calibrated_model.joblib")
        raw_model.save_model(output_dir / "xgboost_model.json")
        (output_dir / "model_metadata.json").write_text(
            json.dumps(
                {
                    "operational_approved": True,
                    "model_version": datetime.now(timezone.utc).strftime(
                        "field-xgb-%Y%m%dT%H%M%SZ"
                    ),
                    "trained_at": datetime.now(timezone.utc).isoformat(),
                    "feature_names": MODEL_FEATURES,
                    "target": "verified bloom occurrence from t+3 through t+5 days",
                    "shap_output_space": "raw_margin_before_probability_calibration",
                    "decision_threshold": full_metrics["threshold"],
                    "validation_report": "validation_report.json",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return report
