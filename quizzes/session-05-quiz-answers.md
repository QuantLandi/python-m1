# Session 5 quiz — Answer key (instructor only)

---

## Question 1 (Chapter 1 — Datetime index from `to_datetime`)

Consider the following code:

```python
import pandas as pd
import numpy as np

Data = {'Close': np.random.normal(size=3, loc=1)}
dates_range = pd.to_datetime(['2026-1-1', '2026-2-3', '2026-3-7'])
df = pd.DataFrame(data=Data, index=dates_range)
print(df)
```

A. `np.random.normal(size=3, loc=1)` generates 3 random numbers from a normal distribution with a mean of 1. — **True**
B. `dates_range` contains 3 dates. — **True**
C. `pd.to_datetime()` converts the date strings into pandas datetime values. — **True**
D. `df` contains 3 rows and 1 column named `"Close"`. — **True**
E. Running the code multiple times will always produce exactly the same values in the `"Close"` column. — **False**

**CORRECT ANSWERS: A, B, C, D**

**Debrief tip:** From Ch 1 — `to_datetime` builds a time-series index; without a seed, `np.random.normal` changes every run. Show `df.index` and re-run once live.

---

## Question 2 (Chapter 1 — Index `.difference()`)

Consider the following code:

```python
import pandas as pd

aapl_dates = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"])
msft_dates = pd.to_datetime(["2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09"])

difference = aapl_dates.difference(msft_dates)
print(difference)
```

A. `aapl_dates.difference(msft_dates)` returns the dates that are present in `aapl_dates` but not in `msft_dates`. — **True**
B. In the example, `"2026-01-05"` is present in `aapl_dates` but not in `msft_dates`. — **True**
C. `msft_dates.difference(aapl_dates)` returns `"2026-01-05"`. — **False**
D. `df1.index.difference(df2.index)` can be used to identify dates that exist in `df1` but are missing from `df2`. — **True**
E. `.difference()` modifies the original Index permanently. — **False**

**CORRECT ANSWERS: A, B, D**

**Debrief tip:** From Ch 1 — `.difference()` is asymmetric and returns a new Index. Live: `msft_dates.difference(aapl_dates)` → `2026-01-09`.

---

## Question 3 (Chapter 2 — `pct_change()` returns)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=5),
    "close": [100, 105, 102, 108, 120]
})

df["rendement"] = df["close"].pct_change() * 100
print(df)
```

A. `pd.date_range("2026-01-01", periods=5)` creates five consecutive daily dates. — **True**
B. `df["close"].pct_change()` calculates the percentage change between consecutive closing prices. — **True**
C. Multiplying by 100 converts the returns from decimal form into percentage form. — **True**
D. The first value of the `"rendement"` column will be `0`. — **False**
E. The return on the second row is 5%. — **True**

**CORRECT ANSWERS: A, B, C, E**

**Debrief tip:** From Ch 2 — first `pct_change` is `NaN` (no prior price). Check: `(105 - 100) / 100 * 100 = 5`.

---

## Question 4 (Chapter 2 — `resample().last()`)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=10, freq="D"),
    "close": [100, 102, 101, 105, 107, 106, 110, 112, 111, 115]
})

df = df.set_index("date")
weekly = df.resample("W").last()
print(df)
```

A. `pd.date_range(..., periods=10, freq="D")` creates 10 consecutive daily dates. — **True**
B. `df.set_index("date")` makes the date column the index of the DataFrame. — **True**
C. `df.resample("W").last()` converts the daily data into weekly data and keeps the last observation of each week. — **True**
D. `print(df)` displays the weekly DataFrame stored in `weekly`. — **False**
E. `resample("W")` is an example of downsampling because the data goes from daily frequency to weekly frequency. — **True**

**CORRECT ANSWERS: A, B, C, E**

**Debrief tip:** From Ch 2 — students often print the wrong object. Contrast `print(df)` vs `print(weekly)`.

