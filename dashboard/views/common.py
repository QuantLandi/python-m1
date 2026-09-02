"""Shared helpers for the Cross-Asset Market Monitor."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Tuple

import pandas as pd
import streamlit as st
import yfinance as yf

DEFAULT_START_DATE = date(1900, 1, 1)
DEFAULT_END_DATE = date.today()

DATA_CACHE_DIR = Path("data_cache")
DATA_CACHE_DIR.mkdir(exist_ok=True)


def _cache_path(symbol: str) -> Path:
    return DATA_CACHE_DIR / f"{symbol}.csv"


@st.cache_data(show_spinner=False)
def download_data(
    tickers: Tuple[str, ...],
    start_date: date,
    end_date: date,
    *,
    use_live: bool = True,
) -> pd.DataFrame:
    """Fetch adjusted close prices with optional CSV fallback when live data is unavailable."""
    if not tickers:
        return pd.DataFrame()

    tickers = tuple(tickers)
    fetched = pd.DataFrame()

    if use_live:
        try:
            price_frame = yf.download(
                list(tickers),
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False,
            )
            close_prices = price_frame["Close"] if "Close" in price_frame else price_frame
            if isinstance(close_prices, pd.Series):
                close_prices = close_prices.to_frame(name=tickers[0])

            close_prices.index = close_prices.index.tz_localize(None)

            if not close_prices.empty:
                fetched = close_prices
                for symbol in tickers:
                    if symbol not in fetched.columns:
                        continue
                    cache_series = fetched[[symbol]].rename(columns={symbol: "Close"})
                    path = _cache_path(symbol)
                    if path.exists():
                        existing = pd.read_csv(path, index_col=0, parse_dates=True)
                        existing.index = existing.index.tz_localize(None)
                        cache_series = pd.concat([existing, cache_series]).sort_index()
                        cache_series = cache_series[~cache_series.index.duplicated(keep="last")]
                    cache_series.to_csv(path)
        except Exception:
            fetched = pd.DataFrame()

    if fetched.empty:
        cached_frames = []
        for symbol in tickers:
            path = _cache_path(symbol)
            if not path.exists():
                continue
            cached = pd.read_csv(path, index_col=0, parse_dates=True)
            cached.index = cached.index.tz_localize(None)
            cached_frames.append(cached.rename(columns={cached.columns[0]: symbol}))
        if cached_frames:
            fetched = pd.concat(cached_frames, axis=1).sort_index()

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
