from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import xgboost as xgb


MODEL_PATH = Path(__file__).parent / "Model" / "models" / "xgboost_model.json"
LIVE_SNAPSHOT_PATH = (
    Path(__file__).parent / "backend" / "data" / "bangsaen_operational_snapshot.json"
)
FEATURES = [
    "B2",
    "B3",
    "B4",
    "B5",
    "B8",
    "NDWI",
    "NDCI",
    "Temperature",
    "WindSpeed",
    "Humidity",
    "Rainfall",
    "DO",
    "Chlorophyll",
]

PRESETS = {
    "ตัวอย่างระดับต่ำ": {
        "B2": 0.08,
        "B3": 0.10,
        "B4": 0.12,
        "B5": 0.07,
        "B8": 0.20,
        "Temperature": 27.0,
        "WindSpeed": 9.0,
        "Humidity": 70.0,
        "Rainfall": 3.0,
        "DO": 7.5,
        "Chlorophyll": 4.0,
    },
    "ตัวอย่างระดับปานกลาง": {
        "B2": 0.10,
        "B3": 0.12,
        "B4": 0.08,
        "B5": 0.20,
        "B8": 0.18,
        "Temperature": 31.0,
        "WindSpeed": 2.0,
        "Humidity": 85.0,
        "Rainfall": 1.0,
        "DO": 5.4,
        "Chlorophyll": 24.0,
    },
    "ตัวอย่างระดับสูง": {
        "B2": 0.09,
        "B3": 0.14,
        "B4": 0.04,
        "B5": 0.23,
        "B8": 0.12,
        "Temperature": 34.0,
        "WindSpeed": 0.8,
        "Humidity": 92.0,
        "Rainfall": 0.0,
        "DO": 4.2,
        "Chlorophyll": 42.0,
    },
}


@st.cache_resource
def load_model() -> xgb.Booster:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"ไม่พบโมเดล: {MODEL_PATH}")
    booster = xgb.Booster()
    booster.load_model(MODEL_PATH)
    return booster


@st.cache_data
def load_live_snapshot() -> dict:
    if not LIVE_SNAPSHOT_PATH.is_file():
        raise FileNotFoundError(f"ไม่พบ Live snapshot: {LIVE_SNAPSHOT_PATH}")
    return json.loads(LIVE_SNAPSHOT_PATH.read_text(encoding="utf-8"))


def index(numerator_a: float, numerator_b: float) -> float:
    return (numerator_a - numerator_b) / (numerator_a + numerator_b + 1e-6)


def model_input(values: dict[str, float]) -> pd.DataFrame:
    row = {
        **values,
        "NDWI": index(values["B3"], values["B8"]),
        "NDCI": index(values["B5"], values["B4"]),
    }
    return pd.DataFrame([[row[name] for name in FEATURES]], columns=FEATURES)


def risk_band(probability: float) -> tuple[str, str]:
    if probability < 0.35:
        return "ต่ำ", "green"
    if probability < 0.65:
        return "ปานกลาง", "orange"
    return "สูง", "red"


st.set_page_config(
    page_title="AquaMind — Synthetic Model Demo",
    page_icon="🌊",
    layout="wide",
)

st.title("AquaMind — XGBoost + SHAP")
st.caption("Synthetic Technical Demo สำหรับตรวจสอบเส้นทาง Model inference และ Explainability")
st.warning(
    "ผลในหน้านี้มาจากโมเดลที่ฝึกด้วยข้อมูลสังเคราะห์ ไม่ใช่ความเสี่ยงปัจจุบันของบางแสน "
    "และยังไม่ผ่านการตรวจสอบความแม่นยำภาคสนาม จึงห้ามใช้ตัดสินใจด้านการเพาะเลี้ยง"
)

forecast_col, satellite_col, verified_col = st.columns(3)
with forecast_col:
    st.markdown("**1. Environmental forecast**")
    st.caption("Weather/Ocean ใช้เฝ้าระวังสภาพแวดล้อม ไม่ใช่การยืนยัน Bloom")
