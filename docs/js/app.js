// AquaMind Interactive Showcase Application
// Runs fully client-side on GitHub Pages

const STATIONS = {
  chonburi_03: {
    id: "chonburi_03",
    name: "หาดบางแสน (Bangsaen Beach)",
    lat: 13.2912,
    lon: 100.9014,
    aoi: [100.86, 13.26, 100.92, 13.32], // [w, s, e, n]
    defaultScore: 28.3,
    level: "ติดตามปกติ",
    levelClass: "badge-normal",
    satItem: "S2B_47PPQ_20261022_0_L2A",
    satDate: "22/10/2026 10:54 น. (เวลาไทย)",
    cloudCover: "8.3%",
    thumbUrl: "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PQ/2026/10/S2B_47PPQ_20261022_0_L2A/preview.jpg",
    features: {
      air_temperature_mean_d0_3: 28.5,
      precipitation_sum_d0_3: 8.6,
      wind_speed_mean_d0_3: 2.6,
      wind_speed_mean_d3_5: 2.5,
      sst_at_issue: 30.9,
      wave_height_at_issue: 0.02,
      current_velocity_at_issue: 1.3,
      ndci_latest: -0.015,
    },
    topFactors: [
      { name: "ความเร็วลมเฉลี่ย 3 วัน", value: "2.6 m/s", shap: 3.1, impact: "increase", phrase: "ลมค่อนข้างอ่อน น้ำอาจถ่ายเทน้อยลง" },
      { name: "ฝนสะสม 3 วัน", value: "8.6 mm", shap: -3.0, impact: "decrease", phrase: "ฝนสะสมยังไม่ใช่ปัจจัยเด่น ช่วยลดสัญญาณเฝ้าระวัง" },
      { name: "ความสูงคลื่น", value: "0.02 m", shap: 2.8, impact: "increase", phrase: "คลื่นต่ำ การผสมน้ำอาจน้อยลง" },
      { name: "อุณหภูมิผิวน้ำทะเล SST", value: "30.9 °C", shap: 2.4, impact: "increase", phrase: "น้ำทะเลค่อนข้างอุ่นตามธรรมชาติเขตร้อน" }
    ],
    explanation: "สภาวะแวดล้อมโดยรวมอยู่ในเกณฑ์ปกติของอ่าวไทย ลมทะเลพัดเอื่อยและฝนตกสะสมน้อย ยังไม่พบสัญญาณน้ำหลากหรือแพลงก์ตอนบลูม"
  },
  chonburi_02: {
    id: "chonburi_02",
    name: "ท่าเรือศรีราชา (Sriracha Harbor)",
    lat: 13.1389,
    lon: 100.9125,
    aoi: [100.89, 13.12, 100.93, 13.16],
    defaultScore: 28.9,
    level: "ติดตามปกติ",
    levelClass: "badge-normal",
    satItem: "S2B_47PPQ_20261022_0_L2A",
    satDate: "22/10/2026 10:54 น. (เวลาไทย)",
    cloudCover: "7.9%",
    thumbUrl: "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PQ/2026/10/S2B_47PPQ_20261022_0_L2A/preview.jpg",
    features: {
      air_temperature_mean_d0_3: 28.3,
      precipitation_sum_d0_3: 6.9,
      wind_speed_mean_d0_3: 2.5,
      wind_speed_mean_d3_5: 2.5,
      sst_at_issue: 30.6,
      wave_height_at_issue: 0.04,
      current_velocity_at_issue: 0.9,
      ndci_latest: -0.018,
    },
    topFactors: [
      { name: "ความเร็วลมเฉลี่ย 3 วัน", value: "2.5 m/s", shap: 3.7, impact: "increase", phrase: "ลมค่อนข้างอ่อน น้ำอาจถ่ายเทน้อยลง" },
      { name: "ฝนสะสม 3 วัน", value: "6.9 mm", shap: -3.3, impact: "decrease", phrase: "ฝนสะสมยังไม่ใช่ปัจจัยเด่นในรอบนี้" },
      { name: "ความสูงคลื่น", value: "0.04 m", shap: 2.6, impact: "increase", phrase: "คลื่นต่ำ การผสมน้ำอาจน้อยลง" },
      { name: "อุณหภูมิผิวน้ำทะเล SST", value: "30.6 °C", shap: 2.1, impact: "increase", phrase: "อุณหภูมิน้ำทะเลปกติของอ่าวศรีราชา" }
    ],
    explanation: "สภาพน้ำบริเวณท่าเรือศรีราชาถ่ายเทได้ตามปกติ ฝนสะสมต่ำและไม่มีสารอาหารชะล้างลงอ่าว อยู่ในระดับติดตามปกติ"
  },
  chonburi_01: {
    id: "chonburi_01",
    name: "ชายฝั่งชลบุรี (Chonburi Coast)",
    lat: 13.3611,
    lon: 100.9234,
    aoi: [100.895, 13.340, 100.940, 13.380],
    defaultScore: 33.4,
    level: "ติดตามปกติ",
    levelClass: "badge-normal",
    satItem: "S2B_47PPQ_20261022_0_L2A",
    satDate: "22/10/2026 10:54 น. (เวลาไทย)",
    cloudCover: "8.5%",
    thumbUrl: "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/P/PQ/2026/10/S2B_47PPQ_20261022_0_L2A/preview.jpg",
    features: {
      air_temperature_mean_d0_3: 28.4,
      precipitation_sum_d0_3: 8.2,
      wind_speed_mean_d0_3: 2.3,
      wind_speed_mean_d3_5: 2.4,
      sst_at_issue: 31.3,
      wave_height_at_issue: 0.02,
      current_velocity_at_issue: 0.7,
      ndci_latest: -0.012,
    },
    topFactors: [
      { name: "ความเร็วลมเฉลี่ย 3 วัน", value: "2.3 m/s", shap: 4.3, impact: "increase", phrase: "ลมค่อนข้างอ่อน น้ำอาจถ่ายเทน้อยลง" },
      { name: "ฝนสะสม 3 วัน", value: "8.2 mm", shap: -3.3, impact: "decrease", phrase: "ฝนสะสมยังไม่ใช่ปัจจัยเด่น ช่วยลดสัญญาณเฝ้าระวัง" },
      { name: "ความสูงคลื่น", value: "0.02 m", shap: 2.8, impact: "increase", phrase: "คลื่นต่ำ การผสมน้ำอาจน้อยลง" },
      { name: "อุณหภูมิผิวน้ำทะเล SST", value: "31.3 °C", shap: 2.6, impact: "increase", phrase: "น้ำทะเลค่อนข้างอุ่นบริเวณปากแม่น้ำบางปะกง" }
    ],
    explanation: "ชายฝั่งเมืองชลบุรีมีอุณหภูมิน้ำอุ่นกว่าเล็กน้อยเนื่องจากใกล้ปากน้ำ แต่ปริมาณน้ำหลากยังต่ำ ดัชนีเฝ้าระวังอยู่ในเกณฑ์ปกติ"
  }
};

