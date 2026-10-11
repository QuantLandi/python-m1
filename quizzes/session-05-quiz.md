# Session 5 quiz — Manipulating Time Series Data in Python

Ungraded in-class practice. Exam-style: code snippet + 5 true/false statements.

- **Review:** one question at a time
- **Scope:** full DataCamp course (Ch 1–4)
- **Plan:** 12 questions (Q11–Q12 are tricky review)

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

A. `np.random.normal(size=3, loc=1)` generates 3 random numbers from a normal distribution with a mean of 1.

B. `dates_range` contains 3 dates.

C. `pd.to_datetime()` converts the date strings into pandas datetime values.

D. `df` contains 3 rows and 1 column named `"Close"`.

E. Running the code multiple times will always produce exactly the same values in the `"Close"` column.

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

A. `aapl_dates.difference(msft_dates)` returns the dates that are present in `aapl_dates` but not in `msft_dates`.

B. In the example, `"2026-01-05"` is present in `aapl_dates` but not in `msft_dates`.

C. `msft_dates.difference(aapl_dates)` returns `"2026-01-05"`.

D. `df1.index.difference(df2.index)` can be used to identify dates that exist in `df1` but are missing from `df2`.

E. `.difference()` modifies the original Index permanently.

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

A. `pd.date_range("2026-01-01", periods=5)` creates five consecutive daily dates.

B. `df["close"].pct_change()` calculates the percentage change between consecutive closing prices.

C. Multiplying by 100 converts the returns from decimal form into percentage form.

D. The first value of the `"rendement"` column will be `0`.

E. The return on the second row is 5%.

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

A. `pd.date_range(..., periods=10, freq="D")` creates 10 consecutive daily dates.

B. `df.set_index("date")` makes the date column the index of the DataFrame.

C. `df.resample("W").last()` converts the daily data into weekly data and keeps the last observation of each week.

D. `print(df)` displays the weekly DataFrame stored in `weekly`.

E. `resample("W")` is an example of downsampling because the data goes from daily frequency to weekly frequency.

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

A. `yf.download("AAPL", ...)` downloads historical market data for Apple.

B. `resample("W-FRI")` converts the daily data into weekly data, with weeks ending on Friday.

C. `"High": "max"` selects the highest price recorded during each week.

D. `"Close": "first"` selects the first closing price of each week.

E. Converting daily data into weekly data using `resample()` is an example of downsampling.

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

A. `range(10, 210, 20)` creates 10 values starting at 10 and increasing by 20.

B. `freq='W'` creates a weekly date index.

C. `weekly.asfreq('D')` converts the weekly DataFrame to daily frequency and automatically fills the new values.

D. `method='bfill'` fills missing values using the next available value.

E. `method='ffill'` fills missing values using the previous available value.

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

A. `df.set_index("date")` makes the date column the index of the DataFrame.

B. `"W-FRI"` means that the data is resampled into weeks ending on Friday.

C. `"close": "last"` selects the last closing price available in each week.

D. The code will run successfully because pandas automatically creates the `"open"`, `"high"`, and `"low"` columns.

E. If the DataFrame contained OHLC data, `"high": "max"` would select the highest value observed during each week.

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

A. `yf.download("AAPL", start="2025-01-01", end="2026-01-01")` downloads Apple's historical market data for the specified period.

B. `stock["MA20"] = stock["Close"].rolling(window=20).mean()` calculates a 20-observation moving average of the closing price.

C. `rolling(20).std()` calculates the standard deviation of the entire `Close` column, rather than a rolling standard deviation.

D. The first 19 values of `MA20` will normally be `NaN` because there aren't yet 20 observations available.

E. `print(df.head())` correctly displays the first five rows of the downloaded data.

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

A. `df["close"].shift(1)` creates a column containing the previous observation's closing price.

B. `df["close"].shift(-1)` creates a column containing the next observation's closing price.

C. The first value of `close_lag1` will be `NaN`.

D. The last value of `close_lag2` will be `NaN`.

E. `df["return"] = df.close - df.close_lag2` calculates the percentage return of the stock.

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

A. `df["close"].pct_change()` calculates the percentage change between consecutive closing prices.

B. The first value of `df["return"]` will be `NaN`.

C. `.cumprod()` calculates the cumulative product of the values over time.

D. `cumulative_return` is calculated by simply adding all the individual returns together.

E. If the initial price is 100 and the final price is 110, the cumulative return will be 10%.

---

## Question 11 (Review — Normalize prices with `.div`)

Consider the following code:

```python
import pandas as pd

df = pd.DataFrame({"AAPL": [100, 105, 110], "MSFT": [200, 210, 220]})
normalized = df.div(df.iloc[0])
performance = df.div(df.iloc[0]).mul(100)
```

A. `df.iloc[0]` selects the first row of the DataFrame.

B. `df.div(df.iloc[0])` divides each column by its corresponding value in the first row.

C. The value of `normalized["AAPL"].iloc[1]` is `1.05`.

D. `performance` contains values expressed as percentages, with the first row equal to `1` for both stocks.

E. `normalized` and `performance` contain the same values.

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

A. `shares` is a pandas Series containing the number of shares held for each stock.

B. `df.mul(shares)` multiplies each stock price by the corresponding number of shares.

C. The value of `position_value["AAPL"].iloc[0]` is `1,000`.

D. The value of `position_value["MSFT"].iloc[2]` is `1,100`.

E. Pandas matches the values in `shares` to the columns of `df` using their labels (`AAPL` and `MSFT`).
