from datetime import date

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
SP500_BUNDLED_FILE = "GSPC.csv"
LOOKBACK_YEARS = {
    "1y": 1,
    "3y": 3,
    "5y": 5,
    "10y": 10,
    "20y": 20,
    "30y": 30,
    "max": None,
}


def _lookback_start(end: date, years: int | None, earliest: date) -> date:
    if years is None:
        return earliest
    try:
        start = end.replace(year=end.year - years)
    except ValueError:
        start = end.replace(year=end.year - years, month=2, day=28)
    return max(earliest, start)


def render() -> None:
    st.header(":material/table_chart_view: Stocks")
    st.caption("Integrated stock analytics covering flagship single names.")

    bounds = get_available_date_bounds(SP500_TICKER)
    if bounds is None:
        st.sidebar.warning("Bundled S&P 500 history file missing — date range may be limited.")
    earliest_date = bounds[0] if bounds else DEFAULT_START_DATE

    def _apply_lookback() -> None:
        end = DEFAULT_END_DATE
        years = LOOKBACK_YEARS[st.session_state.lookback]
        st.session_state.end_date = end
        st.session_state.start_date = _lookback_start(end, years, earliest_date)

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

    cache_file = DATA_CACHE_DIR / SP500_BUNDLED_FILE
    bundled_file = DATA_DIR / SP500_BUNDLED_FILE
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
