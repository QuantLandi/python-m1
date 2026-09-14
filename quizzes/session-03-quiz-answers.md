# Session 3 quiz — Answer key (instructor only)

---

## Question 1 (Chapter 1 — Inspecting a DataFrame)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
print(prices.shape)
print(prices.columns)
print(prices.info())
print(prices.describe())
```

A. `prices.shape` is `(6, 4)`. — **True**

B. `.shape` must be written with parentheses, `prices.shape()`, because it is a method. — **False**

C. `prices.info()` shows the data type of each column and the number of non-missing values. — **True**

D. `prices.columns` returns the row labels of `prices`. — **False**

E. `prices.describe()` includes the `sector` column in its output. — **False**

**CORRECT ANSWERS: A, C**

**Debrief tip:** `.shape` is an attribute (no parentheses) — same as NumPy in Session 1. `.columns` = column labels, `.index` = row labels. `.describe()` only summarises numeric columns by default; show the output live so students see `sector` is absent.

---

## Question 2 (Chapter 1 — Sorting rows with `.sort_values()`)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
top = prices.sort_values('price', ascending=False).head(2)
by_sector = prices.sort_values(['sector', 'price'], ascending=[True, False])
```

A. `top` contains the rows for MSFT and TSLA. — **True**

B. `.sort_values()` sorts `prices` in place, so `prices` is now sorted by price. — **False**

C. The first row of `by_sector` is AAPL. — **False**

D. Within the `'Tech'` sector, `by_sector` lists MSFT before AAPL. — **True**

E. `prices.sort_values('price').head(2)` contains the rows for PFE and XOM. — **True**

**CORRECT ANSWERS: A, D, E**

**Debrief tip:** Contrast with Session 1's `.sort()` on lists: `.sort_values()` returns a **new** DataFrame. Sectors sorted ascending start with `Consumer`, so `by_sector` starts with TSLA — walk through the two-key sort on the board (sector ascending, then price descending within sector).

---

## Question 3 (Chapter 1 — Subsetting columns and rows)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
a = prices['ticker']
b = prices[['ticker', 'price']]
cheap = prices[prices['price'] < 150]
tech_big = prices[(prices['sector'] == 'Tech') & (prices['price'] > 300)]
```

A. `a` is a pandas Series. — **True**

B. `prices['ticker', 'price']` is an equivalent way of writing `b`. — **False**

C. `cheap` has 2 rows. — **True**

D. `tech_big` contains exactly one row, MSFT. — **True**

E. Removing the parentheses around each condition in `tech_big` would give the same result. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** Single brackets → Series, double brackets → DataFrame. `prices['ticker', 'price']` raises a `KeyError`. Without parentheses, `&` binds tighter than `==`/`>` and the line errors — link to the Session 2 NASDAQ date-window example.

---

## Question 4 (Chapter 1 — `.isin()` and new columns)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
defensive = prices[prices['sector'].isin(['Health', 'Energy'])]
prices['pe'] = prices['price'] / prices['eps']
prices['cheap'] = prices['pe'] < 20
print(prices.loc[2, 'pe'])
```

A. `defensive` contains the rows for XOM and PFE. — **True**

B. `prices[prices['sector'] == ['Health', 'Energy']]` is an equivalent way to write `defensive`. — **False**

C. After this code runs, `prices` has 6 columns. — **True**

D. `prices['cheap']` is a column of Booleans. — **True**

