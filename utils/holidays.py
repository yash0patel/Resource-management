from __future__ import annotations

import functools
from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple


@dataclass(frozen=True)
class HolidayInfo:
    holiday_flag: int
    holiday_name: Optional[str]


def _matches_supported_holiday_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None

    lowered = name.lower()
    supported = {
        "new year": "New Year's Day",
        "independence day": "Independence Day",
        "thanksgiving": "Thanksgiving",
        "christmas": "Christmas",
        "labor day": "Labor Day",
    }

    for key, label in supported.items():
        if key in lowered:
            return label
    return None


@functools.lru_cache(maxsize=64)
def get_us_holiday_info(d: date) -> HolidayInfo:
    """
    Detect supported US holidays using `holidays` library.
    If the library is not installed, returns non-holiday fallback (0).
    """
    try:
        import holidays  # type: ignore
    except Exception:
        return HolidayInfo(holiday_flag=0, holiday_name=None)

    us_holidays = holidays.UnitedStates(years=d.year)
    name = us_holidays.get(d)
    matched = _matches_supported_holiday_name(name)
    return HolidayInfo(holiday_flag=1 if matched else 0, holiday_name=matched)


def holiday_promotion_feature(d: date, apply_promotion: bool) -> Tuple[int, int, Optional[str]]:
    """
    Model feature contract:
    - Holiday/Promotion is 1 if either the day is a supported US holiday OR a promotion toggle is applied.
    - Holiday itself is the raw holiday indicator (1/0) before promotion override.
    """
    info = get_us_holiday_info(d)
    holiday_flag = int(info.holiday_flag)
    holiday_promo_flag = 1 if apply_promotion else holiday_flag
    return holiday_flag, holiday_promo_flag, info.holiday_name

