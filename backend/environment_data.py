from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any

import httpx


WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_FORECAST_URL = "https://marine-api.open-meteo.com/v1/marine"
SINGLE_RUNS_URL = "https://single-runs-api.open-meteo.com/v1/forecast"

WEATHER_VARIABLES = (
    "temperature_2m,precipitation,cloud_cover,"
    "wind_speed_10m,wind_gusts_10m"
)
MARINE_VARIABLES = (
    "sea_surface_temperature,wave_height,ocean_current_velocity,"
    "sea_level_height_msl"
)


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _series(payload: dict[str, Any]) -> list[dict[str, Any]]:
    hourly = payload["hourly"]
    keys = [key for key in hourly if key != "time"]
    rows = []
    for index, timestamp in enumerate(hourly["time"]):
        row = {"time": parse_utc(timestamp)}
        for key in keys:
            values = hourly[key]
            row[key] = values[index] if index < len(values) else None
        rows.append(row)
    return rows


def _numeric(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if isinstance(row.get(key), (int, float))]


def _window(
    rows: list[dict[str, Any]],
    issue_time: datetime,
    start_day: int,
    end_day: int,
) -> list[dict[str, Any]]:
    start = issue_time + timedelta(days=start_day)
    end = issue_time + timedelta(days=end_day)
    return [row for row in rows if start <= row["time"] < end]


def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
    values = _numeric(rows, key)
    return round(mean(values), 4) if values else None


def _sum(rows: list[dict[str, Any]], key: str) -> float | None:
    values = _numeric(rows, key)
    return round(sum(values), 4) if values else None


def _max(rows: list[dict[str, Any]], key: str) -> float | None:
    values = _numeric(rows, key)
    return round(max(values), 4) if values else None


def _range(rows: list[dict[str, Any]], key: str) -> float | None:
    values = _numeric(rows, key)
    return round(max(values) - min(values), 4) if values else None


def _aggregate_window(
    weather: list[dict[str, Any]],
    marine: list[dict[str, Any]],
    issue_time: datetime,
    start_day: int,
    end_day: int,
    suffix: str,
) -> dict[str, float | None]:
    weather_window = _window(weather, issue_time, start_day, end_day)
    marine_window = _window(marine, issue_time, start_day, end_day)
    return {
        f"air_temperature_mean_{suffix}": _mean(weather_window, "temperature_2m"),
        f"precipitation_sum_{suffix}": _sum(weather_window, "precipitation"),
        f"cloud_cover_mean_{suffix}": _mean(weather_window, "cloud_cover"),
        f"wind_speed_mean_{suffix}": _mean(weather_window, "wind_speed_10m"),
        f"wind_gust_max_{suffix}": _max(weather_window, "wind_gusts_10m"),
        f"sst_mean_{suffix}": _mean(marine_window, "sea_surface_temperature"),
        f"wave_height_mean_{suffix}": _mean(marine_window, "wave_height"),
        f"current_velocity_mean_{suffix}": _mean(
            marine_window, "ocean_current_velocity"
        ),
        f"sea_level_range_{suffix}": _range(marine_window, "sea_level_height_msl"),
    }


def _closest_ocean_state(
    marine: list[dict[str, Any]], issue_time: datetime
) -> dict[str, float | None]:
    if not marine:
        return {
            "sst_at_issue": None,
            "wave_height_at_issue": None,
            "current_velocity_at_issue": None,
            "sea_level_at_issue": None,
        }
    row = min(marine, key=lambda value: abs((value["time"] - issue_time).total_seconds()))
    return {
        "sst_at_issue": (
            float(row["sea_surface_temperature"])
            if isinstance(row.get("sea_surface_temperature"), (int, float))
            else None
        ),
        "wave_height_at_issue": (
            float(row["wave_height"])
            if isinstance(row.get("wave_height"), (int, float))
            else None
        ),
        "current_velocity_at_issue": (
            float(row["ocean_current_velocity"])
            if isinstance(row.get("ocean_current_velocity"), (int, float))
            else None
        ),
        "sea_level_at_issue": (
            float(row["sea_level_height_msl"])
            if isinstance(row.get("sea_level_height_msl"), (int, float))
            else None
        ),
    }


def build_model_environment_features(
    weather: list[dict[str, Any]],
    marine: list[dict[str, Any]],
    issue_time: datetime,
) -> dict[str, float | None]:
    d0_3 = _aggregate_window(weather, [], issue_time, 0, 3, "d0_3")
    d3_5 = _aggregate_window(weather, [], issue_time, 3, 6, "d3_5")
    weather_only = {
        key: value
        for key, value in {**d0_3, **d3_5}.items()
        if not key.startswith(("sst_", "wave_", "current_", "sea_level_"))
    }
    return {**weather_only, **_closest_ocean_state(marine, issue_time)}


