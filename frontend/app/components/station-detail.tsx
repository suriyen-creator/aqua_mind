import { ArrowRight, Clock3, Gauge, MapPin } from "lucide-react";
import type { MonitoringStation, MonitoringStatus, PredictionData } from "@/lib/dashboard-types";
import { formatScore, getStationArea } from "@/lib/monitoring";

type StationDetailProps = {
  station: MonitoringStation | null;
  risk: PredictionData | null;
  onViewTrend: () => void;
};

const STATUS_LABELS: Record<MonitoringStatus, string> = {
  normal: "ปกติ",
  watch: "เฝ้าระวัง",
  warning: "เตือน",
  unavailable: "ไม่มีข้อมูล",
};

const STATUS_STYLES: Record<MonitoringStatus, string> = {
  normal: "bg-emerald-50 text-emerald-800",
  watch: "bg-amber-50 text-amber-800",
  warning: "bg-rose-50 text-rose-800",
  unavailable: "bg-slate-100 text-slate-700",
};

export default function StationDetail({ station, risk, onViewTrend }: StationDetailProps) {
  if (!station) {
    return <div className="grid min-h-[220px] place-items-center rounded-[16px] border border-dashed border-slate-300 bg-white px-5 text-center text-[15px] leading-6 text-slate-600">เลือกจุดติดตามบนแผนที่เพื่อดูรายละเอียด</div>;
  }

  return (
    <section aria-labelledby="station-detail-heading" className="rounded-[16px] border border-slate-200 bg-white p-4 sm:p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-[13px] text-slate-500"><MapPin className="h-4 w-4 shrink-0 text-sky-700" aria-hidden="true" /><span className="truncate">{getStationArea(station.location)}</span></div>
          <h2 id="station-detail-heading" className="mt-1 text-[19px] font-bold leading-7 text-[#0f1f3d]">{station.name}</h2>
        </div>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-[13px] font-bold ${STATUS_STYLES[station.status]}`}>{STATUS_LABELS[station.status]}</span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2.5 sm:grid-cols-3 lg:grid-cols-2">
        <div className="rounded-[12px] bg-slate-50 px-3 py-2.5"><span className="block text-[13px] text-slate-500">ดัชนีสถานการณ์</span><strong className="mt-1 block text-[24px] leading-7 text-[#0f1f3d]">{formatScore(station.score)}</strong></div>
        <div className="rounded-[12px] bg-slate-50 px-3 py-2.5"><span className="flex items-center gap-1 text-[13px] text-slate-500"><Clock3 className="h-3.5 w-3.5" aria-hidden="true" />อัปเดตล่าสุด</span><strong className="mt-1 block truncate text-[14px] leading-7 text-[#0f1f3d]" title={station.updatedAt}>{station.updatedAt || "—"}</strong></div>
        <div className="col-span-2 flex items-center gap-2 rounded-[12px] border border-dashed border-slate-200 px-3 py-2.5 text-[13px] leading-5 text-slate-600 sm:col-span-1 lg:col-span-2"><Gauge className="h-4 w-4 shrink-0 text-slate-500" aria-hidden="true" />{risk?.history_trend?.length ? `มีข้อมูลแนวโน้ม ${risk.history_trend.length} จุด` : "ยังไม่มีตัวชี้วัดหน้างานเพิ่มเติมจาก API"}</div>
      </div>

      <div className="mt-4 flex flex-col gap-2 sm:flex-row lg:flex-col">
        <button type="button" onClick={onViewTrend} className="inline-flex min-h-11 flex-1 items-center justify-center gap-2 rounded-[11px] bg-[#1479b8] px-3 text-[14px] font-bold text-white transition hover:bg-[#0f659c] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2">ดูแนวโน้ม 30 วัน <ArrowRight className="h-4 w-4" aria-hidden="true" /></button>
      </div>
    </section>
  );
}
