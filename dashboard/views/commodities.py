from datetime import date, timedelta

import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    LOOKBACK_YEARS,
    date_range_error,
    download_data,
    get_available_date_bounds,
    lookback_start,
    render_return_metrics,
)

METALS = [
    ("GC=F", "Gold"),
    ("SI=F", "Silver"),
    ("HG=F", "Copper"),
]

ENERGY = [
    ("CL=F", "WTI crude"),
    ("BZ=F", "Brent crude"),
    ("NG=F", "Natural gas"),
]

GRAINS = [
    ("ZW=F", "Wheat"),
    ("ZC=F", "Corn"),
]

GROUPS = (
    ("Metals", METALS),
    ("Energy", ENERGY),
    ("Grains", GRAINS),
)

ALL_TICKERS = tuple(ticker for _, members in GROUPS for ticker, _ in members)
LABELS = {ticker: label for _, members in GROUPS for ticker, label in members}

COMMODITY_EARLIEST = date(2000, 1, 1)


def render() -> None:
    st.header(":material/oil_barrel: Commodities")
    st.caption("Metals, energy, and grains — trailing and calendar returns.")

    starts = [COMMODITY_EARLIEST]
    for ticker in ALL_TICKERS:
        bounds = get_available_date_bounds(ticker)
        if bounds is not None:
            starts.append(bounds[0])
    earliest_date = min(starts)

    def _apply_lookback() -> None:
        end = DEFAULT_END_DATE
        years = LOOKBACK_YEARS[st.session_state.commodities_lookback]
        st.session_state.commodities_end_date = end
        st.session_state.commodities_start_date = lookback_start(end, years, earliest_date)

    if "commodities_lookback" not in st.session_state:
        st.session_state.commodities_lookback = "1y"
    if (
        "commodities_start_date" not in st.session_state
        or "commodities_end_date" not in st.session_state
    ):
        _apply_lookback()

    with st.sidebar:
        st.selectbox(
            "Lookback",
            list(LOOKBACK_YEARS),
            key="commodities_lookback",
            on_change=_apply_lookback,
        )
        start_date = st.date_input(
            "Start date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="commodities_start_date",
        )
        end_date = st.date_input(
            "End date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="commodities_end_date",
        )
        selected_labels = st.multiselect(
            "Commodities",
            options=[LABELS[ticker] for ticker in ALL_TICKERS],
            default=[LABELS[ticker] for ticker in ALL_TICKERS],
            key="commodity_names",
        )

    range_error = date_range_error(start_date, end_date)
    if range_error:
        st.warning(range_error)
        return

    selected_tickers = tuple(
        ticker for ticker in ALL_TICKERS if LABELS[ticker] in selected_labels
    )
    if not selected_tickers:
        st.info("Select at least one commodity.")
        return

    metrics_start = max(earliest_date, end_date - timedelta(days=365 + 21))
    fetch_start = min(start_date, metrics_start)
    prices = download_data(selected_tickers, fetch_start, end_date, use_live=True)
    if not prices.empty:
        prices = prices.ffill().dropna(how="all")

    if prices.empty:
        st.error(
            "No commodity prices available. "
            "Yahoo Finance may be blocked from this server, and bundled fallback files are missing."
        )
        return

    bundled_ends = []
    for ticker in selected_tickers:
        bounds = get_available_date_bounds(ticker)
        if bounds is not None:
            bundled_ends.append(bounds[1])
    if bundled_ends and prices.index[-1].date() <= max(bundled_ends) < end_date:
        st.info("Showing bundled commodity data (live Yahoo Finance fetch unavailable).")

    st.sidebar.caption(f"Last updated: {prices.index[-1].strftime('%Y-%m-%d')}")

    inject_css = True
    for ticker in selected_tickers:
        if ticker not in prices.columns or prices[ticker].dropna().empty:
            st.info(f"No prices available for {LABELS[ticker]}.")
            continue
        st.subheader(LABELS[ticker])
        render_return_metrics(prices[ticker], inject_css=inject_css)
        inject_css = False


render()