def fetch_current_environment_forecast(
    latitude: float,
    longitude: float,
    *,
    now: datetime | None = None,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Fetch the forecast that is available at the current decision time."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    owns_client = client is None
    client = client or httpx.Client(
        timeout=httpx.Timeout(30.0, connect=10.0),
        follow_redirects=True,
        headers={"User-Agent": "AquaMind-Environment/2.0"},
    )
    common = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "UTC",
        "forecast_days": 7,
        "cell_selection": "sea",
    }
    try:
        weather_response = client.get(
            WEATHER_FORECAST_URL,
            params={
                **common,
                "hourly": WEATHER_VARIABLES,
                "wind_speed_unit": "ms",
            },
        )
        weather_response.raise_for_status()
        marine_response = client.get(
            MARINE_FORECAST_URL,
            params={**common, "hourly": MARINE_VARIABLES},
        )
        marine_response.raise_for_status()
    finally:
        if owns_client:
            client.close()

    weather_payload = weather_response.json()
    marine_payload = marine_response.json()
    weather_rows = _series(weather_payload)
    marine_rows = _series(marine_payload)
    features = build_model_environment_features(weather_rows, marine_rows, now)
    return {
        "issue_time": iso_utc(now),
        "latitude": latitude,
        "longitude": longitude,
        "features": features,
        "lineage": {
            "weather_url": str(weather_response.url),
            "marine_url": str(marine_response.url),
            "weather_grid": {
                "latitude": weather_payload.get("latitude"),
                "longitude": weather_payload.get("longitude"),
                "elevation": weather_payload.get("elevation"),
            },
            "marine_grid": {
                "latitude": marine_payload.get("latitude"),
                "longitude": marine_payload.get("longitude"),
            },
            "warning": (
                "Open-Meteo values are numerical-model grid data. Coastal "
                "currents/tides are coarse context, not farm-scale observations."
            ),
        },
    }


def fetch_historical_weather_run(
    latitude: float,
    longitude: float,
    issue_time: datetime,
    *,
    model: str = "ecmwf_ifs025",
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Retrieve one archived model run so backtests do not use future data."""
    issue_time = issue_time.astimezone(timezone.utc).replace(
        hour=(issue_time.hour // 6) * 6,
        minute=0,
        second=0,
        microsecond=0,
    )
    owns_client = client is None
    client = client or httpx.Client(timeout=45.0, follow_redirects=True)
    try:
        response = client.get(
            SINGLE_RUNS_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": WEATHER_VARIABLES,
                "wind_speed_unit": "ms",
                "timezone": "UTC",
                "forecast_days": 7,
                "models": model,
                "run": issue_time.strftime("%Y-%m-%dT%H:%M"),
            },
        )
        response.raise_for_status()
        payload = response.json()
    finally:
        if owns_client:
            client.close()
    return {
        "issue_time": iso_utc(issue_time),
        "rows": [
            {**row, "time": iso_utc(row["time"])} for row in _series(payload)
        ],
        "lineage": {"url": str(response.url), "model": model},
    }


def fetch_historical_environment_features(
    latitude: float,
    longitude: float,
    decision_time: datetime,
    *,
    forecast_availability_delay_hours: int = 6,
    model: str = "ecmwf_ifs025",
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Reconstruct features known at a past decision time without look-ahead."""
    decision_time = decision_time.astimezone(timezone.utc)
    run_reference = decision_time - timedelta(
        hours=forecast_availability_delay_hours
    )
    owns_client = client is None
    client = client or httpx.Client(
        timeout=httpx.Timeout(60.0, connect=15.0), follow_redirects=True
    )
    try:
        weather_run = fetch_historical_weather_run(
            latitude, longitude, run_reference, model=model, client=client
        )
        day = decision_time.date().isoformat()
        marine_response = client.get(
            MARINE_FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": MARINE_VARIABLES,
                "start_date": day,
                "end_date": day,
                "timezone": "UTC",
                "cell_selection": "sea",
            },
        )
        marine_response.raise_for_status()
        marine_rows = _series(marine_response.json())
    finally:
        if owns_client:
            client.close()
    weather_rows = [
        {**row, "time": parse_utc(row["time"])} for row in weather_run["rows"]
    ]
    return {
        "decision_time": iso_utc(decision_time),
        "forecast_run_initialization_time": weather_run["issue_time"],
        "features": build_model_environment_features(
            weather_rows, marine_rows, decision_time
        ),
        "lineage": {
            "weather": weather_run["lineage"],
            "marine_url": str(marine_response.url),
            "leakage_control": (
                "Weather uses a single archived run initialized before decision time. "
                "Marine variables use only the state nearest decision time, never future values."
            ),
        },
    }
