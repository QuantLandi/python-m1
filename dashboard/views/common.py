"""Shared helpers for the Cross-Asset Market Monitor."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Tuple

import pandas as pd
import pandas_datareader.data as web
import streamlit as st
import yfinance as yf

from paths import DATA_DIR

DEFAULT_START_DATE = date(1927, 12, 30)  # ^GSPC bundled history start; used if CSV missing
DEFAULT_END_DATE = date.today()

LOOKBACK_YEARS = {
    "1y": 1,
    "3y": 3,
    "5y": 5,
    "10y": 10,
    "20y": 20,
    "30y": 30,
    "max": None,
}


def lookback_start(end: date, years: int | None, earliest: date) -> date:
    """Shift `end` back by `years`, clamped to `earliest`. `None` years means max history."""
    if years is None:
        return earliest
    try:
        start = end.replace(year=end.year - years)
    except ValueError:
        # 29 Feb in a non-leap target year (e.g. 2024-02-29 minus 1 year).
        start = end.replace(year=end.year - years, month=2, day=28)
    return max(earliest, start)


def date_range_error(start_date: date, end_date: date) -> str | None:
    """Return a warning message if the selected range is invalid."""
    if start_date > end_date:
        return "Start date must be on or before the end date."
    if start_date == end_date:
        return "Date range must span at least two distinct dates."
    return None


def chart_layout(**kwargs) -> dict:
    """Default Plotly layout shared by the tabs."""
    layout = dict(
        height=420,
        template="plotly_white",
        margin=dict(t=60, b=40),
    )
    layout.update(kwargs)
    return layout


def _storage_filename(symbol: str) -> str:
    """Filesystem-safe name: Yahoo tickers like ^GSPC cannot be filenames."""
    return symbol.replace("^", "").replace("=", "_")


def _read_price_csv(path, symbol: str) -> pd.Series | None:
    if not path.exists():
        return None
    frame = pd.read_csv(path, index_col=0, parse_dates=True)
    frame.index = frame.index.tz_localize(None)
    column = "Close" if "Close" in frame.columns else frame.columns[0]
    return frame[column].rename(symbol)


def _load_bundled_series(symbol: str) -> pd.Series | None:
    # Offline copy shipped in dashboard/data/ — not the process working directory.
    return _read_price_csv(DATA_DIR / f"{_storage_filename(symbol)}.csv", symbol)


def _merge_live_and_stored(symbol: str, live: pd.Series | None) -> pd.Series:
    """Combine bundled history with this run's live prices; live wins on overlapping dates."""
    stored = _load_bundled_series(symbol)
    parts: list[pd.Series] = []
    if stored is not None:
        parts.append(stored)
    if live is not None and not live.empty:
        parts.append(live.dropna())
    if not parts:
        return pd.Series(dtype=float, name=symbol)
    combined = pd.concat(parts).sort_index()
    return combined[~combined.index.duplicated(keep="last")].rename(symbol)


def get_available_date_bounds(symbol: str) -> tuple[date, date] | None:
    """Return the earliest and latest dates in the bundled CSV for a symbol."""
    bundled = _load_bundled_series(symbol)
    if bundled is None or bundled.empty:
        return None
    return bundled.index.min().date(), bundled.index.max().date()


def _live_fetch_start(symbols: Tuple[str, ...], requested_start: date, requested_end: date) -> date | None:
    """Earliest date to request live. Skip the network if the bundled CSV already covers `requested_end`."""
    starts: list[date] = []
    for symbol in symbols:
        bounds = get_available_date_bounds(symbol)
        if bounds is None:
            starts.append(requested_start)
            continue
        stored_latest = bounds[1]
        if stored_latest >= requested_end:
            continue
        starts.append(max(requested_start, stored_latest))
    if not starts:
        return None
    return min(starts)


