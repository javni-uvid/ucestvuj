# The site

Decisions about the pages. Keep it current: a decision made or changed is added at the end of its section, in
the same commit as the change.

## The preview

- **A preview on GitHub Pages** (21 Nov 2026, the maintainer: "publish it on GitHub Pages for now, to see how it
  looks"): https://javni-uvid.github.io/ucestvuj/, built by the **pages** workflow from `data/` as committed
  (`ucestvuj site`). Every page asks search engines not to index it (`noindex`) and says it is a preview, with
  the day the data was read. The site is not in `osnova/design/sites.json`, so the family's other sites don't
  link it yet; its own bar and footer name it among them. A domain and the family's link are the maintainer's.
- **Pages:** the first page (one list of what is ahead and of the last 30 days' announcements, with filters;
  below), the page of actions (below), the municipalities in the Serbian alphabet with what is read from each, a page for each
  municipality with announcements (by year, newest first), the state's consultations, and the project
  (sources with the day each was read, the rules, what is not here yet).
- **The look is the family's** (`osnova/design/osnova.css`: Literata and the system font, black on white, the
  bar and the footer block); `static/site.css` lays out the lists and tables and gives nothing a colour of its
  own. Written once in Cyrillic; the Latin edition is the same page turned letter by letter (`translit.py`),
  its addresses untouched, at the root, the Cyrillic under `cir/`. One script, the site's own (below). The build
  fails on a page that loads anything from another server, keeps a Cyrillic letter in the Latin text, or is
  over 1 MB.

## The first page: where, what about, when

21 Nov 2026, the maintainer: "work out a fitting design for the site, where what matters to us is the location,
what is debated and when; we need filters for places and time; think of what else is useful."

- **One list, and every row answers the three questions in the same places:** where (the municipality's name in
  the serif, linked to its page; for a state body "Република Србија" and the body), what about (the title in
  the source's words, linked to the source, with the kind and the topic as small labels), and when (a column of
  its own: each period or day with what it is of, then the day of publication). The state's open topics are in
  the same list as the municipalities' announcements, as rows of the same shape.
- **The order is by what a reader can still do:** what is under way or yet to start first, the nearest day
  first; then the other announcements of the last 30 days, newest first, the held ones marked. The older ones
  are on each municipality's page.
- **Filters: place, time, kind, topic, a word in the title.** Place lists every municipality, read or not, and
  the republic; a chosen place says what is read of it and links all of its announcements, and one that is not
  read says so instead of showing an empty list. Time: under way or yet to start (the default), something
  starts or ends within 7 days, published in the last 30 days. The choice is kept in the page's address
  (`#mesto=80365&tema=budget`), so a reader can bookmark their municipality or send a link.
- **The topic is read from the title by words** (`announcements.topic`): the budget; taxes, fees and prices;
  urban and spatial plans; the environment; strategies and development plans; the rest. A plan comes before the
  environment, since a plan's inspection names its environmental report in the same title.
- **"The next day: in 2 days"** is counted in the reader's browser from their own today, so it is right on a
  page built earlier.
- **One script, the site's own** (`static/site.js`); this changes "no script on any page" of the same day,
  since filters need one. It hides rows, counts the days and writes the choice into the address. It stores
  nothing on the device and sends nothing (principle 5 holds: nothing from third parties). The page is whole
  without it: the list in its order with every day written out, the filters hidden. The build fails on any
  other script, on one written into a page and on an event attribute.
- **The site is built again every morning** (the **pages** workflow), so that what is ahead and what is over
  is right for a reader without the script.
- **Location is the municipality for now.** The place of a debate (the hall, the address) is in the
  announcement's text and is not read; the row sends the reader to the announcement for it.

Thought of and not built, the maintainer's to choose: a calendar file per row and per municipality ("add to my
calendar"); a feed per municipality of new calls; the place of the debate read from the text; the districts as
a filter above the municipalities; a map. The first two are only worth it once the readings run by themselves,
which they don't yet.

## Design rules

