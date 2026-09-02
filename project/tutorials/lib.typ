#let course = "Python Programming for Finance · PGE M1"
#let project-name = "Cross-Asset Market Monitor"

#let tutorial(session: int, title: "", goal: [], you-leave-with: [], body) = {
  set page(
    paper: "a4",
    margin: (x: 1.8cm, y: 1.7cm),
    numbering: "1",
    header: context {
      set text(size: 8.5pt, fill: luma(80))
      grid(
        columns: (1fr, auto),
        course,
        [Session #session],
      )
      line(length: 100%, stroke: 0.4pt + luma(180))
    },
    footer: context {
      set text(size: 8.5pt, fill: luma(80))
      line(length: 100%, stroke: 0.4pt + luma(180))
      v(4pt)
      grid(
        columns: (1fr, auto),
        project-name,
        [Page #counter(page).display()],
      )
    },
  )
  set text(size: 10.5pt)
  set par(justify: true, leading: 0.65em)
  set heading(numbering: none)
  show heading.where(level: 1): set text(size: 14pt)
  show heading.where(level: 2): set text(size: 12pt)
  show raw.where(block: true): it => {
    set text(size: 7.8pt)
    block(
      width: 100%,
      fill: luma(96%),
      inset: 8pt,
      radius: 2pt,
      stroke: 0.4pt + luma(200),
      it,
    )
  }
  show raw.where(block: false): set text(size: 9pt)
  show link: underline

  heading(level: 1, numbering: none)[Session #session --- #title]

  block(
    width: 100%,
    fill: luma(94%),
    inset: 10pt,
    radius: 2pt,
    [
      *In class (90 min).* Type along with the instructor. The project is *not graded*. The final exam is a closed-book MCQ: you must be able to *explain every line* you type.

      *Goal.* #goal

      *You leave with.* #you-leave-with
    ],
  )

  body
}

#let note(body) = block(
  width: 100%,
  inset: (x: 10pt, y: 8pt),
  stroke: (left: 2.5pt + luma(40)),
  [*Note.* #body],
)

#let warn(body) = block(
  width: 100%,
  inset: (x: 10pt, y: 8pt),
  stroke: (left: 2.5pt + luma(40)),
  [*Watch out.* #body],
)

#let cmd(body) = raw(body, block: true, lang: "bash")
