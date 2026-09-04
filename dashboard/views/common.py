"""Shared helpers for the Cross-Asset Market Monitor."""

from __future__ import annotations

import inspect
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Literal, Tuple

import pandas as pd
import pandas_datareader.data as web
import streamlit as st
import yfinance as yf

from paths import DATA_DIR

DEFAULT_START_DATE = date(1927, 12, 30)  # ^GSPC bundled history start; used if CSV missing
DEFAULT_END_DATE = date.today()

LIVE_REFRESH_TTL_SECONDS = 60 * 60
"""How long a successful network snapshot is considered fresh."""
MAX_YFINANCE_WORKERS = 4
"""Maximum number of per-ticker Yahoo fallback requests in flight."""
RefreshKey = tuple[str, tuple[str, ...], date, date]

logger = logging.getLogger(__name__)


def _cache_data_with_background_refresh(func):
    """Decorate a loader with Streamlit's stale-while-revalidate cache when available.

    ``refresh_mode`` was added after some supported Streamlit versions.  Keeping
    the small compatibility branch lets the synchronous API work in older test
    environments while Streamlit 1.63 serves an expired value and refreshes it
    in the background.
    """
    cache_kwargs = dict(show_spinner=False, ttl=LIVE_REFRESH_TTL_SECONDS)
    try:
        if "refresh_mode" in inspect.signature(st.cache_data).parameters:
            cache_kwargs["refresh_mode"] = "background"
        return st.cache_data(**cache_kwargs)(func)
    except TypeError:
        # Older or unexpected Streamlit builds may reject refresh_mode at call time.
        cache_kwargs.pop("refresh_mode", None)
        return st.cache_data(**cache_kwargs)(func)


@dataclass(frozen=True)
class DataLoadResult:
    """Result returned by the local-first loaders.

    ``data`` is always the best available snapshot.  A caller can render it
    immediately, show ``pending``/``error`` to the user, and call the loader
    again from a ``st.fragment(run_every=...)`` until ``pending`` becomes false.
    """

    data: pd.DataFrame
    status: Literal["fresh", "pending", "error"]
    pending: bool
    error: str | None = None
    last_updated: datetime | None = None
    refresh_key: RefreshKey | None = None


@dataclass
class _RefreshState:
    future: Future | None = None
    live_frame: pd.DataFrame | None = None
    error: str | None = None
    completed_at: float | None = None
    last_updated: datetime | None = None


_REFRESH_LOCK = threading.RLock()
_REFRESH_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="market-refresh")
_REFRESH_STATES: dict[RefreshKey, _RefreshState] = {}

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


def _normalise_yahoo_series(history: pd.DataFrame, symbol: str) -> pd.Series | None:
    """Extract one timezone-naive Close series from a Yahoo history frame."""
    if history is None or history.empty or "Close" not in history.columns:
        return None
    series = history["Close"].dropna()
    if series.empty:
        return None
    series.index = pd.to_datetime(series.index).tz_localize(None)
    return series.rename(symbol)


def _fetch_one_yahoo_ticker(
    symbol: str,
    start_date: date,
    end_exclusive: date,
) -> pd.Series | None:
    """Fetch one Yahoo ticker for the bounded fallback worker pool."""
    try:
        history = yf.Ticker(symbol).history(
            start=start_date,
            end=end_exclusive,
            auto_adjust=True,
        )
        return _normalise_yahoo_series(history, symbol)
    except Exception:
        logger.exception("Yahoo fallback failed for ticker %s", symbol)
        return None