@st.cache_data(show_spinner=False, ttl=60 * 60)
def _fetch_live_prices(
    tickers: Tuple[str, ...],
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """Download live prices from Yahoo Finance. Cached for one hour."""
    if not tickers:
        return pd.DataFrame()

    end_exclusive = end_date + timedelta(days=1)
    frames: list[pd.Series] = []

    try:
        price_frame = yf.download(
            list(tickers),
            start=start_date,
            end=end_exclusive,
            auto_adjust=True,
            progress=False,
        )
        close_prices = price_frame["Close"] if "Close" in price_frame else price_frame
        if isinstance(close_prices, pd.Series):
            close_prices = close_prices.to_frame(name=tickers[0])

        close_prices.index = close_prices.index.tz_localize(None)

        for symbol in tickers:
            if symbol not in close_prices.columns:
                continue
            series = close_prices[symbol].dropna()
            if series.empty:
                continue
            frames.append(series.rename(symbol))
    except Exception:
        # Network or Yahoo errors must not crash the page; callers fall back to bundled CSVs.
        frames = []

    if not frames:
        for symbol in tickers:
            try:
                history = yf.Ticker(symbol).history(
                    start=start_date,
                    end=end_exclusive,
                    auto_adjust=True,
                )
            except Exception:
                continue
            if history.empty or "Close" not in history.columns:
                continue
            series = history["Close"].dropna()
            series.index = series.index.tz_localize(None)
            if series.empty:
                continue
            frames.append(series.rename(symbol))

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, axis=1).sort_index()


