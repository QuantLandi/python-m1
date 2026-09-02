from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    download_fred_data,
    get_available_date_bounds,
    preprocess,
)

CHART_COLOR = "#FF962F"

TREASURY_SERIES = [
    ("DGS1MO", "1M", 1 / 12),
    ("DGS3MO", "3M", 0.25),
    ("DGS6MO", "6M", 0.5),
    ("DGS1", "1Y", 1),
    ("DGS2", "2Y", 2),
    ("DGS3", "3Y", 3),
    ("DGS5", "5Y", 5),
    ("DGS7", "7Y", 7),
    ("DGS10", "10Y", 10),
    ("DGS20", "20Y", 20),
    ("DGS30", "30Y", 30),
]

OECD_10Y_SERIES = [
    ("IRLTLT01USM156N", "United States"),
    ("IRLTLT01DEM156N", "Germany"),
    ("IRLTLT01FRM156N", "France"),
    ("IRLTLT01ITM156N", "Italy"),
    ("IRLTLT01GBM156N", "United Kingdom"),
    ("IRLTLT01JPM156N", "Japan"),
    ("IRLTLT01ESM156N", "Spain"),
    ("IRLTLT01PTM156N", "Portugal"),
    ("IRLTLT01GRM156N", "Greece"),
]

ALL_FRED_IDS = tuple(series_id for series_id, _, _ in TREASURY_SERIES) + tuple(
    series_id for series_id, _ in OECD_10Y_SERIES
)

LOOKBACK_YEARS = {
    "1y": 1,
    "3y": 3,
    "5y": 5,
    "10y": 10,
    "20y": 20,
    "30y": 30,
    "max": None,
}

FRED_EARLIEST = date(1962, 1, 2)


def _lookback_start(end: date, years: int | None, earliest: date) -> date:
    if years is None:
        return earliest
    try:
        start = end.replace(year=end.year - years)
    except ValueError:
        start = end.replace(year=end.year - years, month=2, day=28)
    return max(earliest, start)


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


def _latest_snapshot(frame: pd.DataFrame) -> tuple[pd.Timestamp, pd.Series] | None:
    filled = frame.ffill()
    valid = filled.dropna(how="all")
    if valid.empty:
        return None
    as_of = valid.index[-1]
    return as_of, filled.loc[as_of]