---

## Question 5 (Chapter 2 — OHLC aggregation with `resample`)

Consider the following code:

```python
import yfinance as yf

# Download daily data
df = yf.download("AAPL", start="2025-01-01", end="2026-01-01")

# Downsample daily data to weekly data
weekly = df.resample("W-FRI").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
})
print(weekly)
```

A. `yf.download("AAPL", ...)` downloads historical market data for Apple. — **True**
B. `resample("W-FRI")` converts the daily data into weekly data, with weeks ending on Friday. — **True**
C. `"High": "max"` selects the highest price recorded during each week. — **True**
D. `"Close": "first"` selects the first closing price of each week. — **False**
E. Converting daily data into weekly data using `resample()` is an example of downsampling. — **True**

**CORRECT ANSWERS: A, B, C, E**

**Debrief tip:** From Ch 2 — read the agg dict carefully: the code uses `"Close": "last"`, not `"first"`.

---

## Question 6 (Chapter 2 — `asfreq` with `ffill` / `bfill`)

Consider the following code:

```python
import pandas as pd

weekly = pd.DataFrame(
    data=range(10, 210, 20),
    index=pd.date_range(start='2026-1-1', periods=10, freq='W'),
)
daily1 = weekly.asfreq('D')
daily2 = weekly.asfreq('D', method='bfill')
daily3 = weekly.asfreq('D', method='ffill')
print(daily1)
print(daily2)
print(daily3)
```

A. `range(10, 210, 20)` creates 10 values starting at 10 and increasing by 20. — **True**
B. `freq='W'` creates a weekly date index. — **True**
C. `weekly.asfreq('D')` converts the weekly DataFrame to daily frequency and automatically fills the new values. — **False**
D. `method='bfill'` fills missing values using the next available value. — **True**
E. `method='ffill'` fills missing values using the previous available value. — **True**

**CORRECT ANSWERS: A, B, D, E**

**Debrief tip:** From Ch 2 — bare `asfreq('D')` inserts `NaN`s; filling is opt-in via `method` (or `.ffill()` / `.bfill()` afterward).

---

## Question 7 (Chapter 2 — Resample on missing OHLC columns)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=10),
    "close": [100, 102, 101, 105, 107, 106, 110, 112, 111, 115]
})
df = df.set_index("date")
weekly = df.resample("W-FRI").agg({
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
})
```

A. `df.set_index("date")` makes the date column the index of the DataFrame. — **True**
B. `"W-FRI"` means that the data is resampled into weeks ending on Friday. — **True**
C. `"close": "last"` selects the last closing price available in each week. — **True**
D. The code will run successfully because pandas automatically creates the `"open"`, `"high"`, and `"low"` columns. — **False**
E. If the DataFrame contained OHLC data, `"high": "max"` would select the highest value observed during each week. — **True**

**CORRECT ANSWERS: A, B, C, E**

**Debrief tip:** From Ch 2 — `.agg({"open": ...})` looks up existing columns; missing names → `KeyError`. Only `"close"` exists here.

---

## Question 8 (Chapter 3 — Rolling mean and std)

Consider the following code:

```python
import yfinance as yf

stock = yf.download("AAPL", start="2025-01-01", end="2026-01-01")

print(df.head())

stock["MA20"] = stock["Close"].rolling(window=20).mean()
stock["rolling_std"] = stock["Close"].rolling(20).std()
```

A. `yf.download("AAPL", start="2025-01-01", end="2026-01-01")` downloads Apple's historical market data for the specified period. — **True**
B. `stock["MA20"] = stock["Close"].rolling(window=20).mean()` calculates a 20-observation moving average of the closing price. — **True**
C. `rolling(20).std()` calculates the standard deviation of the entire `Close` column, rather than a rolling standard deviation. — **False**
D. The first 19 values of `MA20` will normally be `NaN` because there aren't yet 20 observations available. — **True**
E. `print(df.head())` correctly displays the first five rows of the downloaded data. — **False**

**CORRECT ANSWERS: A, B, D**

**Debrief tip:** From Ch 3 — rolling windows need `min_periods` worth of data (default = window). Variable name trap: object is `stock`, not `df`.

---

## Question 9 (Chapter 3 — `shift` lags and leads)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({
    "close": [100, 105, 102, 108, 110]
})

df["close_lag1"] = df["close"].shift(1)
df["close_lag2"] = df["close"].shift(-1)
df["return"] = df.close - df.close_lag2
print(df)
```

