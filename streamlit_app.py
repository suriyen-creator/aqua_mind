from __future__ import annotations

import json
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import xgboost as xgb

from backend.environment_data import fetch_current_environment_forecast
from backend.environmental_watch import FEATURE_METADATA, predict_environmental_watch
from backend.sentinel2 import BANGSAEN_AOI, AreaOfInterest, parse_utc, search_sentinel2_items

# Suppress minor version warnings from sklearn unpickling if present
warnings.filterwarnings("ignore", category=UserWarning)

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = BASE_DIR / "backend" / "data" / "bangsaen_operational_snapshot.json"
CHONBURI_TS_PATH = BASE_DIR / "backend" / "data" / "chonburi_station_a1_30d.csv"
GROUND_TRUTH_PATH = BASE_DIR / "backend" / "data" / "ground_truth.csv"
MODEL_DIR = BASE_DIR / "Model" / "models"
XGB_CLASSIFIER_PATH = MODEL_DIR / "xgboost_model.json"
RF_CLASSIFIER_PATH = MODEL_DIR / "random_forest.pkl"
WATCH_MODEL_PATH = BASE_DIR / "backend" / "environmental_watch_model.json"
WATCH_METADATA_PATH = BASE_DIR / "backend" / "environmental_watch_model.metadata.json"

STATIONS_DATABASE = {
    "chonburi_01": {
        "name": "ชายฝั่งชลบุรี (Chonburi Coast)",
        "location": "Chonburi Coast — Weather-first Live Watch",
        "lat": 13.3611,
        "lon": 100.9234,
        "mode_description": "เฝ้าระวังด้วย Weather/Ocean API สดเป็นแกนหลัก + เชื่อมกล้องดาวเทียม",
        "has_satellite": True,
    },
    "chonburi_02": {
        "name": "ท่าเรือศรีราชา (Sriracha Harbor)",
        "location": "Sriracha Harbor — Weather-first Live Watch",
        "lat": 13.1389,
        "lon": 100.9125,
        "mode_description": "เฝ้าระวังด้วย Weather/Ocean API สดเป็นแกนหลัก + เชื่อมกล้องดาวเทียม",
        "has_satellite": True,
    },
    "chonburi_03": {
        "name": "หาดบางแสน (Bangsaen Beach)",
        "location": "Bangsaen — Weather-first + Sentinel-2 Live Watch",
        "lat": 13.2912,
        "lon": 100.9014,
        "mode_description": "Weather/Ocean สด + กล้องดาวเทียม Sentinel-2 MSI L2A (เมื่อผ่าน QC)",
        "has_satellite": True,
    },
}

STATION_AOIS = {
    "chonburi_01": AreaOfInterest(
        station_id="chonburi_01",
        name="Chonburi Coast near-shore AOI",
        west=100.895,
        south=13.340,
        east=100.940,
        north=13.380,
    ),
    "chonburi_02": AreaOfInterest(
        station_id="chonburi_02",
        name="Sriracha Harbor near-shore AOI",
        west=100.890,
        south=13.120,
        east=100.930,
        north=13.160,
    ),
    "chonburi_03": BANGSAEN_AOI,
}

SIMULATOR_FEATURES = [
    "B2", "B3", "B4", "B5", "B8", "NDWI", "NDCI",
    "Temperature", "WindSpeed", "Humidity", "Rainfall", "DO", "Chlorophyll",
]

PRESETS_CLASSIFIER = {
    "ตัวอย่างความเสี่ยงต่ำ (Normal / Background)": {
        "B2": 0.08, "B3": 0.10, "B4": 0.12, "B5": 0.07, "B8": 0.20,
        "Temperature": 27.0, "WindSpeed": 9.0, "Humidity": 70.0, "Rainfall": 3.0,
        "DO": 7.5, "Chlorophyll": 4.0,
    },
    "ตัวอย่างเฝ้าระวัง (Watch / Moderate)": {
        "B2": 0.10, "B3": 0.12, "B4": 0.08, "B5": 0.20, "B8": 0.18,
        "Temperature": 31.0, "WindSpeed": 2.0, "Humidity": 85.0, "Rainfall": 1.0,
        "DO": 5.4, "Chlorophyll": 24.0,
    },
    "ตัวอย่างความเสี่ยงสูง (High Risk / Bloom Alert)": {
        "B2": 0.09, "B3": 0.14, "B4": 0.04, "B5": 0.23, "B8": 0.12,
        "Temperature": 34.0, "WindSpeed": 0.8, "Humidity": 92.0, "Rainfall": 0.0,
        "DO": 4.2, "Chlorophyll": 42.0,
    },
}


# ==============================================================================
# Helper Functions & Cached Resources
# ==============================================================================

@st.cache_resource
def load_xgboost_classifier() -> xgb.Booster | None:
    if not XGB_CLASSIFIER_PATH.is_file():
        return None
    booster = xgb.Booster()
    booster.load_model(XGB_CLASSIFIER_PATH)
    return booster


@st.cache_resource
def load_rf_classifier() -> Any | None:
    if not RF_CLASSIFIER_PATH.is_file():
        return None
    try:
        import joblib
        return joblib.load(RF_CLASSIFIER_PATH)
    except Exception:
        return None


@st.cache_data(ttl=900)
def load_station_data(station_id: str) -> tuple[dict[str, Any], dict[str, Any] | None, str]:
    station = STATIONS_DATABASE[station_id]
    lat, lon = station["lat"], station["lon"]
    source_mode = "Open-Meteo API สด (พยากรณ์ล่วงหน้า 5 วัน)"

    try:
        environment = fetch_current_environment_forecast(lat, lon)
    except Exception:
        if SNAPSHOT_PATH.is_file():
            snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
            environment = dict(snapshot["environment"])
            environment["latitude"] = lat
            environment["longitude"] = lon
            source_mode = "Snapshot จริงล่าสุด (API สำรอง)"
        else:
            raise RuntimeError("ไม่สามารถเชื่อมต่อ Weather/Ocean API และไม่พบ Snapshot สำรอง")

    satellite = None
    if station_id == "chonburi_03" and SNAPSHOT_PATH.is_file():
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        if snapshot.get("sentinel", {}).get("summary"):
            satellite = dict(snapshot["sentinel"]["summary"])
            observed = datetime.fromisoformat(satellite["observed_at"].replace("Z", "+00:00"))
            satellite["data_age_days"] = round(
                max(0.0, (datetime.now(timezone.utc) - observed).total_seconds() / 86400), 2
            )

    return environment, satellite, source_mode


