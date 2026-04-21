# iranwar_svar

This repository contains scripts and notebooks for analyzing energy prices and macro series.

## Data pull scripts

The scripts below export CSV files into `data/raw`.

### 1) FRED (Real GDP + FX)

Required env var:

- `FRED_API_KEY`

Run:

```bash
python src/fetch_fred.py
```

Outputs:

- `data/raw/fred_real_gdp.csv` with columns: `date`, `real_gdp`, `series_id`
- `data/raw/fred_fx_daily.csv` with columns: `date`, `usd_jpy`, `usd_aud`, `usd_eur`, `usd_gbp`, `usd_nok`

FRED FX series used:

- `DEXJPUS` (USD/JPY)
- `DEXUSAL` (USD/AUD)
- `DEXUSEU` (USD/EUR)
- `DEXUSUK` (USD/GBP)
- `DEXNOUS` (USD/NOK)

### 2) EIA (WTI, Brent, Henry Hub)

Required env var:

- `EIA_API_KEY`

Run:

```bash
python src/fetch_eia.py
```

Output:

- `data/raw/eia_energy_prices.csv` with columns: `date`, `wti`, `brent`, `henry_hub`

EIA series IDs used:

- `PET.RWTC.D` (WTI)
- `PET.RBRTE.D` (Brent)
- `NG.RNGWHHD.D` (Henry Hub)

## Date format

Both FRED and EIA exports normalize dates to `MM-DD-YYYY`.
