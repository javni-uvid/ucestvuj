# The code, workflows and tests

Decisions about how the code is laid out, built and tested. Keep it current: a decision made or changed is
added at the end of the section it belongs to, in the same commit as the change. The principles and the rules
of work are in AGENTS.md.

## The code

How the code is written (21 Nov 2026, the maintainer: "take the principles of design and architecture for this
project as the other two projects that use osnova have them"): javni-uvid/zailiprotiv's rules
(`docs/decisions/code.md` there), as javni-uvid/izborna-analiza took them on 20 Nov 2026 and as they fit here.
They are rules for new code and for code being changed.

- **A module per source and per kind of page.** A reader per source: `opendata`, `consultations`, `sites`,
  `announcements` (with `when`: its periods and days); `web` is the one place a source is asked from. `site.py`
  (some 430 lines) loads `data/`, works out what the pages share and writes them all; when a new kind of page
  comes (a guide, a letter-writer), it goes in a module of its own, called from `site.build` with what it
  needs. A move is checked by building before and after and comparing every file.
- **Read once, then work out, then write.** `site.build` reads each file of `data/` once (`site.load`), works
  out what the pages share (the announcements by municipality, what is ahead, the open topics), and only then
  writes pages. Nothing is put into a page after it is written, and no module hands data back through an
  attribute of its function or a global it sets: it returns what it computed.
- **A reading keeps fields, not texts.** A reader returns plain rows (dicts of a few named fields) and the
  command writes them under `data/` with a line in `data/sources.json`; a page is built from `data/` alone, so
  a build asks no source and the same data gives the same site. What a rule reads from words (a kind, a topic,
  "held", a period) is a function of the row's stored words where it can be (`announcements.kind`, `topic`,
  `held`), so that a better rule needs no new reading; only what comes from a text that is not kept
  (`when.read`) is stored.
- **Shared helpers, not copies.** A store is written by `cli.save` (one entry per line, so git shows what
  changed); the transliteration is `translit`; a helper two modules need goes in one place rather than in both.
- **A guard on the built site.** `site.check` fails the build, and **pages** then publishes nothing, when a
  page loads anything from another server (principle 5), carries a script other than the site's own file,
  keeps a Cyrillic letter in the Latin text, or is over 1 MB. A list that can grow without bound gets pages of
  its own (a municipality's announcements) rather than growing the first page.
- **One page written once, in Cyrillic;** the Latin edition is the same page turned letter by letter
  (`translit.latin_page`), its addresses untouched. A page's words are never written twice.
- **The script only adds.** `static/site.js` filters the first page's list and counts days; a page is whole
  without it, and what it needs to say is in the page's own text, so that it is in the right script.
- **Faster without changing the output.** A cheaper count is checked to give the same files byte for byte, and
  the time is measured before and after (`osnova/work.md`, "Measured, then changed").

Not taken yet, to be weighed when the site gets its address: links without ".html" (zailiprotiv's
`publish.clean_urls`), and a size budget per kind of page.

## Workflows

| Workflow | When | What |
|---|---|---|
| test | on every pull request and push to `main` | the whole test suite |
| security | on code or workflow changes, Mondays, by hand | actionlint, zizmor, pip-audit, CodeQL; reads only |
| pages | on a push that changes the site or its data, every morning, by hand | build the site and publish it to GitHub Pages |
| list | Tuesdays, by hand | the list of the municipalities' sites copied from `javni-uvid/izborna-analiza`; starts **pages** |
| osnova | daily, by hand | the organization's shared rules, look and tools copied into `osnova/` |

The readings (`opendata`, `consultations`, `sites`, `announcements`) are run by hand for now; no workflow asks a
source. A run started with `GITHUB_TOKEN` can start another workflow (`gh workflow run`), which is how **list**
starts **pages**: a push by a workflow's own token starts none.

## Tests

- **No test asks a source.** A reader is tested on small made-up answers (`tests/test_reading.py`); the site is
  built from the data in the repository (`tests/test_site.py`); the stylesheet and the pages' frame are held to
  the design rules (`tests/test_design.py`).
- **A wrong reading becomes a test** with the sentence that caused it (`docs/decisions/data.md`), so a rule can
  be changed without losing what it already reads right.
- When new real data breaks a test on the data in the repository, find the cause in the code first; change the
  expectation only when the new data is right and the old expectation was wrong.
