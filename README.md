# Učestvuj

Guides to how a person takes part in decisions where they live, in Serbia: what the law gives them (a citizens'
assembly, a citizens' initiative, a local referendum, a public debate, a request for information of public
importance, a petition), what their own municipality's statute adds, where to send what, and by when. Every
step with the article it rests on.

One of [Javni uvid](https://javni-uvid.github.io/osnova/)'s sites, beside Za ili Protiv and Izborni podaci.

**Status:** started on 20 Nov 2026. A preview of the site: https://javni-uvid.github.io/ucestvuj/ (not indexed by
search engines). The first sources are read
into `data/` (the bodies a letter can be sent to, the municipalities, the state's consultations, and what 49
municipalities announce on their own sites, with when what each calls to is on: the period of a debate or an
inspection, a session's day and hour, the last day for remarks; so the site lists first what is still ahead); no guide is written yet. `docs/decisions/data.md` says what each
source gave and what is not read.

## Commands

```sh
uv sync
uv run ucestvuj opendata        # the bodies, the municipalities and local government's tasks, from data.gov.rs
uv run ucestvuj consultations   # every topic on eKonsultacije
uv run ucestvuj sites           # what each municipality's own site is and links to (one request per site)
uv run ucestvuj actions         # actions to join: blood drives, volunteer shifts, clean-ups (after `sites`)
uv run ucestvuj announcements   # public debates and inspections the municipalities announce, and when each is on (after `sites`)
uv run ucestvuj site --out _site   # the site from data/ (fails on a page that loads anything from elsewhere)
uv run pytest -q              # no test asks a source
```

## Workflows

| Workflow | When | What |
|---|---|---|
| test | on push and pull requests | the test suite |
| security | on code or workflow changes, Mondays, by hand | actionlint and zizmor (the workflows), pip-audit (the packages), CodeQL (the code) |
| pages | on a push that changes the site or its data, every morning, and by hand | build the site and publish it to GitHub Pages |
| actions | daily, Mondays in whole, and by hand | the actions to join (blood drives, volunteer shifts) read from the institutes' and the service's pages and the municipalities' posts; starts pages |
| osnova | daily, and by hand | the organization's shared rules, look and tools copied into `osnova/` |

The readings are run by hand for now; only **actions** asks a source by itself.

**An action the page of actions lacks** is reported by a form (`.github/ISSUE_TEMPLATE/akcija.yml`, linked from the
page); an organizer's or a news site's feed is added to `data/action_feeds.csv`; a checked report goes into
`data/actions_manual.json`.

**A municipality's site that is missing or wrong** is reported to
[osnova](https://github.com/javni-uvid/osnova/issues): the list (`osnova/data/municipalities.csv`) is one for
every javni-uvid project, and a correction there reaches this site with the next copy of osnova.

## What it will hold

- **A guide per mechanism**, one template for all: who may use it, what it takes (signatures, a deadline, a
  form), where it is sent, what the body must do and by when, what to do when it doesn't, and the articles.
- **What a municipality's own statute says** where the law leaves it to the statute (how many signatures, who
  calls an assembly), with a link to the statute.
- **Small tools:** a letter written from the reader's answers (a request for information first), sent by the
  reader themselves; the site sends nothing and keeps nothing.

## Principles

The family's (`osnova/principles.md`), whole in `AGENTS.md`.

## Layout

```
osnova/            the organization's shared rules, look and tools (a copy; changed in javni-uvid/osnova)
docs/decisions/    the decisions by part: data.md (the sources), site.md (the pages, the design rules), code.md
src/ucestvuj/        the readers: opendata, consultations, sites, announcements (when: its periods and days), actions; web; cli
                   site.py, translit.py, static/ (the look, and site.js: the first page's filters): the site from data/
data/              what was read, and sources.json: where each file came from and when
tests/
tools/             one-line callers of osnova/tools/
.github/           the workflows; dependabot (monthly); the pull request's template
```

## License

Code: MIT (`LICENSE`).
