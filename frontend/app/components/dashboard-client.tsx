"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, Clock3, LocateFixed, MapPin, RefreshCw, SlidersHorizontal } from "lucide-react";
import Assistant from "@/app/components/assistant";
import MonitoringMap from "@/app/components/monitoring-map";
import StationDetail from "@/app/components/station-detail";
import StationTrendChart from "@/app/components/station-trend-chart";
import TechnicalDetails from "@/app/components/technical-details";
import type { AssistantContext } from "@/lib/assistant";
import { getMonitoringStatus, getStationArea, getStationName, stationCoordinatesAreValid } from "@/lib/monitoring";
import {
  buildWatchPresentation,
  getFreshnessMessage,
  type PresentationApiStatus,
  type SatelliteStatus,
} from "@/lib/watch-presentation";
import type {
  ApiStatus,
  DataSourceInfo,
  Factor,
  MonitoringStation,
  MonitoringStatus,
  PredictionData,
  StationMetadata,
  TestScenarioKey,
  TestState,
} from "@/lib/dashboard-types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "/backend-api").replace(/\/$/, "");
const TEST_MODE_ID = "ui_score_test";

const TEST_SCENARIOS: Record<TestScenarioKey, { state: TestState }> = {
  normal: {
    state: {
      score: 30,
      factors: [
        { name: "Wind speed", feature_key: "wind_speed", value: 14, unit: "km/h", impact: "decrease", shap_value: -3.1 },
        { name: "SST anomaly", feature_key: "sst_anomaly", value: 0.2, unit: "°C", impact: "increase", shap_value: 0.8 },
        { name: "NDCI", feature_key: "ndci", value: 0.04, unit: "index", impact: "decrease", shap_value: -1.2 },
      ],
      satelliteStatus: "available",
      fieldVerificationCount: 1,
      apiStatus: "mocked",
    },
  },
  watch: {
    state: {
      score: 56,
      factors: [
        { name: "Wind speed", feature_key: "wind_speed", value: 5.5, unit: "km/h", impact: "increase", shap_value: 4.6 },
        { name: "SST anomaly", feature_key: "sst_anomaly", value: 1.2, unit: "°C", impact: "increase", shap_value: 3.1 },
        { name: "NDCI", feature_key: "ndci", value: 0.18, unit: "index", impact: "decrease", shap_value: -2.2 },
      ],
      satelliteStatus: "stale",
      fieldVerificationCount: 0,
      apiStatus: "mocked",
    },
  },
  urgent: {
    state: {
      score: 82,
      factors: [
        { name: "Wind speed", feature_key: "wind_speed", value: 2.5, unit: "km/h", impact: "increase", shap_value: 6.2 },
        { name: "SST anomaly", feature_key: "sst_anomaly", value: 2.1, unit: "°C", impact: "increase", shap_value: 5.4 },
        { name: "NDCI", feature_key: "ndci", value: 0.31, unit: "index", impact: "increase", shap_value: 4.1 },
      ],
      satelliteStatus: "unavailable",
      fieldVerificationCount: 0,
      apiStatus: "mocked",
    },
  },
};

function cloneTestScenario(key: TestScenarioKey): TestState {
  const state = TEST_SCENARIOS[key].state;
  return { ...state, factors: state.factors.map((factor) => ({ ...factor })) };
}

const EMPTY_DATA: PredictionData = {
  station_id: "chonburi_01",
  assessment_status: "insufficient_data",
  risk_score: null,
  score_label: "ดัชนีเฝ้าระวังสภาพแวดล้อม",
  score_is_probability: false,
  risk_level: "กำลังโหลด",
  alert_status: "Loading",
  shap_explanation: "กำลังโหลดผลจาก AquaMind API",
  location: "Chonburi Coast",
  lat: 13.3611,
  lon: 100.9234,
  timestamp: "waiting for API",
  recommendations: ["รอข้อมูลจาก Backend"],
  features: [],
  history_trend: [],
  data_status: "synthetic_model_demo",
  data_source: "waiting for API",
  observed_at: "waiting for API",
  is_demo: true,
  data_age_hours: null,
  confidence_score: null,
  confidence_level: "กำลังโหลด",
  confidence_note: "กำลังโหลด",
  imagery_status: "simulated",
  imagery_mode: "simulated_fresh",
  analysis_method: "insufficient_data",
  history_period_days: 0,
  data_sources: [],
  limitations: [],
  model_name: null,
  model_version: null,
  forecast_horizon: null,
  shap_output_space: null,
  rule_basis: [],
};

