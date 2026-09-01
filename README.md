# Python Programming for Finance

PGE M1 · Fall 2026 · instructor repo

## Setup

**Editor:** [Cursor](https://cursor.com/) (AI-native code editor — course standard).

We use an AI-native editor because AI is part of how code gets written now, and exams still require reading code without it. Cursor is the course standard: VS Code–compatible, widely used, and easy to use as a normal editor with AI only when you choose.

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). Then:

```bash
uv sync
```

Run scripts with `uv run python path/to/script.py`.

## AI policy

Exams test **reading and predicting code without AI**. Use Cursor’s AI to learn faster — not to skip understanding.

- **Encouraged (with limits):** after you try yourself, use AI to explain errors/tracebacks, explain what a line does, or suggest a fix (including Tab autocomplete).
- **Counterproductive:** having AI generate a full solution, script, or notebook for you — you won’t be able to explain it, and exams give you no AI.
- **Class practice / quizzes / DataCamp / project:** try without AI first; AI is OK only if you can explain every line of the result.
- **Midterm & final:** closed book, **no AI**.

## Contributing quizzes (instructors)

How to write a quiz (format, item-writing, QA, in class): [instructor-guide.md — Creating quizzes](instructor-guide.md#creating-quizzes).

For remaining DataCamp sessions (3–7), add quizzes via pull request (do not push straight to `main`). Sessions 8–12 are in-class project, not this quiz format.

1. Clone this repo and create a branch (one **session per PR**).
2. Add `quizzes/session-NN-quiz.md` and `quizzes/session-NN-quiz-answers.md`, matching the session 1–2 pattern (exam-style code + 5 true/false; answer key with **CORRECT ANSWERS** and a short **Debrief tip**). Link the student file to the answer key and align scope with that session’s DataCamp course in [syllabus.md](syllabus.md).
3. Update the file table below with both new links.
4. Open a PR. Do **not** commit `.venv/` (or other local IDE junk); `uv.lock` / `pyproject.toml` only if you intentionally change dependencies.

| File                                                                     | Purpose                                         |
| ------------------------------------------------------------------------ | ----------------------------------------------- |
| [syllabus.md](syllabus.md)                                               | Course syllabus                                 |
| [instructor-guide.md](instructor-guide.md)                               | Teaching notes; how to create quizzes           |
| [pyproject.toml](pyproject.toml)                                         | Python project / dependencies (managed with uv) |
| [quizzes/session-01-quiz.md](quizzes/session-01-quiz.md)                 | Session 1 in-class practice quiz                |
| [quizzes/session-01-quiz-answers.md](quizzes/session-01-quiz-answers.md) | Session 1 answer key (instructor only)          |
| [quizzes/session-02-quiz.md](quizzes/session-02-quiz.md)                 | Session 2 in-class practice quiz                |
| [quizzes/session-02-quiz-answers.md](quizzes/session-02-quiz-answers.md) | Session 2 answer key (instructor only)          |


