from __future__ import annotations

import functools
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Optional

import math

import requests


WEATHER_LABELS = ("Sunny", "Rainy", "Cloudy", "Snowy")


def _owm_main_to_label(main: str) -> str:
    lowered = (main or "").lower()
    if lowered == "clear":
        return "Sunny"
    if lowered in ("clouds", "mist", "smoke", "haze", "fog"):
        return "Cloudy"
    if lowered in ("rain", "drizzle", "thunderstorm"):
        return "Rainy"
    if lowered in ("snow",):
        return "Snowy"
    # Sensible default if we get an unknown condition.
    return "Sunny"


def _fallback_weather_label(d: date) -> str:
    """
    Fallback logic (if API fails):
    - Dec–Feb -> Snowy
    - Mar–May -> Cloudy
    - Jun–Sep -> Sunny/Rainy (deterministic)
    - Else -> Sunny
    """
    m = d.month
    if m in (12, 1, 2):
        return "Snowy"
    if m in (3, 4, 5):
        return "Cloudy"
    if m in (6, 7, 8, 9):
        # Deterministic alternation to avoid randomness across reruns.
        return "Rainy" if (d.day % 2 == 0) else "Sunny"
    return "Sunny"


@dataclass(frozen=True)
class StoreLocation:
    city: str = "New York"
    country: str = "US"
    lat: float = 40.7128
    lon: float = -74.0060


class WeatherProvider:
    """
    Fetches US store weather for a short planning horizon and maps it into
    the one-hot categories used by the ML model.

    Notes:
    - OpenWeatherMap free endpoints provide limited forecast horizons.
    - For dates outside the forecast window, we apply the deterministic fallback.
    """

    def __init__(self, location: StoreLocation, api_key: Optional[str]):
        self.location = location
        self.api_key = api_key

    @functools.lru_cache(maxsize=8)
    def _fetch_forecast(self) -> Optional[dict]:
        if not self.api_key:
            return None

        # 5-day / 3-hour forecast is commonly available.
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": self.location.lat,
            "lon": self.location.lon,
            "units": "imperial",
            "appid": self.api_key,
        }
        try:
            # Keep timeout low so the UI doesn't appear to "freeze".
            resp = requests.get(url, params=params, timeout=(3.5, 6))
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception:
            return None

    def condition_for_date(self, d: date) -> str:
        """
        Returns one of: Sunny, Rainy, Cloudy, Snowy
        """
        payload = self._fetch_forecast()
        if not payload:
            return _fallback_weather_label(d)

        # Forecast entries are in list['list'] with dt_txt like "2026-04-08 12:00:00"
        entries = payload.get("list") or []
        if not entries:
            return _fallback_weather_label(d)

        target = datetime(d.year, d.month, d.day).date()
        # Find entries that fall on target day.
        day_entries = []
        for e in entries:
            dt_txt = e.get("dt_txt")
            if not dt_txt:
                continue
            try:
                # dt_txt is ISO-ish.
                ts = datetime.fromisoformat(dt_txt)
            except Exception:
                continue
            if ts.date() == target:
                day_entries.append(e)

        if not day_entries:
            return _fallback_weather_label(d)

        # Prefer around noon if present, otherwise pick the closest timestamp.
        noon = datetime(d.year, d.month, d.day, 12, 0, 0)
        best = None
        best_dist = None
        for e in day_entries:
            dt_txt = e.get("dt_txt")
            if not dt_txt:
                continue
            try:
                ts = datetime.fromisoformat(dt_txt)
            except Exception:
                continue
            dist = abs((ts - noon).total_seconds())
            if best is None or dist < best_dist:
                best = e
                best_dist = dist

        if not best:
            return _fallback_weather_label(d)

        weather = (best.get("weather") or [{}])[0]
        main = weather.get("main") or ""
        return _owm_main_to_label(main)

