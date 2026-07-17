"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Eye,
  ExternalLink,
  MapPin,
  RefreshCw,
  Satellite,
  Server,
  Sparkles,
  Waves,
  TrendingUp,
} from "lucide-react";

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/backend-api"
).replace(/\/$/, "");

type Scenario = "low" | "medium" | "high";
type ApiStatus = "connecting" | "connected" | "error";

interface Factor {
  name: string;
  feature_key?: string | null;
  value: number;
  unit: string;
  impact: "increase" | "decrease" | "none";
  shap_value?: number | null;
}

interface DataSourceInfo {
  name: string;
  source_type: string;
  status: string;
  observed_at: string | null;
  age_hours: number | null;
  note: string;
  url?: string | null;
}

interface PredictionData {
  station_id: string;
  assessment_status: "model_demo" | "operational_model" | "insufficient_data";
  risk_score: number | null;
  risk_level: string;
  alert_status: string;
  shap_explanation: string;
  location: string;
  lat: number;
  lon: number;
  timestamp: string;
  recommendations: string[];
  features: Factor[];
  history_trend: number[];
  data_status: "synthetic_model_demo" | "live_context" | "live_operational";
  data_source: string;
  observed_at: string;
  is_demo: boolean;
  data_age_hours: number | null;
  confidence_score: number | null;
  confidence_level: string;
  confidence_note: string;
  imagery_status: "simulated" | "available" | "stale" | "unavailable";
  imagery_mode: "simulated_fresh" | "context_only" | "no_imagery";
  analysis_method: "xgboost_shap_demo" | "xgboost_shap_operational" | "insufficient_data";
  history_period_days: number;
  data_sources: DataSourceInfo[];
  limitations: string[];
  model_name: string | null;
  model_version: string | null;
  forecast_horizon: string | null;
  shap_output_space: "raw_margin" | null;
}

interface StationMetadata {
  location: string;
  lat: number;
  lon: number;
  data_mode: "synthetic_model_demo" | "live_context";
}

const EMPTY_DATA: PredictionData = {
  station_id: "chonburi_01",
  assessment_status: "insufficient_data",
  risk_score: null,
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
};

function formatDataAge(hours: number | null) {
  if (hours === null) return "ไม่มีข้อมูลจริง";
  if (hours < 1) return `${Math.max(1, Math.round(hours * 60))} นาที`;
  if (hours < 48) return `${hours.toFixed(hours < 10 ? 1 : 0)} ชม.`;
  return `${Math.round(hours / 24)} วัน`;
}

