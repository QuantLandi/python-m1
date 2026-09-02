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

## Launch (local)

From this folder:

```bash
uv run streamlit run dashboard.py
```

From the repository root (matches Streamlit Cloud):

```bash
uv run --project dashboard streamlit run dashboard/dashboard.py
```

Streamlit opens in wide mode. Use the sidebar to switch between Stocks, Bonds, Commodities, and Currencies.

## Deploy

See [DEPLOY.md](DEPLOY.md). On Streamlit Community Cloud, set **Main file path** to `dashboard/dashboard.py` and **Python** to `3.12`.

## Milestones

- [x] **Phase 0** — App shell with four navigable tabs
- [x] **Phase 1** — Data pipeline in `views/common.py` (`download_data`, `preprocess`, `normalize`)
- [ ] **Phase 2** — Equities tab complete (charts, metrics, CSV export)
- [ ] **Phase 3** — Regime overlays and badges
- [ ] **Phase 4** — Bonds tab (FRED API)
- [ ] **Phase 5** — Commodities and Currencies tabs
- [ ] **Phase 6** — Tests, polish, Streamlit Cloud deploy

See [BUILD_PLAN.md](BUILD_PLAN.md) for the full instructor build plan.

## Project layout

| Path | Purpose |
|------|---------|
| `dashboard.py` | Entry point — Streamlit navigation |
| `views/common.py` | Shared loaders, caching, regime helpers |
| `views/equities.py` | Stocks tab |
| `views/bonds.py` | Bonds tab |
| `views/commodities.py` | Commodities tab |
| `views/currencies.py` | Currencies tab |
| `data/` | Bundled CSV fallbacks (offline mode) |
| `data_cache/` | Auto-generated cache (not committed) |
| `.streamlit/config.toml` | Dark theme and styling |

## AI policy

Same as the course README: AI is OK if you can **explain every line** of your code. Exams test code reading without AI.
