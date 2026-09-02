# Sessions 8–12 — teaching plan (90 min × 5)

Instructor notes. Students never see this file. Aligns with [dashboard/BUILD_PLAN.md](../../dashboard/BUILD_PLAN.md).

**Room model:** you live-code the reference; they type along from a **Phase-0 stub** GitHub template. Almost no homework. First contact with `dashboard/` is session 8. **No student demos.** Accountability is the **final MCQ** only.

**Must have (everyone):** Stocks + Bonds running locally, plus a **class walkthrough** of Streamlit Cloud (they leave knowing the clicks; a personal public URL is success if they finish it, not a gate).

**Stretch:** Commodities and/or Currencies after Bonds is solid.

Do not live-code regime overlays, heatmaps, or Enes extras.

---

## Constraints this plan respects

| Choice | Implication |
|--------|-------------|
| In-class only | Each session ends with a **saved git commit** they can reopen next week. No “finish at home” as the design. |
| Live-code follow | You stay on the projector. Circulate only in the last 10–15 min. |
| Two tabs + deploy | Sessions 8–10 are the minimum path. 11 is stretch. 12 is Cloud. |
| No demos | Session 12 is not a showcase. Use the time for deploy + exam-shaped reading of *their* code. |
| Phase-0 stub | Stub has four empty `render()` pages, `pyproject.toml`, theme, `data/` seeds, tests folder optional/empty. |

**Campus:** same script in Lille and Sophia. If one room is slower, drop stretch (session 11) before dropping Bonds or Cloud.

---

## What you prepare once (before session 8)

- [ ] Publish the **student template** (Phase 0 only). Instructor `dashboard/` stays private.
- [ ] Clone the stub yourself and time a dry run of sessions 8 and 9 (aim: you can type the equities chart in &lt;25 min).
- [ ] Confirm `uv` + GitHub access on lab machines (or student laptops).
- [ ] Bookmark the instructor Cloud app as “what good looks like” — show it **once** at the start of session 8, then close it so they do not copy finished tabs.
- [ ] One-page cheat sheet (project in class): `uv sync`, `uv run streamlit run dashboard.py`, Streamlit reruns on save, `st.session_state` keys.

Students do **not** get `BUILD_PLAN.md`.

---

## Minimum vs stretch (say this in session 8)

**Minimum path — passing the room:** navigation works; S&P 500 chart + return tables; four FRED yield charts; you have seen Cloud deploy.

**Stretch path — if Bonds is done before the end of session 10, or during session 11:** commodities returns snapshot; then FX matrix. Skip FX if commodities is still messy.

Nobody is behind if they skip stretch. Final MCQ can still use snippets from `common.py` and equities/bonds.

---

## Session 8 (90 min) — Meet the app; one live chart

**Phases:** 0 (clone + run) and 1 (pipeline enough for a line).

**They leave with:** stub running; `download_data` + `preprocess` sketched; Stocks tab shows **one** Plotly series for `^GSPC` (lookback optional; returns tables **next week**).

| Min | You do | They do |
|----:|--------|---------|
| 0–10 | Why this project (4 tabs, ungraded, MCQ). Show instructor URL 60 seconds. Min vs stretch. | Listen |
| 10–25 | Clone template, `uv sync`, `uv run streamlit run dashboard.py`. Click four tabs. | Same on their machine |
| 25–35 | Streamlit mental model: script reruns; `st.Page`; sidebar vs main. | Follow; broken env → TA/you |
| 35–75 | Live-code `DATA_DIR`, load bundled `GSPC.csv`, `download_data` (live tail + merge, **do not write `data/`**), `preprocess`, one `plotly` line on equities | Type along |
| 75–85 | If Yahoo fails: show bundled fallback message. Commit: `session 8: S&P chart`. | Commit |
| 85–90 | Preview session 9 (returns + dates). No homework. | — |

**Drop if late:** live Yahoo. Bundled CSV only still counts.

**Do not start:** return tables, FRED, other tabs.

---

## Session 9 (90 min) — Stocks tab complete (minimum)

**Phase:** 2 frozen scope.

**They leave with:** lookback + start/end; trailing + calendar tables; extra history for 1y metrics; info banner when using bundled data.

| Min | You do | They do |
|----:|--------|---------|
| 0–8 | Re-run last week’s app. Fix clone/`uv` stragglers in the room, not as a lecture. | Open project |
| 8–25 | Sidebar: lookback presets, `lookback_start`, `date_range_error`. Prefixed keys later for bonds — today unprefixed is OK (matches reference equities). | Follow |
| 25–70 | `render_return_metrics`; fetch window vs chart window; Plotly layout helper. | Follow |
| 70–85 | Circulate. Pair the stuck with a neighbour who has a chart. | Catch-up |
| 85–90 | Commit `session 9: equities snapshot`. Next week = FRED, new keys `bonds_*`. | Commit |

