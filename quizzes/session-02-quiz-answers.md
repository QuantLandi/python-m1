# Session 2 quiz — Answer key (instructor only)

---

## Question 1 (Chapter 1 — `datetime()` constructor)

Consider the following code:

```python
from datetime import datetime
black_monday = datetime(1987, 10, 19)
print(black_monday)
```

A. `print(black_monday)` displays exactly the string `'1987-10-19'`. — **False**
B. `datetime(1987, 19, 10)` creates the same datetime object as `datetime(1987, 10, 19)`. — **False**
C. `black_monday.month` is equal to `10`. — **True**
D. The type of `black_monday` is `<class 'datetime.date'>`. — **False**
E. `black_monday.day` is equal to `19`. — **True**

**CORRECT ANSWERS: C, E**

**Debrief tip:** From the slides — Black Monday example (`datetime(1987, 10, 19)`). Mention that omitted time arguments default to midnight (`hour=0`, `minute=0`, `second=0`). Contrast `datetime` vs `date`; show what `print()` actually outputs (`1987-10-19 00:00:00`).

---

## Question 2 (Chapter 1 — `strptime()` and format codes)

Consider the following code:

```python
from datetime import datetime
text = "10/27/1997"
format_str = "%m/%d/%Y"
sell_date = datetime.strptime(text, format_str)
print(sell_date)
```

A. `datetime.strptime(text, format_str)` returns a string. — **False**
B. `sell_date.day` is equal to `27`. — **True**
C. Replacing `format_str` with `"%d/%m/%Y"` would produce a datetime with `month` equal to `10`. — **False**
D. `sell_date.year` is equal to `1997`. — **True**
E. `sell_date.month` is equal to `10`. — **True**

**CORRECT ANSWERS: B, D, E**

**Debrief tip:** From the slides — parsing `"10/27/1997"` to compare with `datetime(1997, 10, 27)`. Walk through `%m` (month), `%d` (day), `%Y` (4-digit year). Mention US vs European date order if students ask about E.

---

## Question 3 (Chapter 1 — `strftime()` and datetime attributes)

Consider the following code:

```python
from datetime import datetime
crash = datetime(1929, 10, 29)
label = crash.strftime("%Y-%m-%d")
print(label)
```

A. `crash.strftime("%Y-%m-%d")` returns a `datetime` object. — **False**
B. `label` is equal to `'1929-10-29'`. — **True**
C. The format string `"%Y-%m-%d"` includes the code `%b` for abbreviated month name. — **False**
D. `crash.hour` is equal to `12`. — **False**
E. `crash.month` is equal to `10`. — **True**

**CORRECT ANSWERS: B, E**

**Debrief tip:** From the slides — Great Depression crash example. Contrast `strftime` (datetime → string) with `strptime` (string → datetime). Numeric codes `%Y`, `%m`, `%d` are locale-independent; `%a` / `%b` depend on system locale.

---

## Question 4 (Chapter 1 — Comparing datetimes)

Consider the following code:

```python
from datetime import datetime
asian_crisis = datetime(1997, 7, 2)
world_mini_crash = datetime(1997, 10, 27)
print(asian_crisis < world_mini_crash)
print(asian_crisis == world_mini_crash)
```

A. Datetimes can be compared with `<`, `>`, `==`, and other comparison operators. — **True**
B. `asian_crisis == world_mini_crash` evaluates to `True`. — **False**
C. `datetime(1997, 7, 2) < datetime(1997, 7, 2)` evaluates to `True`. — **False**
D. `asian_crisis > world_mini_crash` evaluates to `True`. — **False**
E. `asian_crisis < world_mini_crash` evaluates to `True`. — **True**

**CORRECT ANSWERS: A, E**

**Debrief tip:** From the slides — Asian crisis vs world mini-crash dates. Earlier date is “less than” later date. Equal datetimes compare with `==`; a date is not less than itself.

---

## Question 5 (Chapter 2 — `==` vs `=` and cross-type equality)

Consider the following code:

```python
x = 13
print(3 == 3.0)
print(3 == '3')
print(x == 13)
```

A. The operator `==` assigns the value on the right to the name on the left. — **False**
B. `print(x == 13)` outputs `True`. — **True**
C. `3 == 3` evaluates to `False`. — **False**
D. `print(3 == '3')` outputs `True`. — **False**
E. `print(3 == 3.0)` outputs `True`. — **True**

**CORRECT ANSWERS: B, E**

**Debrief tip:** From the slides — `==` tests equality, `=` assigns. `3 == 3.0` is `True` (numeric equality across int/float); `3 == '3'` is `False` (different types).

---

## Question 6 (Chapter 2 — Order operators)

Consider the following code:

```python
print(3 < 4)
print('e' <= 'a')
print(4 >= 4)
```

A. `print(4 >= 4)` outputs `False`. — **False**
B. `print('e' <= 'a')` outputs `True`. — **False**
C. The expression `'a' < 23` raises a `TypeError`. — **True**
D. `print(3 < 3)` outputs `True`. — **False**
E. `print(3 < 4)` outputs `True`. — **True**

**CORRECT ANSWERS: C, E**

**Debrief tip:** From the slides — order operators on numbers and strings; `'e' <= 'a'` is `False` (lexicographic order). Cross-type comparisons like `'a' < 23` are not allowed in Python 3.

---

