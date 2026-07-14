# Session 1 quiz — Answer key (instructor only)

---

## Question 1 (Chapter 1 — Variables and operators)

Consider the following code:

```python
price = 120
earnings = 4
pe_ratio = price / earnings
print(pe_ratio)
```

A. The variable `pe_ratio` will be equal to 30.0. — **True**
B. The type of `pe_ratio` is `int`. — **False**
C. In Python 3, `price / earnings` performs true division (not integer division). — **True**
D. `print(pe_ratio)` will display `30` without a decimal point. — **False**
E. Replacing `earnings = 4` with `earnings = "4"` would still produce `pe_ratio = 30.0`. — **False**

**CORRECT ANSWERS: A, C**

**Debrief tip:** Connect to P/E ratio from the slides (`price / earnings`). Contrast with Fall exam trap: string `"4"` vs int `4`.

---

## Question 2 (Chapter 1 — Data types and `type()`)

Consider the following code:

```python
x = 5
y = 'stock'
print(x * 3)
print(y * 3)
```

A. `print(x * 3)` outputs `15`. — **True**
B. `type(x)` is `<class 'int'>`. — **True**
C. `print(y * 3)` outputs `'stockstockstock'`. — **True**
D. The expression `y + 3` evaluates to `'stock3'`. — **False**
E. Multiplying a string by an integer repeats the string that many times. — **True**

**CORRECT ANSWERS: A, B, C, E**

**Debrief tip:** From the slides — `y * 3` works, `y + 3` does not. Mention `str()` conversion if students ask how to fix it.

---

## Question 3 (Chapter 2 — List indexing and slicing)

Consider the following code:

```python
months = ['January', 'February', 'March', 'April', 'May', 'June']
a = months[0]
b = months[-1]
c = months[2:5]
```

A. `a` is equal to `'January'`. — **True**
B. `b` is equal to `'June'`. — **True**
C. `c` is equal to `['March', 'April', 'May']`. — **True**
D. `months[2:5]` includes the element at index 5 (`'June'`). — **False**
E. `months[6]` returns `'June'`. — **False**

**CORRECT ANSWERS: A, B, C**

**Debrief tip:** Emphasize zero-indexing and that the end of a slice is **not** included.

---

## Question 4 (Chapter 2 — Slicing with step)

Consider the following code:

```python
sectors = ['Tech', 'Finance', 'Energy', 'Health', 'Consumer', 'Utilities']
subset = sectors[1:5:2]
```

A. `subset` is equal to `['Finance', 'Health']`. — **True**
B. `sectors[-1]` returns `'Consumer'`. — **False**
C. `sectors[:3]` returns `['Tech', 'Finance', 'Energy']`. — **True**
D. `sectors[1:5]` returns four elements. — **True**
E. `sectors[0:6:3]` returns `['Tech', 'Energy', 'Consumer']`. — **False**

**CORRECT ANSWERS: A, C, D**

**Debrief tip:** Walk through `1:5:2` on the board index by index. Common mistake: assuming step-3 slices hit indices 0, 2, 4.

---

## Question 5 (Chapter 2 — Methods and `.sort()`)

Consider the following code:

```python
prices = [238.11, 237.81, 238.91]
sorted_prices = prices.sort()
print(sorted_prices)
print(prices)
```

A. `prices.sort()` modifies `prices` in place. — **True**
B. After `prices.sort()`, `print(prices)` displays `[237.81, 238.11, 238.91]`. — **True**
C. `sorted_prices` contains the sorted list `[237.81, 238.11, 238.91]`. — **False**
D. `print(sorted_prices)` displays `None`. — **True**
E. `.sort()` is a method called on a list object. — **True**

**CORRECT ANSWERS: A, B, D, E**

**Debrief tip:** Contrast with built-in `sorted(prices)`, which returns a new list and leaves the original unchanged.

---

## Question 6 (Chapter 3 — NumPy arrays and element-wise operations)

Consider the following code:

```python
import numpy as np
prices = np.array([100, 200, 300])
earnings = np.array([5, 10, 15])
pe_ratios = prices / earnings
print(pe_ratios)
```

A. `print(pe_ratios)` outputs `[20. 20. 20.]`. — **True**
B. If `prices` and `earnings` were Python lists, `prices / earnings` would perform element-wise division. — **False**
C. `np.mean(pe_ratios)` returns `20.0`. — **True**
D. `pe_ratios` has two dimensions (a 2-D array). — **False**
E. All elements of `pe_ratios` are equal to each other. — **True**

**CORRECT ANSWERS: A, C, E**

**Debrief tip:** Side-by-side demo with lists (`+` concatenates) vs arrays (`+` is element-wise).

---

## Question 7 (Chapter 3 — Array shape and `.size`)

Consider the following code:

```python
import numpy as np
months = [1, 2, 3]
prices = [238.11, 237.81, 238.91]
cpi_array = np.array([months, prices])
```

