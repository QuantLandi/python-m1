# Session 2 quiz — Intermediate Python for Finance

Ungraded in-class practice. Exam-style: code snippet + 5 true/false statements.

- **Review:** one question at a time
- **Scope:** full DataCamp course (Ch 1–4)
- **Plan:** 12 questions (Q11–Q12 are tricky review); allow ~70 min for Q1–Q10

Instructor answer key: [session-02-quiz-answers.md](session-02-quiz-answers.md)

---

## Question 1 (Chapter 1 — `datetime()` constructor)

Consider the following code:

```python
from datetime import datetime
black_monday = datetime(1987, 10, 19)
print(black_monday)
```

A. `black_monday.month` is equal to `10`.

B. `black_monday.day` is equal to `19`.

C. The type of `black_monday` is `<class 'datetime.date'>`.

D. `print(black_monday)` displays exactly the string `'1987-10-19'`.

E. `datetime(1987, 19, 10)` creates the same datetime object as `datetime(1987, 10, 19)`.

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

A. `sell_date.year` is equal to `1997`.

B. `sell_date.month` is equal to `10`.

C. `sell_date.day` is equal to `27`.

D. `datetime.strptime(text, format_str)` returns a string.

E. Replacing `format_str` with `"%d/%m/%Y"` would produce a datetime with `month` equal to `10`.

---

<!-- Questions 3–12 to be added one at a time -->