export default function Home() {
  const [data, setData] = useState<PredictionData>(EMPTY_DATA);
  const [stations, setStations] = useState<Record<string, StationMetadata>>({});
  const [selectedStation, setSelectedStation] = useState("chonburi_01");
  const [scenario, setScenario] = useState<Scenario>("medium");
  const [apiStatus, setApiStatus] = useState<ApiStatus>("connecting");
  const [loading, setLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRisk = useCallback(
    async (stationId: string, selectedScenario: Scenario, signal?: AbortSignal) => {
      setLoading(true);
      setError(null);
      setApiStatus("connecting");

      try {
        const params = new URLSearchParams({
          station_id: stationId,
          scenario: selectedScenario,
        });
        const response = await fetch(`${API_BASE_URL}/api/risk/current?${params}`, {
          cache: "no-store",
          signal,
        });
        if (!response.ok) {
          const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
          throw new Error(payload?.detail ?? `Backend ตอบ HTTP ${response.status}`);
        }

        setData((await response.json()) as PredictionData);
        setApiStatus("connected");
      } catch (requestError) {
        if (requestError instanceof DOMException && requestError.name === "AbortError") return;
        setApiStatus("error");
        setError(requestError instanceof Error ? requestError.message : "เชื่อมต่อ API ไม่สำเร็จ");
      } finally {
        if (!signal?.aborted) setLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    const controller = new AbortController();
    async function loadStations() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stations`, {
          cache: "no-store",
          signal: controller.signal,
        });
        if (!response.ok) throw new Error(`โหลดสถานีไม่สำเร็จ (HTTP ${response.status})`);
        setStations((await response.json()) as Record<string, StationMetadata>);
      } catch (requestError) {
        if (!(requestError instanceof DOMException && requestError.name === "AbortError")) {
          setError(requestError instanceof Error ? requestError.message : "โหลดสถานีไม่สำเร็จ");
        }
      }
    }
    void loadStations();
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => {
      void loadRisk(selectedStation, scenario, controller.signal);
    }, 0);
    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, [loadRisk, scenario, selectedStation]);

  const isModelDemo = data.assessment_status === "model_demo";
  const isOperational = data.assessment_status === "operational_model";
  const isInsufficient = data.assessment_status === "insufficient_data";
  const modelExecuted = isModelDemo || isOperational;
  const hasRealSentinel = data.data_sources.some(
    (source) => source.source_type === "sentinel2_l2a" && source.status !== "unavailable",
  );
  const selectedMode = stations[selectedStation]?.data_mode;
  const riskScore = data.risk_score;
  const topShapFactors = useMemo(
    () =>
      data.features
        .filter((factor) => factor.shap_value !== null && factor.shap_value !== undefined)
        .sort((a, b) => Math.abs(b.shap_value ?? 0) - Math.abs(a.shap_value ?? 0))
        .slice(0, 3),
    [data.features],
  );

  const theme = riskScore === null
    ? { fill: "#94a3b8", text: "text-slate-300", bg: "bg-slate-500/10", border: "border-slate-500/30" }
    : riskScore >= 70
      ? { fill: "#f87171", text: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30" }
      : riskScore >= 40
        ? { fill: "#facc15", text: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/30" }
        : { fill: "#4ade80", text: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/30" };

  const trendPoints = data.history_trend.length > 1
    ? data.history_trend
      .map((value, index) => `${(index / (data.history_trend.length - 1)) * 300},${100 - value}`)
      .join(" ")
    : "";

  return (
    <div className="min-h-screen bg-slate-950 p-5 font-sans text-slate-100">
      <header className="mx-auto mb-4 flex max-w-7xl flex-col justify-between gap-4 border-b border-slate-800 pb-4 lg:flex-row lg:items-center">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-2xl font-bold text-transparent">AquaMind AI</h1>
            <span className="rounded border border-cyan-500/20 bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-cyan-400">Proposal-aligned MVP</span>
          </div>
          <p className="text-xs text-slate-400">ต้นแบบ Weather/Ocean forecast → Sentinel‑2 evidence → XGBoost + SHAP</p>
          <a
            href="https://aquamind-d8apywwzzyvy25ydmw8ufh.streamlit.app"
            target="_blank"
            rel="noreferrer"
            className="mt-1 inline-flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300"
          >
            เปิด Streamlit Synthetic Model Demo <ExternalLink className="h-3 w-3" />
          </a>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 p-2">
            <label htmlFor="station" className="text-xs text-slate-400">โหมด/พื้นที่:</label>
            <select
              id="station"
              value={selectedStation}
              onChange={(event) => setSelectedStation(event.target.value)}
              disabled={loading || Object.keys(stations).length === 0}
              className="max-w-sm rounded-lg border border-slate-700 bg-slate-950 px-2 py-1 text-xs disabled:opacity-50"
            >
              {Object.entries(stations).length ? Object.entries(stations).map(([id, station]) => (
                <option key={id} value={id}>{station.location}</option>
              )) : <option value="chonburi_01">XGBoost/SHAP Technical Demo</option>}
            </select>
            <span className={`rounded-lg border px-2 py-1 text-[10px] ${apiStatus === "connected" ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300" : apiStatus === "error" ? "border-amber-500/30 bg-amber-500/10 text-amber-300" : "border-cyan-500/30 bg-cyan-500/10 text-cyan-300"}`}>
              {apiStatus === "connected" ? "API connected" : apiStatus === "error" ? "API error" : "Connecting"}
            </span>
            <button
              type="button"
              onClick={() => void loadRisk(selectedStation, scenario)}
              disabled={loading}
              className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} /> โหลดใหม่
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 p-2">
            <span className="flex items-center gap-1 px-1 text-xs text-slate-400"><Server className="h-3.5 w-3.5" /> Synthetic model scenarios:</span>
            {(["low", "medium", "high"] as Scenario[]).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setScenario(item)}
                disabled={selectedMode === "live_context"}
                className={`rounded-lg border px-3 py-1 text-xs capitalize transition disabled:opacity-30 ${scenario === item ? "border-violet-400 bg-violet-500/20 text-violet-200" : "border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700"}`}
              >
                {item}
              </button>
            ))}
            <button type="button" onClick={() => setShowDebug((value) => !value)} className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-300 hover:bg-slate-700">
              <Eye className="h-3.5 w-3.5" /> {showDebug ? "ปิด Inspector" : "เปิด Inspector"}
            </button>
          </div>
        </div>
      </header>

      {error && (
        <div className="mx-auto mb-4 flex max-w-7xl items-start gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-xs text-amber-100">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" /> {error}
        </div>
      )}

      <section className="mx-auto mb-4 grid max-w-7xl grid-cols-2 gap-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900 px-3 py-2">
          <span className="block text-[9px] uppercase tracking-wider text-slate-500">System mode</span>
          <strong className="text-sm text-cyan-300">{isModelDemo ? "Model Technical Demo" : isOperational ? "Live Operational Model" : "Live Data Readiness"}</strong>
          <span className="block text-[9px] text-slate-500">{data.data_status}</span>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900 px-3 py-2">
          <span className="block text-[9px] uppercase tracking-wider text-slate-500">Data age / confidence</span>
          <strong className="text-sm text-slate-100">{formatDataAge(data.data_age_hours)}</strong>
          <span className="block text-[9px] text-slate-500">{data.confidence_level}</span>
        </div>
        <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 px-3 py-2 text-blue-200">
          <span className="block text-[9px] uppercase tracking-wider opacity-70">Satellite mode</span>
          <strong className="text-sm">{data.imagery_mode === "simulated_fresh" ? "Sentinel‑2 features (simulated)" : hasRealSentinel ? "Sentinel‑2 L2A/NDCI real input" : "No usable Sentinel‑2 imagery"}</strong>
          <span className="block text-[9px] opacity-70">{data.imagery_status}</span>
        </div>
        <div className="rounded-xl border border-violet-500/30 bg-violet-500/10 px-3 py-2 text-violet-200">
          <span className="block text-[9px] uppercase tracking-wider opacity-70">Explainability</span>
          <strong className="text-sm">{modelExecuted ? "XGBoost + SHAP" : "Model not executed"}</strong>
          <span className="block text-[9px] opacity-70">{data.shap_output_space ?? "insufficient data"}</span>
        </div>
      </section>

      {isInsufficient && (
        <div className="mx-auto mb-4 max-w-7xl rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-xs text-amber-100">
          <strong className="mb-1 block">Mode C — ข้อมูลไม่เพียงพอสำหรับประเมินระดับฟาร์ม</strong>
          {hasRealSentinel
            ? "ระบบมี Sentinel‑2 NDCI/NDWI และ Weather/Ocean forecast จริงแล้ว แต่ยังไม่มีโมเดลที่ผ่าน Ground-truth validation จึงไม่แสดง Risk probability และไม่รัน SHAP"
            : "ระบบยังไม่มี Sentinel‑2 ที่ผ่านเกณฑ์และไม่มีโมเดลที่ผ่าน Ground-truth validation จึงไม่แสดง Risk probability และไม่รัน SHAP"}
        </div>
      )}

      <section className="mx-auto mb-4 grid max-w-7xl grid-cols-1 gap-3 md:grid-cols-3">
        <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 p-3">
          <div className="flex items-center gap-2 text-cyan-300"><Waves className="h-4 w-4" /><strong className="text-xs">1. Environmental forecast</strong></div>
          <p className="mt-2 text-[11px] leading-relaxed text-slate-300">Weather/Ocean ใช้เฝ้าระวังว่าสภาพแวดล้อมเอื้อต่อเหตุการณ์หรือไม่ ไม่ใช่หลักฐานว่าเกิด Bloom แล้ว</p>
          <span className="mt-2 block text-[10px] text-cyan-200/70">{isModelDemo ? "Synthetic inputs ใน Technical Demo" : "Forecast context เชื่อมต่อจริง"}</span>
        </div>
        <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 p-3">
          <div className="flex items-center gap-2 text-blue-300"><Satellite className="h-4 w-4" /><strong className="text-xs">2. Satellite evidence</strong></div>
          <p className="mt-2 text-[11px] leading-relaxed text-slate-300">Sentinel‑2 NDCI/NDWI ใช้เพิ่มหลักฐานเชิงแสงเมื่อภาพผ่าน QC พร้อมแสดงอายุภาพและ Valid-pixel ratio</p>
          <span className="mt-2 block text-[10px] text-blue-200/70">{hasRealSentinel ? "มีภาพจริงสำหรับบริบท" : isModelDemo ? "Feature ภาพเป็นข้อมูลสังเคราะห์" : "ยังไม่มีภาพที่ใช้ได้"}</span>
        </div>
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3">
          <div className="flex items-center gap-2 text-emerald-300"><CheckCircle2 className="h-4 w-4" /><strong className="text-xs">3. Field verification</strong></div>
          <p className="mt-2 text-[11px] leading-relaxed text-slate-300">การยืนยันเหตุการณ์ต้องมาจากการตรวจน้ำหรือผู้เชี่ยวชาญ ภาพดาวเทียมไม่ยืนยันชนิดหรือความเป็นพิษ</p>
          <span className="mt-2 block text-[10px] text-emerald-200/70">Verified ground truth ปัจจุบัน: 0 แถว</span>
        </div>
      </section>

      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-5 lg:grid-cols-3">
        <section className="flex flex-col justify-between rounded-2xl border border-slate-800 bg-slate-900 p-4">
          <div className="mb-3 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2"><MapPin className="h-4 w-4 text-cyan-400" /><h2 className="text-sm font-semibold text-slate-300">พื้นที่และชั้นข้อมูลเชิงพื้นที่</h2></div>
              <p className="mt-1 text-xs text-slate-400">{data.location}</p>
            </div>
            <span className="rounded border border-slate-700 bg-slate-950 px-2 py-1 text-[9px] text-slate-400">{data.station_id}</span>
          </div>

          <div className="relative flex h-56 items-center justify-center overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
            <svg viewBox="0 0 240 180" className="h-full w-full">
              <path d="M25 5 Q55 45 35 85 T75 145 T105 178" fill="none" stroke="#334155" strokeWidth="3" />
              <path d="M0 25 Q30 65 12 110 T55 165" fill="none" stroke="#1e293b" strokeWidth="2" strokeDasharray="5 4" />
              {isModelDemo && (
                <>
                  <circle cx="105" cy="92" r="34" fill={theme.fill} opacity="0.10" />
                  <circle cx="105" cy="92" r="22" fill={theme.fill} opacity="0.18" />
                  <circle cx="105" cy="92" r="10" fill={theme.fill} opacity="0.35" />
                </>
              )}
            </svg>
            <div className="absolute inset-x-3 bottom-3 rounded-lg border border-slate-700 bg-slate-900/95 p-2 text-[10px] text-slate-300">
              {isModelDemo
                ? "NDCI heatmap placeholder — Sentinel‑2 Feature เป็นข้อมูลจำลอง"
                : hasRealSentinel
                  ? "Sentinel‑2 NDCI/NDWI summary จาก AOI จริง — แผนที่รายพิกเซลอยู่ในขั้น Visualization"
                  : "NDCI layer unavailable — ระบบไม่สร้างภาพหรือค่าทดแทน"}
            </div>
          </div>
          <div className="mt-3 flex justify-between rounded-lg border border-slate-800 bg-slate-950 p-2 font-mono text-[10px] text-slate-500">
            <span>Lat {data.lat.toFixed(4)}</span><span>Lon {data.lon.toFixed(4)}</span><span>{data.imagery_status}</span>
          </div>
        </section>

        <section className="flex flex-col items-center justify-between rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex w-full items-center gap-2"><Activity className="h-4 w-4 text-cyan-400" /><h2 className="text-sm font-semibold text-slate-300">{isModelDemo ? "ผลโมเดลจากสถานการณ์สังเคราะห์" : isOperational ? "ความเสี่ยงล่วงหน้า 3–5 วัน (Validated model)" : "ผลการประเมินความเสี่ยง"}</h2></div>

          {riskScore !== null ? (
            <div className="relative my-3 flex h-40 w-40 items-center justify-center">
              <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" stroke="#1e293b" strokeWidth="9" fill="transparent" />
                <circle cx="50" cy="50" r="40" stroke={theme.fill} strokeWidth="9" fill="transparent" strokeDasharray={2 * Math.PI * 40} strokeDashoffset={2 * Math.PI * 40 * (1 - riskScore / 100)} className="transition-all duration-500" />
              </svg>
              <div className="absolute text-center"><strong className="block text-3xl">{Math.round(riskScore)}%</strong><span className={`mt-1 inline-block rounded-full border px-2 py-0.5 text-[10px] ${theme.bg} ${theme.text} ${theme.border}`}>{isModelDemo ? "Scenario" : "Validated"} {data.risk_level}</span></div>
            </div>
          ) : (
            <div className="my-5 flex h-36 w-full flex-col items-center justify-center rounded-2xl border border-dashed border-amber-500/30 bg-amber-500/5 text-center">
              <AlertTriangle className="mb-2 h-8 w-8 text-amber-400" />
              <strong className="text-lg text-amber-200">ข้อมูลไม่เพียงพอ</strong>
              <span className="mt-1 max-w-xs text-[10px] text-amber-100/70">ไม่แสดงเปอร์เซ็นต์เพื่อป้องกันการแจ้งเตือนเกินจริง</span>
            </div>
          )}

          <div className="w-full rounded-xl border border-slate-800 bg-slate-950 p-3">
            <span className="mb-1 block text-[9px] font-bold uppercase tracking-wider text-slate-500">{isModelDemo ? "SHAP explanation — XGBoost synthetic demo" : isOperational ? "SHAP explanation — validated XGBoost" : "Assessment gate"}</span>
            <p className="text-xs leading-relaxed text-slate-300">{data.shap_explanation}</p>
          </div>
        </section>

        <section className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900 p-4">
          <div>
            <div className="flex items-center gap-2"><TrendingUp className="h-4 w-4 text-cyan-400" /><h2 className="text-sm font-semibold text-slate-300">{isModelDemo ? "แนวโน้ม Scenario Model Demo" : "Risk trend"}</h2></div>
            {trendPoints ? (
              <div className="relative mt-2 h-24 rounded-xl border border-slate-800 bg-slate-950 p-1">
                <svg viewBox="0 0 300 100" className="h-full w-full overflow-visible">
                  <line x1="0" y1="30" x2="300" y2="30" stroke="#1e293b" strokeDasharray="3 3" />
                  <line x1="0" y1="70" x2="300" y2="70" stroke="#1e293b" strokeDasharray="3 3" />
                  <polyline fill="none" stroke={theme.fill} strokeWidth="2.5" points={trendPoints} />
                </svg>
              </div>
            ) : <div className="mt-2 rounded-xl border border-dashed border-slate-700 bg-slate-950 p-6 text-center text-xs text-slate-500">ไม่มี Risk history เพราะไม่ได้รันโมเดล</div>}
          </div>

          <div className="flex-1 rounded-xl border border-slate-800 bg-slate-950 p-3">
            <span className="mb-2 flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider text-slate-400"><CheckCircle2 className="h-3 w-3 text-cyan-400" /> Farmer response protocol</span>
            <ul className="space-y-1.5">{data.recommendations.map((recommendation) => <li key={recommendation} className="flex gap-1.5 text-xs text-slate-300"><span className="text-cyan-500">•</span><span>{recommendation}</span></li>)}</ul>
          </div>
        </section>
      </main>

      <section className="mx-auto mt-5 max-w-7xl rounded-2xl border border-slate-800 bg-slate-900 p-4">
        <div className="mb-3 flex items-center gap-2"><Sparkles className="h-4 w-4 text-violet-400" /><h2 className="text-sm font-semibold text-slate-200">Top contributing factors</h2><span className="text-[10px] text-slate-500">{modelExecuted ? "คำนวณด้วย XGBoost SHAP ใน raw-margin space" : "ไม่คำนวณเมื่อข้อมูลไม่ครบ/โมเดลยังไม่ผ่าน Validation"}</span></div>
        {topShapFactors.length ? (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {topShapFactors.map((factor, index) => {
              const shap = factor.shap_value ?? 0;
              return (
                <div key={factor.name} className="rounded-xl border border-slate-800 bg-slate-950 p-3">
                  <div className="flex justify-between"><span className="text-[10px] text-slate-500">#{index + 1}</span><span className={`font-mono text-xs ${shap >= 0 ? "text-red-400" : "text-green-400"}`}>{shap >= 0 ? "+" : ""}{shap.toFixed(4)} SHAP</span></div>
                  <strong className="mt-1 block text-sm text-slate-200">{factor.name}</strong>
                  <span className="text-[10px] text-slate-500">Input {factor.value} {factor.unit} · {shap >= 0 ? "ผลักค่าทำนายขึ้น" : "ผลักค่าทำนายลง"}</span>
                </div>
              );
            })}
          </div>
        ) : <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950 p-5 text-center text-xs text-slate-500">SHAP ถูกระงับ เพราะไม่มีการรันโมเดล</div>}
      </section>

      {showDebug && (
        <section className="mx-auto mt-5 max-w-7xl rounded-2xl border border-slate-700 bg-slate-900 p-4">
          <div className="mb-3 flex items-center gap-2 border-b border-slate-800 pb-2"><Database className="h-4 w-4 text-cyan-400" /><h2 className="text-sm font-semibold">Model &amp; Data Inspector</h2></div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3 text-xs">
              <strong className="mb-2 block text-cyan-300">Feature vector / SHAP</strong>
              <div className="space-y-1.5">{data.features.map((factor) => <div key={factor.name} className="border-b border-slate-900 pb-1"><div className="flex justify-between gap-2"><span className="text-slate-400">{factor.name}</span><span className="font-mono text-slate-200">{factor.value} {factor.unit}</span></div>{factor.shap_value !== null && factor.shap_value !== undefined && <div className="text-right font-mono text-[10px] text-violet-400">SHAP {factor.shap_value}</div>}</div>)}</div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3 text-xs">
              <strong className="mb-2 block text-emerald-300">Provenance</strong>
              <div className="space-y-2">{data.data_sources.map((source) => <div key={source.name} className="border-b border-slate-900 pb-2"><div className="flex justify-between gap-2"><span className="text-slate-200">{source.name}</span><span className="text-slate-500">{source.status}</span></div><p className="mt-1 text-[10px] text-slate-500">{source.note}</p></div>)}</div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3 text-xs">
              <strong className="mb-2 block text-amber-300">Model contract &amp; limitations</strong>
              <p className="text-slate-400">Model: <span className="text-slate-200">{data.model_name ?? "not executed"}</span></p>
              <p className="text-slate-400">Version: <span className="text-slate-200">{data.model_version ?? "—"}</span></p>
              <p className="text-slate-400">Horizon: <span className="text-slate-200">{data.forecast_horizon ?? "—"}</span></p>
              <ul className="mt-3 space-y-1 text-slate-500">{data.limitations.map((limitation) => <li key={limitation} className="flex gap-1"><span>•</span><span>{limitation}</span></li>)}</ul>
            </div>
          </div>
        </section>
      )}

      <footer className="mx-auto mt-5 max-w-7xl text-center font-mono text-[10px] text-slate-600">
        AquaMind MVP • {isModelDemo ? "XGBoost + SHAP synthetic technical demo" : isOperational ? "Validated live model" : "Real Sentinel‑2 + forecast context — risk suppressed until validation"} • {data.timestamp}
      </footer>
    </div>
  );
}
