"use client";

import { useEffect, useRef, useState } from "react";
import type { MonitoringStation } from "@/lib/dashboard-types";

type MonitoringMapProps = {
  stations: MonitoringStation[];
  selectedStationId: string | null;
  onSelectStation: (stationId: string) => void;
  recenterRequest: number;
};

const STATUS_COLORS = {
  normal: { stroke: "#15803d", fill: "#22c55e" },
  watch: { stroke: "#b45309", fill: "#f59e0b" },
  warning: { stroke: "#b91c1c", fill: "#ef4444" },
  unavailable: { stroke: "#64748b", fill: "#94a3b8" },
} as const;

const STATUS_LABELS = {
  normal: "ปกติ",
  watch: "เฝ้าระวัง",
  warning: "เตือน",
  unavailable: "ไม่มีข้อมูล",
} as const;

export default function MonitoringMap({ stations, selectedStationId, onSelectStation, recenterRequest }: MonitoringMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<import("leaflet").Map | null>(null);
  const layerRef = useRef<import("leaflet").LayerGroup | null>(null);
  const leafletRef = useRef<typeof import("leaflet") | null>(null);
  const hasInitialFit = useRef(false);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    let disposed = false;
    let map: import("leaflet").Map | null = null;

    async function createMap() {
      if (!containerRef.current) return;
      const leaflet = await import("leaflet");
      if (disposed || !containerRef.current) return;

      const leafletModule = leaflet as typeof import("leaflet") & { default?: typeof import("leaflet") };
      const L = leafletModule.default ?? leafletModule;
      leafletRef.current = L;
      map = L.map(containerRef.current, {
        // Known Chonburi fallback from the existing station data; fitBounds takes over once API stations arrive.
        center: [13.3611, 100.9234],
        zoom: 10,
        zoomControl: false,
        attributionControl: true,
      });
      L.control.zoom({ position: "bottomright" }).addTo(map);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);
      layerRef.current = L.layerGroup().addTo(map);
      mapRef.current = map;
      setMapReady(true);
      window.setTimeout(() => map?.invalidateSize(), 0);
    }

    void createMap();
    return () => {
      disposed = true;
      setMapReady(false);
      layerRef.current = null;
      mapRef.current = null;
      map?.remove();
    };
  }, []);

  useEffect(() => {
    if (!mapReady || !mapRef.current || !leafletRef.current || !layerRef.current) return;
    const L = leafletRef.current;
    const layer = layerRef.current;
    layer.clearLayers();

    stations.forEach((station) => {
      const selected = station.id === selectedStationId;
      const colors = STATUS_COLORS[station.status];
      const marker = L.circleMarker([station.latitude, station.longitude], {
        radius: selected ? 10 : 7,
        color: selected ? "#0f1f3d" : colors.stroke,
        fillColor: colors.fill,
        fillOpacity: station.status === "unavailable" ? 0.7 : 0.95,
        weight: selected ? 3 : 2,
      });
      marker.bindTooltip(`${station.name} · ${STATUS_LABELS[station.status]}`, {
        direction: "top",
        offset: [0, -6],
        opacity: 0.96,
      });
      marker.on("click", () => onSelectStation(station.id));
      marker.addTo(layer);
    });

    if (stations.length > 0 && !hasInitialFit.current) {
      const bounds = L.latLngBounds(stations.map((station) => [station.latitude, station.longitude] as [number, number]));
      mapRef.current.fitBounds(bounds, { padding: [28, 28], maxZoom: 12 });
      hasInitialFit.current = true;
    }
  }, [mapReady, onSelectStation, selectedStationId, stations]);

  useEffect(() => {
    if (!mapReady || !mapRef.current || !leafletRef.current || stations.length === 0) return;
    const L = leafletRef.current;
    const bounds = L.latLngBounds(stations.map((station) => [station.latitude, station.longitude] as [number, number]));
    mapRef.current.fitBounds(bounds, { padding: [28, 28], maxZoom: 12 });
  }, [mapReady, recenterRequest, stations]);

  return (
    <div className="relative h-[390px] overflow-hidden rounded-[18px] bg-slate-200 sm:h-[440px] lg:h-[560px]" aria-label="แผนที่จุดติดตามน้ำ">
      <div ref={containerRef} className="h-full w-full" />
      {!mapReady && <div className="absolute inset-0 grid place-items-center bg-slate-100/90 text-[14px] text-slate-600">กำลังโหลดแผนที่…</div>}
      {mapReady && stations.length === 0 && <div className="pointer-events-none absolute inset-x-4 top-4 rounded-[12px] bg-white/95 px-3 py-2 text-[14px] text-slate-700 shadow-sm">ยังไม่มีพิกัดสถานีสำหรับแสดงบนแผนที่</div>}
    </div>
  );
}