@st.cache_data(ttl=1800)
def fetch_live_satellite_scene(station_id: str) -> dict[str, Any] | None:
    """Fetch live Sentinel-2 MSI optical camera scene from Earth Search STAC API."""
    aoi = STATION_AOIS.get(station_id, BANGSAEN_AOI)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=90)
    try:
        with httpx.Client(timeout=httpx.Timeout(4.0, connect=2.0), follow_redirects=True) as client:
            items = search_sentinel2_items(start, end, aoi, limit=1, client=client)
        if items:
            item = items[0]
            assets = item.get("assets", {})
            props = item.get("properties", {})
            thumb = assets.get("thumbnail", {}).get("href")
            dt_raw = props.get("datetime")
            dt_str = dt_raw
            age_days = None
            if dt_raw:
                dt_obj = parse_utc(dt_raw)
                dt_local = dt_obj.astimezone(timezone(timedelta(hours=7)))
                dt_str = dt_local.strftime("%d/%m/%Y เวลา %H:%M น. (เวลาไทย)")
                age_days = round(
                    max(0.0, (datetime.now(timezone.utc) - dt_obj).total_seconds() / 86400), 1
                )

            return {
                "item_id": item.get("id"),
                "thumbnail_url": thumb,
                "observed_at_str": dt_str,
                "observed_at_iso": dt_raw,
                "data_age_days": age_days,
                "cloud_cover": round(float(props.get("eo:cloud_cover", 0.0)), 1),
                "platform": str(props.get("platform", "Sentinel-2")).upper(),
                "constellation": str(props.get("constellation", "Sentinel-2")),
                "bbox": item.get("bbox", aoi.bbox),
                "is_live": True,
                "source_catalog": "Copernicus Sentinel-2 L2A (AWS S3 & Element84 Earth Search)",
                "visual_href": assets.get("visual", {}).get("href"),
            }
    except Exception:
        pass

    # Snapshot fallback if network is restricted
    if SNAPSHOT_PATH.is_file():
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        summary = snapshot.get("sentinel", {}).get("summary", {})
        return {
            "item_id": summary.get("latest_item_id", "S2B_47PPQ_20261022_0_L2A"),
            "thumbnail_url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PQ/2026/10/S2B_47PPQ_20261022_0_L2A/preview.jpg",
            "observed_at_str": "22/10/2026 เวลา 10:54 น. (เวลาไทย)",
            "observed_at_iso": summary.get("observed_at"),
            "data_age_days": summary.get("data_age_days", 0.0),
            "cloud_cover": round(float(summary.get("scene_cloud_cover_percent", 8.3)), 1),
            "platform": "SENTINEL-2B",
            "constellation": "Sentinel-2",
            "bbox": aoi.bbox,
            "is_live": False,
            "source_catalog": "Copernicus Sentinel-2 L2A Snapshot (AWS S3 Archive)",
            "visual_href": None,
        }
    return None


@st.cache_data
def load_timeseries_data() -> pd.DataFrame | None:
    if CHONBURI_TS_PATH.is_file():
        return pd.read_csv(CHONBURI_TS_PATH)
    return None


@st.cache_data
def load_ground_truth_data() -> pd.DataFrame | None:
    if GROUND_TRUTH_PATH.is_file():
        df = pd.read_csv(GROUND_TRUTH_PATH)
        if not df.empty:
            return df
    return None


def calculate_indices(b3: float, b4: float, b5: float, b8: float) -> tuple[float, float]:
    ndwi = (b3 - b8) / (b3 + b8 + 1e-6)
    ndci = (b5 - b4) / (b5 + b4 + 1e-6)
    return float(ndwi), float(ndci)


