from datetime import date

import pandas as pd

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
