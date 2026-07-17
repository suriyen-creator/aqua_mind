from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.live_data import age_hours, fetch_bangsaen_live_inputs
from backend.environment_data import fetch_current_environment_forecast
from backend.environmental_watch import predict_environmental_watch
from backend.model_service import MODEL_PATH, predict_model_demo
from backend.operational_model import (
    get_operational_model_status,
    predict_operational,
)
from backend.pipeline import pipeline_status


app = FastAPI(title="AquaMind AI Engine Core", version="1.2.0")

BACKEND_DIR = Path(__file__).resolve().parent
MOCK_DATA_PATH = BACKEND_DIR / "mock_data.csv"
DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("AQUAMIND_CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

STATIONS_DATABASE = {
    "chonburi_01": {
        "location": "Chonburi Coast — Weather-first Live Watch",
        "lat": 13.3611,
        "lon": 100.9234,
        "data_mode": "live_weather_watch",
    },
    "chonburi_02": {
        "location": "Sriracha Harbor — Weather-first Live Watch",
        "lat": 13.1389,
        "lon": 100.9125,
        "data_mode": "live_weather_watch",
    },
    "chonburi_03": {
        "location": "Bangsaen — Weather-first + Sentinel-2 Live Watch",
        "lat": 13.2912,
        "lon": 100.9014,
        "data_mode": "live_weather_watch",
    },
}


class Factor(BaseModel):
    name: str
    feature_key: str | None = None
    value: float
    unit: str
    impact: Literal["increase", "decrease", "none"]
    shap_value: float | None = None
    plain_language: str | None = None


class DataSourceInfo(BaseModel):
    name: str
    source_type: Literal[
        "synthetic_training_data",
        "simulated_sentinel2",
        "marine_model",
        "satellite_context",
        "sentinel2_l2a",
        "weather_forecast",
    ]
    status: Literal[
        "available", "stale", "unavailable", "cached", "synthetic"
    ]
    observed_at: str | None
    age_hours: float | None
    note: str
    url: str | None = None


class CurrentRiskResponse(BaseModel):
    station_id: str
    assessment_status: Literal[
        "model_demo", "operational_model", "environmental_watch", "insufficient_data"
    ]
    risk_score: float | None
    score_label: str = "ดัชนีเฝ้าระวังสภาพแวดล้อม"
    score_is_probability: bool = False
    risk_level: str
    alert_status: str
    shap_explanation: str
    location: str
    lat: float
    lon: float
    timestamp: str
    recommendations: list[str]
    features: list[Factor]
    history_trend: list[float]
    data_status: Literal[
        "synthetic_model_demo", "live_context", "live_watch", "live_operational"
    ]
    data_source: str
    observed_at: str
    is_demo: bool
    data_age_hours: float | None
    confidence_score: int | None
    confidence_level: str
    confidence_note: str
    imagery_status: Literal["simulated", "available", "stale", "unavailable"]
    imagery_mode: Literal["simulated_fresh", "context_only", "no_imagery"]
    analysis_method: Literal[
        "xgboost_shap_demo",
        "xgboost_shap_operational",
        "weather_first_xgboost_shap_rule_watch",
        "insufficient_data",
    ]
    history_period_days: int
    data_sources: list[DataSourceInfo]
    limitations: list[str]
    model_name: str | None
    model_version: str | None
    forecast_horizon: str | None
    shap_output_space: Literal["raw_margin", "watch_index_points"] | None
    rule_basis: list[str] = []


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_available: bool
    mock_data_available: bool
    live_context_available: bool
    operational_model_available: bool


def _risk_metadata(score: float) -> tuple[str, str, list[str]]:
    if score >= 70:
        return (
            "สูง",
            "High Alert (Demo)",
            [
                "ตรวจ DO, pH และสีของน้ำในพื้นที่ก่อนดำเนินมาตรการ",
                "เก็บตัวอย่างน้ำเพื่อยืนยันชนิดและความหนาแน่นของแพลงก์ตอน",
                "เตรียมระบบเติมอากาศและประสานเจ้าหน้าที่หากผลภาคสนามผิดปกติ",
            ],
        )
    if score >= 40:
        return (
            "ปานกลาง",
            "Watch (Demo)",
            [
                "เพิ่มรอบตรวจ DO และสังเกตสีของน้ำภายใน 24 ชั่วโมง",
                "เปรียบเทียบกับภาพ Sentinel-2 รอบถัดไปเมื่อผ่าน Cloud mask",
                "ยังไม่ประกาศเหตุบลูมจนกว่าจะมีข้อมูลภาคสนามยืนยัน",
            ],
        )
    return (
        "ต่ำ",
        "Normal (Demo)",
        [
            "ติดตามข้อมูลตามรอบปกติ",
            "บันทึกค่าคุณภาพน้ำเพื่อสร้าง Ground truth สำหรับ Validation",
        ],
    )


def _history_for_scenario(scenario: str, score: float) -> list[float]:
    if scenario == "low":
        return [8.0, 9.5, 10.2, 9.8, 10.5, score]
    if scenario == "high":
        return [42.0, 51.0, 63.0, 74.0, 86.0, score]
    return [22.0, 29.0, 35.0, 43.0, 51.0, score]


def build_model_demo_response(
    station_id: str,
    scenario: Literal["low", "medium", "high"],
) -> CurrentRiskResponse:
    station = STATIONS_DATABASE[station_id]
    prediction = predict_model_demo(scenario)
    score = prediction["risk_score"]
    level, alert, recommendations = _risk_metadata(score)

    factor_phrases = []
    for factor in prediction["top_factors"]:
        direction = "เพิ่ม" if factor["shap_value"] > 0 else "ลด"
        factor_phrases.append(
            f"{factor['name']} {direction}ค่า raw margin {abs(factor['shap_value']):.3f}"
        )
    explanation = (
        "SHAP Technical Demo: "
        + "; ".join(factor_phrases)
        + ". ค่า SHAP อยู่ใน raw-margin space และอธิบายโมเดล XGBoost "
        "ที่ฝึกจากข้อมูลสังเคราะห์ ไม่ใช่สาเหตุเชิงชีววิทยาหรือหลักฐานความแม่นยำภาคสนาม"
    )

    return CurrentRiskResponse(
        station_id=station_id,
        assessment_status="model_demo",
        risk_score=score,
        risk_level=level,
        alert_status=alert,
        shap_explanation=explanation,
        location=station["location"],
        lat=station["lat"],
        lon=station["lon"],
        timestamp=f"Synthetic model scenario: {scenario}",
        recommendations=recommendations,
        features=[Factor(**factor) for factor in prediction["factors"]],
        history_trend=_history_for_scenario(scenario, score),
        data_status="synthetic_model_demo",
        data_source="backend/mock_data.csv + backend/xgboost_model.json",
        observed_at="synthetic scenario — no field observation",
        is_demo=True,
        data_age_hours=None,
        confidence_score=None,
        confidence_level="ยังไม่ผ่าน Calibration",
        confidence_note=(
            "ไม่แสดง Confidence เชิงปฏิบัติการ เพราะโมเดลฝึกจากข้อมูลสังเคราะห์ "
            "และยังไม่มี Independent field validation"
        ),
        imagery_status="simulated",
        imagery_mode="simulated_fresh",
        analysis_method="xgboost_shap_demo",
        history_period_days=6,
        data_sources=[
            DataSourceInfo(
                name="Synthetic Sentinel-2 feature scenario",
                source_type="simulated_sentinel2",
                status="synthetic",
                observed_at=None,
                age_hours=None,
                note="NDCI และตัวแปรประกอบเป็นข้อมูลจำลองเพื่อทดสอบ pipeline",
            ),
            DataSourceInfo(
                name="AquaMind synthetic training dataset",
                source_type="synthetic_training_data",
                status="synthetic",
                observed_at=None,
                age_hours=None,
                note="ใช้ทดสอบ XGBoost inference และ SHAP เท่านั้น",
            ),
        ],
        limitations=[
            "ผลนี้เป็น Technical Demo บนข้อมูลสังเคราะห์ ไม่ใช่ผลจากบางแสนวันนี้",
            "Probability ยังไม่ผ่าน Calibration กับ Ground truth ภาคสนาม",
            "SHAP อธิบายพฤติกรรมโมเดล ไม่ได้พิสูจน์ว่า Feature เป็นสาเหตุของ Bloom",
        ],
        model_name="XGBoost binary classifier",
        model_version="synthetic-mvp-1",
        forecast_horizon="เป้าหมาย 3–5 วัน; Technical Demo ยังไม่ผ่านการยืนยัน horizon",
        shap_output_space="raw_margin",
    )


def build_bangsaen_context_response(inputs: dict) -> CurrentRiskResponse:
    station_id = "chonburi_03"
    station = STATIONS_DATABASE[station_id]
    marine = inputs["marine"]
    satellite = inputs["satellite"]
    retrieved_at = datetime.fromisoformat(
        inputs["retrieved_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)
    marine_age = round(age_hours(marine["observed_at"], retrieved_at), 1)
    satellite_observed_at = satellite.get("observed_at")
    satellite_age = (
        round(age_hours(satellite_observed_at, retrieved_at), 1)
        if satellite_observed_at
        else None
    )
    marine_status = "cached" if inputs.get("from_snapshot") else "available"
    satellite_status = satellite["status"]
    imagery_mode = "context_only" if satellite_status == "available" else "no_imagery"
    primary_age = satellite_age if satellite_age is not None else marine_age
    primary_observed_at = satellite_observed_at or marine["observed_at"]
    operational_snapshot = inputs.get("operational_snapshot")
    forecast = (
        operational_snapshot.get("environment") if operational_snapshot else None
    )

    features = [
        Factor(
            name="Sea Surface Temperature (marine context)",
            feature_key="sea_surface_temperature",
            value=marine["sea_surface_temperature"],
            unit="°C",
            impact="none",
        ),
        Factor(
            name="Wave Height (marine context)",
            feature_key="wave_height",
            value=marine["wave_height"],
            unit="m",
            impact="none",
        ),
        Factor(
            name="Ocean Current Velocity (marine context)",
            feature_key="ocean_current_velocity",
            value=marine["ocean_current_velocity"],
            unit="km/h",
            impact="none",
        ),
    ]
    if satellite.get("ndci_mean") is not None:
        features.extend(
            [
                Factor(
                    name="Sentinel-2 NDCI median (real L2A)",
                    feature_key="ndci_latest",
                    value=satellite["ndci_mean"],
                    unit="index",
                    impact="none",
                ),
                Factor(
                    name="Sentinel-2 NDWI median (real L2A)",
                    feature_key="ndwi_latest",
                    value=satellite["ndwi_mean"],
                    unit="index",
                    impact="none",
                ),
                Factor(
                    name="Sentinel-2 valid water pixel ratio",
                    feature_key="valid_pixel_ratio",
                    value=satellite["valid_pixel_ratio"],
                    unit="ratio",
                    impact="none",
                ),
            ]
        )
    if forecast:
        forecast_features = forecast.get("features", {})
        for key, label, unit in (
            ("wind_speed_mean_d0_3", "Forecast wind mean day 0–3", "m/s"),
            ("precipitation_sum_d0_3", "Forecast precipitation day 0–3", "mm"),
            ("sst_at_issue", "Sea surface temperature at issue time", "°C"),
        ):
            value = forecast_features.get(key)
            if value is not None:
                features.append(
                    Factor(
                        name=label,
                        feature_key=key,
                        value=value,
                        unit=unit,
                        impact="none",
                    )
                )

    has_real_sentinel = satellite.get("ndci_mean") is not None
    explanation = (
        "มี Sentinel-2 L2A/NDCI/NDWI และ Weather/Ocean forecast จริงแล้ว "
        "แต่ยังไม่รัน XGBoost/SHAP เพราะยังไม่มีโมเดลที่ผ่าน Ground-truth "
        "validation และได้รับอนุมัติเป็น Operational artifact"
        if has_real_sentinel
        else "ยังไม่รัน XGBoost/SHAP เพราะไม่มี Sentinel-2 ที่ผ่านเกณฑ์ข้อมูล "
        "และยังไม่มีโมเดลที่ผ่าน Ground-truth validation"
    )

    return CurrentRiskResponse(
        station_id=station_id,
        assessment_status="insufficient_data",
        risk_score=None,
        risk_level="ประเมินไม่ได้",
        alert_status="Insufficient data",
        shap_explanation=explanation,
        location=station["location"],
        lat=station["lat"],
        lon=station["lon"],
        timestamp=f"Latest decision snapshot at {inputs['retrieved_at']}",
        recommendations=[
            "ไม่ประกาศระดับความเสี่ยงจากข้อมูลชุดนี้",
            "เพิ่มผลตรวจน้ำภาคสนามแบบ VERIFIED เพื่อฝึกและ Validate โมเดล",
            "ตรวจ DO, pH, ความขุ่น และสีของน้ำหากพบความผิดปกติในพื้นที่",
        ],
        features=features,
        history_trend=[],
        data_status="live_context",
        data_source="Sentinel-2 L2A + Open-Meteo Weather/Marine (prediction gated)",
        observed_at=primary_observed_at,
        is_demo=False,
        data_age_hours=primary_age,
        confidence_score=None,
        confidence_level="ไม่สามารถประเมิน",
        confidence_note="ยังไม่มี Operational model ที่ผ่านเกณฑ์ จึงไม่คำนวณ Risk confidence",
        imagery_status=satellite_status,
        imagery_mode=imagery_mode,
        analysis_method="insufficient_data",
        history_period_days=0,
        data_sources=[
            DataSourceInfo(
                name="Open-Meteo Marine API",
                source_type="marine_model",
                status=marine_status,
                observed_at=marine["observed_at"],
                age_hours=marine_age,
                note="บริบท SST คลื่น และกระแสน้ำจากแบบจำลอง ไม่ใช่ Sentinel-2",
                url="https://open-meteo.com/en/docs/marine-weather-api",
            ),
            DataSourceInfo(
                name="Sentinel-2 L2A via Earth Search",
                source_type="sentinel2_l2a",
                status=satellite_status,
                observed_at=satellite_observed_at,
                age_hours=satellite_age,
                note=(
                    "NDCI/NDWI จาก B03/B04/B05/B08 หลังใช้ SCL water mask; "
                    "ยังไม่ใช้ทำนายจนกว่าโมเดลจริงผ่าน Validation"
                ),
                url="https://earth-search.aws.element84.com/v1/",
            ),
        ]
        + (
            [
                DataSourceInfo(
                    name="Open-Meteo Weather/Ocean forecast",
                    source_type="weather_forecast",
                    status="available",
                    observed_at=forecast["issue_time"],
                    age_hours=round(age_hours(forecast["issue_time"], retrieved_at), 1),
                    note=(
                        "Forecast variables use the run available at decision time; "
                        "coastal ocean values remain coarse model context"
                    ),
                    url="https://open-meteo.com/en/docs",
                )
            ]
            if forecast
            else []
        ),
        limitations=[
            "มี Sentinel-2 ingestion แล้ว แต่ยังไม่มี Ground truth ภาคสนามสำหรับฝึกและตรวจสอบโมเดล",
            "NDCI ในชายฝั่งอาจถูกรบกวนจากตะกอน น้ำตื้น และ adjacency effect",
            "ระบบจงใจระงับ Risk score เพื่อป้องกันการแจ้งเตือนเกินจริง",
        ],
        model_name=None,
        model_version=None,
        forecast_horizon=None,
        shap_output_space=None,
    )


def build_environmental_watch_response(
    station_id: str,
    environment: dict,
    satellite: dict | None = None,
) -> CurrentRiskResponse:
    """Build one honest live assessment shared by every AquaMind surface.

    The score is a weather-first environmental watch index. It is not an
    observed bloom probability. Sentinel-2 is optional, quality-gated
    secondary evidence, and SHAP explains the rule-surrogate score.
    """
    station = STATIONS_DATABASE[station_id]
    features = environment["features"]
    prediction = predict_environmental_watch(features, satellite)
    issue_time = environment["issue_time"]
    retrieved_at = datetime.now(timezone.utc)
    data_age = round(age_hours(issue_time, retrieved_at), 1)
    satellite_used = prediction["satellite_used"]
    satellite_status = (
        "available"
        if satellite_used
        else "stale"
        if satellite and satellite.get("observed_at")
        else "unavailable"
    )
    satellite_age_hours = (
        round(float(satellite["data_age_days"]) * 24, 1)
        if satellite and isinstance(satellite.get("data_age_days"), (int, float))
        else None
    )
    evidence = prediction["evidence_completeness"]
    confidence_level = (
        "Weather/Ocean + ภาพดาวเทียมผ่าน QC"
        if satellite_used
        else "Weather/Ocean พร้อมใช้; ไม่มีภาพเสริม"
    )
    lineage = environment.get("lineage", {})

    return CurrentRiskResponse(
        station_id=station_id,
        assessment_status="environmental_watch",
        risk_score=prediction["watch_index"],
        score_label="ดัชนีเฝ้าระวังสภาพแวดล้อม (ไม่ใช่โอกาสเกิดบลูม)",
        score_is_probability=False,
        risk_level=prediction["watch_level"],
        alert_status="Environmental watch — ต้องตรวจน้ำก่อนยืนยัน",
        shap_explanation=(
            prediction["plain_language_explanation"]
            + " คำอธิบายนี้มาจาก SHAP ของ XGBoost ที่เลียนแบบกฎเฝ้าระวัง "
            "จึงอธิบายคะแนน ไม่ได้ยืนยันสาเหตุหรือชนิดแพลงก์ตอน"
        ),
        location=station["location"],
        lat=station["lat"],
        lon=station["lon"],
        timestamp=issue_time,
        recommendations=prediction["recommendations"],
        features=[Factor(**factor) for factor in prediction["factors"]],
        history_trend=[],
        data_status="live_watch",
        data_source=(
            "Open-Meteo Weather/Marine (primary) + Sentinel-2 L2A (secondary)"
            if satellite_used
            else "Open-Meteo Weather/Marine (primary); Sentinel-2 unavailable/stale"
        ),
        observed_at=issue_time,
        is_demo=False,
        data_age_hours=data_age,
        confidence_score=evidence,
        confidence_level=confidence_level,
        confidence_note=(
            f"ความครบถ้วนของหลักฐาน {evidence}/100 ไม่ใช่ความแม่นยำของการทำนาย; "
            "Weather/Ocean คิดเป็นฐานหลัก และภาพเพิ่มความครบถ้วนเมื่อผ่าน QC"
        ),
        imagery_status=satellite_status,
        imagery_mode="context_only" if satellite_used else "no_imagery",
        analysis_method="weather_first_xgboost_shap_rule_watch",
        history_period_days=0,
        data_sources=[
            DataSourceInfo(
                name="Open-Meteo Weather forecast",
                source_type="weather_forecast",
                status="available",
                observed_at=issue_time,
                age_hours=data_age,
                note="ข้อมูลพยากรณ์จริงเป็นแกนหลักของดัชนีสำหรับพิกัดที่เลือก",
                url=lineage.get("weather_url", "https://open-meteo.com/en/docs"),
            ),
            DataSourceInfo(
                name="Open-Meteo Marine forecast",
                source_type="marine_model",
                status="available",
                observed_at=issue_time,
                age_hours=data_age,
                note="SST คลื่น และกระแสน้ำจากกริดแบบจำลอง ใช้เป็นบริบทชายฝั่ง",
                url=lineage.get("marine_url", "https://open-meteo.com/en/docs/marine-weather-api"),
            ),
            DataSourceInfo(
                name="Sentinel-2 L2A via Earth Search",
                source_type="sentinel2_l2a",
                status=satellite_status,
                observed_at=satellite.get("observed_at") if satellite else None,
                age_hours=satellite_age_hours,
                note=(
                    "NDCI/แนวโน้มภาพผ่านเกณฑ์ จึงใช้เป็นหลักฐานรองของคะแนน"
                    if satellite_used
                    else "ไม่มีภาพที่สดและผ่าน QC ระบบไม่เติมค่าภาพแทน และยังคำนวณจาก Weather/Ocean ได้"
                ),
                url="https://earth-search.aws.element84.com/v1/",
            ),
        ],
        limitations=[
            "ดัชนีนี้เป็น Environmental watch index ไม่ใช่ความน่าจะเป็นที่เกิด Bloom",
            "XGBoost ฝึกให้เลียนแบบกฎที่เปิดเผย ยังไม่ได้ฝึกจาก Ground truth ภาคสนาม",
            "SHAP อธิบายการให้คะแนนของโมเดล ไม่ได้พิสูจน์เหตุและผลทางชีววิทยา",
            "ผู้ใช้ต้องตรวจสี กลิ่น DO และตัวอย่างน้ำก่อนดำเนินมาตรการที่มีต้นทุน",
        ],
        model_name="Weather-first XGBoost expert-rule surrogate",
        model_version=prediction["model_metadata"]["model_version"],
        forecast_horizon="Environmental conditions day 0–5; not a verified bloom forecast",
        shap_output_space="watch_index_points",
        rule_basis=[
            "Weather/Ocean และคะแนนฐานรวมได้ไม่เกิน 80 จุด",
            "Sentinel-2 ที่อายุไม่เกิน 10 วันและ valid water pixels ≥ 5% เพิ่มได้ไม่เกิน 20 จุด",
            "ต่ำกว่า 50 = ติดตามปกติ, 50–69 = เฝ้าระวัง, ตั้งแต่ 70 = ควรตรวจน้ำเร็วขึ้น",
            "ทุกระดับเป็นคำแนะนำเฝ้าระวัง ไม่ใช่คำยืนยันว่าเกิดแพลงก์ตอนบลูม",
        ],
    )


def build_bangsaen_operational_response(
    inputs: dict, prediction: dict
) -> CurrentRiskResponse:
    station = STATIONS_DATABASE["chonburi_03"]
    satellite = inputs["satellite"]
    marine = inputs["marine"]
    retrieved_at = datetime.fromisoformat(
        inputs["retrieved_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)
    satellite_age = round(age_hours(satellite["observed_at"], retrieved_at), 1)
    score = prediction["risk_score"]
    level, _, recommendations = _risk_metadata(score)
    metadata = prediction["model_metadata"]
    units = {
        "ndci_latest": "index",
        "ndci_mean_30d": "index",
        "ndci_slope_30d": "index/day",
        "ndwi_latest": "index",
        "valid_pixel_ratio": "ratio",
        "satellite_age_days": "days",
    }
    factors = [
        Factor(
            name=factor["name"],
            feature_key=factor["name"],
            value=round(factor["value"], 5),
            unit=units.get(factor["name"], "model unit"),
            impact=factor["impact"],
            shap_value=round(factor["shap_value"], 5),
        )
        for factor in prediction["factors"]
    ]
    top = "; ".join(
        f"{factor['name']} {'เพิ่ม' if factor['shap_value'] > 0 else 'ลด'} raw margin"
        for factor in prediction["top_factors"]
    )
    return CurrentRiskResponse(
        station_id="chonburi_03",
        assessment_status="operational_model",
        risk_score=score,
        risk_level=level,
        alert_status="Validated model assessment",
        shap_explanation=f"SHAP จาก Operational XGBoost: {top}",
        location=station["location"],
        lat=station["lat"],
        lon=station["lon"],
        timestamp=inputs["retrieved_at"],
        recommendations=recommendations,
        features=factors,
        history_trend=[],
        data_status="live_operational",
        data_source="Sentinel-2 L2A + Open-Meteo forecast",
        observed_at=satellite["observed_at"],
        is_demo=False,
        data_age_hours=satellite_age,
        confidence_score=None,
        confidence_level="ผ่าน Validation policy",
        confidence_note="Probability ผ่าน Calibration ตาม Model metadata; ไม่ใช่ Accuracy รายครั้ง",
        imagery_status=satellite["status"],
        imagery_mode="context_only",
        analysis_method="xgboost_shap_operational",
        history_period_days=0,
        data_sources=[
            DataSourceInfo(
                name="Sentinel-2 L2A via Earth Search",
                source_type="sentinel2_l2a",
                status=satellite["status"],
                observed_at=satellite["observed_at"],
                age_hours=satellite_age,
                note=f"Item {satellite.get('item_id')}",
                url="https://earth-search.aws.element84.com/v1/",
            ),
            DataSourceInfo(
                name="Open-Meteo Weather/Marine forecast",
                source_type="weather_forecast",
                status="available",
                observed_at=inputs["operational_snapshot"]["environment"]["issue_time"],
                age_hours=0,
                note="Forecast grid data; coastal resolution limitations apply",
                url="https://open-meteo.com/en/docs",
            ),
        ],
        limitations=[
            "SHAP อธิบาย Raw XGBoost margin ก่อน Probability calibration",
            "ผลต้องยืนยันด้วยการตรวจน้ำและใช้เฉพาะพื้นที่/ฤดูกาลใน Validation support",
        ],
        model_name="Calibrated XGBoost",
        model_version=metadata.get("model_version", "operational"),
        forecast_horizon="3–5 days",
        shap_output_space="raw_margin",
    )


@app.get("/api/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    operational_status = get_operational_model_status()
    return HealthResponse(
        status="ok",
        model_available=MODEL_PATH.is_file(),
        mock_data_available=MOCK_DATA_PATH.is_file(),
        live_context_available=True,
        operational_model_available=operational_status["available"],
    )


@app.get("/api/stations")
def get_all_stations() -> dict:
    return STATIONS_DATABASE


@app.get("/api/pipeline/status")
def get_pipeline_status() -> dict:
    return pipeline_status()


@app.get("/api/risk/current", response_model=CurrentRiskResponse)
async def get_current_risk(
    station_id: str = "chonburi_01",
    scenario: Literal["low", "medium", "high"] = "medium",
) -> CurrentRiskResponse:
    if station_id not in STATIONS_DATABASE:
        raise HTTPException(status_code=404, detail="ไม่พบรหัสสถานีนี้ในระบบ")

    station = STATIONS_DATABASE[station_id]
    environment_task = asyncio.to_thread(
        fetch_current_environment_forecast,
        station["lat"],
        station["lon"],
    )

    live_inputs = None
    try:
        if station_id == "chonburi_03":
            environment, live_inputs = await asyncio.gather(
                environment_task, fetch_bangsaen_live_inputs()
            )
        else:
            environment = await environment_task
    except Exception as exc:
        # Bangsaen can fail over to the last real, timestamped snapshot. Other
        # locations fail closed instead of inventing replacement observations.
        if station_id == "chonburi_03":
            live_inputs = live_inputs or await fetch_bangsaen_live_inputs()
            snapshot = live_inputs.get("operational_snapshot")
            if snapshot and snapshot.get("environment"):
                environment = snapshot["environment"]
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Weather/Ocean API ไม่พร้อมและไม่มี Snapshot จริงสำรอง",
                ) from exc
        else:
            raise HTTPException(
                status_code=503,
                detail="Weather/Ocean API ไม่พร้อม จึงไม่สร้างดัชนีทดแทน",
            ) from exc

    satellite = None
    if station_id == "chonburi_03" and live_inputs:
        snapshot = live_inputs.get("operational_snapshot")
        if snapshot and snapshot.get("sentinel", {}).get("summary"):
            satellite = dict(snapshot["sentinel"]["summary"])
            satellite["data_age_days"] = round(
                age_hours(satellite["observed_at"], datetime.now(timezone.utc)) / 24,
                2,
            )

    return build_environmental_watch_response(station_id, environment, satellite)
