from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    LOOKBACK_YEARS,
    chart_layout,
    date_range_error,
    download_data,
    get_available_date_bounds,
    lookback_start,
    normalize,
)

CHART_COLOR = "#FF962F"

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


def _orange_gradient(count: int) -> list[str]:
    if count <= 0:
        return []
    colors = []
    for i in range(count):
        t = 0.0 if count == 1 else i / (count - 1)
        green = int(round(255 + (0x96 - 255) * t))
        blue = int(round(255 + (0x2F - 255) * t))
        colors.append(f"#FF{green:02X}{blue:02X}")
    return colors


def _period_return(series: pd.Series) -> float | None:
    clean = series.dropna()
    if len(clean) < 2:
        return None
    base = float(clean.iloc[0])
    if base == 0:
        return None
    return float(clean.iloc[-1] / base - 1)


def render() -> None:
    st.header(":material/oil_barrel: Commodities")
    st.caption("Metals, energy, and grains — futures prices from Yahoo Finance.")

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
        st.session_state.commodities_lookback = "5y"
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
        st.info("Select at least one commodity to display prices.")
        return

    prices = download_data(selected_tickers, start_date, end_date, use_live=True)
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

    returns = {
        ticker: _period_return(prices[ticker])
        for ticker in selected_tickers
        if ticker in prices.columns
    }
    ranked = sorted(
        ((ticker, value) for ticker, value in returns.items() if value is not None),
        key=lambda item: item[1],
    )
    if ranked:
        labels = [LABELS[ticker] for ticker, _ in ranked]
        values = [value * 100 for _, value in ranked]
        fig = go.Figure(
            data=[
                go.Bar(
                    x=labels,
                    y=values,
                    marker=dict(color=_orange_gradient(len(ranked))),
                    hovertemplate="%{x}: %{y:+.1f}%<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            **chart_layout(
                title="Return over the selected window",
                yaxis_title="Return (%)",
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    for group_name, members in GROUPS:
        group_tickers = [
            ticker
            for ticker, _ in members
            if ticker in selected_tickers and ticker in prices.columns
        ]
        if not group_tickers:
            continue
        group_prices = prices[group_tickers].dropna(how="all")
        if group_prices.empty:
            st.info(f"{group_name} prices unavailable for this date range.")
            continue
        indexed = normalize(group_prices)
        fig = go.Figure()
        for ticker in group_tickers:
            fig.add_trace(
                go.Scatter(
                    x=indexed.index,
                    y=indexed[ticker],
                    mode="lines",
                    name=LABELS[ticker],
                    hovertemplate="%{y:.2f}×<br>%{x|%Y-%m-%d}<extra>%{fullData.name}</extra>",
                )
            )
        fig.update_layout(
            **chart_layout(
                title=f"{group_name} (indexed to 1.0 at start of window)",
                yaxis_title="Indexed price",
                xaxis_title="Date",
                hovermode="x unified",
            )
        )
        st.plotly_chart(fig, use_container_width=True)


render()
