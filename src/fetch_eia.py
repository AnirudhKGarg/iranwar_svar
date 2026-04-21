"""Fetch selected EIA price series and export CSV to data/raw.

Required env var:
    EIA_API_KEY
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BASE_URL = "https://api.eia.gov/series/"
OUTPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "eia_energy_prices.csv"

SERIES = {
    "wti": "PET.RWTC.D",
    "brent": "PET.RBRTE.D",
    "henry_hub": "NG.RNGWHHD.D",
}


def _require_api_key() -> str:
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        raise RuntimeError("Missing EIA_API_KEY environment variable.")
    return api_key


def _normalize_date(raw: str) -> str:
    if "-" in raw:
        dt = datetime.strptime(raw, "%Y-%m-%d")
    else:
        dt = datetime.strptime(raw, "%Y%m%d")
    return dt.strftime("%m-%d-%Y")


def _fetch_series(series_id: str, api_key: str) -> list[list[str]]:
    params = {"api_key": api_key, "series_id": series_id}
    with urlopen(f"{BASE_URL}?{urlencode(params)}") as response:  # nosec B310
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("error"):
        raise RuntimeError(f"EIA error for {series_id}: {payload['error']}")

    series_list = payload.get("series", [])
    if not series_list:
        return []
    return series_list[0].get("data", [])


def main() -> None:
    api_key = _require_api_key()
    by_date: dict[str, dict[str, str]] = {}

    for label, series_id in SERIES.items():
        for point in _fetch_series(series_id, api_key):
            if len(point) < 2:
                continue
            raw_date, value = point[0], point[1]
            if value in (None, "."):
                continue
            date = _normalize_date(str(raw_date))
            if date not in by_date:
                by_date[date] = {"date": date}
            by_date[date][label] = str(value)

    ordered_dates = sorted(by_date, key=lambda date: datetime.strptime(date, "%m-%d-%Y"))
    rows = [by_date[date] for date in ordered_dates]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=["date", *SERIES.keys()])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved EIA CSV to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
