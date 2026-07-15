# Session 2 quiz — Answer key (instructor only)

---

## Question 1 (Chapter 1 — `datetime()` constructor)

Consider the following code:

```python
from datetime import datetime
black_monday = datetime(1987, 10, 19)
print(black_monday)
```

A. `black_monday.month` is equal to `10`. — **True**
B. `black_monday.day` is equal to `19`. — **True**
C. The type of `black_monday` is `<class 'datetime.date'>`. — **False**
D. `print(black_monday)` displays exactly the string `'1987-10-19'`. — **False**
E. `datetime(1987, 19, 10)` creates the same datetime object as `datetime(1987, 10, 19)`. — **False**

**CORRECT ANSWERS: A, B**

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

A. `sell_date.year` is equal to `1997`. — **True**
B. `sell_date.month` is equal to `10`. — **True**
C. `sell_date.day` is equal to `27`. — **True**
D. `datetime.strptime(text, format_str)` returns a string. — **False**
E. Replacing `format_str` with `"%d/%m/%Y"` would produce a datetime with `month` equal to `10`. — **False**

**CORRECT ANSWERS: A, B, C**

**Debrief tip:** From the slides — parsing `"10/27/1997"` to compare with `datetime(1997, 10, 27)`. Walk through `%m` (month), `%d` (day), `%Y` (4-digit year). Mention US vs European date order if students ask about E.

---

<!-- Questions 3–12 to be added one at a time -->
