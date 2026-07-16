from fastapi.testclient import TestClient

from backend.main import app, build_bangsaen_context_response
from backend.model_service import predict_model_demo


client = TestClient(app)


def test_health_reports_model_and_data_assets() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_available": True,
        "mock_data_available": True,
        "live_context_available": True,
        "operational_model_available": False,
    }


def test_station_list_separates_model_demo_from_live_context() -> None:
    response = client.get("/api/stations")
    stations = response.json()

    assert response.status_code == 200
    assert stations["chonburi_01"]["data_mode"] == "synthetic_model_demo"
    assert stations["chonburi_03"]["data_mode"] == "live_context"


def test_default_model_demo_runs_xgboost_and_real_shap_contributions() -> None:
    response = client.get("/api/risk/current", params={"station_id": "chonburi_01"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["assessment_status"] == "model_demo"
    assert payload["analysis_method"] == "xgboost_shap_demo"
    assert payload["risk_score"] == 58.7
    assert payload["shap_output_space"] == "raw_margin"
    assert len(payload["features"]) == 5
    assert all(item["shap_value"] is not None for item in payload["features"])
    assert payload["confidence_score"] is None


def test_model_shap_values_add_up_to_prediction() -> None:
    prediction = predict_model_demo("medium")

    assert prediction["shap_sum_matches_probability"] is True


def test_model_scenarios_preserve_low_medium_high_order() -> None:
    scores = []
    for scenario in ("low", "medium", "high"):
        response = client.get(
            "/api/risk/current",
            params={"station_id": "chonburi_01", "scenario": scenario},
        )
        scores.append(response.json()["risk_score"])

    assert scores == sorted(scores)
    assert scores[0] < 40 < scores[1] < 70 < scores[2]


def test_live_context_suppresses_risk_without_model_compatible_sentinel2() -> None:
    payload = build_bangsaen_context_response(
        {
            "retrieved_at": "2026-07-17T01:10:00Z",
            "from_snapshot": False,
            "errors": [],
            "marine": {
                "observed_at": "2026-07-17T01:00:00Z",
                "sea_surface_temperature": 30.0,
                "wave_height": 0.58,
                "ocean_current_velocity": 0.3,
            },
            "satellite": {
                "status": "unavailable",
                "observed_at": None,
                "chlorophyll_a": None,
                "valid_pixel_count": 0,
            },
        }
    ).model_dump()

    assert payload["assessment_status"] == "insufficient_data"
    assert payload["risk_score"] is None
    assert payload["analysis_method"] == "insufficient_data"
    assert payload["confidence_score"] is None
    assert payload["imagery_mode"] == "no_imagery"
    assert all(item["shap_value"] is None for item in payload["features"])


def test_unknown_station_returns_404() -> None:
    response = client.get("/api/risk/current", params={"station_id": "missing"})

    assert response.status_code == 404


def test_pipeline_status_exposes_ground_truth_and_operational_gate() -> None:
    response = client.get("/api/pipeline/status")
    payload = response.json()

    assert response.status_code == 200
    assert payload["verified_ground_truth_rows"] >= 0
    assert payload["operational_model"]["available"] is False
