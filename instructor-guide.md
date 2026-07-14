# Instructor guide — Python Programming for Finance

Private notes for teaching PGE M1, Fall 2026. See [syllabus.md](syllabus.md) for the official course document.


## What drives student evaluations

Students rate a course well when they feel they **can succeed**, not when the most content is covered. For this cohort — **no prior programming**, flipped DataCamp model, MCQ exams — evaluations hinge on:

1. **Predictability** — class matches what the exam tests
2. **Preparation paying off** — showing up after doing DataCamp feels worthwhile
3. **Early wins** — something working by session 2–3
4. **Relevance** — finance examples and track projects tied to their specialization
5. **Low friction** — Python environment works; materials are easy to find


## Before the semester

- [ ] Confirm DataCamp access for all students (license or individual accounts)
- [ ] Send a welcome email: explain the flipped model, link to session 1 DataCamp course, state expected workload outside class


## Pre-class work — make it stick

The course design assumes students complete the DataCamp course **before** each session. Without this, 90 minutes is not enough.

**Encourage compliance (without a separate grade):**

- Start warm-ups with: *"Hands up if you finished the DataCamp course."* — no shaming, but makes gaps visible
- Tie warm-up questions directly to DataCamp chapters
- If many students are unprepared, spend Q&A on essentials and assign the rest as catch-up — but **do not** reschedule the whole course; adjust within the session


## Known content gaps

The DataCamp finance courses teach students to **call** functions and methods, but barely cover:

- **`if` / `for` / `while`** — needed for the project
- **Writing functions** — until session 6 (Introduction to Functions)

**Recommendation:** spend 15–20 minutes in session 1 on a minimal `if` and `for` loop with a finance example (e.g. filter positive returns). Repeat briefly in session 6 when introducing `def`.


## Exam alignment

Exams are **code-reading MCQ**: 40 questions, 5 true/false statements each, closed book.

**What students appreciate:**

- Every exam question type appears in a warm-up or practice block before the exam
- No surprises in library behaviour or trick questions outside course material
- After the midterm, share **general** feedback (*"many students confused `.cummax()` with `.cumsum()`"*) without revealing answers


## Small habits that improve evaluations

- **Start and end on time**
- **Show enthusiasm** for Python — contagious for beginners
