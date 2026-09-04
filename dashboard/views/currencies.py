from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    LOOKBACK_YEARS,
    _format_observation_timestamp,
    chart_layout,
    date_range_error,
    get_available_date_bounds,
    load_data_local_first,
    lookback_start,
    preprocess,
    render_data_refresh_status,
)

# G8 currencies. Spot crosses are implied from USD legs (Yahoo Finance).
CURRENCIES = ("USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD")

# usd_quote: ticker is XXXUSD (USD per 1 unit of XXX).
# usd_base: ticker is USDXXX (XXX per 1 USD).
USD_LEGS: dict[str, tuple[str, str]] = {
    "EUR": ("EURUSD=X", "usd_quote"),
    "GBP": ("GBPUSD=X", "usd_quote"),
    "AUD": ("AUDUSD=X", "usd_quote"),
    "NZD": ("NZDUSD=X", "usd_quote"),
    "JPY": ("USDJPY=X", "usd_base"),
    "CHF": ("USDCHF=X", "usd_base"),
    "CAD": ("USDCAD=X", "usd_base"),
}

FX_TICKERS = tuple(ticker for ticker, _ in USD_LEGS.values())
FX_EARLIEST = date(2000, 1, 1)


def usd_per_unit(leg_price: float, convention: str) -> float:
    """USD amount equivalent to 1 unit of the foreign currency."""
    if convention == "usd_quote":
        return float(leg_price)
    return 1.0 / float(leg_price)


def spot_cross_matrix(usd_per: pd.Series) -> pd.DataFrame:
    """Units of column currency per 1 unit of row currency."""
    names = list(usd_per.index)
    values = {
        row: {col: float(usd_per[row] / usd_per[col]) for col in names} for row in names
    }
    return pd.DataFrame(values).T.loc[names, names]