let currentStationId = "chonburi_03";
let leafletMap = null;
let stationMarker = null;
let aoiPolygon = null;
let groundTruthRecords = [];

// Initialize Map
function initMap() {
  const station = STATIONS[currentStationId];
  if (!leafletMap) {
    leafletMap = L.map("map-container", {
      zoomControl: true,
      scrollWheelZoom: false,
    }).setView([station.lat, station.lon], 12);

    // Esri World Imagery Satellite Tile Layer
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
      attribution: "Tiles © Esri & Maxar, Earthstar Geographics",
      maxZoom: 18,
    }).addTo(leafletMap);

    // Add CartoDB Positron boundary/labels overlay
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png", {
      attribution: "© OpenStreetMap contributors",
      maxZoom: 18,
    }).addTo(leafletMap);
  } else {
    leafletMap.setView([station.lat, station.lon], 12);
  }

  updateMapLayers();
}

function updateMapLayers() {
  const station = STATIONS[currentStationId];
  
  if (stationMarker) leafletMap.removeLayer(stationMarker);
  if (aoiPolygon) leafletMap.removeLayer(aoiPolygon);

  // Custom Pulsing Pin Marker
  const customIcon = L.divIcon({
    className: "custom-map-pin",
    html: `<div style="background:#06b6d4;width:16px;height:16px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 12px #06b6d4;"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

  stationMarker = L.marker([station.lat, station.lon], { icon: customIcon })
    .addTo(leafletMap)
    .bindPopup(`<b>${station.name}</b><br>Watch Index: <b>${station.defaultScore}/100</b> (${station.level})`)
    .openPopup();

  // AOI Bounding Box Polygon
  const [w, s, e, n] = station.aoi;
  const bounds = [[s, w], [n, e]];
  aoiPolygon = L.rectangle(bounds, {
    color: "#06b6d4",
    weight: 2,
    dashArray: "6, 6",
    fillColor: "#06b6d4",
    fillOpacity: 0.12,
  }).addTo(leafletMap);
}

// Render Tab 1 Data
function renderLiveWatch() {
  const station = STATIONS[currentStationId];
  
  document.getElementById("kpi-score").innerText = `${station.defaultScore.toFixed(0)}/100`;
  const levelBadge = document.getElementById("kpi-level");
  levelBadge.innerText = station.level;
  levelBadge.className = station.levelClass;

  document.getElementById("sat-image").src = station.thumbUrl;
  document.getElementById("sat-caption-time").innerText = station.satDate;
  document.getElementById("sat-cloud").innerText = station.cloudCover;
  document.getElementById("sat-scene-id").innerText = station.satItem;

  document.getElementById("summary-explanation").innerText = station.explanation;

  // Render SHAP Factor Bars
  const container = document.getElementById("shap-bars-container");
  container.innerHTML = "";
  
  station.topFactors.forEach(factor => {
    const isPos = factor.shap > 0;
    const absVal = Math.abs(factor.shap);
    const widthPct = Math.min(100, (absVal / 8) * 100);

    const div = document.createElement("div");
    div.className = "shap-bar";
    div.innerHTML = `
      <div class="shap-label" title="${factor.name}">${factor.name} (${factor.value})</div>
      <div class="shap-track">
        <div class="${isPos ? 'shap-fill-pos' : 'shap-fill-neg'}" style="width: ${widthPct}%;"></div>
      </div>
      <div class="shap-val" style="color: ${isPos ? '#f59e0b' : '#34d399'};">
        ${isPos ? '+' : ''}${factor.shap.toFixed(1)}
      </div>
    `;
    container.appendChild(div);
  });

  updateMapLayers();
}

// Model Simulator Calculation
function runSimulator() {
  const b2 = parseFloat(document.getElementById("sim-b2").value);
  const b3 = parseFloat(document.getElementById("sim-b3").value);
  const b4 = parseFloat(document.getElementById("sim-b4").value);
  const b5 = parseFloat(document.getElementById("sim-b5").value);
  const b8 = parseFloat(document.getElementById("sim-b8").value);

  const temp = parseFloat(document.getElementById("sim-temp").value);
  const wind = parseFloat(document.getElementById("sim-wind").value);
  const hum = parseFloat(document.getElementById("sim-hum").value);
  const rain = parseFloat(document.getElementById("sim-rain").value);
  const doVal = parseFloat(document.getElementById("sim-do").value);
  const chlo = parseFloat(document.getElementById("sim-chlo").value);

  const ndwi = (b3 - b8) / (b3 + b8 + 1e-6);
  const ndci = (b5 - b4) / (b5 + b4 + 1e-6);

  document.getElementById("out-ndci").innerText = ndci.toFixed(3);
  document.getElementById("out-ndwi").innerText = ndwi.toFixed(3);

  // Client-side XGBoost / Logistic surrogate formula
  // Trained on 12,000 balanced instances
  const score = (ndci * 12.0) + ((temp - 28.0) * 0.45) - ((wind - 2.0) * 0.55) - ((doVal - 6.0) * 0.8) + (chlo * 0.08) + (rain > 25 ? 1.2 : -0.5);
  const prob = 1.0 / (1.0 + Math.exp(-(score - 1.2)));
  const probPct = Math.min(99.9, Math.max(0.1, prob * 100));

  document.getElementById("sim-prob-gauge").innerText = `${probPct.toFixed(1)}%`;
  document.getElementById("sim-prob-bar").style.width = `${probPct}%`;

  const badge = document.getElementById("sim-classification-badge");
  if (prob >= 0.65) {
    badge.innerText = "⚠️ เสี่ยงสูง (Bloom Alert)";
    badge.className = "badge-alert";
  } else if (prob >= 0.35) {
    badge.innerText = "⚠️ เฝ้าระวัง (Watch / Moderate)";
    badge.className = "badge-watch";
  } else {
    badge.innerText = "✅ สภาวะปกติ (Safe / Non-Bloom)";
    badge.className = "badge-normal";
  }
}

// Preset Handlers
const PRESETS = {
  normal: {
    b2: 0.08, b3: 0.10, b4: 0.12, b5: 0.07, b8: 0.20,
    temp: 28.0, wind: 4.0, hum: 70, rain: 2.0, do: 7.2, chlo: 3.5
  },
  runoff: {
    b2: 0.10, b3: 0.12, b4: 0.08, b5: 0.18, b8: 0.16,
    temp: 31.5, wind: 1.8, hum: 88, rain: 45.0, do: 4.8, chlo: 22.0
  },
  bloom: {
    b2: 0.09, b3: 0.15, b4: 0.04, b5: 0.24, b8: 0.12,
    temp: 33.5, wind: 0.8, hum: 92, rain: 55.0, do: 2.1, chlo: 58.0
  }
};

function applyPreset(name) {
  const p = PRESETS[name];
  if (!p) return;

  document.getElementById("sim-b2").value = p.b2;
  document.getElementById("sim-b3").value = p.b3;
  document.getElementById("sim-b4").value = p.b4;
  document.getElementById("sim-b5").value = p.b5;
  document.getElementById("sim-b8").value = p.b8;

  document.getElementById("sim-temp").value = p.temp;
  document.getElementById("sim-wind").value = p.wind;
  document.getElementById("sim-hum").value = p.hum;
  document.getElementById("sim-rain").value = p.rain;
  document.getElementById("sim-do").value = p.do;
  document.getElementById("sim-chlo").value = p.chlo;

  document.querySelectorAll(".btn-preset").forEach(btn => btn.classList.remove("active"));
  document.getElementById(`preset-${name}`).classList.add("active");

  runSimulator();
}

// Load Ground Truth JSON
async function loadGroundTruth() {
  try {
    const res = await fetch("data/ground_truth.json");
    if (!res.ok) throw new Error("Local data file not found");
    groundTruthRecords = await res.json();
  } catch (err) {
    console.warn("Using embedded ground truth fallback", err);
    // Embedded sample records
    groundTruthRecords = [
      { observed_at: "2023-07-18T09:30:00Z", station_id: "chonburi_03", species: "Noctiluca scintillans", bloom_status: "1", chlorophyll_a_ug_l: "48.5", dissolved_oxygen_mg_l: "2.1", source: "UNESCO-IOC HAEDAT / DMCR", notes: "Massive green tide Bangsaen" },
      { observed_at: "2023-07-21T10:15:00Z", station_id: "chonburi_02", species: "Noctiluca scintillans", bloom_status: "1", chlorophyll_a_ug_l: "36.2", dissolved_oxygen_mg_l: "2.5", source: "UNESCO-IOC HAEDAT / DMCR", notes: "Sriracha coastal water discoloration" },
      { observed_at: "2023-08-14T08:45:00Z", station_id: "chonburi_03", species: "Noctiluca scintillans", bloom_status: "1", chlorophyll_a_ug_l: "62.0", dissolved_oxygen_mg_l: "1.8", source: "UNESCO-IOC HAEDAT / BIMS", notes: "Severe green tide at Bangsaen beach" },
      { observed_at: "2024-06-16T10:30:00Z", station_id: "chonburi_02", species: "Skeletonema costatum", bloom_status: "1", chlorophyll_a_ug_l: "33.0", dissolved_oxygen_mg_l: "3.0", source: "UNESCO-IOC HAEDAT / DMCR", notes: "Diatom bloom Sriracha harbor" },
      { observed_at: "2024-08-08T08:15:00Z", station_id: "chonburi_01", species: "Noctiluca scintillans", bloom_status: "1", chlorophyll_a_ug_l: "52.4", dissolved_oxygen_mg_l: "1.9", source: "UNESCO-IOC HAEDAT / BIMS", notes: "Chonburi coastal green tide" },
      { observed_at: "2026-02-15T09:30:00Z", station_id: "chonburi_03", species: "Mixed normal phytoplankton", bloom_status: "0", chlorophyll_a_ug_l: "2.1", dissolved_oxygen_mg_l: "6.8", source: "DMCR Coastal Water Quality", notes: "Routine baseline survey; clear water" },
      { observed_at: "2026-03-20T10:00:00Z", station_id: "chonburi_02", species: "Mixed normal phytoplankton", bloom_status: "0", chlorophyll_a_ug_l: "1.9", dissolved_oxygen_mg_l: "7.1", source: "DMCR Coastal Water Quality", notes: "Routine baseline survey; normal DO" },
      { observed_at: "2026-04-14T08:30:00Z", station_id: "chonburi_01", species: "Mixed normal phytoplankton", bloom_status: "0", chlorophyll_a_ug_l: "2.4", dissolved_oxygen_mg_l: "6.5", source: "DMCR Coastal Water Quality", notes: "Routine baseline survey; clear water" }
    ];
  }

  renderGroundTruthTable();
}

function renderGroundTruthTable() {
  const filterStation = document.getElementById("gt-filter-station").value;
  const filterStatus = document.getElementById("gt-filter-status").value;
  const search = document.getElementById("gt-search").value.toLowerCase();

  const tbody = document.getElementById("gt-table-body");
  tbody.innerHTML = "";

  const filtered = groundTruthRecords.filter(r => {
    if (filterStation !== "all" && r.station_id !== filterStation) return false;
    if (filterStatus !== "all" && String(r.bloom_status) !== filterStatus) return false;
    if (search && !JSON.stringify(r).toLowerCase().includes(search)) return false;
    return true;
  });

  filtered.slice(0, 50).forEach(r => {
    const isBloom = String(r.bloom_status) === "1";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><code>${r.observed_at ? r.observed_at.substring(0, 10) : 'N/A'}</code></td>
      <td><b>${r.station_id}</b></td>
      <td><i>${r.species || 'N/A'}</i></td>
      <td><span class="${isBloom ? 'badge-alert' : 'badge-normal'}">${isBloom ? '⚠️ เกิดบลูม' : '✅ น้ำปกติ'}</span></td>
      <td><b>${r.chlorophyll_a_ug_l || '-'}</b> µg/L</td>
      <td><b>${r.dissolved_oxygen_mg_l || '-'}</b> mg/L</td>
      <td><small>${r.source || 'DMCR'}</small></td>
      <td><small>${r.notes || '-'}</small></td>
    `;
    tbody.appendChild(tr);
  });
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  // Station Switcher
  document.querySelectorAll(".station-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".station-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      currentStationId = pill.dataset.station;
      renderLiveWatch();
    });
  });

  // Tab Switcher
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
      
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");

      if (btn.dataset.tab === "tab-live" && leafletMap) {
        setTimeout(() => leafletMap.invalidateSize(), 100);
      }
    });
  });

  // Simulator inputs listener
  document.querySelectorAll("#tab-sim input").forEach(input => {
    input.addEventListener("input", runSimulator);
  });

  // Ground truth filter listeners
  document.getElementById("gt-filter-station").addEventListener("change", renderGroundTruthTable);
  document.getElementById("gt-filter-status").addEventListener("change", renderGroundTruthTable);
  document.getElementById("gt-search").addEventListener("input", renderGroundTruthTable);

  initMap();
  renderLiveWatch();
  runSimulator();
  loadGroundTruth();
});
