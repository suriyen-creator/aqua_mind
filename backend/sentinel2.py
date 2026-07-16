from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import httpx
import numpy as np


EARTH_SEARCH_URL = "https://earth-search.aws.element84.com/v1/search"


@dataclass(frozen=True)
class AreaOfInterest:
    station_id: str
    name: str
    west: float
    south: float
    east: float
    north: float

    @property
    def bbox(self) -> list[float]:
        return [self.west, self.south, self.east, self.north]


# A small offshore box west of Bangsaen Beach. It intentionally avoids most
# land pixels; the SCL water class is still required before an index is used.
BANGSAEN_AOI = AreaOfInterest(
    station_id="chonburi_03",
    name="Bangsaen near-shore water AOI",
    west=100.875,
    south=13.275,
    east=100.895,
    north=13.305,
)

REQUIRED_ASSETS = ("red", "rededge1", "green", "nir", "scl")
SCL_WATER_CLASS = 6


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def search_sentinel2_items(
    start: datetime,
    end: datetime,
    aoi: AreaOfInterest = BANGSAEN_AOI,
    *,
    max_scene_cloud_percent: float = 90.0,
    limit: int = 40,
    client: httpx.Client | None = None,
) -> list[dict[str, Any]]:
    """Search public Sentinel-2 L2A COGs without requiring an API key."""
    body = {
        "collections": ["sentinel-2-l2a"],
        "bbox": aoi.bbox,
        "datetime": f"{iso_utc(start)}/{iso_utc(end)}",
        "limit": limit,
        "query": {"eo:cloud_cover": {"lt": max_scene_cloud_percent}},
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
    }
    owns_client = client is None
    client = client or httpx.Client(
        timeout=httpx.Timeout(30.0, connect=10.0),
        follow_redirects=True,
        headers={"User-Agent": "AquaMind-Sentinel2/2.0"},
    )
    try:
        response = client.post(EARTH_SEARCH_URL, json=body)
        response.raise_for_status()
        items = response.json().get("features", [])
    finally:
        if owns_client:
            client.close()

    usable = []
    for item in items:
        assets = item.get("assets", {})
        if all(key in assets and assets[key].get("href") for key in REQUIRED_ASSETS):
            usable.append(item)
    return usable


def _read_band_to_grid(
    href: str,
    *,
    target_crs: Any,
    target_transform: Any,
    width: int,
    height: int,
) -> np.ndarray:
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.vrt import WarpedVRT

    with rasterio.open(href) as source:
        with WarpedVRT(
            source,
            crs=target_crs,
            transform=target_transform,
            width=width,
            height=height,
            resampling=Resampling.bilinear,
        ) as vrt:
            return vrt.read(1).astype("float32")


def _finite_stats(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": round(float(np.mean(values)), 6),
        "median": round(float(np.median(values)), 6),
        "std": round(float(np.std(values)), 6),
        "p10": round(float(np.percentile(values, 10)), 6),
        "p90": round(float(np.percentile(values, 90)), 6),
    }


def extract_scene_indices(
    item: dict[str, Any],
    aoi: AreaOfInterest = BANGSAEN_AOI,
) -> dict[str, Any]:
    """Read only the AOI window and calculate NDCI/NDWI after SCL masking."""
    import rasterio
    from rasterio.windows import Window, from_bounds
    from rasterio.warp import transform_bounds

    assets = item["assets"]
    env_options = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "GDAL_HTTP_MULTIRANGE": "YES",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
        "AWS_NO_SIGN_REQUEST": "YES",
    }
    with rasterio.Env(**env_options):
        with rasterio.open(assets["scl"]["href"]) as scl_source:
            bounds = transform_bounds(
                "EPSG:4326",
                scl_source.crs,
                *aoi.bbox,
                densify_pts=21,
            )
            raw_window = from_bounds(*bounds, transform=scl_source.transform)
            window = raw_window.round_offsets().round_lengths()
            full = Window(0, 0, scl_source.width, scl_source.height)
            window = window.intersection(full)
            if window.width < 1 or window.height < 1:
                raise ValueError("AOI does not overlap the Sentinel-2 scene")

            scl = scl_source.read(1, window=window)
            target_transform = scl_source.window_transform(window)
            target_crs = scl_source.crs
            height, width = scl.shape

        bands = {
            name: _read_band_to_grid(
                assets[name]["href"],
                target_crs=target_crs,
                target_transform=target_transform,
                width=width,
                height=height,
            )
            for name in ("red", "rededge1", "green", "nir")
        }

    water_mask = scl == SCL_WATER_CLASS
    all_finite = np.logical_and.reduce(
        [np.isfinite(array) & (array > 0) for array in bands.values()]
    )
    ndci_denominator = bands["rededge1"] + bands["red"]
    ndwi_denominator = bands["green"] + bands["nir"]
    valid = (
        water_mask
        & all_finite
        & (np.abs(ndci_denominator) > 1e-6)
        & (np.abs(ndwi_denominator) > 1e-6)
    )
    valid_count = int(np.count_nonzero(valid))
    total_count = int(valid.size)
    if valid_count == 0:
        raise ValueError("No SCL water pixels with valid reflectance in AOI")

    ndci = np.clip(
        (bands["rededge1"] - bands["red"]) / ndci_denominator,
        -1,
        1,
    )[valid]
    ndwi = np.clip(
        (bands["green"] - bands["nir"]) / ndwi_denominator,
        -1,
        1,
    )[valid]
    properties = item.get("properties", {})
    observed_at = properties.get("datetime") or properties.get("start_datetime")
    if not observed_at:
        raise ValueError("Sentinel-2 item has no observation timestamp")

    return {
        "station_id": aoi.station_id,
        "aoi": asdict(aoi),
        "item_id": item["id"],
        "observed_at": iso_utc(parse_utc(observed_at)),
        "scene_cloud_cover_percent": round(
            float(properties.get("eo:cloud_cover", math.nan)), 3
        ),
        "valid_pixel_count": valid_count,
        "aoi_pixel_count": total_count,
        "valid_pixel_ratio": round(valid_count / total_count, 4),
        "ndci": _finite_stats(ndci),
        "ndwi": _finite_stats(ndwi),
        "source": {
            "catalog": EARTH_SEARCH_URL,
            "collection": "sentinel-2-l2a",
            "processing_level": "L2A surface reflectance",
            "cloud_mask": "SCL class 6 (water) only",
            "asset_urls": {
                key: assets[key]["href"] for key in REQUIRED_ASSETS
            },
        },
    }


