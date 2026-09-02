"""Shared helpers for the Cross-Asset Market Monitor.

Planned functions (implement in Phases 1–3):

Data pipeline (Phase 1)
    download_data       Fetch prices via yfinance with CSV cache fallback
    load_data           Load a price series from disk
    preprocess          Forward-fill and drop missing values
    ensure_datetime_index
    normalize           Cumulative return index starting at 1

Regime engine (Phase 3)
    classify_regime
    get_market_regime_data
    add_regime_shading
    render_regime_status_panel
    render_regime_legend
    filter_by_regime
    regime_options
"""
