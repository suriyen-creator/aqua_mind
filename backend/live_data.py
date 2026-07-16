from __future__ import annotations

import copy
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx


BANGSAEN_LAT = 13.2912
BANGSAEN_LON = 100.9014
MARINE_API_URL = "https://marine-api.open-meteo.com/v1/marine"
SNAPSHOT_PATH = Path(__file__).resolve().parent / "data" / "bangsaen_live_snapshot.json"
OPERATIONAL_SNAPSHOT_PATH = (
    Path(__file__).resolve().parent / "data" / "bangsaen_operational_snapshot.json"
)
LIVE_CACHE_TTL = timedelta(minutes=15)
_live_cache: dict[str, Any] | None = None


def parse_utc(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def age_hours(observed_at: str, now: datetime) -> float:
    return max(0.0, (now - parse_utc(observed_at)).total_seconds() / 3600)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


async def _fetch_marine(client: httpx.AsyncClient) -> dict[str, Any]:
    response = await client.get(
        MARINE_API_URL,
        params={
            "latitude": BANGSAEN_LAT,
            "longitude": BANGSAEN_LON,
            "current": (
                "sea_surface_temperature,wave_height,ocean_current_velocity"
            ),
            "timezone": "UTC",
            "cell_selection": "sea",
        },
    )
    response.raise_for_status()
    payload = response.json()
    current = payload["current"]

    sst = current.get("sea_surface_temperature")
    wave = current.get("wave_height")
    current_velocity = current.get("ocean_current_velocity")
    if not all(_is_number(value) for value in (sst, wave, current_velocity)):
        raise ValueError("Open-Meteo Marine returned incomplete current values")

    return {
        "observed_at": iso_utc(parse_utc(str(current["time"]))),
        "sea_surface_temperature": float(sst),
        "wave_height": float(wave),
        "ocean_current_velocity": float(current_velocity),
        "grid_latitude": float(payload.get("latitude", BANGSAEN_LAT)),
        "grid_longitude": float(payload.get("longitude", BANGSAEN_LON)),
    }


def _load_operational_snapshot(now: datetime) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if not OPERATIONAL_SNAPSHOT_PATH.is_file():
        return (
            {
                "status": "unavailable",
                "observed_at": None,
                "ndci_mean": None,
                "ndwi_mean": None,
                "valid_pixel_ratio": 0.0,
                "item_id": None,
            },
            None,
        )
    payload = json.loads(OPERATIONAL_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    summary = payload["sentinel"]["summary"]
    satellite_age = age_hours(summary["observed_at"], now)
    status = (
        "available"
        if satellite_age <= 10 * 24 and summary["valid_pixel_ratio"] >= 0.05
        else "stale"
    )
    return (
        {
            "status": status,
            "observed_at": summary["observed_at"],
            "ndci_mean": summary["ndci_latest"],
            "ndwi_mean": summary["ndwi_latest"],
            "valid_pixel_ratio": summary["valid_pixel_ratio"],
            "item_id": summary["latest_item_id"],
            "scene_cloud_cover_percent": summary["scene_cloud_cover_percent"],
        },
        payload,
    )


def _load_snapshot() -> dict[str, Any]:
    with SNAPSHOT_PATH.open(encoding="utf-8") as snapshot_file:
        return json.load(snapshot_file)


async def fetch_bangsaen_live_inputs(
    now: datetime | None = None,
) -> dict[str, Any]:
    global _live_cache

    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if _live_cache is not None:
        cached_at = parse_utc(_live_cache["retrieved_at"])
        if now - cached_at < LIVE_CACHE_TTL:
            cached = copy.deepcopy(_live_cache)
            cached["retrieved_at"] = iso_utc(now)
            cached["from_memory_cache"] = True
            # Marine calls are cached, but a locally refreshed Sentinel/forecast
            # snapshot must be visible immediately.
            satellite, operational_snapshot = _load_operational_snapshot(now)
            cached["satellite"] = satellite
            cached["operational_snapshot"] = operational_snapshot
            return cached

    errors: list[str] = []
    satellite, operational_snapshot = _load_operational_snapshot(now)

    timeout = httpx.Timeout(12.0, connect=6.0)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": "AquaMind-MVP/1.2"},
    ) as client:
        try:
            marine_result: dict[str, Any] | BaseException = await _fetch_marine(client)
        except BaseException as exc:
            marine_result = exc

    from_snapshot = False
    if isinstance(marine_result, BaseException):
        errors.append(f"marine_api: {type(marine_result).__name__}")
        snapshot = _load_snapshot()
        marine = snapshot["marine"]
        from_snapshot = True
    else:
        marine = marine_result

    result = {
        "retrieved_at": iso_utc(now),
        "marine": marine,
        "satellite": satellite,
        "operational_snapshot": operational_snapshot,
        "from_snapshot": from_snapshot,
        "errors": errors,
    }
    _live_cache = copy.deepcopy(result)
    return result
