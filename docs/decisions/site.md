# The site

Decisions about the pages. Keep it current: a decision made or changed is added at the end of its section, in
the same commit as the change.

## The preview

- **A preview on GitHub Pages** (21 Nov 2026, the maintainer: "publish it on GitHub Pages for now, to see how it
  looks"): https://javni-uvid.github.io/ucestvuj/, built by the **pages** workflow from `data/` as committed
  (`ucestvuj site`). Every page asks search engines not to index it (`noindex`) and says it is a preview, with
  the day the data was read. The site is not in `osnova/design/sites.json`, so the family's other sites don't
  link it yet; its own bar and footer name it among them. A domain and the family's link are the maintainer's.
- **Pages:** the first page (the municipalities' announcements of the last 30 days, then the state's topics
  open today), the municipalities in the Serbian alphabet with what is read from each, a page for each
  municipality with announcements (by year, newest first), the state's consultations, and the project
  (sources with the day each was read, the rules, what is not here yet).
- **The look is the family's** (`osnova/design/osnova.css`: Literata and the system font, black on white, the
  bar and the footer block); `static/site.css` lays out the lists and tables and gives nothing a colour of its
  own. Written once in Cyrillic; the Latin edition is the same page turned letter by letter (`translit.py`),
  its addresses untouched, at the root, the Cyrillic under `cir/`. No script on any page. The build fails on a
  page that loads anything from another server, keeps a Cyrillic letter in the Latin text, or is over 1 MB.

## What a page says

- **An announcement's title is the municipality's words,** shown as written and linked to its page there; the
  Latin edition transliterates it. Its kind (public debate, public inspection, early public inspection) comes
  from the title by the rule in `announcements.py`. A title may be news that a debate was held: each
  municipality's page says so.
- **Public officials in a title are kept** (21 Nov 2026, the maintainer: "if they are public officials, we
  can"). **A title that names the one who asked for a plan or a study** (an investor, an applicant, a project's
  holder) may name a private person, so it is not shown: the row gives the kind and a link to the
  municipality's page (`site.APPLICANT`). The rule goes by words and errs on the side of hiding: a company named
  as investor is hidden too. A private person named otherwise is not caught by it; a reader's report is
  answered by a correction of the rule.
- **A debate that was held is shown as held** (21 Nov 2026, the maintainer: "if the debate was held, then that is
  how it is"). An announcement whose title says the debate or the inspection is over (news that it was held, a
  report on it; `announcements.held`) is kept, marked "одржано", and on the first page listed apart, under the
  calls and notices. Of the 1,530 titles 65 say so; of the 32 of the last 30 days, 3. A title that doesn't say
  so may still be news of a debate ("the mayor at the public debate on the budget"): the rule goes by words and
  the pages say that. The days of a debate are read from the announcement's text (below).
- **What is ahead comes first** (21 Nov 2026, the maintainer: "we should also read when the debate is"). The
  first page opens with the municipalities' announcements, not said to be held, in which something named is
  still under way or yet to start, the nearest day first (12 from 7 municipalities on 21 Nov 2026); then the
  other calls and notices of the last 30 days; then what was held.
- **A row says what is when, as the announcement does** (21 Nov 2026, the maintainer, on a row that showed one
  bare date for a month-long inspection): under the title, a line for each period or day with what it is of
  ("Јавни увид: од 30. 10. 2026. до 28. 11. 2026.", "Јавна седница: 8. 12. 2026. у 13:00", "Примедбе: до …",
  "Јавни увид: од 30. 10. 2026., 30 дана"), also on the municipality's page. A period or day the words don't
  name is shown as "У објави" and does not put the announcement among what is ahead. How they are read is in
  `docs/decisions/data.md`; the project's page says it in short and asks for a wrong one to be reported.
- **Open is what is under way today:** a state topic is listed as open when its phase under way, by the
  portal's own days (`consultations.phases`), ends today or later. Of the 181 topics the portal kept as not
  ended on 21 Nov 2026, 7 were.
- **The municipalities' states are said, not judged:** "we read it", "not yet" (the site answers, its
  announcements can't be read yet), "doesn't answer", "no address". The page says that this is no mark of the
  municipality.
- **The list of sites is shared with Izborni podaci, and the page says so** (21 Nov 2026, the maintainer: a
  connection between the two for when someone finds a new local site). The municipalities' page links
  izborna-analiza's issues for an address that is missing or wrong, since the list is kept there
  (`docs/decisions/data.md`). A municipality whose address in the list is not the one last looked at says
  "the address is new, not read yet", and links the list's address.
