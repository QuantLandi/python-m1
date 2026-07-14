# Syllabus — Python Programming for Finance

## Administrative information

| Field | Value |
|-------|-------|
| Programme / Program | PGE |
| Campus | Multicampus (Lille / Sophia) |
| Year of study | M1 |
| Academic year | 2026/2027 |
| Semester | Fall |
| Course title | Python Programming for Finance |
| Course leader | Alexandre LANDI |
| Language of instruction | English |

---

## Course description

This course introduces Python programming for financial data analysis. Students with **no prior programming experience** learn to write Python scripts, manipulate numerical data with NumPy, work with tabular financial datasets using pandas, import data from CSV and Excel files, and perform basic time-series operations.

The course uses finance-themed examples (stock prices, market listings, returns) but focuses on programming and data skills rather than financial theory.

**Prerequisite:** none. Familiarity with spreadsheets is helpful but not required.

---

## Learning outcomes

Upon completion, students will be able to:

1. Write and debug short Python scripts using variables, built-in types, lists, and user-defined functions
2. Apply software engineering basics: readable code structure, docstrings, and simple testing concepts
3. Perform vectorized numerical operations with NumPy arrays
4. Parse and format dates with the `datetime` module; compare values across types
5. Create, explore, filter, and aggregate pandas DataFrames
6. Import and clean financial data from CSV, Excel, and online sources
7. Build and manipulate time-series indexes; apply rolling and expanding window operations
8. Read Python code and predict its output without executing it (exam skill)

---

### DataCamp courses used

**Midterm** — exam covers:

- [Introduction to Python for Finance](https://app.datacamp.com/learn/courses/introduction-to-python-for-finance)
- [Intermediate Python for Finance](https://app.datacamp.com/learn/courses/intermediate-python-for-finance)
- [Data Manipulation with Pandas](https://app.datacamp.com/learn/courses/data-manipulation-with-pandas)
- [Importing and Managing Financial Data in Python](https://app.datacamp.com/learn/courses/importing-and-managing-financial-data-in-python)
- [Manipulating Time Series Data in Python](https://app.datacamp.com/learn/courses/manipulating-time-series-data-in-python)
- [Introduction to Functions in Python](https://app.datacamp.com/learn/courses/introduction-to-functions-in-python)

**Final** — exam covers all midterm courses, plus:

- [Software Engineering Principles in Python](https://app.datacamp.com/learn/courses/software-engineering-principles-in-python)

> Verify DataCamp licensing before classroom use.

### Pre-class work

Students complete the corresponding DataCamp course **before** each session. Class time is not used for first exposure to new material; it focuses on clarification, live coding, and exam-style exercises.

---

## Schedule

**Contact time:** 12 sessions × 90 minutes (18 hours total).

Complete the listed DataCamp course **before** the corresponding session (see [Pre-class work](#pre-class-work)).

| Session | Complete before class | In class |
|--------:|----------------------|----------|
| 1 | [Introduction to Python for Finance](https://app.datacamp.com/learn/courses/introduction-to-python-for-finance) | Python basics, lists, NumPy — clarification and exam-style exercises |
| 2 | [Intermediate Python for Finance](https://app.datacamp.com/learn/courses/intermediate-python-for-finance) | Datetimes, comparisons, DataFrame basics — clarification and exam-style exercises |
| 3 | [Data Manipulation with Pandas](https://app.datacamp.com/learn/courses/data-manipulation-with-pandas) | DataFrames, filtering, aggregation, indexing — clarification and exam-style exercises |
| 4 | [Importing and Managing Financial Data in Python](https://app.datacamp.com/learn/courses/importing-and-managing-financial-data-in-python) | CSV/Excel import, cleaning, groupby — clarification and exam-style exercises |
| 5 | [Manipulating Time Series Data in Python](https://app.datacamp.com/learn/courses/manipulating-time-series-data-in-python) | Timestamps, resampling, rolling/expanding windows — clarification and exam-style exercises |
| 6 | [Introduction to Functions in Python](https://app.datacamp.com/learn/courses/introduction-to-functions-in-python) | User-defined functions, scope, docstrings — clarification and exam-style exercises |
| — | **Midterm exam** | Covers the six courses above |
| 7 | [Software Engineering Principles in Python](https://app.datacamp.com/learn/courses/software-engineering-principles-in-python) | Modularity, PEP 8, testing — clarification and exam-style exercises |
| 8 | — | **In-class project** |
| 9 | — | **In-class project** |
| 10 | — | **In-class project** |
| 11 | — | **In-class project** |
| 12 | — | **In-class project** |

Students follow one of two tracks for sessions 8–12:

- **Structured Products** — build a derivative pricing tool
- **Corporate Valuation** — build a company valuation tool

---

## Assessment

| Component | Format |
|-----------|--------|
| Midterm exam | MCQ — code-based |
| Final exam | MCQ — code-based |

**Midterm coverage:** first six DataCamp courses (see [DataCamp courses used](#datacamp-courses-used)).

**Final coverage:** all midterm courses, plus Software Engineering Principles in Python.

### Exam rules

- **Duration:** 2 hours `[confirm]`
- **Questions:** 40; each presents a code snippet and 5 true/false statements
- **Authorized documents:** none
- **Calculator:** not allowed
- **Draft paper:** not allowed
- **Dictionary:** not allowed

### Scoring — all-or-nothing per question

Each question receives **full credit or zero**:

- Full credit if **all** true/false selections for that question are correct
- Zero credit if **any** selection is wrong or any required selection is missing
- No partial credit within a question
- No penalty scoring

**Maximum score:** 40 points (0.5 point per question)

### Resit

Same format as the final exam. A new question set is used. Resit grade replaces the final exam grade per program rules.
