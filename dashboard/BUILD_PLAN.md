# Build plan — Cross-Asset Market Monitor

Private instructor plan for the M1 project deliverable. Students receive a separate template repo derived from this folder once Phase 0 is complete.

**Model:** inspired by [market_dashboard](https://github.com/enesdesahin/market_dashboard) by Enes SAHIN (cite in student README).

---

## Assessment & constraints

| Decision | Choice |
|----------|--------|
| Grading | **Not graded** — accountability via **MCQ final** (project-specific code-reading questions) |
| Work mode | **Individual**; same brief for Lille & Sophia |
| Demo | **Mandatory** live demo in session 12 (2–3 min) |
| Scope | **4 tabs** (Stocks, Bonds, Commodities, Currencies) + **regime overlays** |
| Data | Live `yfinance` + **FRED via pandas_datareader** (no API key); bundled `data/` CSV fallbacks |
| Deploy | **Streamlit Cloud** (public URL) |
| AI policy | Same as course README — OK if you can explain every line |
| Differentiation | None — one project for everyone |

---

## Folder location

Everything students build lives in `dashboard/` at the repo root. The folder is self-contained (own `pyproject.toml`) so it can be copied to a separate GitHub template repo later.

```
python-m1/                          # instructor repo
├── syllabus.md
├── instructor-guide.md
├── quizzes/
├── slides/
├── project/                        # teaching notes (outside deliverable)
│   ├── session-plans/
│   └── mcq/
└── dashboard/                      # ← the deliverable
    ├── BUILD_PLAN.md               # this file (instructor)
    ├── pyproject.toml
    ├── README.md                   # student brief + milestones
    ├── dashboard.py
    ├── views/
    ├── data/                       # bundled GSPC + FRED CSVs
    ├── .streamlit/
    └── tests/
```

**Run from `dashboard/`:**

```bash
uv sync
uv run streamlit run dashboard.py
```

---

## Target deliverable

| Component | File(s) | Done when |
|-----------|---------|-----------|
| App shell | `dashboard.py` | 4-tab `st.navigation` works |
| Shared layer | `views/common.py` | Loaders, regime engine, Plotly helpers |
| Stocks tab | `views/equities.py` | S&P 500 levels + trailing/calendar returns (scope frozen; see below) |
| Bonds tab | `views/bonds.py` | US Treasury curve + OECD 10Y (pandas_datareader / FRED; scope frozen) |
| Commodities tab | `views/commodities.py` | Metals, energy, grains charts |
| Currencies tab | `views/currencies.py` | FX pairs + correlation heatmap |
| Offline fallback | `data/` | Stocks + bonds work without internet (`GSPC.csv`, FRED series) |
| Theme | `.streamlit/config.toml` | Dark theme, orange accent |
| Tests | `tests/test_loaders.py` | Smoke tests on core helpers |
| Deploy | Streamlit Cloud | Public URL |

---

## Implementation phases

Build in **6 phases**. Each phase ends with something runnable or testable.

### Phase 0 — Scaffold

**Goal:** app launches; four tabs navigate; no data yet.

| File | Contents |
|------|----------|
| `pyproject.toml` | `streamlit`, `pandas`, `numpy`, `plotly`, `yfinance`, `requests`, `pytest` |
| `dashboard.py` | `st.set_page_config` + `st.navigation` wiring 4 pages |
| `views/equities.py` … `currencies.py` | `render()` with header + placeholder |
| `views/common.py` | Empty module + docstring listing planned functions |
| `.streamlit/config.toml` | Dark theme, orange accent |
| `.gitignore` | `__pycache__/`, `.env` |
| `README.md` | Acknowledgement, setup, launch command, milestone checklist |

**Exit criterion:** `uv run streamlit run dashboard.py` — clicking each tab switches pages.

**Session:** 8 (first 15 min).

---

### Phase 1 — Data pipeline

**Goal:** one function fetches live prices and merges them in memory with bundled CSVs.

Implement in `views/common.py`, in order:

1. `DATA_DIR`, `_load_bundled_series()`
2. `download_data(tickers, start, end)` — `yfinance` tail from the latest bundled date; do not write `data/`
3. `preprocess()`
4. Shared `lookback_start()` / `date_range_error()` / `chart_layout()`

**Exit criterion:** equities tab shows one Plotly line chart of live S&P 500 (`^GSPC`) prices.

**Session:** 8.

---

### Phase 2 — Equities tab (S&P 500 snapshot)

**Goal:** first complete tab. **This scope is frozen** — do not expand toward Enes’ multi-name watchlist.

The Stocks tab is an **index snapshot**, not a relative-performance dashboard:

1. Single series: `^GSPC` (S&P 500), live `yfinance` with bundled `data/GSPC.csv` fallback
2. Sidebar: lookback presets (`1y` … `max`) plus start/end dates
3. Trailing returns (1d / 7d / 30d / 90d / 1y) and calendar returns (WTD / MTD / QTD / YTD)
4. One Plotly **index-level** chart (not normalized multi-asset)
5. Fetch extra history so 1-year trailing metrics still work on a short chart window

**Out of scope** (reference repo only; do not implement): ticker multiselect, Top Gainers, normalized overlay, rolling vol / drawdown tabs, correlation heatmap, Sharpe table, CSV download, regime toggle on this tab.

**Exit criterion:** lookback + date range drive the chart; both return tables render; bundled fallback works if Yahoo is down.

**Session:** 9.

---

### Phase 3 — Regime engine

**Goal:** macro overlays work on any tab.

In `views/common.py`:

1. `REGIME_COLORS`, `REGIME_ACCENTS`, `REGIME_DESCRIPTIONS`
2. `classify_regime(growth, inflation, vol)`
3. `get_market_regime_data()` — ^GSPC, ^VIX, CL=F proxies
4. `add_regime_shading()`, `render_regime_status_panel()`, `render_regime_legend()`
5. Wire regime toggle on **commodities or currencies** (not equities or bonds)

**Exit criterion:** toggle on → shaded chart + regime badge in sidebar on a non-equities tab.

**Session:** 10 (first half).

---

### Phase 4 — Bonds tab (yield curves)

**Goal:** second tab with live FRED yields. **This scope is frozen.**

Uses `pandas_datareader` (`DataReader(..., "fred")`) — **no FRED API key**.

1. `download_fred_data()` in `views/common.py` — same bundled CSV fallback as Yahoo prices
2. Four charts only:
   - latest OECD 10Y bar chart
   - latest US Treasury curve by tenor
   - OECD 10Y history
   - US Treasury history
3. Sidebar lookback + start/end dates (keys prefixed `bonds_` so they do not clash with Stocks)

**Out of scope:** series multiselect, top movers, spreads, vol surface, correlation, CSV download, regime overlay, FRED API key.

**Exit criterion:** all four charts render from live FRED; bundled `data/DGS*.csv` and `data/IRLTLT01*.csv` cover offline.

**Session:** 10.

---

### Phase 5 — Commodities & Currencies tabs

**Goal:** remaining asset-class tabs; reuse `common.py` (do not clone the slim equities snapshot).

1. `commodities.py` — metals, energy, grains ticker maps + tab-specific charts
2. `currencies.py` — FX pairs, normalized scores, correlation heatmap
3. Both reuse `common.py` helpers (no duplicated download logic)
4. Regime overlay optional, following Phase 3 — still not on equities

**Exit criterion:** all 4 tabs functional with live data.

**Session:** 11.

---

### Phase 6 — Tests, polish, deploy

1. `tests/test_loaders.py` — smoke tests on `preprocess`, disk fallback, date helpers
2. `.streamlit/config.toml` — dark theme, orange accent (no custom font bundle)
3. Bundled `data/` CSVs: `GSPC.csv` plus all Treasury (`DGS*`) and OECD 10Y (`IRLTLT01*`) series
4. Streamlit Cloud deploy
5. README: deploy steps + demo checklist

**Exit criterion:** public URL; student demos 2 tabs + explains one function.

**Session:** 12.

---

## Build order

```
Phase 0 (scaffold)
    → Phase 1 (data pipeline)
        → Phase 2 (equities)
            → Phase 3 (regime)
                → Phase 4 (bonds)
                → Phase 5 (commodities + FX)   ← can parallelise after Phase 3
                    → Phase 6 (deploy)
```

Phases 4 and 5 can overlap once Phase 3 is done.

---

## Session map (8–12)

| Session | Phase(s) | Student outcome |
|--------:|----------|-----------------|
| 8 | 0, 1 | App runs; equities shows one live chart |
| 9 | 2 | Equities tab complete (S&P 500 snapshot) |
| 10 | 3, 4 | Regime overlays + bonds tab |
| 11 | 5 | Commodities + currencies tabs |
| 12 | 6 | Deployed app + live demos |

Assume **30–60 min prep** before each session (linked from `README.md`).

---

## Student template vs instructor copy

| | Student template repo | Instructor `dashboard/` |
|--|----------------------|-------------------------|
| Phase 0 | Scaffold with stubs only | Build here first |
| Phases 1–6 | Students implement | Reference solution |
| `project/session-plans/` | Not included | Per-session teaching notes |
| `project/mcq/` | Not included | Draft final exam items |
| `BUILD_PLAN.md` | Not included | This file |

When ready: publish Phase-0-only scaffold as the student template; keep the full solution private.

---

## MCQ final — project questions

Aim for **8–12 questions** out of 40, same format as course quizzes (snippet + 5 T/F).

| Topic bucket | Example patterns |
|--------------|------------------|
| pandas time series | `.pct_change()`, `.rolling()`, index slicing |
| caching | `@st.cache_data`, behaviour on second run |
| data loading | `yf.download` return shape, empty DataFrame handling |
| functions | `classify_regime()` — trace branches |
| regime logic | `add_regime_shading` loop |
| mutations | `.ffill()` return vs in-place |

Draft items in `project/mcq/project-final-items.md` during sessions 8–11. Run every snippet before adding.

---

## Dependencies (`pyproject.toml`)

```toml
dependencies = [
    "numpy>=2.5",
    "pandas>=3.0",
    "pandas-datareader>=0.10",
    "plotly>=6.0",
    "requests>=2.32",
    "streamlit>=1.40",
    "yfinance>=0.2",
]

[dependency-groups]
dev = ["pytest>=8.0"]
```

---

## Citation (student `README.md`)

```markdown
## Acknowledgement

This project is inspired by the [Cross-Asset Market Monitor](https://github.com/enesdesahin/market_dashboard)
by Enes SAHIN. We reuse the overall architecture and design patterns; implementation is our own coursework.
```

---

## Risk register

| Risk | Mitigation |
|------|------------|
| Reference too large for beginners | Equities stays a slim S&P 500 view; richer analytics live on other tabs |
| AI-generated submissions | Ungraded + MCQ + live demo (explain one function) |
| FRED key friction | Use `pandas_datareader` public FRED feed (no key) |
| yfinance / FRED outages | Bundled `data/` (GSPC + FRED) |
| Deploy failures on session 12 | Front-load deploy walkthrough; troubleshoot in room |

---

## Repo hygiene

- Update `syllabus.md`: replace two-track paragraph with single project + link to `dashboard/README.md`
- Update root `README.md`: one row pointing to `dashboard/`
- Commit `data/` seeds; never rewrite them at runtime

---

## Next step

Implement **Phase 5** — commodities and currencies tabs (reuse `common.py`). Regime overlays (Phase 3) stay deferred until one of those tabs exists.
