"use client";

import { Database, Settings2 } from "lucide-react";
import type { DataSourceInfo, Factor, PredictionData, TestScenarioKey, TestState } from "@/lib/dashboard-types";
import type { PresentedFactor, SatelliteStatus } from "@/lib/watch-presentation";

interface TechnicalDetailsProps {
  data: PredictionData;
  factors: Factor[];
  sources: DataSourceInfo[];
  limitations: string[];
  topFactors: PresentedFactor[];
  isTestMode: boolean;
  testState: TestState;
  showTestControls: boolean;
  onToggleTestControls: () => void;
  onSetTestScenario: (key: TestScenarioKey) => void;
  onUpdateScore: (score: number) => void;
  onUpdateSatelliteStatus: (status: SatelliteStatus) => void;
  onUpdateFieldVerification: (count: number) => void;
  onUpdateApiStatus: (status: TestState["apiStatus"]) => void;
  onUpdateFactor: (index: number, update: Partial<Factor>) => void;
  apiStatus: string;
}

export default function TechnicalDetails({
  data,
  factors,
  sources,
  limitations,
  topFactors,
  isTestMode,
  testState,
  showTestControls,
  onToggleTestControls,
  onSetTestScenario,
  onUpdateScore,
  onUpdateSatelliteStatus,
  onUpdateFieldVerification,
  onUpdateApiStatus,
  onUpdateFactor,
  apiStatus,
}: TechnicalDetailsProps) {
  return (
    <details className="rounded-[18px] border border-slate-200 bg-white shadow-none">
      <summary className="flex min-h-14 cursor-pointer list-none items-center gap-3 px-4 py-3 text-[18px] font-bold text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 sm:px-5">
        <Database className="h-5 w-5 shrink-0 text-slate-600" aria-hidden="true" />
        ข้อมูลเทคนิค แหล่งข้อมูล และโหมดทดสอบ
      </summary>
      <div className="border-t border-slate-200 p-4 text-[15px] text-slate-700 sm:p-5">
        <p className="max-w-3xl leading-6 text-slate-600">
          ส่วนนี้มี SHAP, NDCI, รุ่นโมเดล, แหล่งข้อมูล, พิกัด และข้อจำกัดสำหรับผู้ตรวจสอบระบบ คะแนนเป็นดัชนีเฝ้าระวังสภาพแวดล้อม ไม่ใช่ Probability และข้อมูลดาวเทียมไม่ใช่ผลยืนยันเหตุการณ์ภาคสนาม
        </p>

        {isTestMode && (
          <section className="mt-4 rounded-[14px] border border-violet-200 bg-violet-50 p-3" aria-labelledby="test-controls-heading">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Settings2 className="h-5 w-5 text-violet-700" aria-hidden="true" />
                <h3 id="test-controls-heading" className="text-[17px] font-bold text-violet-900">UI test controls</h3>
              </div>
              <button type="button" aria-expanded={showTestControls} onClick={onToggleTestControls} className="min-h-11 rounded-[12px] border border-violet-300 bg-white px-3 text-[14px] font-semibold text-violet-900 hover:bg-violet-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-600">
                {showTestControls ? "ซ่อน controls" : "แสดง controls"}
              </button>
            </div>
            {showTestControls && (
              <div className="mt-3">
                <div className="flex flex-wrap gap-2" role="group" aria-label="เลือกระดับคะแนนทดสอบ">
                  {(["normal", "watch", "urgent"] as TestScenarioKey[]).map((key) => (
                    <button key={key} type="button" onClick={() => onSetTestScenario(key)} className="min-h-11 rounded-[12px] border border-violet-300 bg-white px-3 text-[14px] font-semibold text-violet-900 hover:bg-violet-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-600">
                      {key === "normal" ? "0–49 ปกติ" : key === "watch" ? "50–69 ควรตรวจเพิ่ม" : "70–100 ตรวจทันที"}
                    </button>
                  ))}
                </div>
                <div className="mt-3 grid gap-3 text-[14px] sm:grid-cols-2 lg:grid-cols-4">
                  <label className="block">คะแนนดัชนี
                    <input type="number" min="0" max="100" value={testState.score} onChange={(event) => onUpdateScore(Math.max(0, Math.min(100, Number(event.target.value))))} className="mt-1 min-h-11 w-full rounded-[10px] border border-slate-300 bg-white px-3 text-[15px]" />
                  </label>
                  <label className="block">ภาพดาวเทียม
                    <select value={testState.satelliteStatus} onChange={(event) => onUpdateSatelliteStatus(event.target.value as SatelliteStatus)} className="mt-1 min-h-11 w-full rounded-[10px] border border-slate-300 bg-white px-3 text-[15px]">
                      <option value="available">พร้อมใช้</option><option value="stale">เก่า</option><option value="unavailable">ไม่มี</option>
                    </select>
                  </label>
                  <label className="block">ผลตรวจภาคสนาม
                    <input type="number" min="0" value={testState.fieldVerificationCount} onChange={(event) => onUpdateFieldVerification(Math.max(0, Number(event.target.value)))} className="mt-1 min-h-11 w-full rounded-[10px] border border-slate-300 bg-white px-3 text-[15px]" />
                  </label>
                  <label className="block">สถานะ API
                    <select value={testState.apiStatus} onChange={(event) => onUpdateApiStatus(event.target.value as TestState["apiStatus"])} className="mt-1 min-h-11 w-full rounded-[10px] border border-slate-300 bg-white px-3 text-[15px]">
                      <option value="mocked">จำลอง</option><option value="connected">เชื่อมต่อ</option>
                    </select>
                  </label>
                </div>
                <div className="mt-3 grid gap-3 lg:grid-cols-3">
                  {testState.factors.map((factor, index) => (
                    <div key={factor.feature_key ?? factor.name} className="rounded-[12px] border border-violet-200 bg-white p-3">
                      <strong className="block">{factor.name}</strong>
                        <div className="mt-2 grid grid-cols-2 gap-2 text-[13px]">
                        <label>ค่าปัจจัย
                          <input type="number" step="0.1" value={factor.value} onChange={(event) => onUpdateFactor(index, { value: Number(event.target.value) })} className="mt-1 min-h-10 w-full rounded-[10px] border border-slate-300 bg-white px-2 text-[14px]" />
                        </label>
                        <label>SHAP จุด
                          <input type="number" step="0.1" value={factor.shap_value ?? 0} onChange={(event) => { const shapValue = Number(event.target.value); onUpdateFactor(index, { shap_value: shapValue, impact: shapValue > 0 ? "increase" : shapValue < 0 ? "decrease" : "none" }); }} className="mt-1 min-h-10 w-full rounded-[10px] border border-slate-300 bg-white px-2 text-[14px]" />
                        </label>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          <section className="rounded-[14px] border border-slate-200 bg-slate-50 p-3" aria-labelledby="technical-factors-heading">
            <h3 id="technical-factors-heading" className="font-bold text-slate-900">Feature vector / SHAP</h3>
            <div className="mt-3 space-y-2.5">
              {factors.length ? factors.map((factor) => (
                <div key={factor.name} className="border-b border-slate-200 pb-2">
                  <div className="flex justify-between gap-3"><span>{factor.name}</span><span className="font-mono">{factor.value} {factor.unit}</span></div>
                  {factor.shap_value !== null && factor.shap_value !== undefined && <div className="text-right font-mono text-[13px] text-violet-700">SHAP {factor.shap_value}</div>}
                </div>
              )) : <p className="text-slate-500">ยังไม่มี feature ที่ใช้แสดง</p>}
            </div>
          </section>
          <section className="rounded-[14px] border border-slate-200 bg-slate-50 p-3" aria-labelledby="technical-sources-heading">
            <h3 id="technical-sources-heading" className="font-bold text-slate-900">แหล่งข้อมูลและหลักฐาน</h3>
            <div className="mt-3 space-y-2.5">
              {sources.length ? sources.map((source) => (
                <div key={source.name} className="border-b border-slate-200 pb-2"><div className="flex justify-between gap-3"><strong>{source.name}</strong><span className="text-slate-500">{source.status}</span></div><p className="mt-1 text-[13px] leading-5 text-slate-600">{source.note}</p>{source.observed_at && <p className="mt-1 font-mono text-xs text-slate-500">{source.observed_at}</p>}</div>
              )) : <p className="text-slate-500">ยังไม่มีรายละเอียดแหล่งข้อมูล</p>}
            </div>
          </section>
          <section className="rounded-[14px] border border-slate-200 bg-slate-50 p-3" aria-labelledby="technical-contract-heading">
            <h3 id="technical-contract-heading" className="font-bold text-slate-900">รุ่นโมเดลและข้อจำกัด</h3>
            <dl className="mt-3 space-y-2 text-[13px]"><div className="flex justify-between gap-3"><dt>API</dt><dd>{apiStatus}</dd></div><div className="flex justify-between gap-3"><dt>Model</dt><dd>{data.model_name ?? "ยังไม่รัน"}</dd></div><div className="flex justify-between gap-3"><dt>Version</dt><dd>{data.model_version ?? "—"}</dd></div><div className="flex justify-between gap-3"><dt>Horizon</dt><dd>{data.forecast_horizon ?? "—"}</dd></div><div className="flex justify-between gap-3"><dt>พิกัด</dt><dd className="font-mono">{data.lat.toFixed(4)}, {data.lon.toFixed(4)}</dd></div></dl>
            <ul className="mt-3 space-y-2 text-[13px] leading-5 text-slate-600">{limitations.map((limitation) => <li key={limitation}>• {limitation}</li>)}</ul>
            {topFactors.length > 0 && <p className="mt-3 text-[13px] leading-5 text-slate-600">ปัจจัยเด่นเชิงเทคนิค: {topFactors.map((factor) => `${factor.displayName} (${factor.shapValue > 0 ? "+" : ""}${factor.shapValue.toFixed(1)} จุด)`).join(", ")}</p>}
          </section>
        </div>
      </div>
    </details>
  );
}
