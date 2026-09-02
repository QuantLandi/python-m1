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
| Data | Live `yfinance` + **FRED** (bonds); bundled `data/` CSV fallbacks |
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
    ├── data/
    ├── data_cache/                 # gitignored
    ├── static/
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
| Shared layer | `views/common.py` | Loaders, cache, regime engine, Plotly helpers |
| Stocks tab | `views/equities.py` | Full analytics + regime toggle |
| Bonds tab | `views/bonds.py` | FRED yield curve + spreads |
| Commodities tab | `views/commodities.py` | Metals, energy, grains charts |
| Currencies tab | `views/currencies.py` | FX pairs + correlation heatmap |
| Offline fallback | `data/` | App works without internet |
| Cache | `data_cache/` | Live fetches persist between runs |
| Theme | `.streamlit/config.toml`, `static/` | Dark theme, orange accent |
| Tests | `tests/test_loaders.py` | Smoke tests on core helpers |
| Deploy | Streamlit Cloud | Public URL + `FRED_API_KEY` in secrets |

---

## Implementation phases

Build in **6 phases**. Each phase ends with something runnable or testable.

### Phase 0 — Scaffold

**Goal:** app launches; four tabs navigate; no data yet.

| File | Contents |
|------|----------|
| `pyproject.toml` | `streamlit`, `pandas`, `numpy`, `plotly`, `yfinance`, `matplotlib`, `requests`, `pytest` |
| `dashboard.py` | `st.set_page_config` + `st.navigation` wiring 4 pages |
| `views/equities.py` … `currencies.py` | `render()` with header + placeholder |
| `views/common.py` | Empty module + docstring listing planned functions |
| `.streamlit/config.toml` | Dark theme, orange accent |
| `.gitignore` | `data_cache/`, `__pycache__/`, `.env` |
| `README.md` | Acknowledgement, setup, launch command, milestone checklist |

**Exit criterion:** `uv run streamlit run dashboard.py` — clicking each tab switches pages.

**Session:** 8 (first 15 min).

---

### Phase 1 — Data pipeline

**Goal:** one function fetches live prices and caches to disk.

Implement in `views/common.py`, in order:

1. `DATA_CACHE_DIR`, `_cache_path()`
2. `download_data(tickers, start, end)` — `yfinance` + CSV cache merge
3. `load_data()`, `preprocess()`, `ensure_datetime_index()`
4. `normalize()` — cumulative return index starting at 1

**Exit criterion:** equities tab shows one Plotly line chart of live AAPL prices.

**Session:** 8.

---

### Phase 2 — Equities tab (full)

**Goal:** first complete tab — template for the other three.

1. `STOCK_TICKERS`, `COLOR_PALETTE` constants
2. Sidebar: multiselect, date range
3. `load_equity_prices()` (cached wrapper)
4. `compute_metrics()` — returns, vol, Sharpe, drawdown
5. Plotly charts: normalized performance, rolling vol, drawdown, correlation heatmap
6. Top Gainers cards, metrics table, CSV download

**Exit criterion:** equities tab matches reference feature set (without regime toggle).

**Session:** 9.

---

### Phase 3 — Regime engine

**Goal:** macro overlays work on any tab.

In `views/common.py`:

1. `REGIME_COLORS`, `REGIME_ACCENTS`, `REGIME_DESCRIPTIONS`
2. `classify_regime(growth, inflation, vol)`
3. `get_market_regime_data()` — ^GSPC, ^VIX, CL=F proxies
4. `add_regime_shading()`, `render_regime_status_panel()`, `render_regime_legend()`
5. Wire regime toggle on equities tab

**Exit criterion:** toggle on → shaded chart + regime badge in sidebar.

**Session:** 10 (first half).

---

### Phase 4 — Bonds tab (+ FRED)

**Goal:** second tab with live macro data.

1. FRED API helper (env var `FRED_API_KEY`)
2. US Treasury yield curve chart
3. OECD 10Y peer comparison (CSV endpoint)
4. Spread / vol surface views (as in reference)
5. Reuse regime overlay from Phase 3

Document FRED key setup in README (local `.env` + Streamlit Cloud secrets).

**Exit criterion:** bonds tab loads live yields; works offline via `data/` fallback.

**Session:** 10 (second half).

---

### Phase 5 — Commodities & Currencies tabs

**Goal:** copy the equities pattern; prove modularity.

1. `commodities.py` — metals, energy, grains ticker maps + tab-specific charts
2. `currencies.py` — FX pairs, normalized scores, correlation heatmap
3. Both reuse `common.py` helpers (no duplicated download logic)

**Exit criterion:** all 4 tabs functional with live data.

**Session:** 11.

---

### Phase 6 — Tests, polish, deploy

1. `tests/test_loaders.py` — smoke tests on `preprocess`, `normalize`, `classify_regime`
2. `static/` fonts + full `.streamlit/config.toml` (match reference branding)
3. Bundled `data/` CSVs for offline demo
4. Streamlit Cloud deploy; `FRED_API_KEY` in secrets
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
| 9 | 2 | Equities tab complete |
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
    "matplotlib>=3.9",
    "numpy>=2.5",
    "pandas>=3.0",
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
| Reference too large for beginners | Milestone gates; equities first, then copy pattern |
| AI-generated submissions | Ungraded + MCQ + live demo (explain one function) |
| FRED key friction | Class setup in session 10; document Streamlit secrets |
| yfinance outages | Bundled `data/` + `data_cache/` fallback |
| Deploy failures on session 12 | Front-load deploy walkthrough; troubleshoot in room |

---

## Repo hygiene

- Root `.gitignore`: add `dashboard/data_cache/`
- Update `syllabus.md`: replace two-track paragraph with single project + link to `dashboard/README.md`
- Update root `README.md`: one row pointing to `dashboard/`
- Never commit FRED API keys or live cache files

---

## Next step

Implement **Phase 0** only — scaffold, stubs, theme, README. Verify the app launches before starting Phase 1.
