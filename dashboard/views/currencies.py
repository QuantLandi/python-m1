from datetime import date, timedelta

import pandas as pd
import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    LOOKBACK_YEARS,
    RETURNS_TABLE_CSS,
    date_range_error,
    download_data,
    get_available_date_bounds,
    lookback_start,
    preprocess,
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


def last_usd_per_units(prices: pd.DataFrame) -> tuple[pd.Timestamp, pd.Series] | None:
    """Last aligned USD-per-unit vector from USD-leg closes."""
    if prices.empty:
        return None

    usd_paths: dict[str, pd.Series] = {"USD": pd.Series(1.0, index=prices.index)}
    for currency, (ticker, convention) in USD_LEGS.items():
        if ticker not in prices.columns:
            continue
        series = prices[ticker].dropna()
        if series.empty:
            continue
        usd_paths[currency] = series.map(lambda price: usd_per_unit(price, convention))

    aligned = pd.DataFrame(usd_paths).ffill().dropna(how="any")
    if aligned.empty:
        return None
    last_date = aligned.index[-1]
    return last_date, aligned.loc[last_date]


def _format_rate(value: float, quote: str) -> str:
    if quote == "JPY" or value >= 100:
        return f"{value:,.2f}"
    if value >= 10:
        return f"{value:,.3f}"
    return f"{value:,.4f}"


def _show_spot_matrix(matrix: pd.DataFrame) -> None:
    display = pd.DataFrame(
        {
            col: [_format_rate(matrix.loc[row, col], col) for row in matrix.index]
            for col in matrix.columns
        },
        index=matrix.index,
    )
    display.insert(0, "Base \\ Quote", list(matrix.index))
    html = display.to_html(
        index=False,
        classes="returns-table",
        border=0,
        justify="center",
        escape=False,
    )
    st.markdown(RETURNS_TABLE_CSS, unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)


def render() -> None:
    st.header(":material/euro_symbol: Currencies")
    st.caption(
        "Spot cross matrix for USD, EUR, GBP, JPY, CHF, AUD, CAD, and NZD. "
        "Each cell is units of the column currency per 1 unit of the row currency."
    )

    starts = [FX_EARLIEST]
    for ticker in FX_TICKERS:
        bounds = get_available_date_bounds(ticker)
        if bounds is not None:
            starts.append(bounds[0])
    earliest_date = min(starts)

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

    range_error = date_range_error(start_date, end_date)
    if range_error:
        st.warning(range_error)
        return

    fetch_start = max(earliest_date, end_date - timedelta(days=30))
    fetch_start = min(start_date, fetch_start)
    prices = download_data(FX_TICKERS, fetch_start, end_date, use_live=True)
    prices = preprocess(prices)

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

    snapshot = last_usd_per_units(prices)
    if snapshot is None:
        st.error("Could not align USD legs into a complete currency matrix.")
        return

    as_of, usd_per = snapshot
    missing = [ccy for ccy in CURRENCIES if ccy not in usd_per.index]
    if missing:
        st.warning("Missing USD legs for: " + ", ".join(missing))

    ordered = [ccy for ccy in CURRENCIES if ccy in usd_per.index]
    matrix = spot_cross_matrix(usd_per.loc[ordered])

    st.sidebar.caption(f"Last updated: {as_of.strftime('%Y-%m-%d')}")
    st.subheader(f"Spot matrix — {as_of.strftime('%Y-%m-%d')}")
    _show_spot_matrix(matrix)


try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    if get_script_run_ctx() is not None:
        render()
except ImportError:
    pass
