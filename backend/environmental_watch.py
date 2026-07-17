from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import xgboost as xgb

from backend.train_watch_model import FEATURE_NAMES


BACKEND_DIR = Path(__file__).resolve().parent
MODEL_PATH = BACKEND_DIR / "environmental_watch_model.json"
METADATA_PATH = BACKEND_DIR / "environmental_watch_model.metadata.json"

FEATURE_METADATA = {
    "air_temperature_mean_d0_3": ("อุณหภูมิอากาศเฉลี่ย 3 วัน", "°C"),
    "precipitation_sum_d0_3": ("ฝนสะสม 3 วัน", "mm"),
    "wind_speed_mean_d0_3": ("ลมเฉลี่ย 3 วัน", "m/s"),
    "wind_gust_max_d0_3": ("ลมกระโชกสูงสุด 3 วัน", "m/s"),
    "air_temperature_mean_d3_5": ("อุณหภูมิอากาศช่วงวันที่ 3–5", "°C"),
    "precipitation_sum_d3_5": ("ฝนสะสมช่วงวันที่ 3–5", "mm"),
    "wind_speed_mean_d3_5": ("ลมเฉลี่ยช่วงวันที่ 3–5", "m/s"),
    "sst_at_issue": ("อุณหภูมิผิวน้ำทะเล", "°C"),
    "wave_height_at_issue": ("ความสูงคลื่น", "m"),
    "current_velocity_at_issue": ("ความเร็วกระแสน้ำ", "km/h"),
    "ndci_latest": ("สัญญาณสีของน้ำจากภาพ NDCI", "index"),
    "ndci_slope_30d": ("แนวโน้ม NDCI 30 วัน", "index/day"),
    "satellite_age_days": ("อายุภาพดาวเทียม", "days"),
    "valid_pixel_ratio": ("สัดส่วนพิกเซลน้ำที่ผ่าน QC", "ratio"),
}


