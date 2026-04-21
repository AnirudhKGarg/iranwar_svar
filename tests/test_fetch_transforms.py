import unittest

from src import fetch_eia, fetch_fred


class TestFetchTransforms(unittest.TestCase):
    def test_fred_date_format(self):
        self.assertEqual(fetch_fred._format_date("2026-01-09"), "01-09-2026")

    def test_eia_date_format_yyyymmdd(self):
        self.assertEqual(fetch_eia._normalize_date("20260109"), "01-09-2026")

    def test_eia_date_format_iso(self):
        self.assertEqual(fetch_eia._normalize_date("2026-01-09"), "01-09-2026")

    def test_fred_fx_row_assembly_with_missing_values(self):
        original_fetch = fetch_fred._fetch_series
        try:
            def fake_fetch(series_id, api_key):
                payloads = {
                    "DEXJPUS": [{"date": "2026-01-02", "value": "157.0"}],
                    "DEXUSAL": [{"date": "2026-01-02", "value": "."}],
                    "DEXUSEU": [{"date": "2026-01-02", "value": "0.93"}],
                    "DEXUSUK": [{"date": "2026-01-02", "value": "0.79"}],
                    "DEXNOUS": [{"date": "2026-01-02", "value": "10.5"}],
                }
                return payloads[series_id]

            fetch_fred._fetch_series = fake_fetch
            by_date = {}
            for label, series_id in fetch_fred.FX_SERIES.items():
                for obs in fetch_fred._fetch_series(series_id, "x"):
                    if obs["value"] in (None, "."):
                        continue
                    date_key = fetch_fred._format_date(obs["date"])
                    if date_key not in by_date:
                        by_date[date_key] = {"date": date_key}
                    by_date[date_key][label] = obs["value"]

            row = by_date["01-02-2026"]
            self.assertEqual(row["usd_jpy"], "157.0")
            self.assertNotIn("usd_aud", row)
            self.assertEqual(row["usd_eur"], "0.93")
        finally:
            fetch_fred._fetch_series = original_fetch


if __name__ == "__main__":
    unittest.main()