def _fetch_live_prices_uncached(
    tickers: Tuple[str, ...],
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """Download live prices, using a bounded parallel fallback per ticker."""
    if not tickers:
        return pd.DataFrame()

    end_exclusive = end_date + timedelta(days=1)
    by_symbol: dict[str, pd.Series] = {}
    group_failed = False

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

        close_prices.index = pd.to_datetime(close_prices.index).tz_localize(None)

        for symbol in tickers:
            if symbol not in close_prices.columns:
                continue
            series = close_prices[symbol].dropna()
            if series.empty:
                continue
            by_symbol[symbol] = series.rename(symbol)
    except Exception:
        # The grouped endpoint is fast when healthy, but can fail independently
        # of the per-ticker endpoint.  Fill every missing ticker below.
        group_failed = True
        logger.exception("Grouped Yahoo download failed for tickers %s", tickers)

    missing = [symbol for symbol in tickers if symbol not in by_symbol]
    if group_failed or missing:
        worker_count = min(MAX_YFINANCE_WORKERS, max(1, len(missing)))
        with ThreadPoolExecutor(
            max_workers=worker_count,
            thread_name_prefix="yahoo-fallback",
        ) as executor:
            futures = {
                executor.submit(_fetch_one_yahoo_ticker, symbol, start_date, end_exclusive): symbol
                for symbol in missing
            }
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    series = future.result()
                except Exception:
                    # _fetch_one_yahoo_ticker logs expected failures; this
                    # guard also covers an unexpected worker implementation bug.
                    logger.exception("Yahoo fallback worker failed for ticker %s", symbol)
                    continue
                if series is not None and not series.empty:
                    by_symbol[symbol] = series

    if not by_symbol:
        return pd.DataFrame()

    # Dict insertion order follows completion order, so explicitly construct
    # columns from the caller's tuple to keep stable downstream semantics.
    return pd.concat(
        [by_symbol[symbol] for symbol in tickers if symbol in by_symbol],
        axis=1,
    ).sort_index()


@_cache_data_with_background_refresh
def _fetch_live_prices(
    tickers: Tuple[str, ...],
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """Cached synchronous wrapper; expired values refresh in the background."""
    return _fetch_live_prices_uncached(tickers, start_date, end_date)


def _fetch_live_fred_uncached(
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
        logger.exception("FRED download failed for series %s", series_ids)
        return pd.DataFrame()

    if frame is None or frame.empty:
        return pd.DataFrame()

    if isinstance(frame, pd.Series):
        frame = frame.to_frame(name=series_ids[0])

    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    return frame


@_cache_data_with_background_refresh
def _fetch_live_fred(
    series_ids: Tuple[str, ...],
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """Cached synchronous wrapper; expired values refresh in the background."""
    return _fetch_live_fred_uncached(series_ids, start_date, end_date)


def _filter_requested_range(frame: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
    """Return a defensive, date-filtered copy for a view."""
    if frame.empty:
        return frame.copy()
    mask = (frame.index >= pd.Timestamp(start_date)) & (frame.index <= pd.Timestamp(end_date))
    return frame.loc[mask].copy()


def _refresh_worker(
    source: str,
    symbols: tuple[str, ...],
    live_start: date,
    end_date: date,
) -> pd.DataFrame:
    """Network-only worker.  It deliberately calls no Streamlit API."""
    if source == "yahoo":
        frame = _fetch_live_prices_uncached(symbols, live_start, end_date)
    else:
        frame = _fetch_live_fred_uncached(symbols, live_start, end_date)
    if frame.empty:
        raise RuntimeError(f"{source} returned no usable data for {symbols}")
    return frame


def _collect_refreshes() -> None:
    """Commit completed worker results; safe to call on every Streamlit rerun."""
    with _REFRESH_LOCK:
        for state in _REFRESH_STATES.values():
            future = state.future
            if future is None or not future.done():
                continue
            state.future = None
            try:
                state.live_frame = future.result()
                state.error = None
                state.last_updated = datetime.now(timezone.utc)
            except Exception as exc:
                state.error = str(exc)
                # Keep the previous successful snapshot when revalidation fails.
                # This is the "stale" half of stale-while-revalidate; on a first
                # load ``live_frame`` is already None and bundled CSVs remain the
                # fallback.
                logger.exception("Background %s refresh failed", "market data")
            state.completed_at = time.monotonic()


def _start_refresh(
    source: str,
    symbols: tuple[str, ...],
    live_start: date,
    end_date: date,
    *,
    force: bool = False,
) -> _RefreshState:
    key = (source, symbols, live_start, end_date)
    now = time.monotonic()
    with _REFRESH_LOCK:
        state = _REFRESH_STATES.get(key)
        if state is None:
            state = _RefreshState()
            _REFRESH_STATES[key] = state
        elif state.future is not None and state.future.done():
            # A worker can finish between the caller's collection pass and this
            # lock acquisition. Commit it before deciding whether another
            # refresh is needed, otherwise the completed result could be
            # overwritten by a duplicate submission.
            future = state.future
            state.future = None
            try:
                state.live_frame = future.result()
                state.error = None
                state.last_updated = datetime.now(timezone.utc)
            except Exception as exc:
                state.error = str(exc)
                logger.exception("Background market data refresh failed")
            state.completed_at = now
        active = state.future is not None and not state.future.done()
        fresh = (
            state.completed_at is not None
            and now - state.completed_at < LIVE_REFRESH_TTL_SECONDS
        )
        if force or (not active and not fresh):
            if not active:
                state.error = None
                state.future = _REFRESH_EXECUTOR.submit(
                    _refresh_worker,
                    source,
                    symbols,
                    live_start,
                    end_date,
                )
        # Bound process-lifetime state if users switch among many date ranges.
        if len(_REFRESH_STATES) > 128:
            old_keys = sorted(
                _REFRESH_STATES,
                key=lambda item: _REFRESH_STATES[item].completed_at or now,
            )[:32]
            for old_key in old_keys:
                if old_key != key and _REFRESH_STATES[old_key].future is None:
                    del _REFRESH_STATES[old_key]
        return state


def poll_data_refresh(refresh_key: RefreshKey | None = None) -> bool:
    """Poll refreshes and return whether the selected refresh remains pending.

    Call this from a view's ``st.fragment(run_every=...)`` (or another normal
    Streamlit rerun).  The next rerun observes the completed snapshot without
    blocking the initial local render.  Pass ``DataLoadResult.refresh_key`` so a
    page polls only its own request; omitting it polls all requests in-process.
    No Streamlit function is called by the worker threads.
    """
    _collect_refreshes()
    with _REFRESH_LOCK:
        states = (
            (_REFRESH_STATES.get(refresh_key),)
            if refresh_key is not None
            else tuple(_REFRESH_STATES.values())
        )
        return any(
            state.future is not None and not state.future.done()
            for state in states
            if state is not None
        )


def _poll_refresh_once(refresh_key: RefreshKey) -> None:
    """Trigger one full rerun when the selected background refresh completes."""
    if not poll_data_refresh(refresh_key):
        st.rerun()


# Lazily built on first render — never call st.fragment at import time.
# Module-level fragment registration breaks multipage imports on Streamlit Cloud.
_refresh_status_poller = None


def _get_refresh_status_poller():
    """Return a fragment poller, creating it once inside an active script run."""
    global _refresh_status_poller
    if _refresh_status_poller is not None:
        return _refresh_status_poller
    if not hasattr(st, "fragment"):
        _refresh_status_poller = False
        return None
    try:
        _refresh_status_poller = st.fragment(run_every=2.0)(_poll_refresh_once)
    except Exception:
        logger.exception("Could not create refresh-status fragment poller")
        _refresh_status_poller = False
        return None
    return _refresh_status_poller


def render_data_refresh_status(result: DataLoadResult, source: str) -> None:
    """Explain which snapshot is shown and poll only this view's refresh."""
    if result.pending:
        st.caption(f"Live {source} update in progress — showing bundled data.")
        poller = _get_refresh_status_poller()
        if result.refresh_key is not None and poller:
            poller(result.refresh_key)
    elif result.status == "error":
        detail = f" Details: {result.error}" if result.error else ""
        st.warning(f"Live {source} update unavailable — showing bundled data.{detail}")


def _local_first_load(
    source: str,
    symbols: Tuple[str, ...],
    start_date: date,
    end_date: date,
    *,
    use_live: bool,
    force_refresh: bool,
) -> DataLoadResult:
    symbols = tuple(symbols)
    _collect_refreshes()

    live_start = _live_fetch_start(symbols, start_date, end_date) if use_live else None
    if live_start is None:
        merged = []
        for symbol in symbols:
            series = _merge_live_and_stored(symbol, None)
            if not series.empty:
                merged.append(series)
        frame = pd.concat(merged, axis=1).sort_index() if merged else pd.DataFrame()
        return DataLoadResult(_filter_requested_range(frame, start_date, end_date), "fresh", False)

    refresh_key = (source, symbols, live_start, end_date)
    state = _start_refresh(
        source,
        symbols,
        live_start,
        end_date,
        force=force_refresh,
    )
    with _REFRESH_LOCK:
        live_frame = state.live_frame.copy() if state.live_frame is not None else pd.DataFrame()
        pending = state.future is not None and not state.future.done()
        error = state.error
        last_updated = state.last_updated

    merged_frames: list[pd.Series] = []
    for symbol in symbols:
        live_series = live_frame[symbol] if symbol in live_frame.columns else None
        series = _merge_live_and_stored(symbol, live_series)
        if not series.empty:
            merged_frames.append(series)
    frame = pd.concat(merged_frames, axis=1).sort_index() if merged_frames else pd.DataFrame()
    status: Literal["fresh", "pending", "error"]
    if pending:
        status = "pending"
    elif error:
        status = "error"
    else:
        status = "fresh"
    return DataLoadResult(
        _filter_requested_range(frame, start_date, end_date),
        status,
        pending,
        error,
        last_updated,
        refresh_key,
    )


def load_data_local_first(
    tickers: Tuple[str, ...],
    start_date: date,
    end_date: date,
    *,
    use_live: bool = True,
    force_refresh: bool = False,
) -> DataLoadResult:
    """Render bundled prices immediately and revalidate Yahoo in the background."""
    return _local_first_load(
        "yahoo", tickers, start_date, end_date,
        use_live=use_live, force_refresh=force_refresh,
    )


def load_fred_data_local_first(
    series_ids: Tuple[str, ...],
    start_date: date,
    end_date: date,
    *,
    use_live: bool = True,
    force_refresh: bool = False,
) -> DataLoadResult:
    """Render bundled FRED series immediately and revalidate in the background."""
    return _local_first_load(
        "fred", series_ids, start_date, end_date,
        use_live=use_live, force_refresh=force_refresh,
    )


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


TRAILING_HORIZONS = ("7-day", "30-day", "90-day", "1-year")
CALENDAR_HORIZONS = (
    "Week to date",
    "Month to date",
    "Quarter to date",
    "Year to date",
)


def compute_return_metrics(
    prices: pd.Series,
) -> tuple[dict[str, float | None], dict[str, float | None]] | None:
    """Trailing (7d–1y) and calendar (WTD–YTD) returns for one price series."""
    series = prices.dropna()
    if series.empty:
        return None

    last_day = series.index[-1]
    week_start = last_day - pd.Timedelta(days=int(last_day.weekday()))
    month_start = last_day.replace(day=1)
    quarter_month = ((last_day.month - 1) // 3) * 3 + 1
    quarter_start = last_day.replace(month=quarter_month, day=1)
    year_start = last_day.replace(month=1, day=1)

    trailing = {
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
    return trailing, calendar


def _format_observation_timestamp(timestamp: pd.Timestamp) -> str:
    """Format the observation timestamp from the price index."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def render_latest_prices_table(
    prices: pd.DataFrame,
    labels: dict[str, str] | None = None,
    *,
    inject_css: bool = True,
    transpose: bool = False,
) -> pd.Timestamp | None:
    """Show a table with the latest observed price for each column.

    When *transpose* is True the table has assets as columns and a single row,
    and the "Observed at" column is omitted (caller should display it elsewhere).

    Returns the latest observation timestamp across all columns, or None.
    """
    formatted: dict[str, str] = {}
    latest_ts: pd.Timestamp | None = None
    for col in prices.columns:
        series = prices[col].dropna()
        if series.empty:
            continue
        last_ts = series.index[-1]
        if latest_ts is None or last_ts > latest_ts:
            latest_ts = last_ts
        name = labels[col] if labels and col in labels else col
        formatted[name] = f"{series.iloc[-1]:,.2f}"
    if not formatted:
        return None
    if inject_css:
        st.markdown(RETURNS_TABLE_CSS, unsafe_allow_html=True)
    if transpose:
        table = pd.DataFrame(formatted, index=["Last price"])
    else:
        rows = []
        for name, price in formatted.items():
            row: dict[str, str] = {"Asset": name, "Last price": price}
            row["Observed at"] = _format_observation_timestamp(latest_ts)  # type: ignore[arg-type]
            rows.append(row)
        table = pd.DataFrame(rows)
    _show_returns_table(table)
    return latest_ts


def render_return_metrics(prices: pd.Series, *, inject_css: bool = True) -> None:
    """Trailing and calendar return tables for one price series."""
    metrics = compute_return_metrics(prices)
    if metrics is None:
        st.info("No prices available to compute returns.")
        return
    trailing, calendar = metrics

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
