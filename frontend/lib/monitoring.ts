import type { MonitoringStatus, StationMetadata } from "@/lib/dashboard-types";

export function getMonitoringStatus(score: number | null): MonitoringStatus {
  if (score === null || !Number.isFinite(score)) return "unavailable";
  if (score >= 70) return "warning";
  if (score >= 50) return "watch";
  return "normal";
}

export function getStationName(location: string): string {
  return location.split(" — ")[0]?.trim() || location;
}

export function getStationArea(location: string): string {
  return location.split(" — ").slice(1).join(" — ").trim() || "พื้นที่ติดตามน้ำ";
}

export function formatScore(score: number | null): string {
  return score === null || !Number.isFinite(score) ? "—" : `${Math.round(score)} / 100`;
}

export function stationCoordinatesAreValid(station: StationMetadata): boolean {
  return Number.isFinite(station.lat) && Number.isFinite(station.lon)
    && station.lat >= -90 && station.lat <= 90
    && station.lon >= -180 && station.lon <= 180;
}
