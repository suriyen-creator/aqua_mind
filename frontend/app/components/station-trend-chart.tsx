"use client";

import { useState } from "react";

type StationTrendChartProps = {
  points: number[];
  periodDays: number;
  metricLabel: string;
};

function formatValue(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

export default function StationTrendChart({ points, periodDays, metricLabel }: StationTrendChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(points.length ? points.length - 1 : null);

  if (points.length === 0) {
    return <div className="grid min-h-64 place-items-center rounded-[14px] bg-slate-50 px-4 text-center text-[15px] text-slate-600">ยังไม่มีข้อมูลย้อนหลัง 30 วันสำหรับสถานีนี้</div>;
  }

  const width = 720;
  const height = 280;
  const padding = { top: 24, right: 22, bottom: 44, left: 44 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const minValue = Math.min(0, ...points);
  const maxValue = Math.max(100, ...points);
  const valueRange = Math.max(1, maxValue - minValue);
  const xFor = (index: number) => padding.left + (points.length === 1 ? chartWidth / 2 : (index / (points.length - 1)) * chartWidth);
  const yFor = (value: number) => padding.top + ((maxValue - value) / valueRange) * chartHeight;
  const path = points.map((point, index) => `${index === 0 ? "M" : "L"} ${xFor(index).toFixed(2)} ${yFor(point).toFixed(2)}`).join(" ");
  const tickValues = [maxValue, minValue + valueRange / 2, minValue];
  const activePoint = activeIndex === null ? null : points[activeIndex];
  const activeX = activeIndex === null ? 0 : xFor(activeIndex);
  const activeY = activePoint === null ? 0 : yFor(activePoint);
  const tooltipX = Math.min(Math.max(activeX - 55, padding.left), width - padding.right - 110);
  const firstLabel = periodDays > 0 ? `-${periodDays} วัน` : "จุดแรก";
  const middleLabel = periodDays > 0 ? `-${Math.max(1, Math.round(periodDays / 2))} วัน` : `จุด ${Math.max(1, Math.ceil(points.length / 2))}`;

  return (
    <div className="w-full">
      <div className="w-full overflow-hidden">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-auto w-full" role="img" aria-label={`กราฟ${metricLabel}ย้อนหลังจากข้อมูลที่มี`}>
          {tickValues.map((value, index) => {
            const y = yFor(value);
            return (
              <g key={`${value}-${index}`}>
                <line x1={padding.left} x2={width - padding.right} y1={y} y2={y} stroke="#e2e8f0" strokeWidth="1" />
                <text x={padding.left - 10} y={y + 4} textAnchor="end" fontSize="12" fill="#64748b">{formatValue(value)}</text>
              </g>
            );
          })}
          <path d={path} fill="none" stroke="#1479b8" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
          {points.map((point, index) => (
            <circle
              key={`${point}-${index}`}
              cx={xFor(index)}
              cy={yFor(point)}
              r={activeIndex === index ? 6 : 4}
              fill="#ffffff"
              stroke="#1479b8"
              strokeWidth="3"
              tabIndex={0}
              role="button"
              aria-label={`${metricLabel} จุดที่ ${index + 1}: ${formatValue(point)}`}
              onMouseEnter={() => setActiveIndex(index)}
              onFocus={() => setActiveIndex(index)}
              onClick={() => setActiveIndex(index)}
            />
          ))}
          {activePoint !== null && (
            <g pointerEvents="none">
              <line x1={activeX} x2={activeX} y1={padding.top} y2={padding.top + chartHeight} stroke="#94a3b8" strokeDasharray="4 4" />
              <rect x={tooltipX} y={Math.max(4, activeY - 42)} width="110" height="32" rx="7" fill="#0f1f3d" />
              <text x={tooltipX + 55} y={Math.max(24, activeY - 21)} textAnchor="middle" fontSize="13" fontWeight="700" fill="#ffffff">{formatValue(activePoint)} / 100</text>
            </g>
          )}
          <text x={padding.left} y={height - 14} fontSize="12" fill="#64748b">{firstLabel}</text>
          <text x={width / 2} y={height - 14} textAnchor="middle" fontSize="12" fill="#64748b">{middleLabel}</text>
          <text x={width - padding.right} y={height - 14} textAnchor="end" fontSize="12" fill="#64748b">วันนี้</text>
        </svg>
      </div>
      {periodDays > 0 && periodDays < 30 && <p className="mt-1 text-[13px] leading-5 text-slate-500">แสดง {points.length} จุดจากช่วงข้อมูล {periodDays} วันของ API ปัจจุบัน ยังไม่ครบ 30 วัน</p>}
    </div>
  );
}
