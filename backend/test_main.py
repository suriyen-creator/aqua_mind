from fastapi.testclient import TestClient

from backend.environmental_watch import predict_environmental_watch
from backend.main import app, build_environmental_watch_response


client = TestClient(app)


ENVIRONMENT = {
    "issue_time": "2026-07-17T05:00:00Z",
    "latitude": 13.2912,
    "longitude": 100.9014,
    "features": {
        "air_temperature_mean_d0_3": 29.2,
        "precipitation_sum_d0_3": 1.6,
        "cloud_cover_mean_d0_3": 83.0,
        "wind_speed_mean_d0_3": 5.6,
        "wind_gust_max_d0_3": 10.4,
        "air_temperature_mean_d3_5": 29.1,
        "precipitation_sum_d3_5": 10.1,
        "cloud_cover_mean_d3_5": 98.1,
        "wind_speed_mean_d3_5": 5.6,
        "wind_gust_max_d3_5": 11.9,
        "sst_at_issue": 29.9,
        "wave_height_at_issue": 0.66,
        "current_velocity_at_issue": 0.2,
        "sea_level_at_issue": 1.24,
    },
    "lineage": {
        "weather_url": "https://api.open-meteo.com/test-weather",
        "marine_url": "https://marine-api.open-meteo.com/test-marine",
    },
}

SATELLITE = {
    "observed_at": "2026-07-14T03:54:36Z",
    "data_age_days": 3.0,
    "ndci_latest": 0.0157,
    "ndci_slope_30d": -0.00047,
    "valid_pixel_ratio": 1.0,
}


def test_health_reports_model_and_data_assets() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_available"] is True


def test_every_station_uses_one_weather_first_live_mode() -> None:
    response = client.get("/api/stations")
    stations = response.json()
    assert response.status_code == 200
    assert {station["data_mode"] for station in stations.values()} == {
        "live_weather_watch"
    }


def test_live_endpoint_uses_real_weather_contract_without_satellite(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.main.fetch_current_environment_forecast",
        lambda latitude, longitude: ENVIRONMENT,
    )
    response = client.get("/api/risk/current", params={"station_id": "chonburi_01"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["assessment_status"] == "environmental_watch"
    assert payload["analysis_method"] == "weather_first_xgboost_shap_rule_watch"
    assert payload["score_is_probability"] is False
    assert payload["risk_score"] is not None
    assert payload["imagery_mode"] == "no_imagery"
    assert payload["confidence_score"] == 75
    assert all(source["status"] == "available" for source in payload["data_sources"][:2])
    assert any(item["shap_value"] is not None for item in payload["features"])


def test_bangsaen_watch_uses_quality_gated_satellite_as_secondary_evidence() -> None:
    payload = build_environmental_watch_response(
        "chonburi_03", ENVIRONMENT, SATELLITE
    ).model_dump()

    assert payload["assessment_status"] == "environmental_watch"
    assert payload["imagery_mode"] == "context_only"
    assert payload["confidence_score"] == 100
    assert payload["score_is_probability"] is False
    assert payload["shap_output_space"] == "watch_index_points"
    assert "ไม่ใช่โอกาสเกิดบลูม" in payload["score_label"]
    assert len(payload["rule_basis"]) == 4


def test_stale_satellite_is_excluded_but_weather_watch_still_runs() -> None:
    stale = {**SATELLITE, "data_age_days": 12.0}
    prediction = predict_environmental_watch(ENVIRONMENT["features"], stale)

    assert prediction["satellite_used"] is False
    assert prediction["evidence_completeness"] == 75
    assert prediction["watch_index"] >= 0
    assert prediction["shap_sum_matches_score"] is True
    assert "ไม่มีภาพ Sentinel-2" in prediction["plain_language_explanation"]


def test_unknown_station_returns_404() -> None:
    response = client.get("/api/risk/current", params={"station_id": "missing"})
    assert response.status_code == 404


def test_pipeline_status_exposes_ground_truth_and_operational_gate() -> None:
    response = client.get("/api/pipeline/status")
    payload = response.json()
    assert response.status_code == 200
    assert payload["verified_ground_truth_rows"] >= 0
    assert payload["operational_model"]["available"] is False
