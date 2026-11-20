# Učestvuj

Guides to how a person takes part in decisions where they live, in Serbia: what the law gives them (a citizens'
assembly, a citizens' initiative, a local referendum, a public debate, a request for information of public
importance, a petition), what their own municipality's statute adds, where to send what, and by when. Every
step with the article it rests on.

One of [Javni uvid](https://javni-uvid.github.io/osnova/)'s sites, beside Za ili Protiv and Izborni podaci.

**Status:** started on 20 Nov 2026; the repository is javni-uvid/ucestvuj, and there is no site yet. The first sources are read
into `data/` (the bodies a letter can be sent to, the municipalities, the state's consultations, and what 49
municipalities announce on their own sites); no guide is written yet. `docs/decisions/data.md` says what each
source gave and what is not read.

## Commands

```sh
uv sync
uv run ucestvuj opendata        # the bodies, the municipalities and local government's tasks, from data.gov.rs
uv run ucestvuj consultations   # every topic on eKonsultacije
uv run ucestvuj sites           # what each municipality's own site is and links to (one request per site)
uv run ucestvuj announcements   # public debates and inspections the municipalities announce (after `sites`)
uv run pytest -q              # no test asks a source
```

## Workflows

| Workflow | When | What |
|---|---|---|
| test | on push and pull requests | the test suite |
| security | on code or workflow changes, Mondays, by hand | actionlint and zizmor (the workflows), pip-audit (the packages), CodeQL (the code) |
| osnova | daily, and by hand | the organization's shared rules, look and tools copied into `osnova/` |

The readings are run by hand for now; no workflow asks a source.

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
docs/decisions/    the decisions by part; data.md has the sources
src/ucestvuj/        the readers: opendata, consultations, sites, announcements; web (asking a source); cli
data/              what was read, and sources.json: where each file came from and when
tests/
tools/             one-line callers of osnova/tools/
.github/           the workflows; dependabot (monthly); the pull request's template
```

## License

Code: MIT (`LICENSE`).