@lru_cache(maxsize=1)
def load_model() -> tuple[xgb.Booster, dict[str, Any]]:
    booster = xgb.Booster()
    booster.load_model(MODEL_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return booster, metadata


def _satellite_usable(satellite: dict[str, Any] | None) -> bool:
    if not satellite:
        return False
    age = satellite.get("data_age_days")
    valid = satellite.get("valid_pixel_ratio")
    ndci = satellite.get("ndci_latest")
    return bool(
        isinstance(age, (int, float))
        and age <= 10
        and isinstance(valid, (int, float))
        and valid >= 0.05
        and isinstance(ndci, (int, float))
    )


def build_feature_values(
    environment: dict[str, Any], satellite: dict[str, Any] | None
) -> dict[str, float]:
    values = {
        name: float(environment[name])
        if isinstance(environment.get(name), (int, float))
        else math.nan
        for name in FEATURE_NAMES
    }
    if _satellite_usable(satellite):
        values.update(
            {
                "ndci_latest": float(satellite["ndci_latest"]),
                "ndci_slope_30d": float(satellite.get("ndci_slope_30d", 0.0)),
                "satellite_age_days": float(satellite["data_age_days"]),
                "valid_pixel_ratio": float(satellite["valid_pixel_ratio"]),
            }
        )
    else:
        for name in (
            "ndci_latest",
            "ndci_slope_30d",
            "satellite_age_days",
            "valid_pixel_ratio",
        ):
            values[name] = math.nan
    return values


def _farmer_phrase(feature: str, shap_value: float, value: float) -> str:
    up = shap_value >= 0
    phrases = {
        "sst_at_issue": (
            "น้ำทะเลค่อนข้างอุ่น จึงควรเฝ้าดูใกล้ขึ้น"
            if up
            else "อุณหภูมิน้ำยังช่วยลดสัญญาณเฝ้าระวัง"
        ),
        "wind_speed_mean_d0_3": (
            "ลมค่อนข้างอ่อน น้ำอาจถ่ายเทน้อยลง"
            if up
            else "ลมช่วยให้น้ำถ่ายเท จึงลดสัญญาณเฝ้าระวัง"
        ),
        "wind_speed_mean_d3_5": (
            "ช่วงวันที่ 3–5 ลมมีแนวโน้มอ่อน ควรติดตามต่อ"
            if up
            else "ช่วงวันที่ 3–5 ลมยังช่วยให้น้ำถ่ายเท"
        ),
        "wave_height_at_issue": (
            "คลื่นต่ำ การผสมน้ำอาจน้อยลง"
            if up
            else "คลื่นช่วยผสมน้ำ จึงลดสัญญาณเฝ้าระวัง"
        ),
        "current_velocity_at_issue": (
            "กระแสน้ำค่อนข้างอ่อน จึงควรตรวจสภาพน้ำ"
            if up
            else "กระแสน้ำช่วยถ่ายเทมวลน้ำ"
        ),
        "precipitation_sum_d0_3": (
            "มีฝนสะสม ควรระวังน้ำไหลบ่าพาสารอาหารลงแหล่งน้ำ"
            if up
            else "ฝนสะสมยังไม่ใช่ปัจจัยเด่นในรอบนี้"
        ),
        "precipitation_sum_d3_5": (
            "ช่วงวันที่ 3–5 มีฝนสะสม ควรติดตามน้ำไหลบ่า"
            if up
            else "ฝนช่วงวันที่ 3–5 ยังไม่เพิ่มสัญญาณมาก"
        ),
        "ndci_latest": (
            "ภาพล่าสุดเห็นสัญญาณสีของน้ำเพิ่มขึ้น แต่ยังไม่ยืนยันว่าเป็นบลูม"
            if up
            else "ภาพล่าสุดยังไม่เห็นสัญญาณสีของน้ำเด่น"
        ),
        "ndci_slope_30d": (
            "สัญญาณจากภาพมีแนวโน้มเพิ่มขึ้น ควรตรวจน้ำประกอบ"
            if up
            else "แนวโน้มจากภาพกำลังลดลง"
        ),
    }
    if feature in phrases:
        return phrases[feature]
    label = FEATURE_METADATA[feature][0]
    direction = "เพิ่ม" if up else "ลด"
    return f"{label} {direction}ดัชนีเฝ้าระวัง"


def _rule_actions(score: float, values: dict[str, float], satellite_used: bool) -> list[str]:
    actions = []
    if score >= 70:
        actions.extend(
            [
                "ตรวจสี กลิ่น และออกซิเจนละลายน้ำภายใน 6–12 ชั่วโมงก่อนตัดสินใจ",
                "เตรียมเครื่องเติมอากาศ แต่ยังไม่ต้องประกาศว่าเกิดแพลงก์ตอนบลูม",
            ]
        )
    elif score >= 50:
        actions.extend(
            [
                "เพิ่มรอบสังเกตน้ำเป็นเช้า–เย็นในช่วง 3 วันข้างหน้า",
                "ตรวจออกซิเจนละลายน้ำช่วงใกล้รุ่ง หากมีเครื่องมือ",
            ]
        )
    else:
        actions.append("ติดตามตามรอบปกติและบันทึกสีของน้ำไว้เปรียบเทียบ")

    if values.get("precipitation_sum_d0_3", 0.0) >= 20:
        actions.append("หลังฝนตกหนักให้ตรวจน้ำบริเวณทางน้ำไหลเข้าฟาร์ม")
    if not satellite_used:
        actions.append("รอภาพดาวเทียมรอบถัดไปได้ แต่ไม่ต้องหยุดการเฝ้าระวังจากอากาศ")
    else:
        actions.append("ใช้ภาพดาวเทียมเป็นหลักฐานเสริม และยืนยันด้วยการตรวจน้ำในพื้นที่")
    return actions


def predict_environmental_watch(
    environment: dict[str, Any], satellite: dict[str, Any] | None = None
) -> dict[str, Any]:
    values = build_feature_values(environment, satellite)
    matrix = xgb.DMatrix(
        [[values[name] for name in FEATURE_NAMES]], feature_names=FEATURE_NAMES
    )
    booster, metadata = load_model()
    raw_score = float(booster.predict(matrix)[0])
    contributions = booster.predict(matrix, pred_contribs=True)[0]
    shap_values = contributions[:-1]
    base_value = float(contributions[-1])
    score = min(100.0, max(0.0, raw_score))
    satellite_used = _satellite_usable(satellite)

    factors = []
    for name, shap_value in zip(FEATURE_NAMES, shap_values, strict=True):
        value = values[name]
        if not math.isfinite(value):
            continue
        label, unit = FEATURE_METADATA[name]
        factors.append(
            {
                "name": label,
                "feature_key": name,
                "value": round(value, 4),
                "unit": unit,
                "impact": "increase" if shap_value > 0.05 else "decrease" if shap_value < -0.05 else "none",
                "shap_value": round(float(shap_value), 3),
                "plain_language": _farmer_phrase(name, float(shap_value), value),
            }
        )
    # Data-age and QC fields gate whether imagery may be used; they are not
    # environmental causes, so keep them in the inspector but not in the
    # farmer-facing explanation ranking.
    explanation_factors = [
        item
        for item in factors
        if item["feature_key"]
        not in {"satellite_age_days", "valid_pixel_ratio", "wind_gust_max_d0_3"}
    ]
    top_factors = sorted(
        explanation_factors,
        key=lambda item: abs(item["shap_value"]),
        reverse=True,
    )[:4]

    weather_present = sum(
        math.isfinite(values[name]) for name in FEATURE_NAMES[:10]
    )
    evidence_completeness = round(75 * weather_present / 10 + (25 if satellite_used else 0))
    if score >= 70:
        level = "ควรตรวจน้ำเร็วขึ้น"
    elif score >= 50:
        level = "เฝ้าระวัง"
    else:
        level = "ติดตามปกติ"

    explanation = " ".join(item["plain_language"] for item in top_factors[:3])
    if not satellite_used:
        explanation += " วันนี้ไม่มีภาพ Sentinel-2 ที่ผ่านเกณฑ์ ระบบจึงใช้ Weather/Ocean เพียงอย่างเดียว"
    return {
        "watch_index": round(score, 1),
        "watch_level": level,
        "evidence_completeness": evidence_completeness,
        "satellite_used": satellite_used,
        "factors": factors,
        "top_factors": top_factors,
        "plain_language_explanation": explanation,
        "recommendations": _rule_actions(score, values, satellite_used),
        "base_value": base_value,
        "shap_sum_matches_score": math.isclose(
            base_value + float(np.sum(shap_values)), raw_score, rel_tol=1e-5, abs_tol=1e-4
        ),
        "model_metadata": metadata,
    }
