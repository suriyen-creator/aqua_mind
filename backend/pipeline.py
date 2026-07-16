from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from backend.dataset_builder import (
    WEATHER_FEATURES,
    build_supervised_dataset,
    write_dataset_result,
)
from backend.environment_data import (
    fetch_current_environment_forecast,
    fetch_historical_environment_features,
)
from backend.operational_model import get_operational_model_status
from backend.sentinel2 import (
    BANGSAEN_AOI,
    extract_time_series,
    iso_utc,
    search_sentinel2_items,
    summarize_time_series,
)
from backend.train_validated_model import train_and_validate


BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
SNAPSHOT_PATH = DATA_DIR / "bangsaen_operational_snapshot.json"
SATELLITE_CSV = DATA_DIR / "sentinel2_observations.csv"
FORECAST_CSV = DATA_DIR / "environment_forecasts.csv"
GROUND_TRUTH_CSV = DATA_DIR / "ground_truth.csv"
DATASET_CSV = DATA_DIR / "supervised_bloom_t3_t5.csv"
DATASET_AUDIT = DATA_DIR / "supervised_bloom_t3_t5.audit.json"
OPERATIONAL_ARTIFACT_DIR = BACKEND_DIR / "artifacts" / "operational"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _upsert_csv(path: Path, new_frame: pd.DataFrame, keys: list[str]) -> None:
    if path.is_file():
        previous = pd.read_csv(path)
        combined = pd.concat([previous, new_frame], ignore_index=True)
    else:
        combined = new_frame
    combined = combined.drop_duplicates(subset=keys, keep="last")
    combined.to_csv(path, index=False)