type DashboardView = "map" | "trend";
type StatusFilter = "all" | MonitoringStatus;

const STATUS_FILTER_LABELS: Record<StatusFilter, string> = {
  all: "ทั้งหมด",
  normal: "ปกติ",
  watch: "เฝ้าระวัง",
  warning: "เตือน",
  unavailable: "ไม่มีข้อมูล",
};

function toMonitoringStation(id: string, station: StationMetadata, risk: PredictionData | null): MonitoringStation {
  return {
    id,
    name: getStationName(station.location),
    location: station.location,
    latitude: station.lat,
    longitude: station.lon,
    status: getMonitoringStatus(risk?.risk_score ?? null),
    score: risk?.risk_score ?? null,
    updatedAt: risk?.timestamp ?? "รอข้อมูลจาก API",
    history: risk?.history_trend ?? [],
    historyPeriodDays: risk?.history_period_days ?? 0,
  };
}

function getTrendSummary(points: number[]) {
  if (points.length === 0) return { current: null, first: null, maximum: null, minimum: null, delta: null, direction: "ไม่มีข้อมูล" };
  const current = points[points.length - 1];
  const first = points[0];
  const delta = current - first;
  const direction = delta >= 2 ? "เพิ่มขึ้น" : delta <= -2 ? "ลดลง" : "ทรงตัว";
  return { current, first, maximum: Math.max(...points), minimum: Math.min(...points), delta, direction };
}

function formatTrendValue(value: number | null) {
  return value === null ? "—" : Number.isInteger(value) ? String(value) : value.toFixed(1);
}