A. `df["close"].shift(1)` creates a column containing the previous observation's closing price. — **True**
B. `df["close"].shift(-1)` creates a column containing the next observation's closing price. — **True**
C. The first value of `close_lag1` will be `NaN`. — **True**
D. The last value of `close_lag2` will be `NaN`. — **True**
E. `df["return"] = df.close - df.close_lag2` calculates the percentage return of the stock. — **False**

**CORRECT ANSWERS: A, B, C, D**

**Debrief tip:** From Ch 3 — `shift(1)` lags, `shift(-1)` leads; subtraction is a price difference, not a percent return (`pct_change`).

---

## Question 10 (Chapter 2 — Cumulative return with `cumprod`)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({
    "close": [100, 105, 102, 108, 110]
})

df["return"] = df["close"].pct_change()
df["cumulative_return"] = (1 + df["return"]).cumprod() - 1
```

A. `df["close"].pct_change()` calculates the percentage change between consecutive closing prices. — **True**
B. The first value of `df["return"]` will be `NaN`. — **True**
C. `.cumprod()` calculates the cumulative product of the values over time. — **True**
D. `cumulative_return` is calculated by simply adding all the individual returns together. — **False**
E. If the initial price is 100 and the final price is 110, the cumulative return will be 10%. — **True**

**CORRECT ANSWERS: A, B, C, E**

**Debrief tip:** From Ch 2 — cumulative return compounds: `(1 + r).cumprod() - 1`, not a plain sum of returns.

---

## Question 11 (Review — Normalize prices with `.div`)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({"AAPL": [100, 105, 110], "MSFT": [200, 210, 220]})
normalized = df.div(df.iloc[0])
performance = df.div(df.iloc[0]).mul(100)
```

A. `df.iloc[0]` selects the first row of the DataFrame. — **True**
B. `df.div(df.iloc[0])` divides each column by its corresponding value in the first row. — **True**
C. The value of `normalized["AAPL"].iloc[1]` is `1.05`. — **True**
D. `performance` contains values expressed as percentages, with the first row equal to `1` for both stocks. — **False**
E. `normalized` and `performance` contain the same values. — **False**

**CORRECT ANSWERS: A, B, C**

**Debrief tip:** Review — after `.mul(100)`, the first row is `100`, not `1`. `performance` is `normalized * 100`.

---

## Question 12 (Review — Position value with `.mul`)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({
    "AAPL": [100, 105, 110],
    "MSFT": [200, 210, 220]
})

shares = pd.Series({
    "AAPL": 10,
    "MSFT": 5
})
position_value = df.mul(shares)
print(position_value)
```

A. `shares` is a pandas Series containing the number of shares held for each stock. — **True**
B. `df.mul(shares)` multiplies each stock price by the corresponding number of shares. — **True**
C. The value of `position_value["AAPL"].iloc[0]` is `1,000`. — **True**
D. The value of `position_value["MSFT"].iloc[2]` is `1,100`. — **True**
E. Pandas matches the values in `shares` to the columns of `df` using their labels (`AAPL` and `MSFT`). — **True**

**CORRECT ANSWERS: A, B, C, D, E**

**Debrief tip:** Review — label alignment: `AAPL` × 10 and `MSFT` × 5. Spot-check `100 * 10 = 1000` and `220 * 5 = 1100`.