with satellite_col:
    st.markdown("**2. Satellite evidence**")
    st.caption("Sentinel-2 เพิ่มหลักฐานเชิงแสงเมื่อภาพผ่าน QC และต้องแสดง Data age")
with verified_col:
    st.markdown("**3. Field verification**")
    st.caption("การตรวจน้ำหรือผู้เชี่ยวชาญเท่านั้นที่ใช้ยืนยันเหตุการณ์จริง")

st.info(
    "แอปหน้านี้สาธิตขั้น Model inference ด้วยข้อมูลสังเคราะห์ ส่วน Weather/Ocean และ "
    "Sentinel-2 จริงแสดงใน AquaMind Dashboard และยังไม่ถูกใช้สร้าง Live probability"
)

st.divider()
st.subheader("Bangsaen Live Data Readiness")
st.caption("ข้อมูลจริงล่าสุดใน Snapshot ของโครงการ — ใช้ตรวจความพร้อมข้อมูล ไม่ใช่ Operational prediction")

try:
    live = load_live_snapshot()
    sentinel = live["sentinel"]["summary"]
    environment = live["environment"]
    env_features = environment["features"]
    model_status = live["model_status"]

    live_col1, live_col2, live_col3, live_col4 = st.columns(4)
    live_col1.metric("Sentinel observed", sentinel["observed_at"][:10])
    live_col2.metric("NDCI / NDWI", f"{sentinel['ndci_latest']:.4f} / {sentinel['ndwi_latest']:.4f}")
    live_col3.metric("Valid water pixels", f"{sentinel['valid_pixel_ratio']:.1%}")
    live_col4.metric("SST / Wave", f"{env_features['sst_at_issue']:.1f} °C / {env_features['wave_height_at_issue']:.2f} m")

    st.warning(
        "Operational probability ถูกระงับ: "
        f"{model_status['reason']}. Weather/Ocean จึงเป็นเพียง Environmental forecast context "
        "และ Sentinel-2 เป็น Satellite evidence ที่ยังต้องยืนยันภาคสนาม"
    )
    with st.expander("ดู Weather/Ocean forecast และ Data lineage"):
        forecast_rows = [
            {"Feature": name, "Value": value}
            for name, value in env_features.items()
        ]
        st.dataframe(pd.DataFrame(forecast_rows), hide_index=True, width="stretch")
        st.caption(
            f"Snapshot generated: {live['generated_at']} · Forecast issue time: "
            f"{environment['issue_time']} · Sentinel item: {sentinel['latest_item_id']}"
        )
        st.caption(environment["lineage"]["warning"])
except Exception as exc:
    st.error(f"ไม่สามารถอ่าน Bangsaen Live snapshot ได้: {exc}")

st.divider()
st.subheader("XGBoost + SHAP Synthetic Technical Demo")

preset_name = st.selectbox("เลือกสถานการณ์สังเคราะห์", list(PRESETS))
preset = PRESETS[preset_name]

with st.form("synthetic-features"):
    st.subheader("ตัวแปรนำเข้า")
    spectral_col, environment_col, field_col = st.columns(3)

    with spectral_col:
        st.markdown("**Sentinel-2 reflectance จำลอง**")
        b2 = st.number_input("B2", 0.0, 1.0, float(preset["B2"]), 0.01)
        b3 = st.number_input("B3", 0.0, 1.0, float(preset["B3"]), 0.01)
        b4 = st.number_input("B4", 0.0, 1.0, float(preset["B4"]), 0.01)
        b5 = st.number_input("B5", 0.0, 1.0, float(preset["B5"]), 0.01)
        b8 = st.number_input("B8", 0.0, 1.0, float(preset["B8"]), 0.01)

    with environment_col:
        st.markdown("**สภาพอากาศจำลอง**")
        temperature = st.number_input(
            "Temperature (°C)", 15.0, 45.0, float(preset["Temperature"]), 0.5
        )
        wind_speed = st.number_input(
            "Wind speed (m/s)", 0.0, 30.0, float(preset["WindSpeed"]), 0.5
        )
        humidity = st.number_input(
            "Humidity (%)", 0.0, 100.0, float(preset["Humidity"]), 1.0
        )
        rainfall = st.number_input(
            "Rainfall (mm)", 0.0, 300.0, float(preset["Rainfall"]), 1.0
        )

    with field_col:
        st.markdown("**ค่าตรวจวัดจำลอง**")
        dissolved_oxygen = st.number_input(
            "DO (mg/L)", 0.0, 20.0, float(preset["DO"]), 0.1
        )
        chlorophyll = st.number_input(
            "Chlorophyll (µg/L)", 0.0, 200.0, float(preset["Chlorophyll"]), 1.0
        )
        st.info("NDCI และ NDWI คำนวณจากแถบคลื่นโดยอัตโนมัติ")

    submitted = st.form_submit_button("ประเมินสถานการณ์สังเคราะห์", type="primary")