def render() -> None:
    st.header(":material/stacked_line_chart: Bonds")
    st.caption("U.S. Treasury curve and OECD 10-year government yields (FRED).")

    bounds = get_available_date_bounds("DGS10")
    earliest_date = bounds[0] if bounds else FRED_EARLIEST

    def _apply_lookback() -> None:
        end = DEFAULT_END_DATE
        years = LOOKBACK_YEARS[st.session_state.bonds_lookback]
        st.session_state.bonds_end_date = end
        st.session_state.bonds_start_date = _lookback_start(end, years, earliest_date)

    if "bonds_lookback" not in st.session_state:
        st.session_state.bonds_lookback = "5y"
    if "bonds_start_date" not in st.session_state or "bonds_end_date" not in st.session_state:
        _apply_lookback()

    with st.sidebar:
        st.selectbox(
            "Lookback",
            list(LOOKBACK_YEARS),
            key="bonds_lookback",
            on_change=_apply_lookback,
        )
        start_date = st.date_input(
            "Start date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="bonds_start_date",
        )
        end_date = st.date_input(
            "End date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="bonds_end_date",
        )

    if start_date > end_date:
        st.warning("Start date must be on or before the end date.")
        return
    if start_date == end_date:
        st.warning("Date range must span at least two distinct dates.")
        return

    yields = download_fred_data(ALL_FRED_IDS, start_date, end_date, use_live=True)
    yields = preprocess(yields)

    if yields.empty:
        st.error(
            "No yield data returned from FRED. "
            "The public feed may be unavailable — bundled fallback data is missing too."
        )
        return

    snapshot = _latest_snapshot(yields)
    if snapshot is None:
        st.warning("No observations in the selected date range.")
        return
    as_of, latest = snapshot
    as_of_text = as_of.strftime("%Y-%m-%d")
    st.sidebar.caption(f"Last updated: {as_of_text}")

    treasury_ids = [series_id for series_id, _, _ in TREASURY_SERIES]
    oecd_ids = [series_id for series_id, _ in OECD_10Y_SERIES]
    oecd_labels = {series_id: label for series_id, label in OECD_10Y_SERIES}
    treasury_labels = {series_id: label for series_id, label, _ in TREASURY_SERIES}

    oecd_latest = latest.reindex(oecd_ids).dropna().sort_values()
    if oecd_latest.empty:
        st.info("OECD 10Y yield snapshot unavailable.")
    else:
        labels = [oecd_labels[series_id] for series_id in oecd_latest.index]
        fig = go.Figure(
            data=[
                go.Bar(
                    x=labels,
                    y=oecd_latest.astype(float),
                    marker=dict(color=_orange_gradient(len(oecd_latest))),
                    hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            title=f"OECD 10-year yields ({as_of_text})",
            yaxis_title="Yield (%)",
            height=420,
            template="plotly_white",
            margin=dict(t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    curve_rows = []
    for series_id, tenor, years in TREASURY_SERIES:
        value = latest.get(series_id)
        if pd.isna(value):
            continue
        curve_rows.append((years, tenor, float(value)))
    if not curve_rows:
        st.info("U.S. Treasury yield curve snapshot unavailable.")
    else:
        curve_rows.sort(key=lambda row: row[0])
        maturities, tenors, values = zip(*curve_rows)
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=list(maturities),
                    y=list(values),
                    mode="lines+markers",
                    line=dict(width=2, color=CHART_COLOR),
                    marker=dict(size=8, color=CHART_COLOR),
                    customdata=list(tenors),
                    hovertemplate="Tenor: %{customdata}<br>Yield: %{y:.2f}%<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            title=f"U.S. Treasury curve ({as_of_text})",
            xaxis_title="Maturity (years)",
            yaxis_title="Yield (%)",
            height=420,
            template="plotly_white",
            margin=dict(t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    oecd_history = yields[[col for col in oecd_ids if col in yields.columns]].dropna(how="all")
    if oecd_history.empty:
        st.info("OECD 10Y time series unavailable.")
    else:
        fig = go.Figure()
        for series_id in oecd_history.columns:
            fig.add_trace(
                go.Scatter(
                    x=oecd_history.index,
                    y=oecd_history[series_id],
                    mode="lines",
                    name=oecd_labels[series_id],
                    hovertemplate="%{y:.2f}%<br>%{x|%Y-%m-%d}<extra>%{fullData.name}</extra>",
                )
            )
        fig.update_layout(
            title="OECD 10-year yields over time",
            yaxis_title="Yield (%)",
            xaxis_title="Date",
            height=420,
            template="plotly_white",
            hovermode="x unified",
            margin=dict(t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    treasury_history = yields[
        [col for col in treasury_ids if col in yields.columns]
    ].dropna(how="all")
    if treasury_history.empty:
        st.info("U.S. Treasury time series unavailable.")
    else:
        fig = go.Figure()
        for series_id in treasury_history.columns:
            fig.add_trace(
                go.Scatter(
                    x=treasury_history.index,
                    y=treasury_history[series_id],
                    mode="lines",
                    name=treasury_labels[series_id],
                    hovertemplate="%{y:.2f}%<br>%{x|%Y-%m-%d}<extra>%{fullData.name}</extra>",
                )
            )
        fig.update_layout(
            title="U.S. Treasury yields over time",
            yaxis_title="Yield (%)",
            xaxis_title="Date",
            height=420,
            template="plotly_white",
            hovermode="x unified",
            margin=dict(t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)


render()
