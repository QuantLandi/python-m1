# Session 4 quiz — Answer key (instructor only)

---

## Question 1 (Chapter 1 — `read_csv()` with `na_values` and `parse_dates`)

Consider the file `amex-listings.csv`:

```text
Stock Symbol,Company Name,Last Sale,IPO Year,Last Update
XXII,22nd Century Group,1.33,n/a,2017-04-26
FAX,Aberdeen Asia-Pacific Income Fund,5.00,1986,2017-04-25
IAF,Aberdeen Australia Equity Fund,n/a,n/a,2017-04-23
```

and the following code:

```python
import pandas as pd
amex = pd.read_csv('amex-listings.csv', na_values='n/a', parse_dates=['Last Update'])
print(amex['Last Sale'].dtype)
print(amex['IPO Year'].isna().sum())
```

A. `amex['Last Sale'].mean()` is equal to `3.165`. — **True**
B. `amex['IPO Year'].isna().sum()` is equal to `2`. — **True**
C. `amex.loc[2, 'Last Sale']` is the string `'n/a'`. — **False**
D. Without `parse_dates=['Last Update']`, the `Last Update` column would still have a datetime dtype. — **False**
E. `na_values='n/a'` tells pandas to read the text `n/a` as a missing value (`NaN`). — **True**

**CORRECT ANSWERS: A, B, E**

**Debrief tip:** From Ch 1 — `.info()` before and after `na_values` / `parse_dates`. Missing cells become `NaN` (so `Last Sale` is `float64` and `.mean()` skips them); dates stay text unless you ask pandas to parse them.

---

## Question 2 (Chapter 1 — `read_excel()` with several sheets)

The workbook `listings.xlsx` has three sheets named `amex`, `nasdaq`, and `nyse`. Consider the following code:

```python
import pandas as pd
xls = pd.ExcelFile('listings.xlsx')
print(xls.sheet_names)
listings = pd.read_excel('listings.xlsx', sheet_name=['amex', 'nasdaq'], na_values='n/a')
print(type(listings))
print(type(listings['nasdaq']))
```

A. `xls.sheet_names` is equal to `['amex', 'nasdaq', 'nyse']`. — **True**
B. `listings` is a DataFrame containing the rows of both sheets stacked together. — **False**
C. `listings['nasdaq']` is a DataFrame. — **True**
D. `pd.read_excel('listings.xlsx', na_values='n/a')` with no `sheet_name` argument reads all three sheets. — **False**
E. `list(listings.keys())` is equal to `['amex', 'nasdaq']`. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** From Ch 1 — a list in `sheet_name` returns a **dictionary** (keys = sheet names, values = DataFrames); no `sheet_name` means the first sheet only. Show `listings.keys()` live.

---

## Question 3 (Chapter 1 — Combining data with `pd.concat()`)

Consider the following code:

```python
import pandas as pd
amex = pd.DataFrame({'Stock Symbol': ['XXII', 'FAX'], 'Last Sale': [1.33, 5.00]})
nyse = pd.DataFrame({'Stock Symbol': ['JNJ', 'XOM', 'JPM'], 'Last Sale': [124.9, 82.1, 88.4]})
amex['Exchange'] = 'AMEX'
nyse['Exchange'] = 'NYSE'
listings = pd.concat([amex, nyse])
print(listings.shape)
print(listings['Exchange'].value_counts())
```

A. `listings.shape` is `(5, 3)`. — **True**
B. `amex['Exchange'] = 'AMEX'` fills every row of the new `Exchange` column with `'AMEX'`. — **True**
C. `pd.concat([amex, nyse])` places `nyse` to the right of `amex` as extra columns. — **False**
D. After `pd.concat([amex, nyse])`, `amex` has 5 rows. — **False**
E. `listings['Exchange'].value_counts()['NYSE']` is equal to `3`. — **True**

**CORRECT ANSWERS: A, B, E**

**Debrief tip:** From Ch 1 — the "add a reference column, then concatenate" pattern. Default `pd.concat` stacks rows (`axis=0`) and matches columns by name; it returns a new DataFrame and leaves `amex` and `nyse` untouched.