@st.cache_data(show_spinner=False, ttl=60 * 60)
def _fetch_live_fred(
    series_ids: Tuple[str, ...],
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """Download FRED series via pandas_datareader (no API key). Cached for one hour."""
    if not series_ids:
        return pd.DataFrame()

    try:
        frame = web.DataReader(list(series_ids), "fred", start_date, end_date)
    except Exception:
        return pd.DataFrame()

    if frame is None or frame.empty:
        return pd.DataFrame()

    if isinstance(frame, pd.Series):
        frame = frame.to_frame(name=series_ids[0])

    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    return frame


def download_fred_data(
    series_ids: Tuple[str, ...],
    start_date: date,
    end_date: date,
    *,
    use_live: bool = True,
) -> pd.DataFrame:
    """Fetch FRED yields and merge them with bundled CSVs for this run only.

    Live requests start at the latest bundled date, not the chart window start.
    Bundled files in `data/` are never rewritten.
    """
    if not series_ids:
        return pd.DataFrame()

    series_ids = tuple(series_ids)
    live_start = _live_fetch_start(series_ids, start_date, end_date) if use_live else None
    live_frame = (
        _fetch_live_fred(series_ids, live_start, end_date)
        if live_start is not None
        else pd.DataFrame()
    )
    merged_frames: list[pd.Series] = []

    for series_id in series_ids:
        live_series = live_frame[series_id] if series_id in live_frame.columns else None
        if live_series is not None:
            live_series = pd.to_numeric(live_series, errors="coerce").rename(series_id)
        series = _merge_live_and_stored(series_id, live_series)
        if not series.empty:
            merged_frames.append(series)

    if not merged_frames:
        return pd.DataFrame()

    fetched = pd.concat(merged_frames, axis=1).sort_index()
    mask = (fetched.index >= pd.Timestamp(start_date)) & (
        fetched.index <= pd.Timestamp(end_date)
    )
    return fetched.loc[mask]


def download_data(
    tickers: Tuple[str, ...],
    start_date: date,
    end_date: date,
    *,
    use_live: bool = True,
) -> pd.DataFrame:
    """Fetch prices via Yahoo Finance and merge them with bundled CSVs for this run only.

    Live requests start at the latest bundled date, not the chart window start.
    Bundled files in `data/` are never rewritten.
    """
    if not tickers:
        return pd.DataFrame()

    tickers = tuple(tickers)
    merged_frames: list[pd.Series] = []
    live_start = _live_fetch_start(tickers, start_date, end_date) if use_live else None
    live_frame = (
        _fetch_live_prices(tickers, live_start, end_date)
        if live_start is not None
        else pd.DataFrame()
    )

    for symbol in tickers:
        live_series = live_frame[symbol] if symbol in live_frame.columns else None
        series = _merge_live_and_stored(symbol, live_series)
        if not series.empty:
            merged_frames.append(series)

    if not merged_frames:
        return pd.DataFrame()

    fetched = pd.concat(merged_frames, axis=1).sort_index()

    if fetched.empty:
        return pd.DataFrame()

    mask = (fetched.index >= pd.Timestamp(start_date)) & (fetched.index <= pd.Timestamp(end_date))
    return fetched.loc[mask]


def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill and remove missing observations."""
    if data.empty:
        return data
    return data.ffill().dropna()


def normalize(data: pd.DataFrame) -> pd.DataFrame:
    """Index each series to 1.0 at its first valid observation."""
    if data.empty:
        return data
    first = data.apply(
        lambda series: series.dropna().iloc[0] if series.notna().any() else float("nan")
    )
    return data.div(first)


def _simple_return(last: float, base: float) -> float | None:
    if base == 0:
        return None
    return float(last / base - 1)


def _trailing_return(series: pd.Series, days: int) -> float | None:
    series = series.dropna().sort_index()
    if series.empty:
        return None
    last = series.iloc[-1]
    prior = series.loc[: series.index[-1] - pd.Timedelta(days=days)]
    if prior.empty:
        return None
    return _simple_return(last, prior.iloc[-1])


def _trading_day_return(series: pd.Series) -> float | None:
    series = series.dropna().sort_index()
    if len(series) < 2:
        return None
    return _simple_return(series.iloc[-1], series.iloc[-2])


def _since_return(series: pd.Series, period_start: pd.Timestamp) -> float | None:
    series = series.dropna().sort_index()
    window = series.loc[period_start:]
    if window.empty:
        return None
    return _simple_return(window.iloc[-1], window.iloc[0])


# Okabe–Ito palette: readable with red–green colour blindness (signs stay in the text too).
RETURN_COLOR_POSITIVE = "#56B4E9"
RETURN_COLOR_NEGATIVE = "#D55E00"
RETURN_COLOR_NEUTRAL = "#FFFFFF"


def _format_return(value: float | None) -> str:
    if value is None:
        return "—"
    text = f"{value:+.1%}"
    if abs(value) < 0.0005:
        color = RETURN_COLOR_NEUTRAL
    elif value > 0:
        color = RETURN_COLOR_POSITIVE
    else:
        color = RETURN_COLOR_NEGATIVE
    return f'<span style="color:{color}">{text}</span>'


RETURNS_TABLE_CSS = """
<style>
table.returns-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.25rem 0 1rem 0;
  font-size: 1.2rem;
}
table.returns-table th {
  background-color: #2A2118;
  color: #FF962F;
  font-weight: 600;
  padding: 0.65rem 0.75rem;
  text-align: center;
  border: 1px solid #2A2A2A;
}
table.returns-table td {
  background-color: #1F1F1F;
  color: #FFFFFF;
  padding: 0.75rem 0.75rem;
  text-align: center;
  font-size: 1.35rem;
  border: 1px solid #2A2A2A;
}
</style>
"""


def _show_returns_table(frame: pd.DataFrame) -> None:
    html = frame.to_html(
        index=False,
        classes="returns-table",
        border=0,
        justify="center",
        escape=False,
    )
    st.markdown(html, unsafe_allow_html=True)


def render_return_metrics(prices: pd.Series, *, inject_css: bool = True) -> None:
    """Trailing (1d–1y) and calendar (WTD–YTD) return tables for one price series."""
    series = prices.dropna()
    if series.empty:
        st.info("No prices available to compute returns.")
        return

    last_day = series.index[-1]
    week_start = last_day - pd.Timedelta(days=int(last_day.weekday()))
    month_start = last_day.replace(day=1)
    quarter_month = ((last_day.month - 1) // 3) * 3 + 1
    quarter_start = last_day.replace(month=quarter_month, day=1)
    year_start = last_day.replace(month=1, day=1)

    trailing = {
        "1-day": _trading_day_return(prices),
        "7-day": _trailing_return(prices, 7),
        "30-day": _trailing_return(prices, 30),
        "90-day": _trailing_return(prices, 90),
        "1-year": _trailing_return(prices, 365),
    }
    calendar = {
        "Week to date": _since_return(prices, week_start),
        "Month to date": _since_return(prices, month_start),
        "Quarter to date": _since_return(prices, quarter_start),
        "Year to date": _since_return(prices, year_start),
    }

    trailing_table = pd.DataFrame(
        {label: [_format_return(value)] for label, value in trailing.items()},
        index=["Return"],
    )
    calendar_table = pd.DataFrame(
        {label: [_format_return(value)] for label, value in calendar.items()},
        index=["Return"],
    )

    if inject_css:
        st.markdown(RETURNS_TABLE_CSS, unsafe_allow_html=True)
    st.caption("Trailing returns")
    _show_returns_table(trailing_table)
    st.caption("Calendar returns")
    _show_returns_table(calendar_table)
