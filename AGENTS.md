# AGENTS.md

How to work on this repository, what must not change, and why things are as they are. For coding agents and for
people. The rules of work and the principles are here; each part's decisions are in the files the map names.

## How to work here

- **Read `osnova/work.md` first:** the rules every javni-uvid project shares. `osnova/security.md` holds the
  guards, `osnova/principles.md` the promises, `osnova/design/` the family's look. The folder is a copy of
  `javni-uvid/osnova`'s `shared/`: changed there, never here.
- **The repository is `javni-uvid/ucestvuj`** (made by the maintainer on 20 Nov 2026, which also settled the name:
  Učestvuj; first pushed that day with everything read so far, the maintainer's decision). From then on a
  branch and a pull request per task in an Orca worktree (`~/orca/workspaces/ucestvuj/`; `orca.yaml` runs
  `uv sync`), `sh tools/posalji.sh <body file>` to ship. A preview of the site is on GitHub Pages (21 Nov 2026,
  the maintainer's request); a domain and the family's link to it are the maintainer's decisions.
- **The tests are `uv run pytest -q`**; the **test** workflow runs them on every pull request and on `main`,
  and **security** checks the workflows, the packages and the code. On Windows set `PYTHONUTF8=1`.
- **The list of the municipalities' sites is izborna-analiza's** (`data/municipal_sites.csv` is a copy, brought by
  `ucestvuj list` and the **list** workflow): an address found or corrected is written there, never here.
- **The design rules and the code's rules are the family's** (21 Nov 2026, the maintainer's decision): the
  rules javni-uvid/zailiprotiv keeps, as javni-uvid/izborna-analiza took them, adapted here. A change to a page
  is checked against "Design rules" in `docs/decisions/site.md` (the phone first: 320 and 390 px, both
  scripts); a change to the code against `docs/decisions/code.md`. `tests/test_design.py` holds what a test can.
- **Ask a source little,** name the project in the User-Agent (`web.AGENT`), read incrementally. The readings
  are run by hand for now (README.md, Commands); the tests (`uv run pytest -q`) ask no source.
- **Talk to the maintainer in Serbian** (Latin script), briefly. Code, comments and docs are in English.

## Principles

The project's promises to its readers. Never changed without the maintainer. They are the family's seven
(`osnova/principles.md`); what is this project's own is said under each.

1. **The same rules for everyone a guide counts.** Every municipality is described by the same template and the
   same fields; none is singled out, and lists are in alphabetical order.
2. **Facts from primary sources only:** the law as published (the Official Gazette's register), a municipality's
   own statute and decisions as it published them, and an institution's own datasets. A handbook of an
   organization, a news report or another project's reading of the law may help find or check something; it
   never supplies a rule, a number or a deadline.
   - **For the page of actions only** (22 Nov 2026, the maintainer: "we may go outside the municipal sites as long
     as the source is positive and publishes actions", and "news and social networks too, as long as we say it is
     the source"): the source of an action may be an organizer that is not an institution, news or a social
     network, if the row says that this is the source and links it. Never a rule, a number or a deadline of the
     law, never a person's contact. Debates, inspections, consultations and the guides stay with institutions
     (`docs/decisions/data.md`, "The page of actions, and the rule for its sources").
3. **The site shows; it doesn't judge.** A guide says what the law gives and what a body must do. It does not
   say whether a municipality is good or bad at it, and it ranks none.
4. **Only what a person does in public office.** A guide names the body and the office ("the president of the
   assembly"), and links the institution's own page for who holds it. A public official named in a source's
   title stays as the source wrote it; a title that may name a private person is not shown (21 Nov 2026, the
   maintainer's decision; `docs/decisions/site.md`).
5. **Nothing from third parties on the pages.** A letter a reader writes with the site's help is made in their
   browser and sent by them; the site receives nothing.
6. **A source's words stay as they are.** An article is quoted word for word with its number and the version of
   the law it is from. A plain-words explanation says that it is one.
7. **Every rule can be followed to its source:** each step links the article it rests on, and each page says the
   day its sources were last checked.

One more, this project's own:

8. **Not legal advice, and it says so.** A guide states what the law says; where practice is known to differ
   from the text, it says that it doesn't know the practice rather than guess it.

## Where the decisions are

| Part | File |
|---|---|
| The sources, what is read from each and how | `docs/decisions/data.md` |
| The site: its pages, the design rules, what a page says, the preview | `docs/decisions/site.md` |
| The code's layout, the build's steps, the workflows, the tests | `docs/decisions/code.md` |

## Open decisions (the maintainer's)

- The site's address.
- Which mechanisms come first (`docs/decisions/data.md` has a proposal).
- Whether a municipality's statute is read by a model and checked by a person, or by a person only.
- Whether a political call is left out of the page of actions by its content or only by the rule that the organizer
  itself publishes an action open to anyone (`docs/decisions/data.md`).
- Whether a model reads an announcement's text a second time, beside the program (`docs/decisions/data.md`).

Decided on 21 Nov 2026 (`docs/decisions/site.md`, `docs/decisions/data.md`): a debate that was held is shown as
held, apart from the calls; public officials in a title are kept, a title naming an applicant is not shown; the
periods and days of a debate are read from the announcement's text by a program (`when.py`), and only they are
kept, never the text; the first page is one list with filters, run by the site's one own script.
