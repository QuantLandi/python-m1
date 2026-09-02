from datetime import timedelta

import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DATA_CACHE_DIR,
    DATA_DIR,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    download_data,
    get_available_date_bounds,
    normalize,
    preprocess,
)

SP500_TICKER = "^GSPC"
DEFAULT_LOOKBACK_DAYS = 365


def render() -> None:
    st.header(":material/table_chart_view: Stocks")
    st.caption("Integrated stock analytics covering flagship single names.")

    bounds = get_available_date_bounds(SP500_TICKER)
    earliest_date = bounds[0] if bounds else DEFAULT_START_DATE
    default_start = max(earliest_date, DEFAULT_END_DATE - timedelta(days=DEFAULT_LOOKBACK_DAYS))

    with st.sidebar:
        start_date = st.date_input(
            "Start date",
            value=default_start,
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
        )
        end_date = st.date_input(
            "End date",
            value=DEFAULT_END_DATE,
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
        )

    if start_date > end_date:
        st.warning("Start date must be on or before the end date.")
        return

    if start_date == end_date:
        st.warning("Date range must span at least two distinct dates.")
        return

    prices = download_data((SP500_TICKER,), start_date, end_date, use_live=True)
    prices = preprocess(prices)

    if prices.empty:
        st.error(
            "No data returned for the S&P 500. "
            "Yahoo Finance may be unavailable from this server — bundled fallback data is missing too."
        )
        return

    cache_file = DATA_CACHE_DIR / f"{SP500_TICKER.replace('^', '').replace('=', '_')}.csv"
    bundled_file = DATA_DIR / f"{SP500_TICKER.replace('^', '').replace('=', '_')}.csv"
    if not cache_file.exists() and bundled_file.exists():
        st.info("Showing bundled S&P 500 data (live Yahoo Finance fetch unavailable).")

    st.sidebar.caption(f"Last updated: {prices.index[-1].strftime('%Y-%m-%d')}")

    normalized = normalize(prices)
    series = normalized[SP500_TICKER]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series,
            mode="lines",
            name="S&P 500",
            line=dict(width=2, color="#FF962F"),
            hovertemplate="%{y:.2f}x %{x|%Y-%m-%d}<extra>S&P 500</extra>",
        )
    )
    fig.update_layout(
        title="S&P 500 — Normalized Performance",
        height=450,
        template="plotly_white",
        yaxis_title="Cumulative Return (×)",
        xaxis_title="Date",
        hovermode="x unified",
        margin=dict(t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Normalized cumulative returns"):
        st.dataframe(normalized.style.format("{:.2f}"))


render()
