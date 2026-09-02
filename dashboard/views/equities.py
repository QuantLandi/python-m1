from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    LOOKBACK_YEARS,
    chart_layout,
    date_range_error,
    download_data,
    get_available_date_bounds,
    lookback_start,
    preprocess,
    render_return_metrics,
)

SP500_TICKER = "^GSPC"


def render() -> None:
    st.header(":material/table_chart_view: Stocks")

    bounds = get_available_date_bounds(SP500_TICKER)
    if bounds is None:
        st.sidebar.warning("Bundled S&P 500 history file missing — date range may be limited.")
    earliest_date = bounds[0] if bounds else DEFAULT_START_DATE

    def _apply_lookback() -> None:
        end = DEFAULT_END_DATE
        years = LOOKBACK_YEARS[st.session_state.lookback]
        st.session_state.end_date = end
        st.session_state.start_date = lookback_start(end, years, earliest_date)

    if "lookback" not in st.session_state:
        st.session_state.lookback = "1y"
    if "start_date" not in st.session_state or "end_date" not in st.session_state:
        _apply_lookback()

    with st.sidebar:
        st.selectbox(
            "Lookback",
            list(LOOKBACK_YEARS),
            key="lookback",
            on_change=_apply_lookback,
        )
        start_date = st.date_input(
            "Start date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="start_date",
        )
        end_date = st.date_input(
            "End date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="end_date",
        )

    range_error = date_range_error(start_date, end_date)
    if range_error:
        st.warning(range_error)
        return

    metrics_start = max(earliest_date, end_date - timedelta(days=365 + 21))
    fetch_start = min(start_date, metrics_start)
    prices = download_data((SP500_TICKER,), fetch_start, end_date, use_live=True)
    prices = preprocess(prices)

    if prices.empty:
        st.error(
            "No data returned for the S&P 500. "
            "Yahoo Finance may be unavailable from this server — bundled fallback data is missing too."
        )
        return

    chart_mask = (prices.index >= pd.Timestamp(start_date)) & (
        prices.index <= pd.Timestamp(end_date)
    )
    chart_prices = prices.loc[chart_mask]
    if chart_prices.empty:
        st.warning("No observations in the selected date range.")
        return

    bundled_latest = get_available_date_bounds(SP500_TICKER)
    if (
        bundled_latest is not None
        and prices.index[-1].date() <= bundled_latest[1] < end_date
    ):
        st.info("Showing bundled S&P 500 data (live Yahoo Finance fetch unavailable).")

    st.sidebar.caption(f"Last updated: {prices.index[-1].strftime('%Y-%m-%d')}")

    render_return_metrics(prices[SP500_TICKER])

    series = chart_prices[SP500_TICKER]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series,
            mode="lines",
            name="S&P 500",
            line=dict(width=2, color="#FF962F"),
            hovertemplate="%{y:,.2f}<br>%{x|%Y-%m-%d}<extra>S&P 500</extra>",
        )
    )
    fig.update_layout(
        **chart_layout(
            title="S&P 500",
            height=450,
            yaxis_title="Index level",
            xaxis_title="Date",
            hovermode="x unified",
        )
    )

    st.plotly_chart(fig, use_container_width=True)


render()