def usd_per_paths(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily USD amount equivalent to 1 unit of each currency."""
    if prices.empty:
        return pd.DataFrame()

    usd_paths: dict[str, pd.Series] = {"USD": pd.Series(1.0, index=prices.index)}
    for currency, (ticker, convention) in USD_LEGS.items():
        if ticker not in prices.columns:
            continue
        series = prices[ticker].dropna()
        if series.empty:
            continue
        usd_paths[currency] = series.map(lambda price: usd_per_unit(price, convention))

    return pd.DataFrame(usd_paths).ffill()


def last_usd_per_units(prices: pd.DataFrame) -> tuple[pd.Timestamp, pd.Series] | None:
    """Last aligned USD-per-unit vector from USD-leg closes."""
    aligned = usd_per_paths(prices).dropna(how="any")
    if aligned.empty:
        return None
    last_date = aligned.index[-1]
    return last_date, aligned.loc[last_date]


def pair_rate(usd_paths: pd.DataFrame, numerator: str, denominator: str) -> pd.Series:
    """Units of denominator per 1 unit of numerator. Same-currency pairs are 1."""
    name = f"{numerator}/{denominator}"
    if numerator == denominator:
        if numerator in usd_paths.columns:
            index = usd_paths[numerator].dropna().index
        else:
            index = usd_paths.index
        return pd.Series(1.0, index=index, name=name)
    return (usd_paths[numerator] / usd_paths[denominator]).dropna().rename(name)


def _format_rate(value: float, quote: str) -> str:
    if quote == "JPY" or value >= 100:
        return f"{value:,.2f}"
    if value >= 10:
        return f"{value:,.3f}"
    return f"{value:,.4f}"


def _pick_pair(numerator: str, denominator: str) -> None:
    """Button callback: set the plotted pair before the next run."""
    st.session_state.fx_numerator = numerator
    st.session_state.fx_denominator = denominator


def _show_spot_matrix(
    matrix: pd.DataFrame,
    numerator: str,
    denominator: str,
) -> None:
    st.caption("Click a cell to plot that pair (row = numerator, column = denominator).")
    quotes = list(matrix.columns)
    header = st.columns(len(quotes) + 1)
    header[0].markdown("")
    for index, quote in enumerate(quotes):
        header[index + 1].markdown(
            f"<div style='text-align:center'><b>{quote}</b></div>",
            unsafe_allow_html=True,
        )
    for base in matrix.index:
        row = st.columns(len(quotes) + 1)
        row[0].markdown(f"**{base}**")
        for index, quote in enumerate(quotes):
            selected = base == numerator and quote == denominator
            row[index + 1].button(
                _format_rate(float(matrix.loc[base, quote]), quote),
                key=f"fx_cell_{base}_{quote}",
                use_container_width=True,
                type="primary" if selected else "secondary",
                on_click=_pick_pair,
                args=(base, quote),
            )


def render() -> None:
    st.header(":material/euro_symbol: Currencies")
    st.caption(
        "Spot cross matrix for USD, EUR, GBP, JPY, CHF, AUD, CAD, and NZD. "
        "Each cell is units of the column currency per 1 unit of the row currency."
    )

    starts = []
    for ticker in FX_TICKERS:
        bounds = get_available_date_bounds(ticker)
        if bounds is not None:
            starts.append(bounds[0])
    earliest_date = min(starts) if starts else FX_EARLIEST

    def _apply_lookback() -> None:
        end = DEFAULT_END_DATE
        years = LOOKBACK_YEARS[st.session_state.currencies_lookback]
        st.session_state.currencies_end_date = end
        st.session_state.currencies_start_date = lookback_start(end, years, earliest_date)

    if "currencies_lookback" not in st.session_state:
        st.session_state.currencies_lookback = "1y"
    if (
        "currencies_start_date" not in st.session_state
        or "currencies_end_date" not in st.session_state
    ):
        _apply_lookback()

    with st.sidebar:
        st.selectbox(
            "Lookback",
            list(LOOKBACK_YEARS),
            key="currencies_lookback",
            on_change=_apply_lookback,
        )
        start_date = st.date_input(
            "Start date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="currencies_start_date",
        )
        end_date = st.date_input(
            "End date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="currencies_end_date",
        )
        if "fx_numerator" not in st.session_state:
            st.session_state.fx_numerator = "EUR"
        if "fx_denominator" not in st.session_state:
            st.session_state.fx_denominator = "USD"
        numerator = st.selectbox(
            "Numerator (base)",
            options=list(CURRENCIES),
            key="fx_numerator",
        )
        denominator = st.selectbox(
            "Denominator (quote)",
            options=list(CURRENCIES),
            key="fx_denominator",
        )

    range_error = date_range_error(start_date, end_date)
    if range_error:
        st.warning(range_error)
        return

    fetch_start = max(earliest_date, end_date - timedelta(days=30))
    fetch_start = min(start_date, fetch_start)
    prices_result = load_data_local_first(
        FX_TICKERS, fetch_start, end_date, use_live=True
    )
    render_data_refresh_status(prices_result, "Yahoo Finance")
    prices = preprocess(prices_result.data)

    if prices.empty:
        st.error(
            "No FX prices available. "
            "Yahoo Finance may be blocked from this server, and bundled fallback files are missing."
        )
        return

    bundled_ends = []
    for ticker in FX_TICKERS:
        bounds = get_available_date_bounds(ticker)
        if bounds is not None:
            bundled_ends.append(bounds[1])
    if bundled_ends and prices.index[-1].date() <= max(bundled_ends) < end_date:
        st.info("Showing bundled FX data (live Yahoo Finance fetch unavailable).")

    aligned = usd_per_paths(prices)
    complete = aligned.dropna(how="any")
    if complete.empty:
        st.error("Could not align USD legs into a complete currency matrix.")
        return

    as_of = complete.index[-1]
    usd_per = complete.loc[as_of]
    missing = [ccy for ccy in CURRENCIES if ccy not in usd_per.index]
    if missing:
        st.warning("Missing USD legs for: " + ", ".join(missing))

    ordered = [ccy for ccy in CURRENCIES if ccy in usd_per.index]
    matrix = spot_cross_matrix(usd_per.loc[ordered])

    st.sidebar.caption(f"Last updated: {as_of.strftime('%Y-%m-%d')}")

    st.subheader(f"Spot matrix — {_format_observation_timestamp(as_of)}")
    _show_spot_matrix(matrix, numerator, denominator)

    pair_name = f"{numerator}/{denominator}"
    chart_mask = (aligned.index >= pd.Timestamp(start_date)) & (
        aligned.index <= pd.Timestamp(end_date)
    )
    series = pair_rate(aligned.loc[chart_mask], numerator, denominator)
    if series.empty:
        st.warning("No observations in the selected date range.")
    else:
        hover_fmt = ",.4f" if numerator == denominator else (
            ",.2f" if denominator == "JPY" else ",.4f"
        )
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series,
                mode="lines",
                name=pair_name,
                line=dict(width=2, color="#FF962F"),
                hovertemplate=f"%{{y:{hover_fmt}}}<br>%{{x|%Y-%m-%d}}<extra>{pair_name}</extra>",
            )
        )
        yaxis_title = (
            f"{denominator} per 1 {numerator}"
            if numerator != denominator
            else f"{numerator} per 1 {numerator}"
        )
        fig.update_layout(
            **chart_layout(
                title=pair_name,
                height=450,
                yaxis_title=yaxis_title,
                xaxis_title="Date",
                hovermode="x unified",
            )
        )
        st.plotly_chart(fig, use_container_width=True)


try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    if get_script_run_ctx() is not None:
        render()
except ImportError:
    pass