E. `prices.loc[2, 'pe']` (JPM's P/E) is greater than 20. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** `== [list]` is not a membership test — use `.isin()`. The P/E column is the same `price / earnings` idea as Session 1, now vectorised over a DataFrame. JPM's P/E = 195.40 / 16.20 ≈ 12.06, so it is `cheap`.

---

## Question 5 (Chapter 2 — Summary statistics and `.agg()`)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
prices['pe'] = prices['price'] / prices['eps']
prices['cheap'] = prices['pe'] < 20

def iqr(column):
    return column.quantile(0.75) - column.quantile(0.25)

print(prices['pe'].mean())
print(prices['pe'].agg([iqr, 'median']))
print(prices[['price', 'eps']].agg('max'))
```

A. The median P/E is less affected by TSLA's extreme P/E than the mean P/E is. — **True**

B. Inside `.agg()`, the custom function must be called with parentheses: `.agg([iqr(), 'median'])`. — **False**

C. `prices['pe'].agg([iqr, 'median'])` returns two numbers: the IQR and the median of the P/E column. — **True**

D. `prices[['price', 'eps']].agg('max')` returns a single number. — **False**

E. `prices['pe'].mean()` is greater than `prices['pe'].median()`. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** Pass the function object (no parentheses) to `.agg()`. `.agg('max')` on two columns returns one value per column. Mean P/E ≈ 32.8 vs median ≈ 26.6 — TSLA's P/E of 81 drags the mean up; a good moment to discuss robust statistics in valuation screens.

---

## Question 6 (Chapter 2 — Cumulative statistics: running high and drawdown)

Consider the following code:

```python
import pandas as pd
nav = pd.DataFrame({
    'date': pd.date_range('2026-09-01', periods=5, freq='B'),
    'close': [100, 104, 101, 108, 105]
})
nav['running_high'] = nav['close'].cummax()
nav['drawdown'] = nav['close'] / nav['running_high'] - 1
```

A. `nav['running_high']` is `[100, 104, 104, 108, 108]`. — **True**

B. The drawdown on the last row is approximately `-0.028` (about -2.8%). — **True**

C. `.cummax()` returns a single number: the maximum of the `close` column. — **False**

D. `nav['close'].cumsum().iloc[-1]` equals `nav['close'].sum()`. — **True**

E. The cumulative statistics would give the same result if `nav` were sorted by `close` instead of by `date`. — **False**

**CORRECT ANSWERS: A, B, D**

**Debrief tip:** Drawdown = price / running peak − 1 is a real risk metric — students see `.cummax()` doing useful work. Last row: 105 / 108 − 1 ≈ −0.0278. Cumulative statistics depend on row order: sorted by `close`, the drawdown would be 0 everywhere. Always `sort_values('date')` first (as in the DataCamp Walmart exercise).

---

## Question 7 (Chapter 2 — `.drop_duplicates()` and `.value_counts()`)

Consider the following code:

```python
import pandas as pd
trades = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'AAPL', 'JPM', 'AAPL', 'MSFT'],
    'side':   ['buy', 'buy', 'sell', 'buy', 'buy', 'sell'],
    'qty':    [10, 5, 4, 20, 6, 5]
})
unique_tickers = trades.drop_duplicates(subset='ticker')
pairs = trades.drop_duplicates(subset=['ticker', 'side'])
counts = trades['ticker'].value_counts()
props = trades['side'].value_counts(normalize=True)
```

A. `unique_tickers` has 3 rows. — **True**

B. `pairs` has 5 rows. — **True**

C. `counts.iloc[0]` is 3, because AAPL is the most frequent ticker and `.value_counts()` sorts by count in descending order. — **True**

D. `props['buy']` is equal to 4. — **False**

E. By default, `.drop_duplicates()` keeps the last occurrence of each duplicate. — **False**

**CORRECT ANSWERS: A, B, C**

**Debrief tip:** A trade blotter is the natural finance version of the vet-visits example. 3 unique tickers; 5 unique (ticker, side) pairs — only (AAPL, buy) repeats. `normalize=True` gives proportions (`props['buy']` = 4/6 ≈ 0.667). Default is `keep='first'`.

---

## Question 8 (Chapter 2 / 4 — Grouped summaries with `.groupby()` and a bar plot)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
prices['pe'] = prices['price'] / prices['eps']
prices['cheap'] = prices['pe'] < 20
import matplotlib.pyplot as plt
by_sector = prices.groupby('sector')['price'].mean()
stats = prices.groupby('sector')['pe'].agg(['min', 'max'])
by_sector.plot(kind='bar')
plt.show()
```

A. `by_sector['Tech']` is equal to `326.655`. — **True**

B. `by_sector` has 6 entries, one per ticker. — **False**

C. `stats` is a DataFrame with two columns, `min` and `max`. — **True**

D. `stats.loc['Tech', 'max']` is MSFT's P/E. — **False**

E. `by_sector.plot(kind='bar')` draws one bar per sector. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** Tech mean price = (238.11 + 415.20) / 2 = 326.655. Grouping by `sector` gives 5 groups, not 6 rows. Tech max P/E is AAPL's (≈ 37.1 vs MSFT ≈ 35.2) — students often assume the higher price means the higher P/E. Show the bar plot live to connect to Session 1's Matplotlib.

---

## Question 9 (Chapter 2 — Pivot tables)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
prices['pe'] = prices['price'] / prices['eps']
prices['cheap'] = prices['pe'] < 20
pv = prices.pivot_table(values='price', index='sector', columns='cheap',
                        fill_value=0, margins=True)
