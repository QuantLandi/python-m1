from datetime import date, timedelta

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from views.common import (
    CALENDAR_HORIZONS,
    DEFAULT_END_DATE,
    LOOKBACK_YEARS,
    RETURN_COLOR_NEGATIVE,
    RETURN_COLOR_NEUTRAL,
    RETURN_COLOR_POSITIVE,
    TRAILING_HORIZONS,
    _format_observation_timestamp,
    chart_layout,
    compute_return_metrics,
    date_range_error,
    download_data,
    get_available_date_bounds,
    lookback_start,
    render_latest_prices_table,
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


def _bar_color(value: float) -> str:
    if abs(value) < 0.0005:
        return RETURN_COLOR_NEUTRAL
    if value > 0:
        return RETURN_COLOR_POSITIVE
    return RETURN_COLOR_NEGATIVE


def _return_quadrants(
    title: str,
    horizons: tuple[str, ...],
    metrics_by_name: dict[str, dict[str, float | None]],
) -> None:
    fig = make_subplots(rows=2, cols=2, subplot_titles=list(horizons), vertical_spacing=0.16)
    for index, horizon in enumerate(horizons):
        row = index // 2 + 1
        col = index % 2 + 1
        names: list[str] = []
        values: list[float] = []
        colors: list[str] = []
        for name, metrics in metrics_by_name.items():
            value = metrics.get(horizon)
            if value is None:
                continue
            names.append(name)
            values.append(value * 100)
            colors.append(_bar_color(value))
        fig.add_trace(
            go.Bar(
                x=names,
                y=values,
                marker=dict(color=colors),
                hovertemplate="%{x}: %{y:+.1f}%<extra></extra>",
                showlegend=False,
            ),
            row=row,
            col=col,
        )
        fig.update_yaxes(ticksuffix="%", zeroline=True, row=row, col=col)
    fig.update_layout(
        **chart_layout(
            title=title,
            height=560,
            margin=dict(t=80, b=40),
        )
    )
    st.plotly_chart(fig, use_container_width=True)


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

    st.subheader("Latest prices")
    obs_ts = render_latest_prices_table(prices, LABELS, transpose=True, inject_css=True)
    if obs_ts is not None:
        st.caption(f"Observed at {_format_observation_timestamp(obs_ts)}")

    trailing_by_name: dict[str, dict[str, float | None]] = {}
    calendar_by_name: dict[str, dict[str, float | None]] = {}
    for ticker in selected_tickers:
        if ticker not in prices.columns:
            continue
        computed = compute_return_metrics(prices[ticker])
        if computed is None:
            continue
        trailing, calendar = computed
        name = LABELS[ticker]
        trailing_by_name[name] = trailing
        calendar_by_name[name] = calendar

    if trailing_by_name:
        _return_quadrants("Trailing returns", TRAILING_HORIZONS, trailing_by_name)
        _return_quadrants("Calendar returns", CALENDAR_HORIZONS, calendar_by_name)

    inject_css = True
    for ticker in selected_tickers:
        if ticker not in prices.columns or prices[ticker].dropna().empty:
            st.info(f"No prices available for {LABELS[ticker]}.")
            continue
        st.subheader(LABELS[ticker])
        render_return_metrics(prices[ticker], inject_css=inject_css)
        inject_css = False


render()
