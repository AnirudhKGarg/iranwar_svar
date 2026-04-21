"""Fetch selected FRED datasets and export to CSV files in data/raw.

Required env var:
    FRED_API_KEY
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

REAL_GDP_SERIES_ID = "GDPC1"
FX_SERIES = {
    "usd_jpy": "DEXJPUS",
    "usd_aud": "DEXUSAL",
    "usd_eur": "DEXUSEU",
    "usd_gbp": "DEXUSUK",
    "usd_nok": "DEXNOUS",
}


def _require_api_key() -> str:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("Missing FRED_API_KEY environment variable.")
    return api_key


def _format_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%m-%d-%Y")


def _fetch_series(series_id: str, api_key: str) -> list[dict[str, str]]:
    params = {"series_id": series_id, "api_key": api_key, "file_type": "json"}
    url = f"{BASE_URL}?{urlencode(params)}"
    with urlopen(url) as response:  # nosec B310 - trusted HTTPS endpoint
        payload = json.loads(response.read().decode("utf-8"))
    if "error_message" in payload:
        raise RuntimeError(f"FRED error for {series_id}: {payload['error_message']}")
    return payload.get("observations", [])


def _write_csv(path: Path, rows: list[dict[str, str]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def export_real_gdp(api_key: str) -> None:
    rows: list[dict[str, str]] = []
    for obs in _fetch_series(REAL_GDP_SERIES_ID, api_key):
        value = obs.get("value")
        if value in (None, "."):
            continue
        rows.append(
            {
                "date": _format_date(obs["date"]),
                "real_gdp": str(value),
                "series_id": REAL_GDP_SERIES_ID,
            }
        )

    rows.sort(key=lambda row: datetime.strptime(row["date"], "%m-%d-%Y"))
    _write_csv(OUTPUT_DIR / "fred_real_gdp.csv", rows, ["date", "real_gdp", "series_id"])


def export_fx(api_key: str) -> None:
    by_date: dict[str, dict[str, str]] = {}

    for currency_label, series_id in FX_SERIES.items():
        for obs in _fetch_series(series_id, api_key):
            value = obs.get("value")
            if value in (None, "."):
                continue
            date_key = _format_date(obs["date"])
            if date_key not in by_date:
                by_date[date_key] = {"date": date_key}
            by_date[date_key][currency_label] = str(value)

    ordered_dates = sorted(by_date, key=lambda date: datetime.strptime(date, "%m-%d-%Y"))
    rows = [by_date[date] for date in ordered_dates]
    headers = ["date", *FX_SERIES.keys()]
    _write_csv(OUTPUT_DIR / "fred_fx_daily.csv", rows, headers)


def main() -> None:
    api_key = _require_api_key()
    export_real_gdp(api_key)
    export_fx(api_key)
    print(f"Saved FRED CSVs to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
