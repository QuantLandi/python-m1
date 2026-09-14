# Session 3 quiz — Data Manipulation with pandas

Ungraded in-class practice. Exam-style: code snippet + 5 true/false statements.

- **Review:** one question at a time
- **Scope:** full DataCamp course (Ch 1–4)
- **Plan:** 12 questions (Q11–Q12 are tricky review); allow ~70 min for Q1–Q10

Instructor answer key: [session-03-quiz-answers.md](session-03-quiz-answers.md)

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

A. `prices.shape` is `(6, 4)`.

B. `.shape` must be written with parentheses, `prices.shape()`, because it is a method.

C. `prices.info()` shows the data type of each column and the number of non-missing values.

D. `prices.columns` returns the row labels of `prices`.

E. `prices.describe()` includes the `sector` column in its output.

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

A. `top` contains the rows for MSFT and TSLA.

B. `.sort_values()` sorts `prices` in place, so `prices` is now sorted by price.

C. The first row of `by_sector` is AAPL.

D. Within the `'Tech'` sector, `by_sector` lists MSFT before AAPL.

E. `prices.sort_values('price').head(2)` contains the rows for PFE and XOM.

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

A. `a` is a pandas Series.

B. `prices['ticker', 'price']` is an equivalent way of writing `b`.

C. `cheap` has 2 rows.

D. `tech_big` contains exactly one row, MSFT.

E. Removing the parentheses around each condition in `tech_big` would give the same result.

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

A. `defensive` contains the rows for XOM and PFE.

B. `prices[prices['sector'] == ['Health', 'Energy']]` is an equivalent way to write `defensive`.

C. After this code runs, `prices` has 6 columns.

D. `prices['cheap']` is a column of Booleans.

E. `prices.loc[2, 'pe']` (JPM's P/E) is greater than 20.

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

A. The median P/E is less affected by TSLA's extreme P/E than the mean P/E is.

B. Inside `.agg()`, the custom function must be called with parentheses: `.agg([iqr(), 'median'])`.

C. `prices['pe'].agg([iqr, 'median'])` returns two numbers: the IQR and the median of the P/E column.

D. `prices[['price', 'eps']].agg('max')` returns a single number.

E. `prices['pe'].mean()` is greater than `prices['pe'].median()`.

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

A. `nav['running_high']` is `[100, 104, 104, 108, 108]`.

B. The drawdown on the last row is approximately `-0.028` (about -2.8%).

C. `.cummax()` returns a single number: the maximum of the `close` column.

D. `nav['close'].cumsum().iloc[-1]` equals `nav['close'].sum()`.

E. The cumulative statistics would give the same result if `nav` were sorted by `close` instead of by `date`.

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

A. `unique_tickers` has 3 rows.

B. `pairs` has 5 rows.

C. `counts.iloc[0]` is 3, because AAPL is the most frequent ticker and `.value_counts()` sorts by count in descending order.

D. `props['buy']` is equal to 4.

E. By default, `.drop_duplicates()` keeps the last occurrence of each duplicate.

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

A. `by_sector['Tech']` is equal to `326.655`.

B. `by_sector` has 6 entries, one per ticker.

C. `stats` is a DataFrame with two columns, `min` and `max`.

D. `stats.loc['Tech', 'max']` is MSFT's P/E.

E. `by_sector.plot(kind='bar')` draws one bar per sector.

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

A. Without an `aggfunc` argument, `.pivot_table()` computes the mean of `values` for each group.

B. `pv.loc['Tech', False]` is equal to `326.655`.

C. `fill_value=0` replaces the cells that have no data (NaN) with 0.

D. `margins=True` adds a row and a column named `All` containing the **sum** of each row and column.

E. `prices.pivot_table(values='price', index='sector')` gives the same numbers as `prices.groupby('sector')['price'].sum()`.

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

A. `p_ind.loc['JPM', 'price']` is equal to `195.4`.

B. After `set_index('ticker')`, `'ticker'` is still one of the regular columns of `p_ind`.

C. `p_ind.loc[['AAPL', 'TSLA']]` returns two rows.

D. `p_multi.loc['MSFT']` works because `'MSFT'` is a value in the index.

E. `p_ind.reset_index()` moves `ticker` back from the index into a regular column.

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

A. `a` has 3 rows: 2026-09-02, 09-03 and 09-04.

B. `b` has 3 rows.

C. `c` returns all 5 rows, because pandas accepts a partial date string to slice a whole month.

D. `a` and `b` contain exactly the same rows.

E. Slicing by index values with `.loc[]` requires the index to be sorted first.

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

A. `book.isna().sum()` shows 1 missing value in `qty` and 1 missing value in `price`.

B. `clean` has exactly 1 row.

C. `book.dropna()` removes the rows with missing values from `book` itself (in place).

D. `filled.loc[1, 'qty']` is equal to `0`.

E. `pd.read_csv('book.csv')` would reproduce `book` exactly, including its `NaN` values.
