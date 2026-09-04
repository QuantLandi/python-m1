from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier, Event, Lock
import time

import pandas as pd
import pytest

import views.common as common
from views.common import (
    _storage_filename,
    date_range_error,
    download_data,
    download_fred_data,
    get_available_date_bounds,
    lookback_start,
    normalize,
    preprocess,
)
from views.currencies import last_usd_per_units, pair_rate, spot_cross_matrix, usd_per_unit


def test_storage_filename_strips_yahoo_prefix() -> None:
    assert _storage_filename("^GSPC") == "GSPC"
    assert _storage_filename("EURUSD=X") == "EURUSD_X"


def test_download_empty_ids_returns_empty_frame() -> None:
    start, end = date(2020, 1, 1), date(2020, 1, 31)
    assert download_data((), start, end).empty
    assert download_fred_data((), start, end).empty


def test_preprocess_empty_and_forward_fill() -> None:
    empty = pd.DataFrame()
    assert preprocess(empty).empty

    frame = pd.DataFrame(
        {"A": [1.0, None, 3.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    cleaned = preprocess(frame)
    assert list(cleaned["A"]) == [1.0, 1.0, 3.0]


def test_normalize_indexes_each_series_to_one() -> None:
    frame = pd.DataFrame(
        {"A": [50.0, 55.0, 60.0], "B": [200.0, 180.0, 220.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    indexed = normalize(frame)
    assert list(indexed["A"]) == [1.0, 1.1, 1.2]
    assert list(indexed["B"]) == [1.0, 0.9, 1.1]


def test_lookback_start_clamps_and_handles_leap_day() -> None:
    earliest = date(2000, 1, 1)
    assert lookback_start(date(2024, 6, 1), None, earliest) == earliest
    assert lookback_start(date(2024, 6, 1), 1, earliest) == date(2023, 6, 1)
    assert lookback_start(date(2024, 2, 29), 1, earliest) == date(2023, 2, 28)


def test_date_range_error() -> None:
    assert date_range_error(date(2020, 2, 1), date(2020, 1, 1))
    assert date_range_error(date(2020, 1, 1), date(2020, 1, 1))
    assert date_range_error(date(2020, 1, 1), date(2020, 1, 2)) is None


def test_offline_csv_load(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("views.common.DATA_DIR", tmp_path)

    csv_path = tmp_path / "GSPC.csv"
    pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]},
        index=pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"]),
    ).to_csv(csv_path)

    bounds = get_available_date_bounds("^GSPC")
    assert bounds == (date(2020, 1, 2), date(2020, 1, 6))

    prices = download_data(("^GSPC",), date(2020, 1, 2), date(2020, 1, 6), use_live=False)
    assert list(prices["^GSPC"]) == [100.0, 101.0, 102.0]


def test_live_fetch_starts_at_latest_stored_date(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("views.common.DATA_DIR", tmp_path)

    pd.DataFrame(
        {"Close": [4.0, 4.1]},
        index=pd.to_datetime(["2024-01-02", "2024-06-14"]),
    ).to_csv(tmp_path / "DGS10.csv")

    captured: dict[str, date] = {}

    def fake_fred(series_ids, start, end):
        captured["start"] = start
        captured["end"] = end
        return pd.DataFrame()

    monkeypatch.setattr("views.common._fetch_live_fred", fake_fred)
    download_fred_data(("DGS10",), date(1962, 1, 2), date(2024, 12, 31), use_live=True)
    assert captured["start"] == date(2024, 6, 14)
    assert captured["end"] == date(2024, 12, 31)

    captured.clear()
    download_fred_data(("DGS10",), date(1962, 1, 2), date(2024, 6, 14), use_live=True)
    assert captured == {}


def test_usd_per_unit_conventions() -> None:
    assert usd_per_unit(1.10, "usd_quote") == 1.10
    assert usd_per_unit(150.0, "usd_base") == 1.0 / 150.0


def test_spot_cross_matrix_from_usd_legs() -> None:
    usd_per = pd.Series({"USD": 1.0, "EUR": 1.10, "JPY": 1.0 / 150.0})
    matrix = spot_cross_matrix(usd_per)
    assert matrix.loc["EUR", "USD"] == 1.10
    assert matrix.loc["USD", "JPY"] == 150.0
    assert abs(matrix.loc["EUR", "JPY"] - 165.0) < 1e-9
    assert abs(matrix.loc["EUR", "JPY"] * matrix.loc["JPY", "EUR"] - 1.0) < 1e-9
    assert matrix.loc["USD", "USD"] == 1.0


def test_last_usd_per_units_aligns_legs() -> None:
    prices = pd.DataFrame(
        {
            "EURUSD=X": [1.10, 1.12],
            "GBPUSD=X": [1.25, 1.26],
            "AUDUSD=X": [0.65, 0.66],
            "NZDUSD=X": [0.58, 0.59],
            "USDJPY=X": [150.0, 148.0],
            "USDCHF=X": [0.90, 0.88],
            "USDCAD=X": [1.35, 1.36],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    as_of, usd_per = last_usd_per_units(prices)
    assert as_of.date() == date(2024, 1, 3)
    assert abs(usd_per["EUR"] - 1.12) < 1e-12
    assert abs(usd_per["JPY"] - 1.0 / 148.0) < 1e-12
    assert usd_per["USD"] == 1.0


def test_pair_rate_is_numerator_over_denominator() -> None:
    prices = pd.DataFrame(
        {
            "EURUSD=X": [1.10, 1.12],
            "GBPUSD=X": [1.25, 1.26],
            "AUDUSD=X": [0.65, 0.66],
            "NZDUSD=X": [0.58, 0.59],
            "USDJPY=X": [150.0, 148.0],
            "USDCHF=X": [0.90, 0.88],
            "USDCAD=X": [1.35, 1.36],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    _, usd_per = last_usd_per_units(prices)
    paths = pd.DataFrame([usd_per])
    eurusd = pair_rate(paths, "EUR", "USD").iloc[0]
    usdjpy = pair_rate(paths, "USD", "JPY").iloc[0]
    eurjpy = pair_rate(paths, "EUR", "JPY").iloc[0]
    assert abs(eurusd - 1.12) < 1e-12
    assert abs(usdjpy - 148.0) < 1e-12
    assert abs(eurjpy - 1.12 * 148.0) < 1e-9
    ones = pair_rate(paths, "EUR", "EUR")
    assert list(ones) == [1.0]


def test_yahoo_fallback_fetches_tickers_concurrently(monkeypatch) -> None:
    """A grouped Yahoo failure must fan out the per-ticker fallback workers."""
    tickers = ("AAA", "BBB", "CCC")
    entered = Barrier(len(tickers))
    active_lock = Lock()
    active = 0
    max_active = 0

    def fail_grouped(*args, **kwargs):
        raise RuntimeError("grouped endpoint unavailable")

    class FakeTicker:
        def __init__(self, symbol: str):
            self.symbol = symbol

        def history(self, **kwargs):
            nonlocal active, max_active
            with active_lock:
                active += 1
                max_active = max(max_active, active)
            try:
                # If the fallback were sequential, the first worker could
                # never pass this barrier and the test would fail promptly.
                entered.wait(timeout=2)
                index = pd.date_range("2024-01-02", periods=2, freq="D")
                return pd.DataFrame({"Close": [1.0, 2.0]}, index=index)
            finally:
                with active_lock:
                    active -= 1

    monkeypatch.setattr(common.yf, "download", fail_grouped)
    monkeypatch.setattr(common.yf, "Ticker", FakeTicker)

    result = common._fetch_live_prices_uncached(
        tickers, date(2024, 1, 1), date(2024, 1, 3)
    )

    assert max_active == len(tickers)
    assert list(result.columns) == list(tickers)
    assert result.shape == (2, len(tickers))


@pytest.fixture
def isolated_refresh_pool(monkeypatch):
    """Keep background-refresh futures isolated and shut down after each test."""
    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="test-refresh")
    monkeypatch.setattr(common, "_REFRESH_EXECUTOR", executor)
    monkeypatch.setattr(common, "_REFRESH_STATES", {})
    yield
    executor.shutdown(wait=True, cancel_futures=True)


def _write_local_series(tmp_path, symbol: str = "AAA") -> None:
    index = pd.to_datetime(["2024-01-01", "2024-01-02"])
    pd.DataFrame({"Close": [100.0, 101.0]}, index=index).to_csv(
        tmp_path / f"{symbol}.csv"
    )


def test_local_first_returns_local_data_while_refresh_is_pending(
    tmp_path, monkeypatch, isolated_refresh_pool
) -> None:
    _write_local_series(tmp_path)
    monkeypatch.setattr(common, "DATA_DIR", tmp_path)
    started = Event()
    release = Event()

    def blocked_worker(source, symbols, live_start, end_date):
        started.set()
        assert release.wait(timeout=2)
        return pd.DataFrame(
            {"AAA": [102.0]}, index=pd.to_datetime(["2024-01-03"])
        )

    monkeypatch.setattr(common, "_refresh_worker", blocked_worker)
    result = common.load_data_local_first(
        ("AAA",), date(2024, 1, 1), date(2024, 1, 3)
    )
    assert started.wait(timeout=1)
    assert result.status == "pending"
    assert result.pending is True
    assert list(result.data["AAA"]) == [100.0, 101.0]
    assert result.refresh_key is not None

    release.set()
    for _ in range(100):
        if not common.poll_data_refresh(result.refresh_key):
            break
        time.sleep(0.01)
    else:
        pytest.fail("background refresh did not complete")
    completed = common.load_data_local_first(
        ("AAA",), date(2024, 1, 1), date(2024, 1, 3)
    )
    assert completed.status == "fresh"
    assert completed.pending is False
    assert completed.error is None
    assert completed.last_updated is not None
    assert list(completed.data["AAA"]) == [100.0, 101.0, 102.0]


def test_local_first_exposes_background_refresh_error_and_keeps_local_data(
    tmp_path, monkeypatch, isolated_refresh_pool
) -> None:
    _write_local_series(tmp_path)
    monkeypatch.setattr(common, "DATA_DIR", tmp_path)
    started = Event()
    release = Event()

    def failed_worker(source, symbols, live_start, end_date):
        started.set()
        assert release.wait(timeout=2)
        raise RuntimeError("Yahoo unavailable")

    monkeypatch.setattr(common, "_refresh_worker", failed_worker)
    pending = common.load_data_local_first(
        ("AAA",), date(2024, 1, 1), date(2024, 1, 3)
    )
    assert started.wait(timeout=1)
    assert pending.status == "pending"

    release.set()
    for _ in range(100):
        if not common.poll_data_refresh(pending.refresh_key):
            break
        time.sleep(0.01)
    else:
        pytest.fail("background refresh did not complete")
    failed = common.load_data_local_first(
        ("AAA",), date(2024, 1, 1), date(2024, 1, 3)
    )
    assert failed.status == "error"
    assert failed.pending is False
    assert failed.error == "Yahoo unavailable"
    assert list(failed.data["AAA"]) == [100.0, 101.0]


def test_local_first_skips_refresh_when_bundle_covers_requested_end(
    tmp_path, monkeypatch, isolated_refresh_pool
) -> None:
    index = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=index).to_csv(
        tmp_path / "AAA.csv"
    )
    monkeypatch.setattr(common, "DATA_DIR", tmp_path)

    def unexpected_worker(*args, **kwargs):
        raise AssertionError("a covered local range should not refresh")

    monkeypatch.setattr(common, "_refresh_worker", unexpected_worker)
    result = common.load_data_local_first(
        ("AAA",), date(2024, 1, 1), date(2024, 1, 3)
    )
    assert result.status == "fresh"
    assert result.pending is False
    assert result.error is None
    assert result.refresh_key is None
    assert list(result.data["AAA"]) == [100.0, 101.0, 102.0]
