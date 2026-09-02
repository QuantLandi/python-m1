from datetime import timedelta

import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    download_data,
    normalize,
    preprocess,
)

SP500_TICKER = "^GSPC"
DEFAULT_LOOKBACK_DAYS = 365


def render() -> None:
    st.header(":material/table_chart_view: Stocks")
    st.caption("Integrated stock analytics covering flagship single names.")

    default_start = max(DEFAULT_START_DATE, DEFAULT_END_DATE - timedelta(days=DEFAULT_LOOKBACK_DAYS))

    with st.sidebar:
        date_range = st.date_input(
            "Date range",
            value=(default_start, DEFAULT_END_DATE),
            min_value=DEFAULT_START_DATE,
            max_value=DEFAULT_END_DATE,
        )

    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        st.warning("Please select both a start and an end date.")
        return

    start_date, end_date = sorted(date_range)
    if start_date == end_date:
        st.warning("Date range must span at least two distinct dates.")
        return

    prices = download_data((SP500_TICKER,), start_date, end_date, use_live=True)
    prices = preprocess(prices)

    if prices.empty:
        st.error("No data returned for the S&P 500. Check your connection and try again.")
        return

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