---

## Question 4 (Chapter 2 — Selecting stocks with `set_index()`, `idxmax()`, `nlargest()`)

Consider the following code:

```python
import pandas as pd
nyse = pd.DataFrame({
    'Stock Symbol': ['JNJ', 'XOM', 'JPM', 'ORCL', 'TSM'],
    'Sector': ['Health Care', 'Energy', 'Finance', 'Technology', 'Technology'],
    'Market Capitalization': [338.8e9, 338.7e9, 300.3e9, 181.0e9, 170.7e9]
})
nyse = nyse.set_index('Stock Symbol')
largest = nyse['Market Capitalization'].idxmax()
tech = nyse.loc[nyse['Sector'] == 'Technology', 'Market Capitalization'].idxmax()
top_2 = nyse['Market Capitalization'].nlargest(n=2)
```

A. `largest` is equal to `'JNJ'`. — **True**
B. `.idxmax()` returns the largest value, `338800000000.0`. — **False**
C. `tech` is equal to `'ORCL'`. — **True**
D. `top_2.index.tolist()` is equal to `['JNJ', 'XOM']`. — **True**
E. `nyse.loc[nyse['Sector'] == 'Technology']` has 3 rows. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** From Ch 2 — "get the ticker of the largest company": set the ticker as index so `.idxmax()` returns a **label** (ticker), not the value (`.max()`). `.nlargest(n=2)` keeps the index too, so `.index.tolist()` gives the tickers to pass to `DataReader`.

---

## Question 5 (Chapter 2 — MultiIndex and `.unstack()`)

Consider the following code:

```python
import pandas as pd
data = pd.DataFrame({
    'Date': ['2017-05-01', '2017-05-01', '2017-05-02', '2017-05-02'],
    'Ticker': ['AAPL', 'MSFT', 'AAPL', 'MSFT'],
    'Close': [146.6, 69.4, 147.5, 69.3]
}).set_index(['Date', 'Ticker'])
unstacked = data['Close'].unstack()
print(unstacked.shape)
print(unstacked.columns.tolist())
```

A. `data.index` is a MultiIndex with two levels, `Date` and `Ticker`. — **True**
B. `unstacked.shape` is `(4, 1)`. — **False**
C. `unstacked.columns.tolist()` is equal to `['AAPL', 'MSFT']`. — **True**
D. `unstacked.loc['2017-05-02', 'MSFT']` is equal to `69.3`. — **True**
E. `data['Close'].unstack()` returns a Series. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** From Ch 2 — long to wide: `.unstack()` moves the inner index level (`Ticker`) into the columns, giving a 2×2 DataFrame of closing prices, one column per ticker. Print `unstacked` so students see the shape.

---

## Question 6 (Chapter 3 — Central tendency, quantiles, and `.describe()`)

Consider the following code:

```python
import pandas as pd
nasdaq = pd.DataFrame({
    'Stock Symbol': ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'FB', 'XXII'],
    'Market Capitalization': [740.0e9, 569.4e9, 501.9e9, 422.1e9, 402.8e9, 0.12e9]
})
market_cap = nasdaq['Market Capitalization'].div(1e6)
print(market_cap.median())
quantiles = market_cap.quantile([.25, .75])
iqr = quantiles[.75] - quantiles[.25]
print(market_cap.describe())
```

A. `market_cap.median()` is equal to `462000.0`. — **True**
B. `market_cap.mean()` is larger than `market_cap.median()`. — **False**
C. `market_cap.quantile(.5) == market_cap.median()` evaluates to `True`. — **True**
D. `iqr` is equal to `144900.0`. — **True**
E. `.div(1e6)` modifies `nasdaq['Market Capitalization']` in place. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** From Ch 3 — median = 2nd quartile = `.quantile(.5)`; IQR = Q3 − Q1. Here one tiny company pulls the **mean** below the median (mean ≈ 439,387); `.div()` returns a new Series in millions and leaves the column in USD.

---

## Question 7 (Chapter 3 — Categorical variables: `.nunique()`, `.value_counts()`, missing values)

Consider the following code:

```python
import pandas as pd
import numpy as np
amex = pd.DataFrame({
    'Stock Symbol': ['XXII', 'FAX', 'IAF', 'CH', 'ABE', 'BTI'],
    'Sector': ['Health Care', np.nan, 'Health Care', 'Energy', np.nan, 'Health Care'],
    'IPO Year': [np.nan, 1986.0, 2002.0, np.nan, 2002.0, 2015.0]
})
print(amex['Sector'].nunique())
print(amex['Sector'].value_counts())
ipo_by_yr = amex['IPO Year'].dropna().astype(int).value_counts()
print(ipo_by_yr)
```

A. `amex['Sector'].nunique()` is equal to `2`. — **True**
B. `amex['Sector'].value_counts()` includes a row counting the missing values. — **False**
C. `amex['Sector'].value_counts().index[0]` is equal to `'Health Care'`. — **True**
D. `ipo_by_yr[2002]` is equal to `1`. — **False**
E. Without `.dropna()`, `amex['IPO Year'].astype(int)` raises an error because of the missing values. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** From Ch 3 — `.nunique()` and `.value_counts()` both ignore `NaN` by default; the first row of `.value_counts()` is the mode. `IPO Year` is `float64` only because of the missing values, hence `.dropna().astype(int)` before counting.

---

## Question 8 (Chapter 4 — `.groupby()` one column)

Consider the following code:

```python
import pandas as pd
nasdaq = pd.DataFrame({
    'Stock Symbol': ['AAPL', 'MSFT', 'GOOG', 'GILD', 'AMGN', 'AMZN'],
    'Sector': ['Technology', 'Technology', 'Technology', 'Health Care', 'Health Care', 'Consumer Services'],
    'IPO Year': [1980, 1986, 2004, 1992, 1983, 1997],
    'Market Capitalization': [740.0e9, 500.0e9, 560.0e9, 90.0e9, 120.0e9, 420.0e9]
})
nasdaq['market_cap_m'] = nasdaq['Market Capitalization'].div(1e6)
by_sector = nasdaq.groupby('Sector')
mcap_by_sector = by_sector['market_cap_m'].mean()
print(mcap_by_sector)
print(by_sector.size())
```

A. `by_sector` is a GroupBy object, not a DataFrame. — **True**
B. `mcap_by_sector` has 6 values, one per company. — **False**
C. `mcap_by_sector['Technology']` is equal to `600000.0`. — **True**
D. `by_sector.size()['Health Care']` is equal to `2`. — **True**
E. The sectors in `mcap_by_sector` appear in the order they first appear in `nasdaq` (`Technology` first). — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** From Ch 4 — "keep it simple & skip the loop": `groupby` + column + `.mean()` gives one value per **group**, sorted by group label. `.size()` counts rows per group; `mcap_by_sector.plot(kind='barh')` is the slide's follow-up.

---

## Question 9 (Chapter 4 — Several aggregations with `.agg()`)

Consider the following code (same `nasdaq` DataFrame as in Question 8, including `market_cap_m`):

```python
by_sector = nasdaq.groupby('Sector')
summary = by_sector['market_cap_m'].agg(['size', 'mean']).sort_values('size')
print(summary)
mixed = by_sector.agg({'market_cap_m': 'size', 'IPO Year': 'median'})
print(mixed)
```

A. `summary` is a DataFrame with two columns, `size` and `mean`. — **True**
B. The first row of `summary` is `Technology`. — **False**
C. `mixed['IPO Year']['Health Care']` is equal to `1987.5`. — **True**
D. `by_sector['market_cap_m'].agg(['size', 'mean'])` returns a Series. — **False**
E. In `mixed`, `'size'` is applied to `market_cap_m` and `'median'` to `IPO Year`. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** From Ch 4 — a **list** in `.agg()` gives one column per statistic (so a DataFrame); a **dict** maps column → statistic. `.sort_values('size')` is ascending, so the smallest group (`Consumer Services`, 1 company) comes first.

---

## Question 10 (Chapter 4 — Grouping by two columns)

Consider the following code:

```python
import pandas as pd
listings = pd.DataFrame({
    'Stock Symbol': ['AAPL', 'ORCL', 'JPM', 'BAC', 'MSFT'],
    'Sector': ['Technology', 'Technology', 'Finance', 'Finance', 'Technology'],
    'Exchange': ['NASDAQ', 'NYSE', 'NYSE', 'NYSE', 'NASDAQ'],
    'market_cap_m': [740000.0, 181000.0, 300300.0, 240000.0, 500000.0]
})
by_sector_exchange = listings.groupby(['Sector', 'Exchange'])
mcap = by_sector_exchange['market_cap_m'].mean()
print(mcap.loc['Technology'])
print(mcap.unstack())
```

A. `mcap.index` has two levels, `Sector` and `Exchange`. — **True**
B. `mcap` has 5 values, one per company. — **False**
C. `mcap.loc['Technology', 'NASDAQ']` is equal to `620000.0`. — **True**
D. `mcap.unstack()` has `NASDAQ` and `NYSE` as its columns. — **True**
E. `mcap.unstack().loc['Finance', 'NASDAQ']` is equal to `0.0`. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** From Ch 4 — grouping by two columns gives a MultiIndex Series with one value per **combination** that exists (3 here, not 2×2). `.loc['Technology']` selects from the first level; after `.unstack()`, a missing combination (`Finance` / `NASDAQ`) is `NaN`, not `0`.

---

## Question 11 (Review — `pd.concat()` keeps the original row labels)

Consider the following code:

```python
import pandas as pd
amex = pd.DataFrame({'Stock Symbol': ['XXII', 'FAX'], 'Last Sale': [1.33, 5.00]})
nyse = pd.DataFrame({'Stock Symbol': ['JNJ', 'XOM'], 'Last Sale': [124.9, 82.1]})
listings = pd.concat([amex, nyse])
reset = listings.reset_index(drop=True)
print(listings.index.tolist())
print(listings.loc[0])
```

A. `listings.index.tolist()` is equal to `[0, 1, 0, 1]`. — **True**
B. `listings.loc[0]` returns exactly one row. — **False**
C. `listings.iloc[0]['Stock Symbol']` is equal to `'XXII'`. — **True**
D. `reset.index.tolist()` is equal to `[0, 1, 2, 3]`. — **True**
E. `listings.loc[1, 'Stock Symbol']` is equal to `'FAX'`. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** The Ch 1 slide shows it (`Int64Index: 3507 entries, 0 to 3146`): `pd.concat` keeps each sheet's labels, so `.loc[0]` returns **two** rows (a DataFrame) and `.loc[1, 'Stock Symbol']` a two-value Series. `.iloc` is positional and unaffected; `.reset_index(drop=True)` (Session 3) rebuilds `0…n-1`.

---

## Question 12 (Review — Missing values in `.groupby()`: `.size()` vs `.count()`)

Consider the following code:

```python
import pandas as pd
import numpy as np
nyse = pd.DataFrame({
    'Stock Symbol': ['JNJ', 'XOM', 'JPM', 'ORCL', 'TSM'],
    'Sector': ['Health Care', np.nan, 'Finance', 'Technology', 'Technology'],
    'IPO Year': [np.nan, 1980.0, np.nan, 1986.0, 1997.0]
})
by_sector = nyse.groupby('Sector')
print(by_sector.size())
print(by_sector['IPO Year'].count())
```

A. `by_sector.size()` has 3 entries. — **True**
B. `by_sector.size().sum()` is equal to `len(nyse)`. — **False**
C. `by_sector['IPO Year'].count()['Health Care']` is equal to `1`. — **False**
D. `by_sector['IPO Year'].count()['Technology']` is equal to `2`. — **True**
E. `.size()` counts every row in a group, including rows where `IPO Year` is missing. — **True**

**CORRECT ANSWERS: A, D, E**

**Debrief tip:** Two `NaN` traps from the listing data: a row whose group key is missing (`XOM`, no sector) is dropped from every `groupby` result, and `.count()` counts **non-missing** values per column while `.size()` counts rows. On the Ch 4 slide, the sector sizes add up to 2767, not the 3167 rows of `nasdaq`.
