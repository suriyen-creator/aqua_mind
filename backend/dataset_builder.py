from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SATELLITE_FEATURES = [
    "ndci_latest",
    "ndci_mean_30d",
    "ndci_slope_30d",
    "ndwi_latest",
    "valid_pixel_ratio",
    "satellite_age_days",
]

WEATHER_FEATURES = [
    "air_temperature_mean_d0_3",
    "precipitation_sum_d0_3",
    "cloud_cover_mean_d0_3",
    "wind_speed_mean_d0_3",
    "wind_gust_max_d0_3",
    "air_temperature_mean_d3_5",
    "precipitation_sum_d3_5",
    "cloud_cover_mean_d3_5",
    "wind_speed_mean_d3_5",
    "wind_gust_max_d3_5",
    "sst_at_issue",
    "wave_height_at_issue",
    "current_velocity_at_issue",
    "sea_level_at_issue",
]

MODEL_FEATURES = SATELLITE_FEATURES + WEATHER_FEATURES

GROUND_TRUTH_REQUIRED = [
    "event_id",
    "station_id",
    "observed_at",
    "latitude",
    "longitude",
    "bloom_status",
    "verification_status",
    "measurement_method",
    "source",
]


@dataclass(frozen=True)
class DatasetBuildResult:
    data: pd.DataFrame
    audit: dict[str, Any]


