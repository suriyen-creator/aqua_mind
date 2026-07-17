from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from backend.environment_data import fetch_current_environment_forecast
from backend.environmental_watch import predict_environmental_watch


SNAPSHOT_PATH = Path(__file__).parent / "backend" / "data" / "bangsaen_operational_snapshot.json"
BANGSAEN_LAT = 13.2912
BANGSAEN_LON = 100.9014


@st.cache_data(ttl=900)
def load_bangsaen_inputs() -> tuple[dict, dict, str]:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    source_mode = "Open-Meteo API ล่าสุด"
    try:
        environment = fetch_current_environment_forecast(BANGSAEN_LAT, BANGSAEN_LON)
    except Exception:
        environment = snapshot["environment"]
        source_mode = "Snapshot จริงล่าสุด (API สำรอง)"

    satellite = dict(snapshot["sentinel"]["summary"])
    observed = datetime.fromisoformat(satellite["observed_at"].replace("Z", "+00:00"))
    satellite["data_age_days"] = round(
        max(0.0, (datetime.now(timezone.utc) - observed).total_seconds() / 86400), 2
    )
    return environment, satellite, source_mode


st.set_page_config(page_title="AquaMind — Live Environmental Watch", page_icon="🌊", layout="wide")
st.title("AquaMind — ระบบเฝ้าระวังสภาพแวดล้อมชายฝั่ง")
st.caption("Weather/Ocean จริงเป็นหลัก · Sentinel-2 เป็นหลักฐานรอง · XGBoost + SHAP · Rule-based action")
st.warning(
    "ค่าที่แสดงเป็นดัชนีเฝ้าระวัง 0–100 ไม่ใช่เปอร์เซ็นต์โอกาสเกิดแพลงก์ตอนบลูม "
    "และยังใช้แทนการตรวจน้ำหรือคำยืนยันจากผู้เชี่ยวชาญไม่ได้"
)

flow_1, flow_2, flow_3, flow_4 = st.columns(4)
flow_1.markdown("**1. Weather/Ocean หลัก**")
flow_1.caption("API จริงตามพิกัด คำนวณได้แม้ไม่มีภาพ")
flow_2.markdown("**2. Sentinel-2 รอง**")
flow_2.caption("เพิ่มได้ไม่เกิน 20 จุดเมื่อผ่าน QC")
flow_3.markdown("**3. XGBoost + SHAP**")
flow_3.caption("อธิบายว่าปัจจัยใดดันดัชนีขึ้นหรือลง")
flow_4.markdown("**4. กฎแนะนำการตรวจน้ำ**")
flow_4.caption("บอกสิ่งที่ควรทำโดยไม่ประกาศว่าเกิดบลูม")

try:
    environment, satellite, source_mode = load_bangsaen_inputs()
    result = predict_environmental_watch(environment["features"], satellite)
except Exception as exc:
    st.error(f"ระบบไม่สร้างค่าทดแทน เพราะอ่านข้อมูลจริงหรือโมเดลไม่สำเร็จ: {exc}")
    st.stop()

st.divider()
st.subheader("บางแสน — ผลจากข้อมูลจริงล่าสุด")
metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("ดัชนีเฝ้าระวัง", f"{result['watch_index']:.0f}/100")
metric_2.metric("ระดับการติดตาม", result["watch_level"])
metric_3.metric("ความครบถ้วนของหลักฐาน", f"{result['evidence_completeness']}/100")
metric_4.metric(
    "ภาพ Sentinel-2",
    "ใช้เป็นหลักฐานรอง" if result["satellite_used"] else "ไม่ใช้ในรอบนี้",
)

st.info(result["plain_language_explanation"])
st.caption(
    f"Weather source: {source_mode} · Forecast issue: {environment['issue_time']} · "
    f"Sentinel observed: {satellite['observed_at']} · อายุภาพ {satellite['data_age_days']:.1f} วัน"
)

st.subheader("SHAP อธิบายแบบภาษาชาวบ้าน")
factor_rows = [
    {
        "ปัจจัย": factor["name"],
        "ค่าจริง": f"{factor['value']} {factor['unit']}",
        "ผลต่อดัชนี": f"{factor['shap_value']:+.1f} จุด",
        "อธิบายง่าย ๆ": factor["plain_language"],
    }
    for factor in result["top_factors"]
]
st.dataframe(pd.DataFrame(factor_rows), hide_index=True, width="stretch")
st.caption(
    "SHAP อยู่ในหน่วยจุดของดัชนีและอธิบาย XGBoost ที่เลียนแบบกฎเฝ้าระวัง "
    "ไม่ใช่เปอร์เซ็นต์ความเสี่ยงและไม่ใช่หลักฐานเชิงเหตุและผล"
)

action_col, rule_col = st.columns(2)
with action_col:
    st.subheader("วันนี้ควรทำอะไร")
    for action in result["recommendations"]:
        st.markdown(f"- {action}")
with rule_col:
    st.subheader("กฎที่ใช้ตัดสินระดับ")
    st.markdown(
        """
        - Weather/Ocean และคะแนนฐานรวมได้ไม่เกิน 80 จุด
        - Sentinel-2 ที่อายุไม่เกิน 10 วันและ valid water pixels ≥ 5% เพิ่มได้ไม่เกิน 20 จุด
        - ต่ำกว่า 50: ติดตามปกติ
        - 50–69: เฝ้าระวังและเพิ่มรอบสังเกต
        - ตั้งแต่ 70: ควรตรวจน้ำเร็วขึ้น แต่ยังไม่ถือว่าเกิดบลูม
        """
    )

with st.expander("ดู Weather/Ocean, Sentinel-2 และที่มาข้อมูล"):
    env_rows = [
        {"Feature": name, "Value": value}
        for name, value in environment["features"].items()
    ]
    st.dataframe(pd.DataFrame(env_rows), hide_index=True, width="stretch")
    st.markdown(
        f"- Weather API: {environment.get('lineage', {}).get('weather_url', 'stored in snapshot')}\n"
        f"- Marine API: {environment.get('lineage', {}).get('marine_url', 'stored in snapshot')}\n"
        f"- Sentinel item: {satellite.get('latest_item_id')}\n"
        f"- NDCI / trend: {satellite.get('ndci_latest')} / {satellite.get('ndci_slope_30d')}\n"
        f"- Valid water pixels: {satellite.get('valid_pixel_ratio', 0):.1%}"
    )

with st.expander("ข้อจำกัดที่ต้องอ่าน", expanded=True):
    st.markdown(
        """
        - ดัชนีนี้ใช้ข้อมูลจริงเป็น Input แต่ XGBoost ฝึกให้เลียนแบบกฎที่เปิดเผย ไม่ได้ฝึกจาก Ground truth ภาคสนาม
        - จึงยังอ้าง Accuracy, Precision, Recall หรือความน่าจะเป็นของการเกิดบลูมไม่ได้
        - ภาพดาวเทียมเป็นหลักฐานรองและไม่สามารถยืนยันชนิดหรือความเป็นพิษของแพลงก์ตอนได้
        - ก่อนเติมอากาศ ลดอาหาร หรือดำเนินมาตรการที่มีต้นทุน ต้องตรวจสภาพน้ำในพื้นที่ก่อน
        """
    )
