# Deploy to Streamlit Community Cloud

The app lives in a subdirectory of the instructor repo. Streamlit Cloud runs from the **repository root**, so paths in `dashboard.py` are absolute relative to that file.

## Prerequisites

1. Code pushed to GitHub (`QuantLandi/python-m1`)
2. [Streamlit Community Cloud](https://share.streamlit.io/) account linked to GitHub

## One-time setup

1. Open [share.streamlit.io](https://share.streamlit.io/) → **Create app**
2. **Repository:** `QuantLandi/python-m1`
3. **Branch:** `main`
4. **Main file path:** `dashboard/dashboard.py`
5. **Python version:** `3.12` (do not use 3.14 — not yet supported on Cloud)

Streamlit Cloud will detect dependencies from `dashboard/uv.lock` (preferred) or `dashboard/requirements.txt`.

## Secrets (later phases)

When the bonds tab uses FRED, add in the app **Settings → Secrets**:

```toml
FRED_API_KEY = "your-key-here"
```

Never commit API keys to git.

## After each push

Community Cloud rebuilds automatically when `main` changes. Check the deploy log if the app fails to start.

## Local smoke test (same as Cloud)

From the **repository root**:

```bash
uv run --project dashboard streamlit run dashboard/dashboard.py
```

From the `dashboard/` folder (local dev):

```bash
uv sync
uv run streamlit run dashboard.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Module not found | Confirm `dashboard/uv.lock` is committed |
| Wrong Python version | Set 3.12 in Cloud app settings |
| Theme missing on Cloud | Root `.streamlit/config.toml` must exist |
| Page not found | `dashboard.py` uses `Path(__file__).parent` for view paths |