values = {
    "B2": b2,
    "B3": b3,
    "B4": b4,
    "B5": b5,
    "B8": b8,
    "Temperature": temperature,
    "WindSpeed": wind_speed,
    "Humidity": humidity,
    "Rainfall": rainfall,
    "DO": dissolved_oxygen,
    "Chlorophyll": chlorophyll,
}

if submitted:
    try:
        booster = load_model()
        frame = model_input(values)
        matrix = xgb.DMatrix(frame, feature_names=FEATURES)
        probability = float(booster.predict(matrix)[0])
        contributions = booster.predict(matrix, pred_contribs=True)[0]
        shap_values = contributions[:-1]
        raw_base_value = float(contributions[-1])
        raw_margin = float(np.sum(contributions))
        band, color = risk_band(probability)

        st.divider()
        metric_col, band_col, indices_col = st.columns(3)
        metric_col.metric("Synthetic model probability", f"{probability:.1%}")
        band_col.markdown("**ระดับสำหรับการสาธิต**")
        band_col.markdown(f":{color}[{band}]")
        indices_col.metric(
            "NDCI / NDWI",
            f"{frame.at[0, 'NDCI']:.3f} / {frame.at[0, 'NDWI']:.3f}",
        )

        st.progress(min(max(probability, 0.0), 1.0))

        explanation = pd.DataFrame(
            {
                "Feature": FEATURES,
                "Value": frame.iloc[0].to_numpy(dtype=float),
                "SHAP (raw margin)": shap_values,
            }
        )
        explanation["Absolute impact"] = explanation["SHAP (raw margin)"].abs()
        explanation = explanation.sort_values("Absolute impact", ascending=False)

        st.subheader("ปัจจัยสำคัญจาก SHAP")
        st.bar_chart(
            explanation.head(8).set_index("Feature")[["SHAP (raw margin)"]],
            horizontal=True,
        )
        st.dataframe(
            explanation.drop(columns="Absolute impact").head(8),
            hide_index=True,
            width="stretch",
        )
        st.caption(
            f"Base value = {raw_base_value:.4f}, raw margin = {raw_margin:.4f}. "
            "SHAP อธิบายผลของโมเดลในหน่วย raw margin ไม่ใช่จำนวนเปอร์เซ็นต์ความเสี่ยง "
            "และไม่ได้ยืนยันความสัมพันธ์เชิงเหตุและผล"
        )
    except Exception as exc:
        st.error(f"ไม่สามารถประเมินโมเดลได้: {exc}")

with st.expander("ข้อจำกัดของโมเดลนี้", expanded=True):
    st.markdown(
        """
        - Dataset ฝึกจำนวน 12,000 แถวถูกสร้างจากสูตรสังเคราะห์ ไม่ใช่ Ground truth ภาคสนาม
        - ค่า Bloom ถูกสร้างจาก NDCI, อุณหภูมิ, ลม, DO และ Chlorophyll ในเวลาเดียวกัน
        - โมเดลนี้เป็นตัวจำแนกสถานการณ์สังเคราะห์ ไม่ใช่การพยากรณ์ล่วงหน้า 3–5 วัน
        - Probability ยังไม่ผ่าน Calibration ด้วยเหตุการณ์จริง และ Threshold ระดับสีเป็นเพียง UI demo
        - Live AquaMind ต้องใช้ Feature contract และ Operational-validation gate แยกต่างหาก
        """
    )