def render_satellite_map(
    lat: float,
    lon: float,
    station_name: str,
    score: float,
    west: float,
    south: float,
    east: float,
    north: float,
) -> str:
    """Generate high-resolution satellite map component using Esri World Imagery."""
    marker_color = "#ef4444" if score >= 70 else "#f59e0b" if score >= 50 else "#10b981"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            html, body {{ margin: 0; padding: 0; background: #0f172a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
            #map {{ width: 100%; height: 380px; border-radius: 10px; border: 1px solid #334155; }}
            .leaflet-popup-content-wrapper {{ background: #1e293b; color: #f1f5f9; border-radius: 8px; border: 1px solid #475569; }}
            .leaflet-popup-tip {{ background: #1e293b; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map', {{ attributionControl: false }}).setView([{lat}, {lon}], 13);
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 18
            }}).addTo(map);

            // Coastal Monitoring Area (AOI)
            var bounds = [[{south}, {west}], [{north}, {east}]];
            var rect = L.rectangle(bounds, {{
                color: "#38bdf8",
                weight: 2,
                dashArray: "4, 4",
                fillColor: "#0284c7",
                fillOpacity: 0.25
            }}).addTo(map);
            rect.bindPopup("<b>พื้นที่ติดตามคุณภาพน้ำชายฝั่ง (AOI)</b><br>กรอบสกัดพิกเซลผิวน้ำ Sentinel-2");

            // Station Marker
            var marker = L.circleMarker([{lat}, {lon}], {{
                radius: 9,
                fillColor: '{marker_color}',
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.95
            }}).addTo(map);
            marker.bindPopup("<b>{station_name}</b><br>พิกัด: {lat:.4f}, {lon:.4f}<br>ดัชนีเฝ้าระวัง: {score:.0f}/100").openPopup();
        </script>
    </body>
    </html>
    """


# ==============================================================================
# Streamlit App Layout & Styling
# ==============================================================================

st.set_page_config(
    page_title="AquaMind — AI Coastal Environmental Watch & Satellite Camera",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished aesthetic
st.markdown(
    """
    <style>
    .metric-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(51, 65, 85, 0.7);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .badge-normal {
        background-color: #065F46;
        color: #A7F3D0;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-watch {
        background-color: #92400E;
        color: #FDE68A;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-urgent {
        background-color: #991B1B;
        color: #FECACA;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .satellite-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.title("🌊 AquaMind")
    st.markdown("**ระบบเฝ้าระวังสภาพแวดล้อมและพยากรณ์การเกิดแพลงก์ตอนบลูม**")
    st.caption("AI-Driven Marine Early-Warning System")
    st.divider()

    selected_tab_name = st.radio(
        "📌 เลือกโหมดการทำงาน",
        [
            "🌊 1. Live Watch (สถานีจริง & กล้องดาวเทียม)",
            "🔬 2. Model Simulator (จำลองและทดสอบโมเดล)",
            "📊 3. Trend & Model Benchmark (ข้อมูลย้อนหลัง & สถิติ)",
        ],
        index=0,
    )

    st.divider()
    st.markdown("**🛰️ สถานะการเชื่อมต่อดาวเทียม**")
    st.markdown(
        """
        - **Optical Camera:** Sentinel-2 MSI L2A
        - **Data Catalog:** AWS Earth Search STAC
        - **Cloud Mask:** SCL Class 6 (Water Only)
        - **Indices:** NDCI (Chlorophyll) & NDWI
        """
    )
    st.caption("AquaMind MVP Core Version 1.2.0")


# ==============================================================================
# TAB 1: Live Environmental Watch (3 Real Coastal Stations + Satellite Camera)
# ==============================================================================
if selected_tab_name.startswith("🌊 1."):
    st.title("AquaMind — ระบบเฝ้าระวังสภาพแวดล้อมชายฝั่ง & กล้องดาวเทียม")
    st.caption("เชื่อมโยงกล้องดาวเทียมสำรวจโลก Copernicus Sentinel-2 เข้ากับ Weather/Ocean Forecast และ Machine Learning")

    st.warning(
        "⚠️ **ข้อชี้แจงสำคัญ:** ค่าที่แสดงคือ **ดัชนีเฝ้าระวังสภาพแวดล้อม (0–100 จุด)** ไม่ใช่เปอร์เซ็นต์โอกาสเกิดแพลงก์ตอนบลูม "
        "และไม่สามารถใช้แทนการตรวจวัดคุณภาพน้ำภาคสนามหรือคำยืนยันชนิดแพลงก์ตอนจากผู้เชี่ยวชาญได้"
    )

    station_col, refresh_col = st.columns([3, 1])
    with station_col:
        selected_station_id = st.selectbox(
            "📍 เลือกสถานีตรวจวัดชายฝั่ง",
            options=list(STATIONS_DATABASE.keys()),
            format_func=lambda sid: f"{STATIONS_DATABASE[sid]['name']} — {STATIONS_DATABASE[sid]['lat']}°N, {STATIONS_DATABASE[sid]['lon']}°E",
            index=2,  # Default to Bangsaen
        )
    with refresh_col:
        st.write("")
        st.write("")
        if st.button("🔄 รีเฟรชข้อมูลสด", width="stretch"):
            st.cache_data.clear()
            st.rerun()

    station_info = STATIONS_DATABASE[selected_station_id]
    st.caption(f"ℹ️ **โหมดสถานี:** {station_info['mode_description']}")

    # Load data for selected station
    try:
        with st.spinner("กำลังดึงข้อมูล Weather/Ocean และคำนวณโมเดล..."):
            environment, satellite, source_mode = load_station_data(selected_station_id)
            result = predict_environmental_watch(environment["features"], satellite)
    except Exception as exc:
        st.error(f"ระบบไม่สามารถประมวลผลดัชนีสำหรับสถานีนี้ได้: {exc}")
        st.stop()

    score = result["watch_index"]
    level = result["watch_level"]
    evidence = result["evidence_completeness"]
    satellite_used = result["satellite_used"]

    # 4 Main KPI Metrics
    st.divider()
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    metric_1.metric(
        "ดัชนีเฝ้าระวัง (Watch Index)",
        f"{score:.0f}/100",
        help="คะแนนประเมินสภาพแวดล้อมที่เอื้อต่อการบลูม (0=ต่ำสุด, 100=สูงสุด ไม่ใช่เปอร์เซ็นต์โอกาส)",
    )
    metric_2.metric(
        "ระดับการติดตาม",
        level,
        help="ติดตามปกติ (<45) | เฝ้าระวัง (45–64) | ควรตรวจน้ำเร็วขึ้น (≥65)",
    )
    metric_3.metric(
        "ความครบถ้วนของหลักฐาน",
        f"{evidence}/100",
        help="Weather/Ocean 75 คะแนน + ภาพถ่ายดาวเทียมที่ผ่าน QC 25 คะแนน",
    )
    metric_4.metric(
        "ภาพ Sentinel-2",
        "ใช้เป็นหลักฐานรอง" if satellite_used else "ไม่ใช้ในรอบนี้",
        help="ภาพดาวเทียมผ่านเกณฑ์อายุไม่เกิน 10 วันและพิกเซลน้ำ ≥ 5%",
    )

    # Explanation banner
    st.info(f"💡 **บทสรุปการประเมิน:** {result['plain_language_explanation']}")
    st.caption(
        f"ที่มาสภาพอากาศ: {source_mode} · เวลาออกพยากรณ์: {environment.get('issue_time', 'N/A')} · "
        + (
            f"ภาพ Sentinel-2 ล่าสุด: {satellite.get('observed_at', 'N/A')} (อายุภาพ {satellite.get('data_age_days', 0):.1f} วัน)"
            if satellite
            else "ไม่มีภาพดาวเทียมสำหรับพิกัดนี้ในรอบปัจจุบัน"
        )
    )

    # ==========================================================================
    # SATELLITE CAMERA & COASTAL VIEW SECTION
    # ==========================================================================
    st.divider()
    st.subheader("🛰️ การเชื่อมต่อกล้องและภาพถ่ายดาวเทียม (Live Satellite Camera & Coastal View)")
    st.caption("เชื่อมต่อสัญญาณภาพถ่ายจริงจากกล้อง MultiSpectral Instrument (MSI) ของดาวเทียม Copernicus Sentinel-2")

    with st.spinner("กำลังเชื่อมต่อสัญญาณภาพถ่ายดาวเทียมล่าสุดจากอวกาศ..."):
        sat_scene = fetch_live_satellite_scene(selected_station_id)
        aoi = STATION_AOIS.get(selected_station_id, BANGSAEN_AOI)

    col_cam, col_map = st.columns(2)

    with col_cam:
        st.markdown("**📸 ภาพถ่ายจริงจากกล้องดาวเทียม Sentinel-2 (True Color RGB Optical Camera)**")
        if sat_scene and sat_scene.get("thumbnail_url"):
            st.image(
                sat_scene["thumbnail_url"],
                caption=f"Sentinel-2 MSI Camera • บันทึกภาพเมื่อ {sat_scene['observed_at_str']}",
                width="stretch",
            )
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                status_icon = "🟢" if sat_scene.get("is_live") else "🟡"
                status_text = "ออนไลน์สด (Live Earth Search STAC)" if sat_scene.get("is_live") else "Snapshot ล่าสุดในระบบ"
                st.markdown(f"**สถานะสัญญาณกล้อง:** {status_icon} {status_text}")
                st.markdown(f"**ดาวเทียม:** `{sat_scene.get('platform')}`")
            with col_b2:
                st.markdown(f"**เมฆบดบัง (Cloud Cover):** `{sat_scene.get('cloud_cover')}%`")
                if sat_scene.get("data_age_days") is not None:
                    st.markdown(f"**อายุภาพถ่าย:** `{sat_scene.get('data_age_days')} วัน`")

            st.caption(f"Scene Granule ID: `{sat_scene.get('item_id')}` · แหล่งข้อมูล: {sat_scene.get('source_catalog')}")
        else:
            st.info("🛰️ ไม่พบภาพถ่ายดาวเทียมที่ผ่านเกณฑ์ Cloud Mask ในรอบปัจจุบัน")

    with col_map:
        st.markdown(f"**🗺️ แผนที่ภาพถ่ายดาวเทียมความละเอียดสูง (High-Resolution Satellite Map)**")
        w, s, e, n = aoi.bbox
        map_html = render_satellite_map(
            lat=station_info["lat"],
            lon=station_info["lon"],
            station_name=station_info["name"],
            score=score,
            west=w,
            south=s,
            east=e,
            north=n,
        )
        if hasattr(st, "iframe"):
            st.iframe(map_html, height=395, width="stretch")
        else:
            components.html(map_html, height=395)
        st.caption("เส้นประสีฟ้า = ขอบเขตสังเกตการณ์คุณภาพน้ำชายฝั่ง (AOI) สำหรับการคำนวณ NDCI / NDWI จากผิวน้ำ")

    with st.expander("🔬 ข้อมูลเชิงลึก: เซนเซอร์กล้องดาวเทียม MSI และการวิเคราะห์แพลงก์ตอนบลูม"):
        st.markdown(
            """
            - **กล้อง MultiSpectral Instrument (MSI):** ติดตั้งบนดาวเทียม Sentinel-2A และ 2B โคจรที่ความสูง 786 กิโลเมตร บันทึกภาพผิวน้ำด้วยแถบคลื่น 13 แถบ
            - **แบนด์สำคัญสำหรับการตรวจจับบลูม:**
              - `B03 (Green, 560 nm)`: ตรวจจับการสะท้อนแสงของคลอโรฟิลล์ ใช้คู่กับ B08 คำนวณ NDWI เพื่อแยกผืนน้ำ
              - `B04 (Red, 665 nm)`: แถบดูดกลืนแสงสูงสุดของคลอโรฟิลล์-เอ (Chlorophyll-a absorption peak)
              - `B05 (RedEdge, 705 nm)`: แถบสะท้อนแสงจำเพาะของเซลล์แพลงก์ตอนพืชที่กำลังเพิ่มจำนวน
              - `B08 (NIR, 842 nm)`: อินฟราเรดใกล้ น้ำจะดูดกลืนเกือบหมด ใช้แยกเกาะแก่ง เรือ และแนวชายฝั่ง
            - **สูตรคำนวณดัชนี NDCI:** $\\text{NDCI} = \\frac{B05 - B04}{B05 + B04}$ (ยิ่งค่าเป็นบวกมาก สัญญาณเซลล์สาหร่ายยิ่งหนาแน่น)
            - **Cloud & Water Filtering:** ใช้ชั้นข้อมูล Scene Classification Layer (`SCL Class 6 = Water`) เพื่อสกัดเฉพาะพิกเซลผิวน้ำจริงและกรองเมฆ หมอก และแสงสะท้อนออก
            """
        )

    # SHAP Explanations
    st.divider()
    st.subheader("📊 ปัจจัยสำคัญที่ขับเคลื่อนดัชนี (SHAP Explainability)")
    st.markdown("SHAP อธิบายว่าแต่ละตัวแปรผลักดันให้ดัชนีเพิ่มขึ้น (+) หรือลดลง (-) จากค่าฐาน")

    factor_data = [
        {
            "ปัจจัยสภาพแวดล้อม": factor["name"],
            "ค่าที่ตรวจวัดได้จริง": f"{factor['value']} {factor['unit']}",
            "ผลต่อดัชนี (SHAP)": f"{factor['shap_value']:+.1f} จุด",
            "ผลกระทบ": "ดันดัชนีขึ้น ⬆️" if factor["shap_value"] > 0 else "ช่วยกดดัชนีลง ⬇️" if factor["shap_value"] < 0 else "เป็นกลาง ⏺️",
            "คำอธิบายแบบเข้าใจง่าย": factor["plain_language"],
        }
        for factor in result["top_factors"]
    ]
    st.dataframe(pd.DataFrame(factor_data), hide_index=True, width="stretch")

    # Horizontal Bar chart for SHAP
    shap_chart_df = pd.DataFrame(
        {
            "ปัจจัย": [f["name"] for f in result["top_factors"]],
            "ผลต่อดัชนี (จุด)": [f["shap_value"] for f in result["top_factors"]],
        }
    ).set_index("ปัจจัย")
    st.bar_chart(shap_chart_df, horizontal=True)

    # Actions & Rules
    action_col, rule_col = st.columns(2)
    with action_col:
        st.subheader("📋 วันนี้เกษตรกรและผู้เพาะเลี้ยงควรทำอะไร")
        for action in result["recommendations"]:
            st.markdown(f"- ✅ {action}")
    with rule_col:
        st.subheader("📖 กฎเกณฑ์ที่ใช้ตัดสินระดับ (Calibrated Rules)")
        st.markdown(
            """
            - **Weather/Ocean และค่าฐาน:** รวมกันคิดเป็นคะแนนสูงสุด 75 จุด
            - **ภาพถ่าย Sentinel-2:** อายุ ≤ 10 วัน และ valid pixels ≥ 5% เพิ่มได้สูงสุด 20 จุด (หรือช่วยลดแต้มเมื่อน้ำใส)
            - **ต่ำกว่า 45 (ติดตามปกติ 🟢):** สภาพแวดล้อมปกติของอ่าวไทย (คะแนนปกติ 25–35 จุด) ไม่สร้าง False Alarm
            - **45–64 (เฝ้าระวัง 🟡):** เริ่มมีฝนชะล้างธาตุอาหาร หรือน้ำนิ่งอุ่นจัด ควรเพิ่มรอบตรวจน้ำเช้า–เย็น
            - **ตั้งแต่ 65 ขึ้นไป (ควรตรวจน้ำเร็วขึ้น 🔴):** ปัจจัยหนุนหลายด้านพร้อมกัน หรือกล้องดาวเทียมพบสัญญาณสีน้ำผิดปกติ
            """
        )

    # Ground truth expander
    with st.expander("🌍 ฐานข้อมูลภาคสนามสากลและการสอบเทียบ (Ground Truth & HAEDAT Verification)"):
        st.markdown(
            """
            - **การสอบเทียบตามสภาวะอ่าวไทย (Tropical Marine Calibration):** สภาพอากาศปกติของอ่าวไทย (ลม 2–4 m/s, อุณหภูมิน้ำ 29–31°C, ฝน < 15mm) เป็นสภาวะพื้นฐานธรรมชาติ โมเดลได้รับการปรับเทียบใหม่ให้คะแนนปกติอยู่ที่ **25–35 จุด (ติดตามปกติ 🟢)** เพื่อไม่ให้ส่งสัญญาณแจ้งเตือนพร่ำเพรื่อ (False Alarm)
            - **เกณฑ์ยกระดับการเฝ้าระวัง (≥45 จุด 🟡 / ≥65 จุด 🔴):**
              1. **น้ำหลากพาสารอาหาร (Nutrient Runoff):** ฝนสะสม 3 วัน > 25–50 mm ชะล้างธาตุอาหาร (N:P) จากแม่น้ำบางปะกงและชุมชนลงสู่อ่าว
              2. **น้ำนิ่งและน้ำอุ่นจัด (Stagnation & Thermal Stress):** ลมสงบนิ่ง (< 1.5 m/s) ร่วมกับผิวน้ำร้อน (> 31.5°C) ทำให้มวลน้ำไม่ผสมผสานและเกิดการแบ่งชั้น
              3. **สัญญาณดาวเทียมสะท้อนเซลล์สาหร่าย (NDCI > 0.03):** ภาพถ่ายดาวเทียม Sentinel-2 MSI ตรวจพบสัญญาณคลอโรฟิลล์-เอ สูงผิดปกติ
            """
        )
        gt_df = load_ground_truth_data()
        if gt_df is not None:
            n_total = len(gt_df)
            n_pos = int((gt_df["bloom_status"] == 1).sum())
            n_neg = int((gt_df["bloom_status"] == 0).sum())
            col_gt1, col_gt2, col_gt3, col_gt4 = st.columns(4)
            col_gt1.metric("ข้อมูล Ground Truth ทั้งหมด", f"{n_total} รายการ")
            col_gt2.metric("เหตุการณ์บลูมจริง (Positive)", f"{n_pos} เหตุการณ์", help="บันทึกในฐานข้อมูลสากล UNESCO-IOC HAEDAT และ DMCR")
            col_gt3.metric("รอบตรวจปกติน้ำใส (Negative)", f"{n_neg} รายการ", help="รอบตรวจวิเคราะห์คุณภาพน้ำปกติ ยืนยันว่าไม่มีการบลูม")
            col_gt4.metric("มาตรฐานการรับรอง", "HAEDAT + DMCR", help="UNESCO Intergovernmental Oceanographic Commission & กรมทรัพยากรทางทะเลและชายฝั่ง")

            st.caption("ตารางตัวอย่างข้อมูล Ground Truth จริงในจังหวัดชลบุรี (บางแสน, ศรีราชา, ชลบุรี):")
            st.dataframe(
                gt_df[["observed_at", "station_id", "species", "bloom_status", "chlorophyll_a_ug_l", "dissolved_oxygen_mg_l", "source", "notes"]],
                hide_index=True,
                width="stretch",
            )

    with st.expander("🔍 ดูค่าตัวแปร Weather/Ocean ทั้งหมด และ Data Lineage"):
        env_rows = [
            {"ตัวแปร": name, "ค่า": value, "คำอธิบาย": FEATURE_METADATA.get(name, ("", ""))[0], "หน่วย": FEATURE_METADATA.get(name, ("", ""))[1]}
            for name, value in environment["features"].items()
        ]
        st.dataframe(pd.DataFrame(env_rows), hide_index=True, width="stretch")
        st.markdown(
            f"- **Weather API URL:** `{environment.get('lineage', {}).get('weather_url', 'บันทึกในระบบ')}`\n"
            f"- **Marine API URL:** `{environment.get('lineage', {}).get('marine_url', 'บันทึกในระบบ')}`"
        )
        if satellite:
            st.markdown(
                f"- **Sentinel Item ID:** `{satellite.get('latest_item_id')}`\n"
                f"- **NDCI ล่าสุด / ความชัน 30 วัน:** `{satellite.get('ndci_latest')} / {satellite.get('ndci_slope_30d')}`\n"
                f"- **สัดส่วนพิกเซลน้ำที่ผ่าน QC:** `{satellite.get('valid_pixel_ratio', 0):.1%}`"
            )


# ==============================================================================
# TAB 2: Model Simulator & Testing (Dual Simulators)
# ==============================================================================
elif selected_tab_name.startswith("🔬 2."):
    st.title("AquaMind — เครื่องมือจำลองและทดสอบโมเดล (Simulator)")
    st.caption("ทดสอบ Machine Learning Model ที่ฝึกไว้ ทั้งแบบจำแนกบลูม (Classification) และแบบดัชนีเฝ้าระวัง (Watch Regressor)")

    sim_mode = st.radio(
        "เลือกประเภทโมเดลที่ต้องการทดสอบ:",
        [
            "🧪 A) โมเดลจำลอง Bloom Classification (13 ตัวแปร: ดาวเทียม B2-B8, DO, Chlorophyll, สภาพอากาศ)",
            "🌊 B) โมเดล Weather-First Environmental Watch (14 ตัวแปร: สภาพอากาศ/ทะเล + ดาวเทียม)",
        ],
        horizontal=True,
    )

    # --------------------------------------------------------------------------
    # Sub-Mode A: Bloom Classification (13 features)
    # --------------------------------------------------------------------------
    if sim_mode.startswith("🧪 A)"):
        st.subheader("โมเดลจำแนกโอกาสเกิดแพลงก์ตอนบลูม (Bloom Classifier)")
        st.caption("ฝึกจากชุดข้อมูลจำลอง 12,000 แถวด้วย SMOTE และทดสอบกับ XGBoost / Random Forest")

        col_m_select, col_p_select = st.columns([1, 2])
        with col_m_select:
            model_engine = st.selectbox("เลือก Machine Learning Model:", ["XGBoost Classifier (แนะนำ)", "Random Forest Classifier"])
        with col_p_select:
            preset_choice = st.selectbox("เลือกสถานการณ์จำลอง (Preset):", list(PRESETS_CLASSIFIER.keys()) + ["กำหนดค่าเอง (Custom)"])

        preset_vals = PRESETS_CLASSIFIER.get(preset_choice, PRESETS_CLASSIFIER["ตัวอย่างเฝ้าระวัง (Watch / Moderate)"])

        with st.form("classification_form"):
            col_spec, col_meteo, col_water = st.columns(3)

            with col_spec:
                st.markdown("🛰️ **Sentinel-2 Reflectance (แถบแสงจากกล้องดาวเทียม)**")
                b2_in = st.number_input("B2 (Blue 490nm)", 0.0, 1.0, float(preset_vals["B2"]), 0.01)
                b3_in = st.number_input("B3 (Green 560nm)", 0.0, 1.0, float(preset_vals["B3"]), 0.01)
                b4_in = st.number_input("B4 (Red 665nm)", 0.0, 1.0, float(preset_vals["B4"]), 0.01)
                b5_in = st.number_input("B5 (RedEdge 705nm)", 0.0, 1.0, float(preset_vals["B5"]), 0.01)
                b8_in = st.number_input("B8 (NIR 842nm)", 0.0, 1.0, float(preset_vals["B8"]), 0.01)

                calc_ndwi, calc_ndci = calculate_indices(b3_in, b4_in, b5_in, b8_in)
                st.caption(f"ดัชนีคำนวณอัตโนมัติ: **NDCI = {calc_ndci:.3f}**, **NDWI = {calc_ndwi:.3f}**")

            with col_meteo:
                st.markdown("🌤️ **สภาพอากาศ (Weather)**")
                temp_in = st.number_input("อุณหภูมิอากาศ (°C)", 15.0, 45.0, float(preset_vals["Temperature"]), 0.5)
                wind_in = st.number_input("ความเร็วลม (m/s)", 0.0, 30.0, float(preset_vals["WindSpeed"]), 0.5)
                hum_in = st.number_input("ความชื้นสัมพัทธ์ (%)", 20.0, 100.0, float(preset_vals["Humidity"]), 1.0)
                rain_in = st.number_input("ปริมาณฝน (mm)", 0.0, 300.0, float(preset_vals["Rainfall"]), 1.0)

            with col_water:
                st.markdown("💧 **คุณภาพน้ำ (Water Quality)**")
                do_in = st.number_input("ออกซิเจนละลายน้ำ DO (mg/L)", 0.0, 20.0, float(preset_vals["DO"]), 0.1)
                chlo_in = st.number_input("คลอโรฟิลล์-เอ (µg/L)", 0.0, 200.0, float(preset_vals["Chlorophyll"]), 1.0)
                st.caption("ตัวแปรชีวภาพและเคมีจากการตรวจวัดในแปลงเพาะเลี้ยง")

            submit_pred = st.form_submit_button("🚀 ประมวลผลโมเดล (Run Prediction)", width="stretch", type="primary")

        if submit_pred:
            row_dict = {
                "B2": b2_in, "B3": b3_in, "B4": b4_in, "B5": b5_in, "B8": b8_in,
                "NDWI": (b3_in - b8_in) / (b3_in + b8_in + 1e-6),
                "NDCI": (b5_in - b4_in) / (b5_in + b4_in + 1e-6),
                "Temperature": temp_in, "WindSpeed": wind_in, "Humidity": hum_in,
                "Rainfall": rain_in, "DO": do_in, "Chlorophyll": chlo_in,
            }
            input_df = pd.DataFrame([[row_dict[name] for name in SIMULATOR_FEATURES]], columns=SIMULATOR_FEATURES)

            if "XGBoost" in model_engine:
                booster = load_xgboost_classifier()
                if booster is None:
                    st.error("ไม่พบไฟล์โมเดล Model/models/xgboost_model.json")
                else:
                    matrix = xgb.DMatrix(input_df, feature_names=SIMULATOR_FEATURES)
                    prob = float(booster.predict(matrix)[0])
                    contribs = booster.predict(matrix, pred_contribs=True)[0]
                    shap_vals = contribs[:-1]
                    base_val = float(contribs[-1])

                    st.divider()
                    col_res1, col_res2, col_res3 = st.columns(3)
                    col_res1.metric("โอกาสเกิดบลูม (Probability)", f"{prob:.1%}")
                    col_res2.markdown("**การจำแนกประเภท (Classification):**")
                    if prob >= 0.65:
                        col_res2.markdown('<span class="badge-urgent">⚠️ เสี่ยงสูง (Bloom Alert)</span>', unsafe_allow_html=True)
                    elif prob >= 0.35:
                        col_res2.markdown('<span class="badge-watch">⚠️ เฝ้าระวัง (Watch)</span>', unsafe_allow_html=True)
                    else:
                        col_res2.markdown('<span class="badge-normal">✅ สภาวะปกติ (Normal)</span>', unsafe_allow_html=True)

                    col_res3.metric("NDCI / NDWI", f"{row_dict['NDCI']:.3f} / {row_dict['NDWI']:.3f}")
                    st.progress(min(max(prob, 0.0), 1.0))

                    # SHAP Analysis
                    st.subheader("🔍 SHAP Explanation (ปัจจัยที่ดันโอกาสขึ้นหรือลง)")
                    shap_df = pd.DataFrame({
                        "Feature": SIMULATOR_FEATURES,
                        "Value": [f"{row_dict[f]:.3f}" for f in SIMULATOR_FEATURES],
                        "SHAP Impact (raw margin)": shap_vals,
                    })
                    shap_df["AbsImpact"] = shap_df["SHAP Impact (raw margin)"].abs()
                    shap_df = shap_df.sort_values(by="AbsImpact", ascending=False).drop(columns=["AbsImpact"])

                    st.bar_chart(shap_df.set_index("Feature")[["SHAP Impact (raw margin)"]], horizontal=True)
                    st.dataframe(shap_df, hide_index=True, width="stretch")
                    st.caption(f"Base Value = {base_val:.4f} · รวม Raw Margin = {base_val + sum(shap_vals):.4f}")

            else:  # Random Forest
                rf_model = load_rf_classifier()
                if rf_model is None:
                    st.error("ไม่สามารถโหลดไฟล์โมเดล Random Forest (random_forest.pkl)")
                else:
                    prob_rf = float(rf_model.predict_proba(input_df)[0, 1])
                    st.divider()
                    col_rf1, col_rf2 = st.columns(2)
                    col_rf1.metric("Random Forest Probability", f"{prob_rf:.1%}")
                    col_rf2.markdown("**ผลการวินิจฉัย:**")
                    if prob_rf >= 0.5:
                        col_rf2.markdown('<span class="badge-urgent">⚠️ เสี่ยงเกิดบลูม (Bloom Event)</span>', unsafe_allow_html=True)
                    else:
                        col_rf2.markdown('<span class="badge-normal">✅ สภาวะปกติ (Non-Bloom)</span>', unsafe_allow_html=True)

                    st.progress(prob_rf)

                    # Feature importance
                    if hasattr(rf_model, "feature_importances_"):
                        st.subheader("🌲 Random Forest Feature Importance (ความสำคัญของตัวแปร)")
                        rf_imp_df = pd.DataFrame({
                            "Feature": SIMULATOR_FEATURES,
                            "Importance": rf_model.feature_importances_,
                        }).sort_values(by="Importance", ascending=False)
                        st.bar_chart(rf_imp_df.set_index("Feature"), horizontal=True)

    # --------------------------------------------------------------------------
    # Sub-Mode B: Environmental Watch Simulator (14 features)
    # --------------------------------------------------------------------------
    else:
        st.subheader("จำลองการคำนวณดัชนีเฝ้าระวัง (Weather-First Environmental Watch Simulator)")
        st.caption("ปรับแต่งพารามิเตอร์สภาพอากาศ/ทะเล และภาพถ่ายดาวเทียมเพื่อดูปฏิกิริยาของ XGBoost Rule-Surrogate")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.markdown("🌡️ **ตัวแปรสภาพอากาศและผิวน้ำทะเล (Weather & Ocean)**")
            sim_sst = st.slider("อุณหภูมิผิวน้ำทะเล SST (°C)", 24.0, 34.0, 30.5, 0.1)
            sim_air_temp = st.slider("อุณหภูมิอากาศเฉลี่ย 3 วัน (°C)", 24.0, 36.0, 31.0, 0.1)
            sim_wind = st.slider("ความเร็วลมเฉลี่ย 3 วัน (m/s)", 0.5, 15.0, 3.5, 0.1)
            sim_rain = st.slider("ฝนสะสม 3 วัน (mm)", 0.0, 100.0, 15.0, 1.0)
            sim_wave = st.slider("ความสูงคลื่น (m)", 0.1, 2.5, 0.5, 0.05)
            sim_curr = st.slider("ความเร็วกระแสน้ำ (km/h)", 0.05, 2.0, 0.3, 0.05)

        with col_w2:
            st.markdown("🛰️ **ตัวแปรภาพถ่ายดาวเทียม Sentinel-2 (Secondary Evidence)**")
            use_sat = st.checkbox("เปิดใช้ข้อมูลภาพถ่ายดาวเทียมเสริม", value=True)
            if use_sat:
                sim_ndci = st.slider("NDCI ล่าสุด", -0.05, 0.20, 0.045, 0.005)
                sim_slope = st.slider("แนวโน้ม NDCI 30 วัน (Slope)", -0.01, 0.01, 0.001, 0.0005)
                sim_age = st.slider("อายุของภาพถ่าย (วัน)", 0.5, 20.0, 3.0, 0.5)
                sim_valid = st.slider("สัดส่วนพิกเซลน้ำที่ผ่าน QC", 0.0, 1.0, 0.85, 0.05)
            else:
                sim_ndci, sim_slope, sim_age, sim_valid = None, None, None, None

        sim_env_features = {
            "air_temperature_mean_d0_3": sim_air_temp,
            "precipitation_sum_d0_3": sim_rain,
            "wind_speed_mean_d0_3": sim_wind,
            "wind_gust_max_d0_3": sim_wind * 1.5,
            "air_temperature_mean_d3_5": sim_air_temp,
            "precipitation_sum_d3_5": sim_rain * 0.8,
            "wind_speed_mean_d3_5": sim_wind,
            "sst_at_issue": sim_sst,
            "wave_height_at_issue": sim_wave,
            "current_velocity_at_issue": sim_curr,
        }

        sim_sat_dict = (
            {
                "ndci_latest": sim_ndci,
                "ndci_slope_30d": sim_slope,
                "data_age_days": sim_age,
                "valid_pixel_ratio": sim_valid,
            }
            if use_sat
            else None
        )

        sim_result = predict_environmental_watch(sim_env_features, sim_sat_dict)

        st.divider()
        st.subheader("ผลการคำนวณดัชนีเฝ้าระวังแบบ Real-time")
        res_c1, res_c2, res_c3, res_c4 = st.columns(4)
        res_c1.metric("ดัชนีเฝ้าระวัง (Watch Index)", f"{sim_result['watch_index']:.1f}/100")
        res_c2.metric("ระดับ", sim_result["watch_level"])
        res_c3.metric("ความครบถ้วนของหลักฐาน", f"{sim_result['evidence_completeness']}/100")
        res_c4.metric("Sentinel-2 สถานะ", "ผ่าน QC" if sim_result["satellite_used"] else "ไม่ผ่าน / ปิดใช้งาน")

        st.info(sim_result["plain_language_explanation"])


# ==============================================================================
# TAB 3: Historical Trend & Model Benchmark
# ==============================================================================
else:
    st.title("AquaMind — ข้อมูลย้อนหลัง & สถิติประสิทธิภาพโมเดล")
    st.caption("Time-Series Analysis · Model Evaluation Benchmark · Scientific Guardrails")

    ts_df = load_timeseries_data()
    if ts_df is not None:
        st.subheader("📈 แนวโน้มดัชนีและคุณภาพน้ำสถานีชลบุรี (Time-Series Scenario)")
        st.caption("แสดงการเปลี่ยนแปลงของดัชนีเฝ้าระวัง ควบคู่กับ NDCI, SST anomaly, ความเร็วลม และค่า DO ย้อนหลัง")

        # Line chart of Risk Score with Thresholds
        chart_data = ts_df.set_index("date")[["risk_score"]]
        st.line_chart(chart_data)

        # Multi-factor comparison
        st.subheader("📊 เปรียบเทียบความสัมพันธ์ของตัวแปรย้อนหลัง")
        col_ts1, col_ts2 = st.columns(2)
        with col_ts1:
            st.markdown("**สัญญาณดาวเทียม (NDCI) และอุณหภูมิน้ำ (SST Anomaly)**")
            st.line_chart(ts_df.set_index("date")[["ndci", "sst_anomaly"]])
        with col_ts2:
            st.markdown("**ออกซิเจนละลายน้ำ (DO) และความเร็วลม (Wind Speed)**")
            st.line_chart(ts_df.set_index("date")[["do_value", "wind_speed_3d"]])

        with st.expander("📄 ดูตารางข้อมูลย้อนหลังฉบับเต็ม"):
            st.dataframe(ts_df, hide_index=True, width="stretch")

    st.divider()

    # Model Evaluation Metrics Comparison Table
    st.subheader("🏆 ผลการทดสอบเปรียบเทียบโมเดล Machine Learning (Model Benchmark)")
    st.markdown("ผลการประเมินบนชุดข้อมูลทดสอบ (Test Set 20% Stratified) จากกระบวนการฝึกใน `Model/train.py`:")

    eval_data = {
        "โมเดล (Algorithm)": ["Random Forest Classifier", "XGBoost Classifier (คัดเลือก)"],
        "Accuracy": ["98.25%", "98.71%"],
        "Precision": ["97.80%", "98.42%"],
        "Recall": ["98.10%", "98.60%"],
        "F1-Score": ["0.9795", "0.9851"],
        "ROC-AUC": ["0.9982", "0.9991"],
        "จุดเด่นด้านการใช้งาน": [
            "ทนทานต่อ Outlier, วิเคราะห์ Feature Importance จากการแตกกิ่ง",
            "รองรับ SHAP TreeExplainer ระดับแถว, สามารถ Export เป็น JSON พกพาได้",
        ],
    }
    st.dataframe(pd.DataFrame(eval_data), hide_index=True, width="stretch")

    st.divider()
    st.subheader("🌐 ฐานข้อมูลและผลการตรวจสอบความถูกต้องภาคสนาม (Ground Truth Verification)")
    st.caption("บูรณาการข้อมูลน้ำเปลี่ยนสีที่ผ่านการตรวจสอบจริงจาก UNESCO-IOC HAEDAT และเครือข่ายตรวจวัด สบทช./กรมทรัพยากรทางทะเลและชายฝั่ง (DMCR)")

    gt_df_tab3 = load_ground_truth_data()
    if gt_df_tab3 is not None:
        c_gt1, c_gt2, c_gt3 = st.columns(3)
        c_gt1.metric("จำนวนแถวผลตรวจที่ผ่านการรับรอง", f"{len(gt_df_tab3)} รายการ")
        c_gt2.metric("เหตุการณ์บลูมจริงที่บันทึก (Positive)", f"{(gt_df_tab3['bloom_status'] == 1).sum()} ครั้ง")
        c_gt3.metric("รอบตรวจปกติติดตามน้ำใส (Negative)", f"{(gt_df_tab3['bloom_status'] == 0).sum()} ครั้ง")

        st.markdown("**การกระจายตัวของชนิดแพลงก์ตอนบลูมในอ่าวไทยตอนบน (Species Recorded):**")
        species_counts = gt_df_tab3[gt_df_tab3["bloom_status"] == 1]["species"].value_counts().reset_index()
        species_counts.columns = ["ชนิดแพลงก์ตอน", "จำนวนครั้งที่เกิดบลูม"]
        st.dataframe(species_counts, hide_index=True, width="stretch")

    # Scientific Guardrails
    st.subheader("🛡️ ข้อจำกัดทางวิทยาศาสตร์และจริยธรรม AI (Scientific Guardrails)")
    st.markdown(
        """
        1. **การจำแนกสถานการณ์สังเคราะห์ (Synthetic Model):** โมเดลจำลองถูกสร้างขึ้นเพื่อทดสอบ Data Pipeline, Feature Extraction และการอธิบายผลด้วย SHAP ค่าความแม่นยำจึงเป็นค่าเชิงเทคนิค ยังไม่สามารถอ้างอิงเป็น Field Accuracy ในธรรมชาติได้
        2. **ดัชนีเฝ้าระวังสภาพแวดล้อม (Environmental Watch Index):** ดัชนี 0–100 ในโหมด Live Watch วัดความเอื้ออำนวยของสภาพแวดล้อมตามกฎชีววิทยา ไม่ใช่โอกาสความน่าจะเป็น (Probability) ของการเกิดบลูม
        3. **ต้องยืนยันด้วยผลตรวจน้ำภาคสนาม:** ระบบทำหน้าที่เป็นสัญญาณเตือนภัยล่วงหน้า (Early Warning) เพื่อให้เพิ่มความถี่ในการตรวจน้ำ ก่อนดำเนินมาตรการที่มีต้นทุนสูง (เช่น การเติมออกซิเจนหรือการย้ายกระชัง) ต้องเก็บตัวอย่างน้ำตรวจวัดเสมอ
        """
    )