def refresh_live_data(
    *,
    lookback_days: int = 120,
    max_scenes: int = 10,
    minimum_valid_ratio: float = 0.05,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    items = search_sentinel2_items(
        now - timedelta(days=lookback_days),
        now,
        BANGSAEN_AOI,
        limit=max(max_scenes * 3, 20),
    )
    observations, rejected = extract_time_series(
        items[:max_scenes],
        BANGSAEN_AOI,
        minimum_valid_ratio=minimum_valid_ratio,
    )
    if not observations:
        raise RuntimeError(
            "No usable Sentinel-2 observations. See rejected scenes and consider "
            "a longer lookback or AOI review."
        )
    summary = summarize_time_series(observations, now=now)
    environment = fetch_current_environment_forecast(
        latitude=(BANGSAEN_AOI.south + BANGSAEN_AOI.north) / 2,
        longitude=(BANGSAEN_AOI.west + BANGSAEN_AOI.east) / 2,
        now=now,
    )
    model_status = get_operational_model_status()
    snapshot = {
        "generated_at": iso_utc(now),
        "station_id": BANGSAEN_AOI.station_id,
        "aoi": {
            "name": BANGSAEN_AOI.name,
            "bbox": BANGSAEN_AOI.bbox,
        },
        "sentinel": {
            "status": "available" if summary["data_age_days"] <= 10 else "stale",
            "summary": summary,
            "observations": observations,
            "rejected": rejected,
        },
        "environment": environment,
        "model_status": model_status,
        "assessment": {
            "can_predict": model_status["available"],
            "reason": (
                None
                if model_status["available"]
                else "Real inputs are available, but no field-validated model artifact exists."
            ),
        },
    }
    _write_json(SNAPSHOT_PATH, snapshot)

    satellite_rows = []
    for observation in observations:
        satellite_rows.append(
            {
                "station_id": observation["station_id"],
                "observed_at": observation["observed_at"],
                "item_id": observation["item_id"],
                "ndci_mean": observation["ndci"]["mean"],
                "ndci_median": observation["ndci"]["median"],
                "ndci_std": observation["ndci"]["std"],
                "ndwi_mean": observation["ndwi"]["mean"],
                "ndwi_median": observation["ndwi"]["median"],
                "valid_pixel_ratio": observation["valid_pixel_ratio"],
                "scene_cloud_cover_percent": observation[
                    "scene_cloud_cover_percent"
                ],
                "source_collection": "sentinel-2-l2a",
                "cloud_mask": "SCL class 6",
            }
        )
    # The search window is a reproducible source of truth; overwrite it to
    # remove duplicate-tile acquisitions rejected by the latest QC policy.
    pd.DataFrame(satellite_rows).sort_values("observed_at").to_csv(
        SATELLITE_CSV, index=False
    )
    forecast_row = {
        "station_id": BANGSAEN_AOI.station_id,
        "issue_time": environment["issue_time"],
        **{name: environment["features"].get(name) for name in WEATHER_FEATURES},
        "weather_url": environment["lineage"]["weather_url"],
        "marine_url": environment["lineage"]["marine_url"],
    }
    _upsert_csv(
        FORECAST_CSV, pd.DataFrame([forecast_row]), ["station_id", "issue_time"]
    )
    return snapshot


def build_dataset() -> dict[str, Any]:
    if not GROUND_TRUTH_CSV.is_file():
        raise FileNotFoundError(
            f"Missing {GROUND_TRUTH_CSV}. Copy ground_truth_template.csv and add "
            "VERIFIED field observations; do not fabricate negative rows."
        )
    result = build_supervised_dataset(
        SATELLITE_CSV, FORECAST_CSV, GROUND_TRUTH_CSV
    )
    write_dataset_result(result, DATASET_CSV, DATASET_AUDIT)
    return result.audit


def backfill_forecasts(*, processing_latency_hours: int = 8) -> dict[str, Any]:
    if not SATELLITE_CSV.is_file():
        raise FileNotFoundError("Run refresh-live before backfill-forecasts")
    satellite = pd.read_csv(SATELLITE_CSV)
    rows = []
    errors = []
    latitude = (BANGSAEN_AOI.south + BANGSAEN_AOI.north) / 2
    longitude = (BANGSAEN_AOI.west + BANGSAEN_AOI.east) / 2
    for _, observation in satellite.iterrows():
        decision_time = pd.Timestamp(observation["observed_at"])
        if decision_time.tzinfo is None:
            decision_time = decision_time.tz_localize("UTC")
        decision_time = decision_time.to_pydatetime() + timedelta(
            hours=processing_latency_hours
        )
        try:
            result = fetch_historical_environment_features(
                latitude, longitude, decision_time
            )
            rows.append(
                {
                    "station_id": observation["station_id"],
                    "issue_time": result["forecast_run_initialization_time"],
                    "decision_time": result["decision_time"],
                    **{
                        name: result["features"].get(name)
                        for name in WEATHER_FEATURES
                    },
                    "weather_url": result["lineage"]["weather"]["url"],
                    "marine_url": result["lineage"]["marine_url"],
                }
            )
        except Exception as exc:
            errors.append(
                {"item_id": observation["item_id"], "reason": str(exc)}
            )
    if rows:
        _upsert_csv(
            FORECAST_CSV,
            pd.DataFrame(rows),
            ["station_id", "issue_time"],
        )
    return {"created_rows": len(rows), "errors": errors}


def refresh_environment_only() -> dict[str, Any]:
    if not SNAPSHOT_PATH.is_file():
        raise FileNotFoundError("Run refresh-live before refresh-environment")
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    environment = fetch_current_environment_forecast(
        latitude=(BANGSAEN_AOI.south + BANGSAEN_AOI.north) / 2,
        longitude=(BANGSAEN_AOI.west + BANGSAEN_AOI.east) / 2,
        now=now,
    )
    snapshot["generated_at"] = iso_utc(now)
    snapshot["environment"] = environment
    snapshot["model_status"] = get_operational_model_status()
    snapshot["assessment"] = {
        "can_predict": snapshot["model_status"]["available"],
        "reason": (
            None
            if snapshot["model_status"]["available"]
            else snapshot["model_status"]["reason"]
        ),
    }
    _write_json(SNAPSHOT_PATH, snapshot)
    forecast_row = {
        "station_id": BANGSAEN_AOI.station_id,
        "issue_time": environment["issue_time"],
        **{name: environment["features"].get(name) for name in WEATHER_FEATURES},
        "weather_url": environment["lineage"]["weather_url"],
        "marine_url": environment["lineage"]["marine_url"],
    }
    _upsert_csv(
        FORECAST_CSV, pd.DataFrame([forecast_row]), ["station_id", "issue_time"]
    )
    return {
        "generated_at": snapshot["generated_at"],
        "environment_features": environment["features"],
        "assessment": snapshot["assessment"],
    }


def pipeline_status() -> dict[str, Any]:
    ground_truth_rows = 0
    verified_rows = 0
    if GROUND_TRUTH_CSV.is_file():
        truth = pd.read_csv(GROUND_TRUTH_CSV)
        ground_truth_rows = len(truth)
        if "verification_status" in truth:
            verified_rows = int(
                truth["verification_status"].astype(str).str.upper().eq("VERIFIED").sum()
            )
    return {
        "snapshot_exists": SNAPSHOT_PATH.is_file(),
        "satellite_observation_rows": (
            len(pd.read_csv(SATELLITE_CSV)) if SATELLITE_CSV.is_file() else 0
        ),
        "forecast_rows": len(pd.read_csv(FORECAST_CSV)) if FORECAST_CSV.is_file() else 0,
        "ground_truth_rows": ground_truth_rows,
        "verified_ground_truth_rows": verified_rows,
        "supervised_dataset_rows": (
            len(pd.read_csv(DATASET_CSV)) if DATASET_CSV.is_file() else 0
        ),
        "operational_model": get_operational_model_status(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AquaMind real-data pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    refresh = subparsers.add_parser("refresh-live")
    refresh.add_argument("--lookback-days", type=int, default=120)
    refresh.add_argument("--max-scenes", type=int, default=10)
    refresh.add_argument("--minimum-valid-ratio", type=float, default=0.05)
    subparsers.add_parser("build-dataset")
    backfill = subparsers.add_parser("backfill-forecasts")
    backfill.add_argument("--processing-latency-hours", type=int, default=8)
    subparsers.add_parser("refresh-environment")
    subparsers.add_parser("train")
    subparsers.add_parser("status")
    args = parser.parse_args()
    if args.command == "refresh-live":
        result = refresh_live_data(
            lookback_days=args.lookback_days,
            max_scenes=args.max_scenes,
            minimum_valid_ratio=args.minimum_valid_ratio,
        )
        output = {
            "generated_at": result["generated_at"],
            "sentinel_status": result["sentinel"]["status"],
            "sentinel_summary": result["sentinel"]["summary"],
            "rejected_scenes": len(result["sentinel"]["rejected"]),
            "assessment": result["assessment"],
        }
    elif args.command == "build-dataset":
        output = build_dataset()
    elif args.command == "backfill-forecasts":
        output = backfill_forecasts(
            processing_latency_hours=args.processing_latency_hours
        )
    elif args.command == "refresh-environment":
        output = refresh_environment_only()
    elif args.command == "train":
        output = train_and_validate(DATASET_CSV, OPERATIONAL_ARTIFACT_DIR)
    else:
        output = pipeline_status()
    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