export default function DashboardClient() {
  const [data, setData] = useState<PredictionData>(EMPTY_DATA);
  const [stationRisks, setStationRisks] = useState<Record<string, PredictionData>>({});
  const [stations, setStations] = useState<Record<string, StationMetadata>>({});
  const [selectedStation, setSelectedStation] = useState("chonburi_01");
  const [apiStatus, setApiStatus] = useState<ApiStatus>("connecting");
  const [loading, setLoading] = useState(false);
  const [testState, setTestState] = useState<TestState>(() => cloneTestScenario("normal"));
  const [showTestControls, setShowTestControls] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<DashboardView>("map");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [recenterRequest, setRecenterRequest] = useState(0);
  const isTestMode = selectedStation === TEST_MODE_ID;

  const loadRisk = useCallback(async (stationId: string, signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    setApiStatus("connecting");
    try {
      const params = new URLSearchParams({ station_id: stationId });
      const response = await fetch(`${API_BASE_URL}/api/risk/current?${params}`, { cache: "no-store", signal });
      if (!response.ok) {
        const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(payload?.detail ?? `Backend ตอบ HTTP ${response.status}`);
      }
      const nextData = (await response.json()) as PredictionData;
      setData(nextData);
      setStationRisks((current) => ({ ...current, [stationId]: nextData }));
      setApiStatus("connected");
    } catch (requestError) {
      if (requestError instanceof DOMException && requestError.name === "AbortError") return;
      setApiStatus("error");
      setError(requestError instanceof Error ? requestError.message : "เชื่อมต่อ API ไม่สำเร็จ");
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    async function loadStations() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stations`, { cache: "no-store", signal: controller.signal });
        if (!response.ok) throw new Error(`โหลดพื้นที่ไม่สำเร็จ (HTTP ${response.status})`);
        const nextStations = (await response.json()) as Record<string, StationMetadata>;
        setStations(nextStations);
        setSelectedStation((current) => current === TEST_MODE_ID || nextStations[current] ? current : Object.keys(nextStations)[0] ?? current);
      } catch (requestError) {
        if (!(requestError instanceof DOMException && requestError.name === "AbortError")) {
          setError(requestError instanceof Error ? requestError.message : "โหลดพื้นที่ไม่สำเร็จ");
        }
      }
    }
    void loadStations();
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (selectedStation === TEST_MODE_ID) return;
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => void loadRisk(selectedStation, controller.signal), 0);
    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, [loadRisk, selectedStation]);

  useEffect(() => {
    const stationIds = Object.entries(stations)
      .filter(([id, station]) => id !== selectedStation && stationCoordinatesAreValid(station))
      .map(([id]) => id);
    if (stationIds.length === 0) return;

    const controller = new AbortController();
    async function loadMarkerData() {
      const results = await Promise.all(stationIds.map(async (stationId) => {
        try {
          const params = new URLSearchParams({ station_id: stationId });
          const response = await fetch(`${API_BASE_URL}/api/risk/current?${params}`, { cache: "no-store", signal: controller.signal });
          if (!response.ok) return null;
          return [stationId, (await response.json()) as PredictionData] as const;
        } catch {
          return null;
        }
      }));
      if (controller.signal.aborted) return;
      setStationRisks((current) => {
        const next = { ...current };
        results.forEach((result) => {
          if (result) next[result[0]] = result[1];
        });
        return next;
      });
    }
    void loadMarkerData();
    return () => controller.abort();
  }, [selectedStation, stations]);

  const presentationApiStatus: PresentationApiStatus = isTestMode ? testState.apiStatus : apiStatus;
  const selectedRisk = isTestMode ? null : stationRisks[selectedStation] ?? (data.station_id === selectedStation ? data : null);
  const activeData = selectedRisk ?? data;
  const presentationEvidence = {
    satelliteStatus: (isTestMode ? testState.satelliteStatus : activeData.imagery_status) as SatelliteStatus,
    fieldVerificationCount: isTestMode ? testState.fieldVerificationCount : 0,
    apiStatus: presentationApiStatus,
  };
  const presentationFactors = isTestMode ? testState.factors : activeData.features;
  const canUseLiveScore = isTestMode || (apiStatus === "connected" && !loading && selectedRisk !== null);
  const riskScore = canUseLiveScore ? (isTestMode ? testState.score : selectedRisk?.risk_score ?? null) : null;
  const presentation = buildWatchPresentation({ score: riskScore, factors: presentationFactors, evidence: presentationEvidence });
  const selectedStationMetadata = stations[selectedStation];
  const displayedLocation = isTestMode ? data.location : selectedStationMetadata?.location ?? activeData.location;
  const displayedStationId = isTestMode ? TEST_MODE_ID : selectedStation;
  const updatedAt = isTestMode ? "ข้อมูลทดสอบในหน้านี้" : activeData.timestamp;
  const freshnessMessage = getFreshnessMessage({
    updatedAt,
    dataAgeHours: isTestMode ? 0 : activeData.data_age_hours,
    apiStatus: presentationApiStatus,
    satelliteStatus: presentationEvidence.satelliteStatus,
    loading,
  });
  const isErrorState = !isTestMode && apiStatus === "error";
  const isLoadingState = !isTestMode && (loading || apiStatus === "connecting");
  const statusHeadline = isLoadingState
    ? "กำลังโหลดข้อมูลล่าสุด"
    : isErrorState
      ? "ข้อมูลล่าสุดโหลดไม่สำเร็จ"
      : presentation.farmerHeadline;
  const actions = presentation.immediateActions.slice(0, 3);
  const plainFactors = presentation.plainLanguageFactors;
  const sources: DataSourceInfo[] = isTestMode
    ? [
        { name: "Satellite evidence", source_type: "test_satellite", status: testState.satelliteStatus, observed_at: null, age_hours: null, note: "สถานะภาพดาวเทียมจำลองจาก UI test" },
        { name: "Field verification", source_type: "test_field", status: testState.fieldVerificationCount > 0 ? "available" : "unavailable", observed_at: null, age_hours: null, note: `ผลตรวจภาคสนามจำลอง ${testState.fieldVerificationCount} รายการ` },
        { name: "API connection", source_type: "test_api", status: testState.apiStatus, observed_at: null, age_hours: null, note: "สถานะการเชื่อมต่อจำลองจาก UI test" },
      ]
    : activeData.data_sources;
  const limitations = isTestMode
    ? ["ค่า UI test เป็นข้อมูลจำลองสำหรับตรวจการแสดงผลเท่านั้น", ...presentation.evidenceWarnings]
    : activeData.limitations;
  const assistantContext: AssistantContext = {
    stationId: displayedStationId,
    location: displayedLocation,
    watchLevel: statusHeadline,
    score: riskScore,
    scoreIsProbability: false,
    updatedAt,
    actions,
    evidenceWarnings: presentation.evidenceWarnings,
  };

  const markerStations = useMemo(() => Object.entries(stations)
    .filter(([, station]) => stationCoordinatesAreValid(station))
    .map(([id, station]) => {
      const risk = id === selectedStation && (isLoadingState || isErrorState) ? null : stationRisks[id] ?? (data.station_id === id ? data : null);
      return toMonitoringStation(id, station, risk);
    }), [data, isErrorState, isLoadingState, selectedStation, stationRisks, stations]);
  const filteredMarkerStations = statusFilter === "all" ? markerStations : markerStations.filter((station) => station.status === statusFilter);
  const selectedMarker = markerStations.find((station) => station.id === selectedStation) ?? null;
  const trendRisk = isTestMode ? null : stationRisks[selectedStation] ?? (data.station_id === selectedStation ? data : null);
  const trendPoints = trendRisk?.history_trend ?? [];
  const trendSummary = getTrendSummary(trendPoints);

  function updateTestFactor(index: number, update: Partial<Factor>) {
    setTestState((current) => ({
      ...current,
      factors: current.factors.map((factor, factorIndex) => factorIndex === index ? { ...factor, ...update } : factor),
    }));
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] text-[#0f1f3d]">
      <header className="border-b border-slate-200/80 bg-white px-4 py-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-[1280px]">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-[13px] font-bold uppercase tracking-[0.14em] text-[#1479b8]">AQUAMIND</p>
              <h1 className="mt-1 text-[28px] font-bold leading-9 tracking-tight text-[#0f1f3d] sm:text-[30px]">ผู้ช่วยดูสถานการณ์น้ำ</h1>
              <p className="mt-1 flex min-w-0 items-center gap-1.5 truncate text-[14px] leading-6 text-slate-600" title={displayedLocation}><MapPin className="h-4 w-4 shrink-0 text-[#1479b8]" aria-hidden="true" /><span className="truncate">{getStationName(displayedLocation)} · อัปเดตล่าสุด {isTestMode ? "ข้อมูลทดสอบ" : updatedAt}</span></p>
            </div>
            <div className="hidden shrink-0 items-center gap-2 text-right text-[13px] text-slate-500 sm:flex"><Clock3 className="h-4 w-4" aria-hidden="true" /><span>{isTestMode ? "โหมดทดสอบ" : apiStatus === "connected" ? "เชื่อมต่อแล้ว" : "รอการเชื่อมต่อ"}</span></div>
          </div>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <nav aria-label="มุมมองข้อมูล" className="grid h-11 w-full grid-cols-2 rounded-[11px] bg-slate-100 p-1 sm:w-[260px]">
              <button type="button" onClick={() => setView("map")} aria-current={view === "map" ? "page" : undefined} className={`rounded-[8px] px-3 text-[14px] font-bold transition ${view === "map" ? "bg-white text-[#1479b8] shadow-sm" : "text-slate-600 hover:text-[#0f1f3d]"}`}>แผนที่</button>
              <button type="button" onClick={() => setView("trend")} aria-current={view === "trend" ? "page" : undefined} className={`rounded-[8px] px-3 text-[14px] font-bold transition ${view === "trend" ? "bg-white text-[#1479b8] shadow-sm" : "text-slate-600 hover:text-[#0f1f3d]"}`}>แนวโน้ม 30 วัน</button>
            </nav>
            <div className="flex min-h-11 items-center justify-between gap-3 rounded-[11px] border border-slate-200 bg-slate-50 px-3 py-1.5 sm:min-w-[300px] sm:justify-end">
              <span className="flex min-w-0 items-center gap-1.5 truncate text-[13px] text-slate-600"><Clock3 className="h-4 w-4 shrink-0 text-[#1479b8]" aria-hidden="true" />{isTestMode ? "ข้อมูลทดสอบ" : freshnessMessage}</span>
              <button type="button" onClick={() => void loadRisk(selectedStation)} disabled={loading || isTestMode} className="inline-flex min-h-10 shrink-0 items-center gap-1.5 rounded-[9px] bg-[#1479b8] px-3 text-[14px] font-bold text-white hover:bg-[#0f659c] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-600"><RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} aria-hidden="true" /> โหลดใหม่</button>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1280px] px-4 py-5 sm:px-6 sm:py-6 lg:px-8">
        {error && !isTestMode && <div role="alert" className="mb-4 flex items-start gap-2.5 rounded-[11px] border border-amber-200 bg-amber-50 px-3 py-2.5 text-[14px] leading-5 text-amber-950"><AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" /><span>{error}</span></div>}

        {view === "map" ? (
          <section aria-labelledby="map-heading">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div><h2 id="map-heading" className="text-[20px] font-bold leading-7 text-[#0f1f3d]">จุดติดตามน้ำ</h2><p className="mt-0.5 text-[14px] text-slate-600">{markerStations.length} สถานี · {getStationArea(displayedLocation)}</p></div>
              <div className="flex w-full items-center gap-2 sm:w-auto">
                <label className="relative min-w-0 flex-1 sm:w-[210px]"><span className="sr-only">เลือกสถานี</span><select value={selectedStation} onChange={(event) => setSelectedStation(event.target.value)} className="h-11 w-full appearance-none rounded-[10px] border border-slate-300 bg-white px-3 pr-8 text-[14px] text-[#0f1f3d] outline-none focus:border-sky-600 focus:ring-2 focus:ring-sky-200"><option value={TEST_MODE_ID}>โหมดทดสอบหน้าจอ</option>{Object.entries(stations).map(([id, station]) => <option key={id} value={id}>{getStationName(station.location)}</option>)}</select></label>
                <label className="relative w-[112px] shrink-0"><span className="sr-only">กรองสถานี</span><SlidersHorizontal className="pointer-events-none absolute left-2.5 top-3 h-4 w-4 text-slate-500" aria-hidden="true" /><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as StatusFilter)} className="h-11 w-full appearance-none rounded-[10px] border border-slate-300 bg-white pl-8 pr-2 text-[13px] text-[#0f1f3d] outline-none focus:border-sky-600 focus:ring-2 focus:ring-sky-200">{Object.entries(STATUS_FILTER_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
                <button type="button" onClick={() => setRecenterRequest((value) => value + 1)} aria-label="จัดแผนที่ให้เห็นจุดติดตามทั้งหมด" title="จัดแผนที่ใหม่" className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px] border border-slate-300 bg-white text-[#1479b8] hover:bg-sky-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2"><LocateFixed className="h-5 w-5" aria-hidden="true" /></button>
              </div>
            </div>

            <div className="mt-3 grid gap-3 lg:grid-cols-[minmax(0,1.7fr)_minmax(280px,0.75fr)]">
              <MonitoringMap stations={filteredMarkerStations} selectedStationId={isTestMode ? null : selectedStation} onSelectStation={setSelectedStation} recenterRequest={recenterRequest} />
              <StationDetail station={isTestMode ? null : selectedMarker} risk={selectedRisk} onViewTrend={() => setView("trend")} />
            </div>
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[13px] text-slate-600" aria-label="คำอธิบายสถานะ"><span><i className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full bg-emerald-500" />ปกติ</span><span><i className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full bg-amber-500" />เฝ้าระวัง</span><span><i className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full bg-rose-500" />เตือน</span><span><i className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full bg-slate-400" />ไม่มีข้อมูล</span></div>
            {isTestMode && <p className="mt-3 rounded-[10px] bg-amber-50 px-3 py-2 text-[13px] leading-5 text-amber-900">โหมดทดสอบใช้ตรวจการแสดงผลเท่านั้น แผนที่ยังคงแสดงเฉพาะสถานีและพิกัดจริงจากระบบ</p>}
          </section>
        ) : (
          <section aria-labelledby="trend-heading">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div><h2 id="trend-heading" className="text-[20px] font-bold leading-7 text-[#0f1f3d]">แนวโน้ม 30 วัน</h2><p className="mt-0.5 text-[14px] text-slate-600">ดูการเปลี่ยนแปลงของสถานีที่เลือกจากข้อมูลย้อนหลังที่ API ส่งมา</p></div>
              <div className="flex w-full gap-2 sm:w-auto">
                <label className="min-w-0 flex-1 sm:w-[210px]"><span className="mb-1 block text-[13px] font-semibold text-slate-600">สถานี</span><select value={selectedStation} onChange={(event) => setSelectedStation(event.target.value)} className="h-11 w-full rounded-[10px] border border-slate-300 bg-white px-3 text-[14px] text-[#0f1f3d] outline-none focus:border-sky-600 focus:ring-2 focus:ring-sky-200"><option value={TEST_MODE_ID}>โหมดทดสอบหน้าจอ</option>{Object.entries(stations).map(([id, station]) => <option key={id} value={id}>{getStationName(station.location)}</option>)}</select></label>
                <label className="w-[150px] shrink-0"><span className="mb-1 block text-[13px] font-semibold text-slate-600">ตัวแปร</span><select disabled className="h-11 w-full rounded-[10px] border border-slate-300 bg-slate-100 px-3 text-[14px] text-slate-700"><option>ดัชนีสถานการณ์</option></select></label>
              </div>
            </div>

            <div className="mt-4 rounded-[16px] border border-slate-200 bg-white p-4 sm:p-5">
              <div className="flex items-center justify-between gap-3"><div><p className="text-[13px] font-semibold uppercase tracking-[0.08em] text-[#1479b8]">ดัชนีสถานการณ์</p><h3 className="mt-1 text-[18px] font-bold text-[#0f1f3d]">{isTestMode ? "โหมดทดสอบหน้าจอ" : getStationName(displayedLocation)}</h3></div><span className="text-right text-[13px] text-slate-500">{trendRisk?.history_period_days ? `${trendRisk.history_period_days} วัน` : "ข้อมูลที่มี"}</span></div>
              <div className="mt-4"><StationTrendChart points={trendPoints} periodDays={trendRisk?.history_period_days ?? 0} metricLabel="ดัชนีสถานการณ์" /></div>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {[{ label: "ปัจจุบัน", value: formatTrendValue(trendSummary.current) }, { label: "30 วันก่อน", value: trendRisk?.history_period_days && trendRisk.history_period_days >= 30 ? formatTrendValue(trendSummary.first) : "—" }, { label: "สูงสุด", value: formatTrendValue(trendSummary.maximum) }, { label: "ต่ำสุด", value: formatTrendValue(trendSummary.minimum) }].map((stat) => <div key={stat.label} className="rounded-[12px] border border-slate-200 bg-white px-3 py-3"><span className="block text-[13px] text-slate-500">{stat.label}</span><strong className="mt-1 block text-[24px] leading-7 text-[#0f1f3d]">{stat.value}</strong></div>)}
            </div>
            <div className="mt-3 rounded-[12px] bg-sky-50 px-3.5 py-3 text-[14px] leading-5 text-sky-950">{trendPoints.length === 0 ? "ยังไม่มีข้อมูลย้อนหลัง 30 วันสำหรับสถานีนี้" : trendRisk && trendRisk.history_period_days < 30 ? `มีข้อมูล ${trendPoints.length} จุด แนวโน้มช่วงนี้: ${trendSummary.direction} ${trendSummary.delta === null ? "" : `(${trendSummary.delta >= 0 ? "+" : ""}${formatTrendValue(trendSummary.delta)} จุดจากจุดแรกที่มี)`}` : `แนวโน้มช่วง 30 วัน: ${trendSummary.direction} ${trendSummary.delta === null ? "" : `(${trendSummary.delta >= 0 ? "+" : ""}${formatTrendValue(trendSummary.delta)} จุด)`}`}</div>
          </section>
        )}

        <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(280px,0.7fr)]">
          <Assistant context={assistantContext} />
          <section aria-labelledby="freshness-heading" className="rounded-[16px] border border-slate-200 bg-white p-4 sm:p-5"><div className="flex items-start gap-2.5"><Clock3 className="mt-0.5 h-5 w-5 shrink-0 text-[#1479b8]" aria-hidden="true" /><div><h2 id="freshness-heading" className="text-[17px] font-bold text-[#0f1f3d]">ความสดใหม่ของข้อมูล</h2><p className="mt-1.5 text-[14px] leading-5 text-slate-800">{freshnessMessage}</p><p className="mt-1 text-[13px] leading-5 text-slate-600">ข้อมูลเก่าหรือเชื่อมต่อไม่ได้ ให้ใช้ผลตรวจหน้างานประกอบ</p></div></div></section>
        </div>

        <details className="mt-4 rounded-[14px] border border-slate-200 bg-white px-4 py-3"><summary className="flex cursor-pointer list-none items-center gap-2 text-[16px] font-bold text-[#0f1f3d]">คำแนะนำตรวจหน้างานประกอบ<span className="text-[13px] font-normal text-slate-500">{statusHeadline}</span></summary><div className="mt-3 grid gap-3 border-t border-slate-100 pt-3 lg:grid-cols-2"><div><p className="text-[14px] font-bold text-slate-800">เริ่มจาก 3 ขั้นตอนนี้</p><ol className="mt-2 grid gap-2">{actions.map((action, index) => <li key={action} className="flex items-start gap-2 text-[14px] leading-5 text-slate-700"><span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-sky-100 text-[12px] font-bold text-sky-800">{index + 1}</span>{action}</li>)}</ol></div><div><p className="text-[14px] font-bold text-slate-800">สภาพที่ควรสังเกต</p>{plainFactors.length > 0 ? <ul className="mt-2 grid gap-1.5 text-[14px] leading-5 text-slate-700">{plainFactors.map((factor) => <li key={factor}>• {factor}</li>)}</ul> : <p className="mt-2 text-[14px] leading-5 text-amber-800">ยังไม่มีปัจจัยพอให้สรุป ให้ดูสี กลิ่น และพฤติกรรมปลาในพื้นที่จริง</p>}</div></div></details>

        <TechnicalDetails
          data={activeData}
          factors={presentationFactors}
          sources={sources}
          limitations={limitations}
          topFactors={presentation.topFactors}
          isTestMode={isTestMode}
          testState={testState}
          showTestControls={showTestControls}
          onToggleTestControls={() => setShowTestControls((value) => !value)}
          onSetTestScenario={(key) => setTestState(cloneTestScenario(key))}
          onUpdateScore={(score) => setTestState((current) => ({ ...current, score }))}
          onUpdateSatelliteStatus={(satelliteStatus) => setTestState((current) => ({ ...current, satelliteStatus }))}
          onUpdateFieldVerification={(fieldVerificationCount) => setTestState((current) => ({ ...current, fieldVerificationCount }))}
          onUpdateApiStatus={(nextApiStatus) => setTestState((current) => ({ ...current, apiStatus: nextApiStatus }))}
          onUpdateFactor={updateTestFactor}
          apiStatus={presentationApiStatus}
        />
      </main>

      <footer className="px-4 pb-6 text-center text-[13px] text-slate-500">AquaMind • ข้อมูลช่วยจัดลำดับการตรวจ ไม่แทนผลตรวจน้ำหน้างาน</footer>
    </div>
  );
}
