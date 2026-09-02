#import "lib.typ": *

#show: tutorial.with(
  session: 11,
  title: "Stretch --- Commodities then Currencies",
  goal: [Optional: futures return snapshot, then a G8 FX matrix and one pair chart.],
  you-leave-with: [Whatever you finish. Skipping this session's stretch is fine for the exam if Stocks and Bonds work.],
)

This session is *stretch*. If last week is incomplete, stay on Bonds (empty states, captions, last-updated). Session 12 will not add tabs.

*Order:* Commodities first (reuses `download_data` and return tables). Currencies second (new FX logic). Do not start FX if commodities is still messy.

#cmd("uv run streamlit run dashboard.py")

== Part A --- Commodities (first)

Universe (Yahoo futures):

- Metals: `GC=F` Gold, `SI=F` Silver, `HG=F` Copper
- Energy: `CL=F` WTI, `BZ=F` Brent, `NG=F` Natural gas
- Grains: `ZW=F` Wheat, `ZC=F` Corn

Bundled files look like `GC_F.csv` (`=` becomes `_`).

Sidebar keys: `commodities_lookback`, `commodities_start_date`, `commodities_end_date`, plus a multiselect of *names* (default: all).

Fetch extra history like Stocks (`end - 365 days`) so 1-year returns work.

For each selected ticker that has a column in `prices`:

1. `compute_return_metrics(prices[ticker])`
2. `st.subheader` with the human name
3. `render_return_metrics(...)`

Then two *2×2* bar charts (trailing horizons, then calendar horizons). Each subplot is one horizon; bars are the selected names. Use `plotly.subplots.make_subplots(rows=2, cols=2, ...)`.

If time is short: *tables only*, skip the bar grids.

```python
from datetime import date, timedelta

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from views.common import (
    CALENDAR_HORIZONS,
    DEFAULT_END_DATE,
    LOOKBACK_YEARS,
    TRAILING_HORIZONS,
    chart_layout,
    compute_return_metrics,
    date_range_error,
    download_data,
    get_available_date_bounds,
    lookback_start,
    render_return_metrics,
)
```

Add to `common.py` if missing:

```python
TRAILING_HORIZONS = ("7-day", "30-day", "90-day", "1-year")
CALENDAR_HORIZONS = (
    "Week to date",
    "Month to date",
    "Quarter to date",
    "Year to date",
)
```

No price-path line charts on this tab. No regime colours.

== Part B --- Currencies (if Part A works)

G8: USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD.

Yahoo *USD legs* (not every cross):

```python
USD_LEGS = {
    "EUR": ("EURUSD=X", "usd_quote"),
    "GBP": ("GBPUSD=X", "usd_quote"),
    "AUD": ("AUDUSD=X", "usd_quote"),
    "NZD": ("NZDUSD=X", "usd_quote"),
    "JPY": ("USDJPY=X", "usd_base"),
    "CHF": ("USDCHF=X", "usd_base"),
    "CAD": ("USDCAD=X", "usd_base"),
}
```

`usd_quote` means the ticker is already USD per 1 foreign unit. `usd_base` means foreign per 1 USD, so invert: `1 / price`.

```python
def usd_per_unit(leg_price: float, convention: str) -> float:
    if convention == "usd_quote":
        return float(leg_price)
    return 1.0 / float(leg_price)
```

Build daily USD-per-unit paths, then a pair:

```python
def pair_rate(usd_paths, numerator: str, denominator: str):
    name = f"{numerator}/{denominator}"
    if numerator == denominator:
        return pd.Series(1.0, index=usd_paths.index, name=name)
    return (usd_paths[numerator] / usd_paths[denominator]).dropna().rename(name)
```

Spot matrix (latest day): units of *column* per 1 unit of *row* $= "usd_per[row] / usd_per[col]"$.

Sidebar keys: `currencies_lookback`, `currencies_start_date`, `currencies_end_date`, plus numerator and denominator selectboxes.

Download `FX_TICKERS` with `download_data`. Bundled files: `EURUSD_X.csv`, etc.

*Enough for class:* `st.dataframe` of the matrix + one Plotly line for the selected pair. Clickable matrix cells are optional.

No correlation heatmap. No overlays on this tab.

== Commit whatever you have

#cmd("git add views/commodities.py views/currencies.py views/common.py
git commit -m \"session 11: stretch tabs\"")

== Next week

*Feature freeze.* We deploy and practise *reading* code. Do not open new features.
