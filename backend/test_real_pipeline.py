from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from backend.dataset_builder import WEATHER_FEATURES, build_supervised_dataset
from backend.environment_data import _aggregate_window
from backend.sentinel2 import extract_time_series


def test_duplicate_sentinel_tiles_keep_higher_quality_acquisition(monkeypatch) -> None:
    rows = {
        "low": {
            "station_id": "chonburi_03",
            "item_id": "low",
            "observed_at": "2026-06-24T03:54:35Z",
            "valid_pixel_ratio": 0.8,
            "scene_cloud_cover_percent": 20.0,
        },
        "high": {
            "station_id": "chonburi_03",
            "item_id": "high",
            "observed_at": "2026-06-24T03:54:38Z",
            "valid_pixel_ratio": 0.95,
            "scene_cloud_cover_percent": 30.0,
        },
    }

    monkeypatch.setattr(
        "backend.sentinel2.extract_scene_indices",
        lambda item, aoi: rows[item["id"]],
    )
    observations, rejected = extract_time_series(
        [{"id": "low"}, {"id": "high"}], minimum_valid_ratio=0.05
    )

    assert [row["item_id"] for row in observations] == ["high"]
    assert rejected[0]["item_id"] == "low"
    assert "duplicate acquisition date" in rejected[0]["reason"]


def test_environment_features_use_future_windows_from_issue_time() -> None:
    issue = datetime(2026, 1, 1, tzinfo=timezone.utc)
    weather = [
        {
            "time": issue + pd.Timedelta(days=day),
            "temperature_2m": 20 + day,
            "precipitation": 1,
            "cloud_cover": 50,
            "wind_speed_10m": 2,
            "wind_gusts_10m": 3,
        }
        for day in range(6)
    ]
    marine = [
        {
            "time": issue + pd.Timedelta(days=day),
            "sea_surface_temperature": 30 + day,
            "wave_height": 0.5,
            "ocean_current_velocity": 0.2,
            "sea_level_height_msl": float(day),
        }
        for day in range(6)
    ]

    features = _aggregate_window(weather, marine, issue, 3, 6, "d3_5")

    assert features["air_temperature_mean_d3_5"] == 24.0
    assert features["precipitation_sum_d3_5"] == 3.0
    assert features["sea_level_range_d3_5"] == 2.0


def _write_contract_files(tmp_path, truth_rows):
    satellite = pd.DataFrame(
        [
            {
                "station_id": "chonburi_03",
                "observed_at": "2026-01-01T00:00:00Z",
                "item_id": "S2-test",
                "ndci_median": 0.1,
                "ndwi_median": 0.2,
                "valid_pixel_ratio": 0.9,
            }
        ]
    )
    forecast_row = {
        "station_id": "chonburi_03",
        "issue_time": "2026-01-01T00:00:00Z",
        **{feature: 1.0 for feature in WEATHER_FEATURES},
    }
    satellite_path = tmp_path / "satellite.csv"
    forecast_path = tmp_path / "forecast.csv"
    truth_path = tmp_path / "truth.csv"
    satellite.to_csv(satellite_path, index=False)
    pd.DataFrame([forecast_row]).to_csv(forecast_path, index=False)
    pd.DataFrame(truth_rows).to_csv(truth_path, index=False)
    return satellite_path, forecast_path, truth_path


def test_missing_ground_truth_is_excluded_not_labeled_negative(tmp_path) -> None:
    unverified = {
        "event_id": "event-1",
        "station_id": "chonburi_03",
        "observed_at": "2026-01-04T12:00:00Z",
        "latitude": 13.29,
        "longitude": 100.89,
        "bloom_status": 0,
        "verification_status": "UNVERIFIED",
        "measurement_method": "visual",
        "source": "user",
    }
    paths = _write_contract_files(tmp_path, [unverified])

    result = build_supervised_dataset(*paths)

    assert result.data.empty
    assert result.audit["excluded_no_verified_truth_in_horizon"] == 1


def test_verified_t3_event_creates_positive_label(tmp_path) -> None:
    verified = {
        "event_id": "event-2",
        "station_id": "chonburi_03",
        "observed_at": "2026-01-04T12:00:00Z",
        "latitude": 13.29,
        "longitude": 100.89,
        "bloom_status": 1,
        "verification_status": "VERIFIED",
        "measurement_method": "microscopy",
        "source": "field_campaign",
    }
    paths = _write_contract_files(tmp_path, [verified])

    result = build_supervised_dataset(*paths)

    assert len(result.data) == 1
    assert result.data.iloc[0]["is_bloom_t3_t5"] == 1
    assert result.data.iloc[0]["label_event_ids"] == "event-2"