A. `cpi_array.shape` is `(2, 3)`. — **True**
B. `cpi_array.size` is `6`. — **True**
C. `cpi_array` has 2 rows and 3 columns. — **True**
D. `cpi_array.shape` is `(3, 2)`. — **False**
E. `cpi_array.ndim` is `3`. — **False**

**CORRECT ANSWERS: A, B, C**

**Debrief tip:** Print `cpi_array` so students see the 2×3 layout before discussing `.shape` vs `.size`.

---

## Question 8 (Chapter 3 / 5 — Boolean filtering and `np.mean()`)

Consider the following code:

```python
import numpy as np
stock_prices = np.array([50, 120, 200, 80, 300])
filter_array = stock_prices >= 100
filtered = stock_prices[filter_array]
```

A. `filter_array` contains `False`, `True`, `True`, `False`, `True` in that order. — **True**
B. The variable `filtered` is equal to `np.array([120, 200, 300])`. — **True**
C. `np.mean(filtered)` returns `150.0`. — **False**
D. `len(filtered)` returns `5`. — **False**
E. Changing the condition to `stock_prices > 200` would make `filtered` equal to `np.array([300])`. — **True**

**CORRECT ANSWERS: A, B, E**

**Debrief tip:** From the S&P 100 case study — boolean arrays as filters. Recompute the mean live.

---

## Question 9 (Chapter 4 — Matplotlib plotting)

Consider the following code:

```python
import matplotlib.pyplot as plt
months = [1, 2, 3, 4, 5, 6]
prices = [238.11, 237.81, 238.91, 239.05, 238.50, 239.20]
plt.plot(months, prices, color='red', linestyle='--')
plt.xlabel('Months')
plt.ylabel('CPI')
plt.title('Monthly CPI')
plt.show()
```

A. `plt.plot(months, prices, ...)` creates a line plot of `prices` against `months`. — **True**
B. The argument `color='red'` sets the line color to red. — **True**
C. The argument `linestyle='--'` creates a dashed line. — **True**
D. `plt.xlabel('Months')` sets the title of the plot. — **False**
E. `plt.title('Monthly CPI')` sets the title of the plot. — **True**

**CORRECT ANSWERS: A, B, C, E**

**Debrief tip:** From the slides — review the color/linestyle table (`'-'`, `'--'`, `':'`, `'-.'`).

---

## Question 10 (Chapter 5 — S&P 100 case study: P/E ratios and histograms)

Consider the following code:

```python
import numpy as np
import matplotlib.pyplot as plt
prices = np.array([100, 150, 200, 120])
earnings = np.array([5, 10, 20, 4])
pe_ratios = prices / earnings
average = np.mean(pe_ratios)
plt.hist(x=pe_ratios, bins=4)
plt.show()
```

A. `pe_ratios` is computed by element-wise division of `prices` by `earnings`. — **True**
B. `pe_ratios[0]` is equal to `20.0`. — **True**
C. `average` is equal to `15.0`. — **False**
D. `plt.hist(x=pe_ratios, bins=4)` creates a histogram of the P/E ratios. — **True**
E. Increasing `bins` from 4 to 8 would divide the data into more bins. — **True**

**CORRECT ANSWERS: A, B, D, E**

**Debrief tip:** Tie back to the case study mission — explore P/E ratios, then visualize the distribution.

---

## Question 11 (Review — NumPy type coercion vs lists)

Consider the following code:

```python
import numpy as np
mixed = np.array([3, 'is', True])
print(mixed[0])
print(type(mixed[0]))
```

A. All elements of `mixed` are stored as strings. — **True**
B. `mixed[0]` is the integer `3`. — **False**
C. `mixed[0] == 3` (comparison to the integer `3`) is `True`. — **False**
D. `np.array([3, 'is', True])` raises a TypeError because the types are incompatible. — **False**
E. A Python list `[3, 'is', True]` can hold mixed types without conversion. — **True**

**CORRECT ANSWERS: A, E**

**Debrief tip:** From Ch 3 slides — contrast `np.array([3, 'is', True])` with `my_list = [3, 'is', True]`.

---

## Question 12 (Review — `.sort()` in place and list references)

Consider the following code:

```python
prices = [238.91, 237.81, 238.11]
original = prices
result = prices.sort()
```

A. `result` is `None`. — **True**
B. After `prices.sort()`, `prices` is `[237.81, 238.11, 238.91]`. — **True**
C. `original` is still `[238.91, 237.81, 238.11]`. — **False**
D. `original` and `prices` refer to the same list object. — **True**
E. `prices.sort()` modifies the list in place. — **True**

**CORRECT ANSWERS: A, B, D, E**

**Debrief tip:** Show `original is prices` → `True`. Mention `prices.copy()` or `sorted(prices)` to keep an unsorted copy.
