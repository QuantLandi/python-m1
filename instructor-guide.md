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
- Practice quizzes (below) are how class matches this format before the exam


## Small habits that improve evaluations

- **Start and end on time**
- **Show enthusiasm** for Python — contagious for beginners


## Creating quizzes

In-class quizzes train the exam skill: **read a short snippet, judge five true/false statements**. Sessions 1–2 are the template — copy that pair, don’t invent a new layout.

**Non-negotiable**

- Mirror the exam: code-reading only; each item is a snippet + **A–E** true/false. No “write this function” items.
- Finance **flavour** when it helps (`price`, `returns`, tickers) — not finance theory.
- Nothing outside **that session’s** DataCamp course in [syllabus.md](syllabus.md) (no extra libraries, APIs, or syntax).
- Answer keys are **instructor-only**. Never project or share `*-quiz-answers.md` with students.

Sessions 1–2 exist. Add the same pair for each remaining DataCamp session (**3–7**). Sessions 8–12 are project time, not this format.

Skip the rest of this section once the checklist is muscle memory.

### Quick checklist

- [ ] Branch: one **session per PR** (do not push straight to `main`)
- [ ] `quizzes/session-NN-quiz.md` + `quizzes/session-NN-quiz-answers.md` (`NN` zero-padded: `03`, `04`, …)
- [ ] Student file header and question headings match sessions 1–2
- [ ] Student file links to the answer key; **no** True/False labels or **CORRECT ANSWERS** on the student file
- [ ] 12 questions: Q1–Q10 cover the course; Q11–Q12 are trickier review
- [ ] Every answer-key item has **CORRECT ANSWERS** and a **Debrief tip**
- [ ] You ran every snippet; every T/F is one you would defend in class
- [ ] README file table updated with both links
- [ ] No `.venv/` or editor junk; `uv.lock` / `pyproject.toml` only if you meant to change dependencies

### Files and naming

| File | Audience | Contains |
|------|----------|----------|
| `quizzes/session-NN-quiz.md` | Students (shared screen) | Snippets + A–E statements only |
| `quizzes/session-NN-quiz-answers.md` | Instructors | Same items, each statement marked True/False, then the key and debrief |

Student-file title: `# Session N quiz — <DataCamp course title>`. Then the same three bullets as sessions 1–2:

- **Review:** one question at a time
- **Scope:** full DataCamp course (Ch 1–…)
- **Plan:** 12 questions (Q11–Q12 are tricky review); allow ~70 min for Q1–Q10

Link the answer key from the student file (`Instructor answer key: [session-NN-quiz-answers.md](...)`).

Question headings: `## Question N (Chapter K — short topic)` for Q1–Q10; `## Question N (Review — short topic)` for Q11–Q12.

### Anatomy of one question

**Student file** — snippet, then five statements with **no** truth value:

````markdown
## Question 4 (Chapter 2 — Slicing with step)

Consider the following code:

```python
# short snippet
```

A. ...

B. ...

C. ...

D. ...

E. ...
````

**Answer key** — same snippet and wording, each line ends `— **True**` or `— **False**`, then:

```markdown
**CORRECT ANSWERS: A, C**

**Debrief tip:** One or two sentences. Link the slide/DataCamp beat; name the exam trap. Do not restate the key.
```

Keep statement **wording identical** on both files so you can debrief from the student projection. Only the answer file adds True/False, **CORRECT ANSWERS**, and the tip.

### Scope and coverage

- Align Q1–Q10 with **that session’s** DataCamp course (chapter spread like sessions 1–2: walk the course, don’t dump everything in Ch 1).
- Q11–Q12: same course, but the traps students miss on a first pass.
- Budget: **~70 minutes** for Q1–Q10 in a 90-minute session; review items if time remains.
- Set **Scope:** to the actual chapter count of that course (session 1 is Ch 1–5; session 2 is Ch 1–4).

### Item-writing

**Do**

- One idea per statement when you can — the exam is all-or-nothing per question, so muddled T/F punishes the wrong thing.
- Make false options **plausible** (the wrong method name, the wrong dunder, the value before vs after a mutation).
- Keep snippets **short**: enough to read on a slide; names that look like finance data if it clarifies, not if it clutters.
- Test **what the code does** (types, mutation, filtering, what `print` shows).

**Don’t**

- Overlong snippets — if they must scroll, cut.
- Two ideas in one T/F (*“`.sort()` returns `None` and `original` is unchanged”* — split or drop).
- Pandas trivia that isn’t in that course (obscure parameters, version quirks).
- Finance theory dressed as code (*“this P/E is expensive”*).
- Mixing **`print` output** with the **repr** of a value (`print(30.0)` vs `30` vs `"30.0"`) unless that distinction **is** the point — then make it explicit.
- Vague in-place vs copy items — `.sort()` vs `sorted()` is fair game; name which object you mean (`prices` vs `original` vs `result`).

### Debrief tips (required)

Every answer-key item needs one. A good tip:

- Points at the **slide or DataCamp beat** (*“From Ch 3 — contrast `np.array([...])` with a Python list”*)
- Names the **exam trap** (*string `"4"` vs int `4`*; `%m` vs `%M`)
- Does **not** repeat **CORRECT ANSWERS**

Write the tip for you at the whiteboard, 20 seconds after students vote.

### Using AI to draft

Cursor may **draft** items. You still:

1. Edit until the item matches this spec and that session’s course
2. **Run** the snippet (`uv run python`) — don’t trust a model’s predicted output
3. Own every T/F: if a “false” option is actually true, that’s your miss in class

Generic or off-syllabus drafts are expected; throwing them out is part of the job.

### Submit via pull request

Same steps as [README.md](README.md#contributing-quizzes-instructors); repeated here so you can stay in this file.

1. Clone, branch named for the session (one session per PR).
2. Add the two quiz files; match sessions [1](quizzes/session-01-quiz.md) / [2](quizzes/session-02-quiz.md) and their answer keys.
3. Add both files to the table in [README.md](README.md).
4. Open a PR. Do not commit `.venv/` or other local junk.

**Before you open the PR**

- [ ] Filenames are `session-NN-quiz.md` and `session-NN-quiz-answers.md`
- [ ] Student header, 12 × (snippet + A–E), chapter/review titles
- [ ] Answer key: True/False on each line, **CORRECT ANSWERS**, **Debrief tip** — 12 times
- [ ] Student file links to the answer key; answers are not on the student file
- [ ] Snippets run; outputs match what you claim
- [ ] Scope matches the syllabus DataCamp course for that session
- [ ] README table has both links
- [ ] Diff has no `.venv/`, `.cursor/`, or accidental `uv.lock` / `pyproject.toml` edits

### In class

Ungraded practice. Project the **student** file only.

- One question at a time; students vote or write A–E, then you debrief from the tip
- Aim for ~70 minutes on Q1–Q10; use Q11–Q12 if the room is fast
- Don’t open the answers file on the shared screen
- After the item: name the trap, don’t read out the key like a list