**Drop if late:** polish (hover templates). Tables + chart are the win.

---

## Session 10 (90 min) — Bonds tab (minimum)

**Phase:** 4 frozen scope.

**They leave with:** `download_fred_data`; four charts; `bonds_` sidebar keys; OECD/tenor multiselect as in the reference (history filters only).

| Min | You do | They do |
|----:|--------|---------|
| 0–10 | FRED via `pandas_datareader`, **no API key**. Why bonds are not `yfinance`. | Listen |
| 10–40 | `download_fred_data` + bundled `DGS*` / `IRLTLT01*`. | Follow |
| 40–80 | Four charts in the same order as the reference (OECD snapshot → OECD history → Treasury curve → Treasury history). Multiselect last if time. | Follow |
| 80–90 | Commit `session 10: bonds`. Stretch people may peek at commodities **only after** four charts work. | Commit |

**Drop if late:** OECD history **or** Treasury history (keep one snapshot + one history). Stretch waits until session 11.

**Environment:** if FRED is blocked, bundled CSVs are the lesson — say that out loud (same as Cloud).

---

## Session 11 (90 min) — Stretch: Commodities, then FX

**Phase:** 5. **Minimum-path students:** tighten Stocks/Bonds (empty states, captions, “last updated”). That **is** valid use of the hour.

**Stretch order (do not reverse):** commodities first (reuses return tables + `download_data`), currencies second (new FX logic).

### If you stretch as a class (most of the room finished Bonds)

| Min | You do | They do |
|----:|--------|---------|
| 0–5 | Min vs stretch reminder. Nobody must finish FX. | — |
| 5–50 | Commodities: universe, `commodities_` keys, multiselect, 2×2 bar grids + per-name tables. | Follow or watch |
| 50–80 | Currencies: USD legs, `usd_per_unit`, matrix, one pair chart. Stop mid-function if needed. | Follow or watch |
| 80–90 | Commit whatever works. Session 12 = Cloud, not more features. | Commit |

### If half the room is still on Bonds

Live-code **only** commodities for 40 min as a demo they can paste later. Spend the rest circulating on Bonds. **Do not start FX.**

**Drop:** FX matrix click-to-select (selectboxes alone are enough). Bar-grid layout polish.

---

## Session 12 (90 min) — Deploy walkthrough; MCQ-shaped reading

**Phase:** 6. **No demos.**

**They leave with:** they have watched (and if possible performed) Cloud create-app; they know main file `dashboard/dashboard.py`, Python **3.12**, and that Yahoo often fails on Cloud so **bundled `data/`** matters. Optional: run `uv run pytest` once.

| Min | You do | They do |
|----:|--------|---------|
| 0–15 | Feature freeze. GitHub: repo public or Cloud-visible. Paths: Cloud runs from **repo root**. | Push if they have a remote |
| 15–50 | **You** share screen: [share.streamlit.io](https://share.streamlit.io/) → Create app → main file → 3.12. Use **one** student volunteer repo **or** the instructor repo. Read the build log when Yahoo/FRED fails. | Click along on their account if licenses/GitHub allow; otherwise watch and screenshot the settings |
| 50–75 | Code-reading: 10 minutes on `preprocess` / `download_data` / a Streamlit rerun gotcha — **exam flavour**, not a quiz handout. Tie to “explain every line.” | Read their own file |
| 75–90 | Troubleshooting table from [dashboard/DEPLOY.md](../../dashboard/DEPLOY.md). Close: project ungraded; **final MCQ** will quote this code. | — |

**Do not:** add features, start regime, require a unique URL per student.

If Cloud is down: local command from repo root (`uv run --project dashboard streamlit run dashboard/dashboard.py`) and call that the deploy rehearsal.

---

## Clock risks (what to cut first)

1. Session 11 FX  
2. Session 11 commodities bar grids (tables only)  
3. Session 10 second history chart  
4. Session 9 hover/CSS polish  
5. Never cut: session 8 running app, session 10 at least one FRED chart, session 12 Cloud clicks  

---

## Final MCQ (write during 8–11, not in class)

Draft in `project/mcq/` from **shipped** code: pandas slices, `@st.cache_data` if you used it, `yf.download` shape, `.ffill()`, FX `usd_per_unit` **only if** you taught it. **No** `classify_regime`.

---

## After the five sessions

- [ ] Student template vs this script still match (stub must run in session 8)  
- [ ] Syllabus sessions 8–12: single project + link to student README (not two-track valuation/structured products)  
- [ ] Root README: link to `dashboard/`  