What the pages keep to (21 Nov 2026, the maintainer: "take the principles of design and architecture for this
project as the other two projects that use osnova have them"). They are javni-uvid/zailiprotiv's rules, which
came from looks at its site against WCAG 2.2, NN/g, GOV.UK, Stanford's credibility guidelines, the Trust Project
and ProPublica's principles for news graphics, as javni-uvid/izborna-analiza took them on 20 Nov 2026, adapted
to this site's reader: a person who wants to know what they can take part in where they live, most likely on a
phone. Working rules, changed as readers show otherwise, unlike the principles in AGENTS.md. A change to a page
is checked against them.

1. **One scale of letter sizes.** A size is a step of the family's scale (`--ju-t-1` … `--ju-t-8`, `--ju-t-h1`
   in `osnova.css`); body text is 16 px; grey (`--ju-muted`) is for what is secondary. `tests/test_design.py`
   refuses a size outside the scale.
2. **No colour here means anything.** Black ink on a white page, grey for what is secondary and for the cards,
   all from the family's `--ju-*` values; `site.css` declares no colour of its own (a test checks). Nothing
   needs one yet: a kind, a topic and "held" are words in a label. Should the site get a colour that carries
   data, it means a kind of content, never a municipality's merit (principle 3), is never the only way a fact
   is told, and its text keeps 4.5:1.
3. **The most important first.** A page says what it is and gives its main fact in the first screen: on the
   first page, what a reader can still take part in, the nearest day first. On a phone the place is chosen at
   once and the other choices are folded, so that the list begins on the first screen.
