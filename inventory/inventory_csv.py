from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd


INVENTORY_LOG_PATH = Path("single_store_inventory.csv")

INVENTORY_LOG_COLUMNS = [
    "Date",
    "Inventory Level",
    "Units Sold",
    "Category",
    "Region",
    "Weather Condition",
    "Holiday",
    "Holiday/Promotion",
]


def ensure_inventory_log_exists(path: Path = INVENTORY_LOG_PATH) -> None:
    if path.exists():
        return
    df = pd.DataFrame(columns=INVENTORY_LOG_COLUMNS)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def append_inventory_row(
    *,
    d: date,
    inventory_level: float,
    units_sold: float,
    category: str,
    region: str,
    weather_condition: str,
    holiday_flag: int,
    holiday_promotion_flag: int,
    path: Path = INVENTORY_LOG_PATH,
) -> None:
    """
    Append a single daily inventory update row.
    """
    ensure_inventory_log_exists(path)

    row = {
        "Date": d.isoformat(),
        "Inventory Level": float(inventory_level),
        "Units Sold": float(units_sold),
        "Category": category,
        "Region": region,
        "Weather Condition": weather_condition,
        "Holiday": int(holiday_flag),
        "Holiday/Promotion": int(holiday_promotion_flag),
    }
    df = pd.DataFrame([row])

    # Safe-ish append for Streamlit single-user scenario.
    df.to_csv(path, mode="a", header=False, index=False)


def load_inventory_log(path: Path = INVENTORY_LOG_PATH) -> pd.DataFrame:
    ensure_inventory_log_exists(path)
    df = pd.read_csv(path)
    if not df.empty and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

