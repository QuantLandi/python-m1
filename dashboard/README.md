# Cross-Asset Market Monitor

Interactive Streamlit dashboard for stocks, bonds, commodities, and currencies. Built as the M1 **Python Programming for Finance** project (sessions 8–12).

## Live app

[Cross-Asset Market Monitor](https://python-m1-dashboard.streamlit.app/)

## Acknowledgement

This project is inspired by the [Cross-Asset Market Monitor](https://github.com/enesdesahin/market_dashboard) by Enes SAHIN. We reuse the overall architecture and design patterns; implementation is our own coursework.

## Setup

Requires [uv](https://docs.astral.sh/uv/). From this folder:

```bash
uv sync
```

## Tests

From this folder:

```bash
uv run pytest
```

## Launch

From this folder:

```bash
uv run streamlit run dashboard.py
```

From the repository root (matches Streamlit Cloud):

```bash
uv run --project dashboard streamlit run dashboard/dashboard.py
```

Streamlit opens in wide mode. Use the sidebar to switch between Stocks, Bonds, Commodities, and Currencies.

### Data refresh behavior

Each page renders its bundled CSV snapshot first, then refreshes the missing
Yahoo Finance or FRED tail in the background. Successful live snapshots remain
fresh for one hour and the previous snapshot stays visible while it is renewed.
If Yahoo's grouped request fails, missing tickers are retried concurrently with
at most four requests in flight; a failed refresh leaves bundled data visible.

## Deploy

See [DEPLOY.md](DEPLOY.md). On Streamlit Community Cloud, set **Main file path** to `dashboard/dashboard.py` and **Python** to `3.12`.

## Milestones

- [x] **Phase 0** — App shell with four navigable tabs
- [x] **Phase 1** — Data pipeline in `views/common.py` (`download_data`, `preprocess`)
- [x] **Phase 2** — Equities tab: S&P 500 levels, lookback, trailing and calendar returns (scope frozen)
- [x] **Phase 3** — Dropped (no regime overlays)
- [x] **Phase 4** — Bonds tab: US curve + OECD 10Y (pandas_datareader / FRED; scope frozen)
- [x] **Phase 5 (Commodities)** — Futures returns snapshot: tables + 2×2 bar grids (scope frozen)
- [x] **Phase 5 (Currencies)** — G8 spot-cross matrix and pair path (scope frozen)
- [x] **Phase 6** — Tests, polish, Streamlit Cloud deploy

See [BUILD_PLAN.md](BUILD_PLAN.md) for the full instructor build plan.

## Project layout

| Path | Purpose |
|------|---------|
| `dashboard.py` | Entry point — Streamlit navigation |
| `views/common.py` | Shared loaders, lookback and chart helpers |
| `tests/` | Smoke tests for loaders and date helpers |
| `views/equities.py` | Stocks tab (S&P 500 snapshot) |
| `views/bonds.py` | Bonds tab (Treasury curve + OECD 10Y) |
| `views/commodities.py` | Commodities tab (futures returns snapshot) |
| `views/currencies.py` | Currencies tab |
| `data/` | Bundled CSV fallbacks (S&P 500, commodity futures, FRED yields, FX USD legs) |
| `.streamlit/config.toml` | Dark theme and styling |

## AI policy

Same as the course README: AI is OK if you can **explain every line** of your code. Exams test code reading without AI.