## Question 7 (Chapter 2 — Boolean operators and truthiness)

Consider the following code:

```python
price = 56.88
volume = 0
print(True and False)
print(False or True)
print(not volume)
print(bool(price))
```

A. The empty string `""` evaluates as `True` in a Boolean context. — **False**
B. `print(not volume)` outputs `True`. — **True**
C. `print(True and False)` outputs `True`. — **False**
D. `print(bool(price))` outputs `False`. — **False**
E. `print(False or True)` outputs `True`. — **True**

**CORRECT ANSWERS: B, E**

**Debrief tip:** From the slides — `and`, `or`, `not`; falsy values include `0`, `""`, `[]`, `{}`. `not 0` is `True`; a non-zero price is truthy.

---

## Question 8 (Chapter 3 — DataFrame from a dict)

Consider the following code:

```python
import pandas as pd
data = {'Bank Code': ['BA', 'AAD', 'BA'],
        'Account#': ['ajfdk2', '1234nmk', 'mm3d90'],
        'Balance': [1222.00, 390789.11, 13.02]}
df = pd.DataFrame(data=data)
print(df.shape)
print(df.loc[0, 'Balance'])
```

A. `df` has 2 rows. — **False**
B. `df.loc[0, 'Balance']` is equal to `1222.00`. — **True**
C. `df.shape` is `(3, 2)`. — **False**
D. `'Bank Code'` is a column name in `df`. — **True**
E. `df.shape` is `(3, 3)`. — **True**

**CORRECT ANSWERS: B, D, E**

**Debrief tip:** From the slides — dict keys become column names; list lengths set the number of rows (3 rows, 3 columns here).

---

## Question 9 (Chapter 3 — DataFrame from list of lists + `columns=`)

Consider the following code:

```python
import pandas as pd
data = [['BA', 'ajfdk2', 1222.00],
        ['AAD', '1234nmk', 390789.11],
        ['BA', 'mm3d90', 13.02]]
columns = ['Bank Code', 'Account#', 'Balance']
df = pd.DataFrame(data=data, columns=columns)
print(df.loc[1, 'Balance'])
print(list(df.columns))
```

A. Without the `columns=` argument, pandas would still name the columns `'Bank Code'`, `'Account#'`, and `'Balance'`. — **False**
B. `df.loc[1, 'Balance']` is equal to `390789.11`. — **True**
C. `df.shape` is `(3, 2)`. — **False**
D. `list(df.columns)` equals `['Bank Code', 'Account#', 'Balance']`. — **True**
E. `df.shape` is `(3, 3)`. — **True**

**CORRECT ANSWERS: B, D, E**

**Debrief tip:** From the slides — without `columns=`, default names are `0`, `1`, `2`. Contrast with Q12.

---

## Question 10 (Chapter 4 — `.head()`, `.tail()`, and `.describe()`)

Consider the following code:

```python
import pandas as pd
prices = pd.Series([247.74, 258.44, 245.52, 246.88, 224.37])
print(len(prices.head(2)))
print(prices.tail().iloc[-1])
print(prices.describe()['count'])
```

A. `prices.describe()['count']` is equal to `5.0`. — **True**
B. `prices.tail().iloc[-1]` is equal to `247.74`. — **False**
C. `len(prices.head(2))` is equal to `2`. — **True**
D. `prices.head()` without an argument returns 5 rows by default. — **True**
E. `prices.describe()` only works on string columns. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** From the slides — `.head()` / `.tail()` default to 5 rows; `.describe()` summarizes numeric columns (`count`, `mean`, etc.). Last value of `.tail()` here is `224.37`.

---

## Question 11 (Review — format-string trap: `%m` vs `%M`)

Consider the following code:

```python
from datetime import datetime
text = "10/27/1997"
parsed = datetime.strptime(text, "%M/%d/%Y")
print(parsed.month)
print(parsed.minute)
```

A. In a format string, `%M` stands for the month number (`01`–`12`). — **False**
B. `parsed.day` is equal to `27`. — **True**
C. `parsed.month` is equal to `10`. — **False**
D. Replacing `"%M"` with `"%m"` in the format string would make `parsed.month` equal to `10`. — **True**
E. `parsed.minute` is equal to `10`. — **True**

**CORRECT ANSWERS: B, D, E**

**Debrief tip:** Classic trap from the slides — `%m` = month, `%M` = minutes. Here `"10"` is parsed as 10 minutes, not October; month becomes `1` (default when not specified).

---

## Question 12 (Review — DataFrame default column names)

Consider the following code:

```python
import pandas as pd
data = [['BA', 'ajfdk2', 1222.00],
        ['AAD', '1234nmk', 390789.11],
        ['BA', 'mm3d90', 13.02]]
df = pd.DataFrame(data=data)
print(list(df.columns))
print(df.iloc[0, 0])
```

A. `df.iloc[0, 0]` is equal to `'BA'`. — **True**
B. `df.shape` is `(2, 3)`. — **False**
C. `list(df.columns)` equals `[0, 1, 2]`. — **True**
D. `df.columns[0]` is equal to `'Bank Code'`. — **False**
E. Passing `columns=['Bank Code', 'Account#', 'Balance']` to `pd.DataFrame` would assign those column names. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** Pair with Q9 — list-of-lists without `columns=` gets integer column names; data values are unchanged (`'BA'` at row 0, column 0).

