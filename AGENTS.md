# AGENTS.md

How to work on this repository, what must not change, and why things are as they are. For coding agents and for
people. The rules of work and the principles are here; each part's decisions are in the files the map names.

## How to work here

- **Read `osnova/work.md` first:** the rules every javni-uvid project shares. `osnova/security.md` holds the
  guards, `osnova/principles.md` the promises, `osnova/design/` the family's look. The folder is a copy of
  `javni-uvid/osnova`'s `shared/`: changed there, never here.
- **The project is local** (20 Nov 2026, the maintainer: "let us start it locally"). There is no repository on
  GitHub yet, so no pull requests, no workflows and no copy by the **osnova** workflow: `osnova/` here was
  copied by hand and is refreshed by hand until the repository exists. Making the repository, a name, a domain
  and anything published are the maintainer's decisions.
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
3. **The site shows; it doesn't judge.** A guide says what the law gives and what a body must do. It does not
   say whether a municipality is good or bad at it, and it ranks none.
4. **Only what a person does in public office,** and here no person is named at all: a guide names the body and
   the office ("the president of the assembly"), and links the institution's own page for who holds it.
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

## Open decisions (the maintainer's)

- The name and the address.
- Which mechanisms come first (`docs/decisions/data.md` has a proposal).
- Whether a municipality's statute is read by a model and checked by a person, or by a person only.
- Announcements' titles: which count as a call to take part, and what is done with a title that names a person
  (`docs/decisions/data.md`, "What the reading showed"). Nothing from `announcements.json` is published before.