def _require_columns(frame: pd.DataFrame, columns: list[str], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {', '.join(missing)}")


def load_verified_ground_truth(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    _require_columns(frame, GROUND_TRUTH_REQUIRED, "ground truth")
    frame["observed_at"] = pd.to_datetime(
        frame["observed_at"], utc=True, errors="coerce", format="mixed"
    )
    frame["bloom_status"] = pd.to_numeric(frame["bloom_status"], errors="coerce")
    verified = frame[
        frame["verification_status"].astype(str).str.upper().eq("VERIFIED")
        & frame["observed_at"].notna()
        & frame["bloom_status"].isin([0, 1])
    ].copy()
    return verified.sort_values("observed_at")


def _prepare_satellite(
    frame: pd.DataFrame, processing_latency_hours: int = 8
) -> pd.DataFrame:
    required = [
        "station_id",
        "observed_at",
        "item_id",
        "ndci_median",
        "ndwi_median",
        "valid_pixel_ratio",
    ]
    _require_columns(frame, required, "satellite observations")
    frame = frame.copy()
    frame["observed_at"] = pd.to_datetime(
        frame["observed_at"], utc=True, errors="coerce", format="mixed"
    )
    frame = frame.dropna(subset=["observed_at"]).sort_values(
        ["station_id", "observed_at"]
    )
    rows: list[dict[str, Any]] = []
    for station_id, station in frame.groupby("station_id"):
        station = station.sort_values("observed_at")
        for _, current in station.iterrows():
            satellite_observed_at = current["observed_at"]
            issue_time = satellite_observed_at + pd.Timedelta(
                hours=processing_latency_hours
            )
            history = station[
                (station["observed_at"] <= satellite_observed_at)
                & (
                    station["observed_at"]
                    >= satellite_observed_at - pd.Timedelta(days=30)
                )
            ]
            offsets = (
                (history["observed_at"] - history["observed_at"].min())
                .dt.total_seconds()
                .to_numpy()
                / 86400
            )
            ndci = history["ndci_median"].astype(float).to_numpy()
            slope = (
                float(np.polyfit(offsets, ndci, 1)[0])
                if len(history) >= 2 and np.ptp(offsets) > 0
                else 0.0
            )
            rows.append(
                {
                    "station_id": station_id,
                    "issue_time": issue_time,
                    "satellite_item_id": current["item_id"],
                    "satellite_observed_at": satellite_observed_at,
                    "ndci_latest": float(current["ndci_median"]),
                    "ndci_mean_30d": float(np.mean(ndci)),
                    "ndci_slope_30d": slope,
                    "ndwi_latest": float(current["ndwi_median"]),
                    "valid_pixel_ratio": float(current["valid_pixel_ratio"]),
                    "satellite_age_days": processing_latency_hours / 24,
                    "satellite_observation_count_30d": len(history),
                }
            )
    return pd.DataFrame(rows)


def _prepare_forecasts(frame: pd.DataFrame) -> pd.DataFrame:
    _require_columns(frame, ["station_id", "issue_time", *WEATHER_FEATURES], "forecast")
    frame = frame.copy()
    frame["issue_time"] = pd.to_datetime(
        frame["issue_time"], utc=True, errors="coerce", format="mixed"
    )
    return frame.dropna(subset=["issue_time"]).sort_values(
        ["station_id", "issue_time"]
    )


def build_supervised_dataset(
    satellite_csv: str | Path,
    forecast_csv: str | Path,
    ground_truth_csv: str | Path,
    *,
    horizon_start_days: int = 3,
    horizon_end_days: int = 5,
    maximum_forecast_age_hours: int = 12,
) -> DatasetBuildResult:
    """Build t -> t+3..5 rows without treating missing reports as negatives."""
    satellite = _prepare_satellite(pd.read_csv(satellite_csv))
    forecasts = _prepare_forecasts(pd.read_csv(forecast_csv))
    truth = load_verified_ground_truth(ground_truth_csv)
    built: list[dict[str, Any]] = []
    audit: dict[str, Any] = {
        "satellite_candidates": len(satellite),
        "verified_ground_truth_rows": len(truth),
        "excluded_no_prior_forecast": 0,
        "excluded_no_verified_truth_in_horizon": 0,
        "horizon": f"t+{horizon_start_days} through t+{horizon_end_days} days",
        "negative_label_policy": (
            "A negative is created only when at least one VERIFIED field sample "
            "inside the horizon has bloom_status=0. Missing reports are excluded."
        ),
    }
    max_age = pd.Timedelta(hours=maximum_forecast_age_hours)
    for _, satellite_row in satellite.iterrows():
        issue_time = satellite_row["issue_time"]
        station_id = satellite_row["station_id"]
        candidates = forecasts[
            (forecasts["station_id"] == station_id)
            & (forecasts["issue_time"] <= issue_time)
            & (forecasts["issue_time"] >= issue_time - max_age)
        ]
        if candidates.empty:
            audit["excluded_no_prior_forecast"] += 1
            continue
        forecast = candidates.iloc[-1]
        horizon_start = issue_time + pd.Timedelta(days=horizon_start_days)
        horizon_end_exclusive = issue_time + pd.Timedelta(days=horizon_end_days + 1)
        matched_truth = truth[
            (truth["station_id"] == station_id)
            & (truth["observed_at"] >= horizon_start)
            & (truth["observed_at"] < horizon_end_exclusive)
        ]
        if matched_truth.empty:
            audit["excluded_no_verified_truth_in_horizon"] += 1
            continue
        label = int(matched_truth["bloom_status"].max())
        row = {
            **satellite_row.to_dict(),
            **{feature: forecast[feature] for feature in WEATHER_FEATURES},
            "forecast_issue_time": forecast["issue_time"],
            "forecast_age_hours": (
                issue_time - forecast["issue_time"]
            ).total_seconds()
            / 3600,
            "is_bloom_t3_t5": label,
            "label_sample_count": len(matched_truth),
            "label_event_ids": ";".join(matched_truth["event_id"].astype(str)),
            "label_window_start": horizon_start,
            "label_window_end": horizon_end_exclusive - pd.Timedelta(microseconds=1),
        }
        built.append(row)
    data = pd.DataFrame(built)
    if data.empty:
        data = pd.DataFrame(
            columns=[
                "station_id",
                "issue_time",
                "satellite_item_id",
                "satellite_observed_at",
                *MODEL_FEATURES,
                "forecast_issue_time",
                "forecast_age_hours",
                "is_bloom_t3_t5",
                "label_sample_count",
                "label_event_ids",
                "label_window_start",
                "label_window_end",
            ]
        )
    audit["built_rows"] = len(data)
    audit["positive_rows"] = (
        int(data["is_bloom_t3_t5"].sum()) if not data.empty else 0
    )
    audit["stations"] = sorted(data["station_id"].unique().tolist()) if not data.empty else []
    return DatasetBuildResult(data=data, audit=audit)


def write_dataset_result(
    result: DatasetBuildResult,
    output_csv: str | Path,
    audit_json: str | Path,
) -> None:
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    result.data.to_csv(output_csv, index=False)
    Path(audit_json).write_text(
        json.dumps(result.audit, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
