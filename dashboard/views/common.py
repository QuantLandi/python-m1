"""Shared helpers for the Cross-Asset Market Monitor."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Tuple

import pandas as pd
import streamlit as st
import yfinance as yf

APP_DIR = Path(__file__).resolve().parent.parent
DATA_CACHE_DIR = APP_DIR / "data_cache"
DATA_DIR = APP_DIR / "data"
DATA_CACHE_DIR.mkdir(exist_ok=True)

DEFAULT_START_DATE = date(2010, 1, 1)  # fallback when no stored series exists
DEFAULT_END_DATE = date.today()


def _cache_path(symbol: str) -> Path:
    return DATA_CACHE_DIR / f"{symbol}.csv"


def _bundled_path(symbol: str) -> Path:
    return DATA_DIR / f"{symbol}.csv"


def _read_price_csv(path: Path, symbol: str) -> pd.Series | None:
    if not path.exists():
        return None
    frame = pd.read_csv(path, index_col=0, parse_dates=True)
    frame.index = frame.index.tz_localize(None)
    column = "Close" if "Close" in frame.columns else frame.columns[0]
    return frame[column].rename(symbol)


def _load_stored_series(symbol: str) -> pd.Series | None:
    """Load the widest available price series from bundled data and cache."""
    series_parts: list[pd.Series] = []
    for path in (_bundled_path(symbol), _cache_path(symbol)):
        part = _read_price_csv(path, symbol)
        if part is not None:
            series_parts.append(part)
    if not series_parts:
        return None
    combined = pd.concat(series_parts).sort_index()
    return combined[~combined.index.duplicated(keep="last")]


def get_available_date_bounds(symbol: str) -> tuple[date, date] | None:
    """Return the earliest and latest dates available in stored data for a symbol."""
    series = _load_stored_series(symbol)
    if series is None or series.empty:
        return None
    return series.index.min().date(), series.index.max().date()


def _merge_cache(symbol: str, close_series: pd.Series) -> None:
    path = _cache_path(symbol)
    cache_frame = close_series.rename("Close").to_frame()
    if path.exists():
        existing = pd.read_csv(path, index_col=0, parse_dates=True)
        existing.index = existing.index.tz_localize(None)
        cache_frame = pd.concat([existing, cache_frame]).sort_index()
        cache_frame = cache_frame[~cache_frame.index.duplicated(keep="last")]
    cache_frame.to_csv(path)


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
            _merge_cache(symbol, series)
    except Exception:
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
            _merge_cache(symbol, series)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, axis=1).sort_index()


def download_data(
    tickers: Tuple[str, ...],
    start_date: date,
    end_date: date,
    *,
    use_live: bool = True,
) -> pd.DataFrame:
    """Fetch prices via Yahoo Finance, then fall back to cache and bundled CSVs."""
    if not tickers:
        return pd.DataFrame()

    tickers = tuple(tickers)
    fetched = pd.DataFrame()

    if use_live:
        fetched = _fetch_live_prices(tickers, start_date, end_date)

    if fetched.empty:
        stored_frames = []
        for symbol in tickers:
            series = _load_stored_series(symbol)
            if series is not None:
                stored_frames.append(series)
        if stored_frames:
            fetched = pd.concat(stored_frames, axis=1).sort_index()

    if fetched.empty:
        return pd.DataFrame()

    mask = (fetched.index >= pd.Timestamp(start_date)) & (fetched.index <= pd.Timestamp(end_date))
    return fetched.loc[mask]


def load_data(file_path: str) -> pd.DataFrame:
    """Load a price series stored on disk."""
    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
    data.index = data.index.tz_localize(None)
    return data


def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill and remove missing observations."""
    if data.empty:
        return data
    return data.ffill().dropna()


def ensure_datetime_index(data: pd.DataFrame) -> pd.DataFrame:
    """Return a frame with a DatetimeIndex, even when the input is empty."""
    if data.empty:
        if isinstance(data.index, pd.DatetimeIndex):
            return data
        safe = data.copy()
        safe.index = pd.DatetimeIndex([], name="Date")
        return safe
    if isinstance(data.index, pd.DatetimeIndex):
        return data
    safe = data.copy()
    safe.index = pd.to_datetime(safe.index, errors="coerce")
    safe = safe[~safe.index.isna()]
    return safe


def normalize(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert a price series into cumulative returns starting at 1."""
    if prices.empty:
        return prices
    returns = prices.pct_change().fillna(0)
    return (1 + returns).cumprod()