4. **A number never stands alone.** It says what it is counted of and has something to compare it with ("49 of
   168 municipalities", "12 announcements from 7 municipalities"), and a way to how it is read. Unknown is not
   zero: a municipality that is not read says so, and an announcement without a day says that none was found.
5. **A trend is drawn, a table is kept.** There is no chart yet; when the point is how something changed, bars
   from zero come first, in black and grey, and the table follows. No chart without its numbers.
6. **The phone first.** Every change is looked at at 320 and 390 px in both scripts; no page is wider than its
   screen; things to press are 44 px high; a long list shows its first rows and a way to the rest (the first
   page holds what is ahead and the last 30 days, the rest is on each municipality's page).
7. **Everything can be checked.** Each row leads to the institution's own announcement; each page says the day
   its sources were read; the project's page says how each thing is read (a kind, a topic, a period) and that a
   program reads it. Nothing is ranked by preference, and no municipality is marked (principles 1 and 3).
8. **For every reader.** Keyboard and screen reader reach everything; every page works without its script
   (`site.js` only filters and counts days); the keyboard's place is outlined in ink, the first Tab skips to the
   page (`.skip`); nothing moves; the reader is not addressed as a man or a woman.
9. **Measured, then changed.** The size of the pages (the build's 1 MB limit; the largest is 122 KB) and, once
   there are any, visit counts are read before a change to how a page is laid out, and after it.

Checked on 21 Nov 2026: the first page, a municipality's page and the municipalities' table at 320 and 390 px
in both scripts (no page wider than its screen); rules 1, 2 and 8 by `tests/test_design.py`. Not done yet: a
run of axe-core's WCAG 2.2 AA rules on every kind of page, as izborna-analiza does on a template's change.

## The page of actions

22 Nov 2026, the maintainer: "we make a separate tab from the public debates; put all public actions for improving
the environment, giving blood, positive initiatives there".

- **A page of its own, `akcije.html`,** with its own place in the bar ("Расправе | Акције | Општине | Држава"):
  the first page keeps the debates, inspections and consultations; this one the things to do. The first page leads
  to it in one sentence.
- **The same row as the debates': where, what about, when.** The place (the municipality without "Град" or
  "Градска општина"), the venue in grey under it; the title as the source wrote it, linked to the announcement;
  the kind as a label (blood, volunteering, environment); the column of days: the day and the hours, a position's
  application deadline, "Следећи дан: за 2 дана"; and under it **"Извор: <who announces>"**, on every row.
- **The same filters, fewer:** place (the places that have an action), time (from today; something starts or ends
  within 7 days), kind, a word; folded on a phone as on the first page; the choice is in the page's address. The
  script is the same one (`static/site.js`, which takes the fields a page has).
- **The order is the nearest day first;** what is over is not listed. The page says that not every action is open
  to everyone (a firm's or an institution's own employees), and that there are few for the environment, since
  organizers rarely announce them ahead.
- **A reader can report an action:** under the list, a link to a form (`akcija.yml`) with a link to the organizer's
  announcement; it is checked and added with its source said, as a reader's report (`docs/decisions/data.md`).
  A row from a feed says "вести на њиховом сајту"; one without a place says that the place is in the announcement.
- **Who may be a source** and what is read are in `docs/decisions/data.md` ("The page of actions, and the rule for
  its sources").

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

## The guide to the request for information (22 Nov 2026, the first guide)

`zahtev.html`, "Водич" in the bar; written by `guide.py` from `data/laws.json` (the Law on Free Access to
Information of Public Importance as the register prints it, `docs/decisions/data.md`, "The text of the laws").

- **Six steps** (from whom; who may and whether a reason is needed; what the request holds, with the letter;
  the deadline; the cost; refusal or silence and the complaint to the Commissioner). Each is a plain-words line
  marked "Својим речима" and then the law's paragraphs word for word, with the article, the paragraph ("став N")
  where the article's paragraphs are the law's own numbered ones (15, 16, 17, 24; not 22, whose points sit in one
  paragraph), a link to the register, and above all the law's gazette numbers and the day the version took effect
  (principles 6 and 7).
- **A quote the law no longer has stops the build** (`guide.Missing`): the page never shows a paragraph that
  is not in the law as read.
- **Not legal advice, said at the top** (principle 8); how organs keep the deadlines in practice is said to be unknown.
- **The letter** stands in the page as a text with blanks in square brackets, so it is whole without the script. With
  it a form fills the blanks (`site.js`, the second part); what is typed stays in the page, goes nowhere and is not
  stored; a button copies the letter. The blanks are the fields' own placeholders, so the same letter is made in
  both scripts (a test holds this). The organ's name is typed by the reader: the list of municipalities does not say
  whether a name is a city or a municipality, and the organ's own name ("општинска управа") is not ours to guess.
- **The complaint** (step 6) has its own letter, with two grounds (the request was refused or dismissed; it was not
  answered in time). What a complaint holds and the deadline rest on the Law on General Administrative Procedure
  (articles 159 and 153), which article 23 of the law points to, so that law is read too (`laws.LAWS["procedure"]`).
  The organ's name is typed by the reader and cannot be declined by us, so each sentence keeps it in the nominative,
  in brackets.
- **Not done:** a choice of the organ by name with its address from the Commissioner's catalogue. The catalogue's
  names are Latin only (a Cyrillic page would offer Latin names, and turning them into Cyrillic by a program is
  not safe: "nj", "lj", "dž"), and its 12,363 bodies are too many for a page; about 1,080 of them (the republic's
  and the provincial and local organs, the municipal administrations and assemblies) would fit. The decision of
  how is the maintainer's. Also not done: a print or PDF form; the page seen on a phone in a real browser (the
  headless browser would not start on 22 Nov; the letters' logic was run in Node with a stand-in document).

## The guide to the citizens' initiative and assembly (22 Nov 2026)

`inicijativa.html`, with an index of the guides (`vodici.html`, "Водичи" in the bar). It rests on the Law on Local
Self-Government alone (articles 67 to 71: the forms of direct participation, the initiative with its 60 days and its
signatures, the citizens' assembly, the referendum on a citizens' proposal, the complaint about an organ's work), the
same way as the first guide: our words marked, the law's word for word, the version and the register's link.

- **What the statute decides is said to be the statute's, and no statute is read yet.** The page says so at the top
  and sends the reader to the municipalities' page for the municipality's site. The law leaves to the statute the
  area an assembly is convened for, who convenes it and how it works (art. 69), and the rest of the referendum's
  procedure (art. 70); how signatures are collected is for "the regulations on the citizens' initiative", which
  are not read either.
- **Why this order:** the statutes are the hard layer (a PDF in each municipality's gazette; no collection). The
  guide gives what the law gives all the municipalities, the same for each (principle 1), and the statutes
  are read when a guide needs a number from them: a model reads, a person checks (22 Nov 2026), starting with
  municipalities lexifina has, which are mostly Belgrade's own (the fields have to hold before all are read).
- **Update (22 Nov 2026): a table of the six statutes read** (step 6: who may convene an assembly, how many must be
  present, signatures for an initiative), each row with the statute's link and, folded, the article and sentence of
  every field. Marked "Проба, и није проверено": the maintainer's decision is that a person checks what a model
  read; no row is `checked` yet.
- **No letter-writer here:** the law gives no form for a proposal, and a statute may.