print(pv)
```

A. Without an `aggfunc` argument, `.pivot_table()` computes the mean of `values` for each group. — **True**

B. `pv.loc['Tech', False]` is equal to `326.655`. — **True**

C. `fill_value=0` replaces the cells that have no data (NaN) with 0. — **True**

D. `margins=True` adds a row and a column named `All` containing the **sum** of each row and column. — **False**

E. `prices.pivot_table(values='price', index='sector')` gives the same numbers as `prices.groupby('sector')['price'].sum()`. — **False**

**CORRECT ANSWERS: A, B, C**

**Debrief tip:** Default `aggfunc` is mean, so the `All` margins are means, not sums — the bottom-right cell is 207.78, the overall mean price. Print `pv` and point at it. `.pivot_table()` with no `aggfunc` matches `.groupby(...).mean()`, not `.sum()`.

---

## Question 10 (Chapter 3 — Explicit indexes and `.loc[]`)

Consider the following code:

```python
import pandas as pd
prices = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'JPM', 'XOM', 'PFE', 'TSLA'],
    'sector': ['Tech', 'Tech', 'Finance', 'Energy', 'Health', 'Consumer'],
    'price':  [238.11, 415.20, 195.40, 118.75, 27.90, 251.30],
    'eps':    [6.42, 11.80, 16.20, 8.90, 1.55, 3.10]
})
p_ind = prices.set_index('ticker')
print(p_ind.loc['JPM', 'price'])
print(p_ind.loc[['AAPL', 'TSLA']])

p_multi = prices.set_index(['sector', 'ticker']).sort_index()
print(p_multi.loc['Tech'])
print(p_multi.loc[('Tech', 'MSFT'), 'price'])
```

A. `p_ind.loc['JPM', 'price']` is equal to `195.4`. — **True**

B. After `set_index('ticker')`, `'ticker'` is still one of the regular columns of `p_ind`. — **False**

C. `p_ind.loc[['AAPL', 'TSLA']]` returns two rows. — **True**

D. `p_multi.loc['MSFT']` works because `'MSFT'` is a value in the index. — **False**

E. `p_ind.reset_index()` moves `ticker` back from the index into a regular column. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** `set_index` moves the column out of the body (left-aligned in the printout). Passing a list to `.loc[]` selects those rows — cleaner than `.isin()`. `'MSFT'` is in the *inner* level, so `p_multi.loc['MSFT']` raises a `KeyError`; use the tuple `('Tech', 'MSFT')`.

---

## Question 11 (Review — Slicing: `.loc[]` vs `.iloc[]` on a date index)

Consider the following code:

```python
import pandas as pd
nav = pd.DataFrame({
    'date': pd.date_range('2026-09-01', periods=5, freq='B'),
    'close': [100, 104, 101, 108, 105]
})
nav_ind = nav.set_index('date').sort_index()
a = nav_ind.loc['2026-09-02':'2026-09-04']
b = nav_ind.iloc[1:3]
c = nav_ind.loc['2026-09']
```

A. `a` has 3 rows: 2026-09-02, 09-03 and 09-04. — **True**

B. `b` has 3 rows. — **False**

C. `c` returns all 5 rows, because pandas accepts a partial date string to slice a whole month. — **True**

D. `a` and `b` contain exactly the same rows. — **False**

E. Slicing by index values with `.loc[]` requires the index to be sorted first. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** The business days are Sep 1, 2, 3, 4 and 7 (`freq='B'` skips the weekend). `.loc` label slices are **inclusive** → 3 rows; `.iloc[1:3]` is **exclusive** like list slicing (Session 1) → 2 rows (Sep 2, 3). Partial strings like `'2026-09'` select the whole month. Remind students: `sort_index()` before slicing by label.

---

## Question 12 (Review — Missing values, creating DataFrames and CSV)

Consider the following code:

```python
import pandas as pd
book = pd.DataFrame([
    {'ticker': 'AAPL', 'qty': 10,   'price': 238.11},
    {'ticker': 'MSFT', 'qty': None, 'price': 415.20},
    {'ticker': 'JPM',  'qty': 20,   'price': None}
])
print(book.isna().sum())
clean = book.dropna()
filled = book.fillna(0)
filled.to_csv('book.csv')
```

A. `book.isna().sum()` shows 1 missing value in `qty` and 1 missing value in `price`. — **True**

B. `clean` has exactly 1 row. — **True**

C. `book.dropna()` removes the rows with missing values from `book` itself (in place). — **False**

D. `filled.loc[1, 'qty']` is equal to `0`. — **True**

E. `pd.read_csv('book.csv')` would reproduce `book` exactly, including its `NaN` values. — **False**

**CORRECT ANSWERS: A, B, D**

**Debrief tip:** List-of-dicts construction (row by row) vs the dict-of-lists from Session 2. Only AAPL is complete → `clean` has 1 row. `.dropna()` / `.fillna()` return new DataFrames — `book` is unchanged. The CSV was written from `filled`, so reading it back gives 0s, not NaNs (plus an extra unnamed index column — mention `index=False`).
