from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from views.common import (
    DATA_CACHE_DIR,
    DATA_DIR,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    download_data,
    get_available_date_bounds,
    preprocess,
)

SP500_TICKER = "^GSPC"
SP500_BUNDLED_FILE = "GSPC.csv"
LOOKBACK_YEARS = {
    "1y": 1,
    "3y": 3,
    "5y": 5,
    "10y": 10,
    "20y": 20,
    "30y": 30,
    "max": None,
}


def _lookback_start(end: date, years: int | None, earliest: date) -> date:
    if years is None:
        return earliest
    try:
        start = end.replace(year=end.year - years)
    except ValueError:
        start = end.replace(year=end.year - years, month=2, day=28)
    return max(earliest, start)


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


def _format_return(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:+.1%}"


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
    html = frame.to_html(index=False, classes="returns-table", border=0, justify="center")
    st.markdown(html, unsafe_allow_html=True)


def _render_return_metrics(prices: pd.Series) -> None:
    last_day = prices.dropna().index[-1]
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

    st.markdown(RETURNS_TABLE_CSS, unsafe_allow_html=True)
    st.caption("Trailing returns")
    _show_returns_table(trailing_table)
    st.caption("Calendar returns")
    _show_returns_table(calendar_table)


def render() -> None:
    st.header(":material/table_chart_view: Stocks")
    st.caption("Integrated stock analytics covering flagship single names.")

    bounds = get_available_date_bounds(SP500_TICKER)
    if bounds is None:
        st.sidebar.warning("Bundled S&P 500 history file missing — date range may be limited.")
    earliest_date = bounds[0] if bounds else DEFAULT_START_DATE

    def _apply_lookback() -> None:
        end = DEFAULT_END_DATE
        years = LOOKBACK_YEARS[st.session_state.lookback]
        st.session_state.end_date = end
        st.session_state.start_date = _lookback_start(end, years, earliest_date)

    if "lookback" not in st.session_state:
        st.session_state.lookback = "1y"
    if "start_date" not in st.session_state or "end_date" not in st.session_state:
        _apply_lookback()

    with st.sidebar:
        st.selectbox(
            "Lookback",
            list(LOOKBACK_YEARS),
            key="lookback",
            on_change=_apply_lookback,
        )
        start_date = st.date_input(
            "Start date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="start_date",
        )
        end_date = st.date_input(
            "End date",
            min_value=earliest_date,
            max_value=DEFAULT_END_DATE,
            key="end_date",
        )

    if start_date > end_date:
        st.warning("Start date must be on or before the end date.")
        return

    if start_date == end_date:
        st.warning("Date range must span at least two distinct dates.")
        return

    metrics_start = max(earliest_date, end_date - timedelta(days=365 + 21))
    fetch_start = min(start_date, metrics_start)
    prices = download_data((SP500_TICKER,), fetch_start, end_date, use_live=True)
    prices = preprocess(prices)

    if prices.empty:
        st.error(
            "No data returned for the S&P 500. "
            "Yahoo Finance may be unavailable from this server — bundled fallback data is missing too."
        )
        return

    chart_mask = (prices.index >= pd.Timestamp(start_date)) & (
        prices.index <= pd.Timestamp(end_date)
    )
    chart_prices = prices.loc[chart_mask]
    if chart_prices.empty:
        st.warning("No observations in the selected date range.")
        return

    cache_file = DATA_CACHE_DIR / SP500_BUNDLED_FILE
    bundled_file = DATA_DIR / SP500_BUNDLED_FILE
    if not cache_file.exists() and bundled_file.exists():
        st.info("Showing bundled S&P 500 data (live Yahoo Finance fetch unavailable).")

    st.sidebar.caption(f"Last updated: {prices.index[-1].strftime('%Y-%m-%d')}")

    _render_return_metrics(prices[SP500_TICKER])

    series = chart_prices[SP500_TICKER]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series,
            mode="lines",
            name="S&P 500",
            line=dict(width=2, color="#FF962F"),
            hovertemplate="%{y:,.2f}<br>%{x|%Y-%m-%d}<extra>S&P 500</extra>",
        )
    )
    fig.update_layout(
        title="S&P 500",
        height=450,
        template="plotly_white",
        yaxis_title="Index level",
        xaxis_title="Date",
        hovermode="x unified",
        margin=dict(t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

render()
