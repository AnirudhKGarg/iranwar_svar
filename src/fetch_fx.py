"""Compatibility wrapper for fetching FRED FX data.

Use `python src/fetch_fred.py` for the full FRED pull.
"""

from fetch_fred import _require_api_key, export_fx


if __name__ == "__main__":
    export_fx(_require_api_key())