def extract_time_series(
    items: Iterable[dict[str, Any]],
    aoi: AreaOfInterest = BANGSAEN_AOI,
    *,
    minimum_valid_ratio: float = 0.05,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    observations: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    for item in items:
        try:
            result = extract_scene_indices(item, aoi)
            if result["valid_pixel_ratio"] < minimum_valid_ratio:
                raise ValueError(
                    f"valid_pixel_ratio {result['valid_pixel_ratio']} below "
                    f"minimum {minimum_valid_ratio}"
                )
            observations.append(result)
        except Exception as exc:  # each scene is independently recoverable
            rejected.append({"item_id": item.get("id", "unknown"), "reason": str(exc)})
    observations.sort(key=lambda row: parse_utc(row["observed_at"]))
    # Adjacent Sentinel-2 tiles can cover the same AOI in one acquisition. Keep
    # one observation per UTC date so trends are not biased by duplicate passes.
    by_date: dict[str, dict[str, Any]] = {}
    for observation in observations:
        key = parse_utc(observation["observed_at"]).date().isoformat()
        current = by_date.get(key)
        quality = (
            observation["valid_pixel_ratio"],
            -observation["scene_cloud_cover_percent"],
        )
        current_quality = (
            (current["valid_pixel_ratio"], -current["scene_cloud_cover_percent"])
            if current
            else (-1.0, float("-inf"))
        )
        if current is None or quality > current_quality:
            if current is not None:
                rejected.append(
                    {
                        "item_id": current["item_id"],
                        "reason": f"duplicate acquisition date {key}; lower local quality",
                    }
                )
            by_date[key] = observation
        else:
            rejected.append(
                {
                    "item_id": observation["item_id"],
                    "reason": f"duplicate acquisition date {key}; lower local quality",
                }
            )
    deduplicated = sorted(
        by_date.values(), key=lambda row: parse_utc(row["observed_at"])
    )
    return deduplicated, rejected


def summarize_time_series(
    observations: list[dict[str, Any]],
    *,
    now: datetime | None = None,
    lookback_days: int = 30,
) -> dict[str, Any]:
    if not observations:
        raise ValueError("No valid Sentinel-2 observations to summarize")
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    latest = observations[-1]
    cutoff = now - timedelta(days=lookback_days)
    recent = [
        row for row in observations if parse_utc(row["observed_at"]) >= cutoff
    ] or [latest]
    times = np.array(
        [
            (parse_utc(row["observed_at"]) - parse_utc(recent[0]["observed_at"]))
            .total_seconds()
            / 86400
            for row in recent
        ],
        dtype=float,
    )
    ndci_values = np.array([row["ndci"]["median"] for row in recent], dtype=float)
    slope = (
        float(np.polyfit(times, ndci_values, 1)[0])
        if len(recent) >= 2 and np.ptp(times) > 0
        else 0.0
    )
    observed_at = parse_utc(latest["observed_at"])
    return {
        "station_id": latest["station_id"],
        "observed_at": latest["observed_at"],
        "data_age_days": round(max(0.0, (now - observed_at).total_seconds() / 86400), 2),
        "latest_item_id": latest["item_id"],
        "ndci_latest": latest["ndci"]["median"],
        "ndci_mean_30d": round(float(np.mean(ndci_values)), 6),
        "ndci_slope_30d": round(slope, 6),
        "ndwi_latest": latest["ndwi"]["median"],
        "valid_pixel_ratio": latest["valid_pixel_ratio"],
        "observation_count_30d": len(recent),
        "scene_cloud_cover_percent": latest["scene_cloud_cover_percent"],
    }
