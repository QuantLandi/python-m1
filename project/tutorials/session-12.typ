#import "lib.typ": *

#show: tutorial.with(
  session: 12,
  title: "Deploy and read your code",
  goal: [Freeze features, walk through Streamlit Community Cloud, practise exam-style reading.],
  you-leave-with: [You know the Cloud settings and why bundled `data/` matters. There are *no student demos*.],
)

== Feature freeze

Do *not* add tabs, heatmaps, or extra tickers today. Commit a clean tree:

#cmd("git status
git add -A
git commit -m \"session 12: freeze\"
git push")

Your GitHub repo must be visible to Streamlit (usually *public*, or Cloud connected to your GitHub account).

== How Cloud differs from your laptop

On your laptop you often run:

#cmd("uv run streamlit run dashboard.py")

from the folder that *contains* `dashboard.py`.

Streamlit Cloud clones the *GitHub repository root*.

- If the repo *is* the dashboard (template): *Main file path* is `dashboard.py`.
- If the dashboard lives in a subfolder `dashboard/`: *Main file path* is `dashboard/dashboard.py`.

Python version: *3.12* (not 3.14). Dependencies: committed `uv.lock` and/or `requirements.txt` in the folder Cloud inspects (follow the instructor).

`DATA_DIR` uses `Path(__file__)` in `paths.py`, so bundled CSVs still resolve on Cloud. *Never* write into `data/` at runtime.

Yahoo Finance is often *blocked* on Cloud. The app must still render from CSVs. That is a feature, not a failure.

== Walkthrough (follow the shared screen)

- Open #link("https://share.streamlit.io/")[share.streamlit.io] and sign in with GitHub.
- *Create app*.
- Repository: your fork (or the volunteer repo the instructor uses).
- Branch: `main` (unless you were told otherwise).
- *Main file path:* as above.
- Python: *3.12*.
- Deploy. Watch the *build log*. Red text about Yahoo is expected; a crash on *import* is not.

#note[
  No secrets. FRED uses the public `pandas_datareader` feed.
]

If Cloud is down, rehearse locally from the *repository root* (instructor course repo layout):

#cmd("uv run --project dashboard streamlit run dashboard/dashboard.py")

== Troubleshooting

#table(
  columns: (auto, 1fr),
  inset: 6pt,
  stroke: 0.4pt + luma(200),
  [*Symptom*], [*Check*],
  [Module not found], [Is `uv.lock` committed? Did Cloud pick the dashboard project?],
  [Wrong Python], [App settings $->$ 3.12],
  [Theme missing], [`.streamlit/config.toml` next to the app (or repo root --- follow the instructor)],
  [Page not found], [`dashboard.py` builds view paths from `Path(__file__).parent`],
  [Empty charts], [Bundled `data/` present? Live Yahoo/FRED failed --- look for your `st.info` banner],
)

== Exam-shaped reading (in class)

The final is *closed book*, snippet + true/false. Open *your* `views/common.py` and `views/equities.py`. With a neighbour, answer out loud:

- After `@st.cache_data` on `_fetch_live_prices`, does the second identical call hit Yahoo again within the TTL?
- Why is Yahoo's `end` one day after the last date we want on the chart?
- What does `preprocess` do if a column has a hole, then a value? (`.ffill()` then `.dropna()`)
- Why fetch `end_date - 365 days` even when the chart starts yesterday?
- Why must Bonds use `bonds_start_date` instead of `start_date`?

If you built FX: what is the difference between `usd_quote` and `usd_base`?

You will not get a quiz paper today. The *habit* is the point: read the line, predict, then look.

== Optional: tests

If `tests/test_loaders.py` exists:

#cmd("uv run pytest")

A passing test is nice. It is not a grade.

== After class

The project stays ungraded. Revise *your* functions for the final MCQ. AI is allowed while you work *if you can explain every line*; the exam has no AI.
