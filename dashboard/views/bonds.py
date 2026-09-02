from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DEFAULT_END_DATE,
    LOOKBACK_YEARS,
    chart_layout,
    date_range_error,
    download_fred_data,
    get_available_date_bounds,
    lookback_start,
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

DEFAULT_TREASURY_TENORS = ("3M", "2Y", "10Y", "30Y")

FRED_EARLIEST = date(1953, 4, 1)


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


def _earliest_yield_date() -> date:
    """Allow the OECD 10Y start (1953); bundled DGS10 must not raise the floor."""
    starts = [FRED_EARLIEST]
    for series_id in ALL_FRED_IDS:
        bounds = get_available_date_bounds(series_id)
        if bounds is not None:
            starts.append(bounds[0])
    return min(starts)


def render() -> None:
    st.header(":material/stacked_line_chart: Bonds")
    st.caption("U.S. Treasury curve and OECD 10-year government yields (FRED).")

    earliest_date = _earliest_yield_date()

    def _apply_lookback() -> None:
        end = DEFAULT_END_DATE
        years = LOOKBACK_YEARS[st.session_state.bonds_lookback]
        st.session_state.bonds_end_date = end
        st.session_state.bonds_start_date = lookback_start(end, years, earliest_date)

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
        oecd_country_labels = [label for _, label in OECD_10Y_SERIES]
        selected_oecd_labels = st.multiselect(
            "OECD countries",
            options=oecd_country_labels,
            default=oecd_country_labels,
            key="oecd_countries",
        )
        treasury_tenor_labels = [label for _, label, _ in TREASURY_SERIES]
        selected_treasury_tenors = st.multiselect(
            "U.S. Treasury maturities",
            options=treasury_tenor_labels,
            default=list(DEFAULT_TREASURY_TENORS),
            key="treasury_tenors",
        )

    range_error = date_range_error(start_date, end_date)
    if range_error:
        st.warning(range_error)
        return

    yields = download_fred_data(ALL_FRED_IDS, start_date, end_date, use_live=True)
    if not yields.empty:
        yields = yields.ffill().dropna(how="all")

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

    oecd_labels = {series_id: label for series_id, label in OECD_10Y_SERIES}
    treasury_labels = {series_id: label for series_id, label, _ in TREASURY_SERIES}
    selected_oecd_ids = [
        series_id
        for series_id, label in OECD_10Y_SERIES
        if label in selected_oecd_labels
    ]

    if not selected_oecd_ids:
        st.info("Select at least one OECD country to display 10-year yields.")
    else:
        oecd_latest = latest.reindex(selected_oecd_ids).dropna().sort_values()
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
                **chart_layout(
                    title=f"OECD 10-year yields snapshot ({as_of_text})",
                    yaxis_title="Yield (%)",
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        oecd_history = yields[
            [col for col in selected_oecd_ids if col in yields.columns]
        ].dropna(how="all")
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
                **chart_layout(
                    title="OECD 10-year yields over time",
                    yaxis_title="Yield (%)",
                    xaxis_title="Date",
                    hovermode="x unified",
                )
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
        tenors = [row[1] for row in curve_rows]
        values = [row[2] for row in curve_rows]
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=tenors,
                    y=values,
                    mode="lines+markers",
                    line=dict(width=2, color=CHART_COLOR),
                    marker=dict(size=8, color=CHART_COLOR),
                    hovertemplate="Tenor: %{x}<br>Yield: %{y:.2f}%<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            **chart_layout(
                title=f"U.S. Treasury yield curve snapshot ({as_of_text})",
                xaxis_title="Tenor",
                yaxis_title="Yield (%)",
                xaxis=dict(type="category", dtick=1),
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    selected_treasury_ids = [
        series_id
        for series_id, label, _ in TREASURY_SERIES
        if label in selected_treasury_tenors
    ]
    if not selected_treasury_ids:
        st.info("Select at least one U.S. Treasury maturity to display yields over time.")
    else:
        treasury_history = yields[
            [col for col in selected_treasury_ids if col in yields.columns]
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
                **chart_layout(
                    title="U.S. Treasury yield curve over time",
                    yaxis_title="Yield (%)",
                    xaxis_title="Date",
                    hovermode="x unified",
                )
            )
            st.plotly_chart(fig, use_container_width=True)


render()
