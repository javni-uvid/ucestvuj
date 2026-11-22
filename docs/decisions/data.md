# Data: the sources

Where the guides' facts come from, what each source gives and how it is read. Keep it current: a decision made
or changed is added at the end of its section, in the same commit as the change.

"Checked" means read on 20 Nov 2026 from the development computer; "to confirm" means known from before and not
read that day.

## The three layers

1. **The law** says what every person in Serbia may do: the same guide for the whole country.
2. **A municipality's statute** fills in what the law leaves to it (how many signatures an initiative needs, who
   calls a citizens' assembly, how a public debate is run): one row per municipality per mechanism.
3. **The addresses**: which body, at what address, takes the letter.

## The law

| Source | What it gives | How it is read | State |
|---|---|---|---|
| Pravno-informacioni sistem (pravno-informacioni-sistem.rs), the Official Gazette's register | The consolidated text of every law, with a stable address per act (`/eli/rep/sgrs/skupstina/zakon/2007/129/2/reg` is the Law on Local Self-Government) | The address answers, but the page is a script that draws the text in a frame; no documented API was found in its code. How the text itself is fetched is not solved yet. | Checked: address stable, text not read |
| lexifina/serbia-law (GitHub) and its API (global-law.lexifina.com, no key) | The same register read into one file per article, every version with the day it took effect; also 4,034 local acts of 20 cities and municipalities | git clone or JSON. Another project's reading of the register: by principle 2 it finds and checks, and the quoted article is compared with the register before it is published. Its licence is not a standard one: read it before taking text from it. | Checked: exists, pushed 15 Nov 2026 |

The laws the guides rest on (to confirm, each against the register, with the articles):

- Constitution: the right to petition, to information, to local self-government.
- Law on Local Self-Government: citizens' initiative, citizens' assembly, referendum, public debate (mandatory
  for the statute, the budget's investment part, plans), local communities (mesne zajednice), open sittings.
- Law on the Referendum and the People's Initiative (2021): the procedure and the signatures.
- Law on Free Access to Information of Public Importance: the request, the deadlines, the complaint to the
  Commissioner.
- Law on Planning and Construction: early public inspection and public inspection of urban plans.
- Law on the Planning System, and the Budget System Law: consultations and public debates on plans and budgets.
- Law on Environmental Impact Assessment: public inspection and debate on a study.
- Law on Public Assembly: announcing a gathering.
- Law on the Protector of Citizens, and General Administrative Procedure: complaints about a body's work.

## A municipality's statute

The hard layer. Every city and municipality has its own statute, published in its own official gazette, almost
always as a PDF on its own site; there is no central, machine-readable collection.

| Source | What it gives | State |
|---|---|---|
| `javni-uvid/izborna-analiza`, `data/municipal_sites.csv` | The web site of 168 municipalities (from RIK's address book), and a workflow that already finds documents on those sites | Checked: the file exists |
| lexifina/serbia-law | Local acts of 20 cities and municipalities already read | Checked: as its README says; which 20 not looked at |
| Each municipality's own site and gazette | The statute itself | Not read |
| data.gov.rs, "decisions in the public interest" (about 25 cities, mostly one upload in May 2022) | Lists of local decisions | Seen in the survey of 20 Nov; stale |

What the statute is read for is a small, fixed set of fields per mechanism (a number of signatures, who calls,
a deadline, the article), so a municipality is a row, not a text. A start with the 20 municipalities already
read elsewhere, or with the largest cities, shows whether the fields hold before all are read.

## The addresses

| Source | What it gives | How it is read | State |
|---|---|---|---|
| The Commissioner's catalogue of public authorities (data.poverenik.rs, through data.gov.rs) | 12,714 bodies the Law on Free Access applies to: name, category, two classifications, address, post code, seat, web address, contact, authorised persons | One CSV, 2.8 MB, `|` between fields, UTF-8, marked as updated daily | Checked: downloaded and counted |
| Ministry of Public Administration and Local Self-Government, "Kontakt podaci JLS" (data.gov.rs) | 145 cities and municipalities: address, and the mayor's, the assembly president's and the administration head's name, phone and e-mail | CSV and XLSX, uploaded 23 Apr 2026 | Checked |
| The same ministry, "Izvorni i povereni poslovi JLS po oblastima" | 1,203 tasks of local government, each with its area (30), sub-area, legal basis, level of government and competent body: who is responsible for what | CSV, 0.9 MB, uploaded 23 Apr 2026 | Checked |
| The Commissioner's other datasets (complaints, decisions, opinions; 16 more, daily) | How requests and complaints end: how many, against whom | CSV | Checked: listed, not opened |
| The Statistical Office (opendata.stat.gov.rs) | The municipalities' codes and names, to join everything | CSV and JSON | Seen in the survey of 20 Nov |

Two of these name people (the authorised persons; the mayors and presidents). By principle 4 the project keeps
the body and the office and not the name: the columns with names are dropped when the file is read.

## What is open now

| Source | What it gives | State |
|---|---|---|
| eKonsultacije (ekonsultacije.gov.rs) | Public consultations of state bodies: title, start and end, whether open. `/api/announcement/findAll` answers with JSON without a key; not documented, and the list is of the republic's bodies, not of municipalities | Checked: 64 KB of JSON |
| A municipality's own site | Its public debates, calls and sittings | No common form; izborna-analiza's watch of municipal sites is the model |

## Not sources

Handbooks of organizations (Građanske inicijative, SKGO, the students' handbook on assemblies), news, and
Javni uvid's own earlier survey: they help find a rule and never supply one.

## A proposed first step

The request for information of public importance: one law, the same for the whole country, no statute needed,
and the catalogue gives the address of every body. One guide and one letter-writer, then the citizens'
initiative and the citizens' assembly, which need the statutes.

## What was read on 20 Nov 2026

Everything below is in `data/`, with where it came from and the day in `data/sources.json`.

| File | From | What |
|---|---|---|
| `bodies.csv` | the Commissioner's catalogue | 12,363 bodies: name, category, two classifications, address, post code, seat, web address. The contact and authorised-persons columns are not taken; the file's own headings are dropped. |
| `municipalities.csv` | the ministry's contacts of local government | 145 cities and municipalities: name and address. The columns of the mayors, presidents and heads are not taken. |
| `tasks.csv` | the ministry's tasks of local government | 1,203 tasks with area, legal basis, level and competent body. |
| `consultations.json`, `consultation_institutions.json` | eKonsultacije | 679 topics (181 not ended) and the 204 institutions registered. |
| `municipal_sites.csv`, `sites.json` | izborna-analiza's list; each site's first page | 157 sites, 152 answer: what each runs on, its feed, and its first page's links by what they lead to. |
| `announcements.json` | the municipalities' own sites | 1,530 announcements of public debates (688), public inspections (582) and early public inspections (260) from 49 municipalities; 1,088 with a day; 32 in the last 30 days, from 18 municipalities. Read again on 21 Nov 2026 with when what each calls to is on (below). |

## What the reading showed

- **eKonsultacije is the republic's, not the municipalities'.** 148 municipalities are registered there and four
  topics of theirs exist, none open. What a municipality consults on is on its own site only.
- **"Not ended" on eKonsultacije is not "open".** Of the 181 topics not marked ended, 65 were created in 2024 or
  earlier. Whether a topic can still be commented on needs its phases' and methods' dates, which the list does
  not carry (the portal's page of a topic asks for them separately; not read yet).
- **The portal answers nothing to a plain agent name**, and answers the form robots use
  (`Mozilla/5.0 (compatible; name; +address)`). `web.AGENT` is that form and still says who asks.
- **Its list is asked page by page:** `start` is the page's number, and the reading stops when the count it read
  differs from the count the portal says.
- **A third of the municipal sites can be asked directly.** 51 run on WordPress and 45 of them gave
  announcements through their own search; 15 are the state's `ls.gov.rs` sites, which keep announcements as a
  kind of content of their own with a category for public debates. 48 sites have a feed, which gives only the
  newest entries (18 announcements).
- **The other two thirds are not read yet.** Of the 152 sites that answer, 48 link public debates from the first
  page, 40 public inspections, 85 the budget, 92 the assembly's sittings, 52 the official gazette and 43 the
  statute (`sites.json`): for those the list page behind the link has to be read, site by site or by system
  (10 run on Joomla).
- **An announcement's title is the municipality's own words** and is what tells a debate from an inspection. Some
  titles are news that a debate was held, not a call to one; some name an investor or an official. Before
  anything is published: a rule for what is a call, and a decision on titles that name a person (principle 4).
- **Užice and Sevojno share one site** (`uzice.rs`), so the same announcements stand under both.

## One list of the municipalities' sites, kept in izborna-analiza

21 Nov 2026, the maintainer: the two projects are to be connected for when someone finds a new local site.

- **The list is `javni-uvid/izborna-analiza`'s `data/municipal_sites.csv`,** and `data/municipal_sites.csv` here
  is a copy of it, never changed here. Its weekly watch already writes back an address it finds, with the old
  one in the note; a hand correction is made there too.
- **`ucestvuj list` copies it and says what changed** (an address found, changed or lost); the **list** workflow
  runs it on Tuesdays after that watch, commits the copy when it differs and starts **pages**. A list that lost
  its columns or a tenth of its rows is not copied.
- **A site found here goes there:** by a reader through the link on the municipalities' page (an issue in
  izborna-analiza), by us as a pull request there. It comes back with the next copy, so both sites have it.
- **A new address is not read by the workflow.** `ucestvuj sites` and `ucestvuj announcements` are still run by
  hand; until then the site says the address is new.

## When what an announcement calls to is on

21 Nov 2026, the maintainer: "we should also read when the debate is"; and the same day, on the first version,
which kept a bare list of days: Senta's inspection "from 30 October to 28 November" was shown as "28 Nov"
alone, its first day dropped for being before the announcement. "Fix it, and work out how best to establish
the dates."

How the dates are established (`when.py`):

- **From the announcement's own text and title, by a program.** A WordPress site gives the text with the post
  in the same answer, a feed with the entry, so no site is asked more often than before.
- **Periods, ends, starts and days, not a list of dates.** Two days joined by "до" are one period and keep both
  ends, also when the first is before the announcement; a day after "до" or "закључно са" is an end; a day
  after "од" or "почев од" a start, with the length the text gives beside it ("30 дана"); a day alone may have
  its hour. A length is never turned into a last day: whether the first day counts is the body's to say.
- **Each gets the name of what the words just before it speak of:** a public inspection, an early one, a
  debate, a session, a meeting or presentation, remarks. The nearest such word wins; a body named after what it
  runs ("Комисија за јавни увид") is not that thing. Where the words name nothing, a period or a day is kept as
  "in the announcement"; a bare start or end with no name is dropped, as it is as likely the day a decision
  takes effect.
- **Only days written whole.** A day without a year counts only as the start of a range whose end has one ("од
  12. октобра до 23. новембра 2026.", "од 2. до 23. новембра 2026."). One space inside a number is read through
  ("2 0 . новембра 202 6 ."), as several sites' text has them.
- **What was over before the announcement is left out** (the session that adopted the draft, the decision's
  day), and what is more than 400 days after it. What a period of the same thing already says is not repeated.
- **Only these fields are kept, never the text** (principle 4: a text names people and gives their e-mail
  addresses): per announcement a list of `{what, from, to, days, hour}`.
- **Checked on every text read on 21 Nov 2026** (1,029 texts, kept outside the repository for the work and not
  committed): 745 of the 1,088 announcements with a day of publication give at least one period or day; of
  1,309 found, 509 are periods, 524 days, 199 ends, 77 starts; 123 have no name. The last 30 days' were read
  one by one against their texts.
- **A mistake becomes a test.** Each wrong reading found (by us or by a reader's report) is added to
  `tests/test_reading.py` with the sentence that caused it, so the rule can be changed without losing what it
  already reads right. Nobody checks each announcement by hand.
- **Not read:** a text in an attached PDF or image (the call itself, for some municipalities), a day without a
  year, the announcements read by title only (442), and the place.

Proposed, the maintainer's to decide: a second reading of the same text by a model, kept only where it agrees
with the program and listed for a person where it doesn't. It would catch what words can't (a sentence built
another way) at the cost of sending the municipalities' texts to a model and of a person's time.

## Other ways to take part: the sources

22 Nov 2026, the maintainer: "find the sources first, for all of these"; and, mid-task, "we can go outside the
municipal sites as long as the source is positive and publishes actions". Five readings of the open web by
agents, each page opened (a plain request or a fetch that summarises the page: field lists from the latter are
second-hand), then the key claims asked again directly here. The sources it names are read into `data/actions.json` as the last sections say. "Unverified" is said where it applies; where a source answered nothing, that is not a proof
that nothing exists.

### What the municipalities' sites already show

One search of the posts of the 51 WordPress sites read (20 newest per word, a title must hold the word's stem;
the first page's links of all 152 sites that answer are in `sites.json`):

| Kind | Sites | Titles in 2026 | In the last 3 months | What the titles are |
|---|---|---|---|---|
| Sittings of the assembly | 38 | 113 | 38 | Calls with a day ("Saziv 18. sednice za 25.11.2026.") and news that it was held |
| Reception of citizens | 14 | 36 | 14 | Mostly "held"; a standing rule ("every Thursday 10-12") in one dated post (Kula, Odžaci) |
| Blood donation | 17 | 18 | 7 | Real calls with a term (Voždovac, weekly) |
| Volunteers | 25 | 12 | 2 | News about volunteers, few calls |
| Surveys | 23 | 6 | 1 | Surveys of a municipality or its utility; many are not about a decision |
| Clean-ups | 16 | 4 | 0 | Seasonal, mostly news after the action |
| Planting | 17 | 3 | 0 | Seasonal, mostly news after the action |
| Members of councils and bodies | 8 | 2 | 0 | Real calls, rare |
| Local community councils | 8 | 0 | 0 | Notices of elections when held (2021, 2023, 2025) |
| Citizens' assembly | 3 | 0 | 0 | Almost nothing (the 2025 notices of Užice below) |

Lower bounds: 20 posts per word and site, WordPress sites only. Of the 152 first pages, 95 link public calls, 92
the assembly, 53 the local communities, 23 surveys or consultations, 2 petitions.

### Sources outside the municipal sites

| What | Source | One entry has | Form | State on 22 Nov 2026 |
|---|---|---|---|---|
| Blood drives | Zavod za transfuziju krvi Vojvodine, `transfuzija.rs/dobrovoljno-davanje-krvi/akcije-na-terenu/` | place, venue, day, start and end | HTML; the "add to calendar" links hold ISO start and end and the place (checked) | 20 Nov to 25 Nov listed |
| | Institut za transfuziju krvi Srbije, `itks.rs/nedeljni-plan-ekipa.html` | per day: municipality, venue, hours as text ("9-15ч") | hand-written HTML, Cyrillic, a card per day (checked) | 22 to 29 Nov |
| | Crveni krst Beograd, `crvenikrstbeograd.org.rs/blog/spisak-akcija-dobrovoljnog-davanja-krvi/` | same as the Institute's, some lines differ | HTML | 21 to 29 Nov (unverified by us) |
| | Zavod za transfuziju Niš, `transfuzijanis.rs` | a weekly plan: municipality, venue, hours | one PDF a week, text layer, the link changes | 23 to 29 Nov |
| | Crveni krst Srbije | no schedule of its own; links the four above | HTML | n/a |
| People's initiative | eUprava, `elusluge.euprava.gov.rs/einitiative/eserviceapi/Initiative/GetActiveInitiatives` | unknown: the list is empty | JSON, no login (checked: `[]`, 200); undocumented, found in the app's script | no active initiative today. Supporting one needs an e-certificate or the ConsentID app, by territory |
| Working groups | Ministry for Human and Minority Rights, `minljmpdd.gov.rs/wp-json/wp/v2/posts?categories=71` | title, day, the deadline in the text, annexes as Word | WordPress API (checked); the category also holds the ministry's own job competitions | about a call a month; the newest call 3 Aug 2026 (the law on climate change) |
| Assembly | Calendar, `parlament.gov.rs/php/calendar/calendar_ajax.php?display=list&startDate=…&endDate=…&cats1=0` | day, hour, title with the place | HTML fragments; its RSS is empty | sittings and committees seen; a public hearing's place in it not seen |
| | Public hearings, `parlament.gov.rs/…/јавна-слушања.2891.html` | day, title, agenda, annexes | HTML table | past ones only (the last 21 Aug 2026) |
| Sittings of city assemblies | Novi Sad `skupstina.novisad.rs`, Subotica `subotica.ls.gov.rs` | announcement in prose: day, hour, place, number of items | WordPress feed and API | no sitting announced now |
| | Beograd `beograd.rs/cir/najave` | day, hour, place, number of the sitting, on each entry's page only | HTML; the list has no dates | the next on 23 Nov 2026 |
| | Kragujevac `kragujevac.ls.gov.rs` | news: day, hour, items in prose | HTML; the feed answered 403 to one client | 27 Nov 2026; Niš not found |
| Citizens' assembly | Užice `uzice.rs` (2025: Lunovo Selo, Kremna, Drežnik, Dubočko) | day, hour, place, in a dated post and a PDF | WordPress | 2025; none in 2026 found |
| Participatory budgeting | Sombor `sombor.rs` | vote until 20 Nov 2026, a paper ballot by the utility bill, three projects per local community | WordPress post | live |
| Volunteer shifts | Novosadski volonterski servis, `nvs.rs/wp-json/wp/v2/positions` (checked) | start and end, place, application deadline, number of volunteers, hours, age, skills, the host | WordPress API, a post type of its own | three open: 24 Nov, 29 Nov, 6 Dec. The host's phone and e-mail are public in the API |
| Work actions | Zavrni rukave, `zavrnirukave.rs` ("Lokacije i datumi") | place, weekday and day **without a year**, hour, what to bring, a map | HTML in the first response | the last on 15 Nov; nothing ahead |
| | Volonterski centar Vojvodine, `volontiraj.rs/dogadjaji/?ical=1` | start, end, title, description | iCal | one event, 25 Apr 2026 |

### What was not found

- **No central source** for: calls for members of councils and bodies (youth, green, traffic safety, school
  boards); elections of the local community councils (a municipal decision; Kragujevac's assembly decides on
  27 Nov 2026 on the commissions for them); sittings of municipal assemblies; the municipalities' citizens'
  assemblies; a municipal referendum or a samodoprinos (RIK's page for the 2026 local referendums holds no
  rows; Ada's decision of 4 May 2026 is on its own site); participatory budgeting or surveys.
- **Planting and clean-up calls by the state:** Srbijašume, Vojvodinašume and the Ministry of Environmental
  Protection publish news, not dated calls to join. JKP Zelenilo Beograd's "Za zeleniji Beograd" closed on 15 Sep.
- **Red Cross, volunteers and trainings:** the Serbian Red Cross has no list of actions (news; a calendar of
  commemorative days, last entry 6 Feb); a call to volunteer is made to one's local organization.
- **Volunteer firefighters and civil protection:** no call found; the site of the Fire Brigades Association of
  Serbia was not found.
- **Polling boards and observers:** RIK has no page that says how a citizen joins a board (training, plans of
  training for the 25 Oct 2026 election and forms for the minority councils' election of 8 Nov exist); who
  proposes the members was said by an agent from memory and is not to be taken before the law is read.
- **data.gov.rs:** its search answers 0 to every query, generic words included, so it proves nothing.
- **Reports of problems are not events:** eUprava's "Prijava komunalnog problema" names 7 local governments
  (Šabac, Krupanj, Mali Zvornik, Medveđa, Ćuprija, Knjaževac, Osečina); Beograd has the call centre 11011; the
  national inspections form is `inspektor.gov.rs/submission` (a citizen, an organization or anonymous; the
  environmental inspection too); the Protector of Citizens takes a complaint by e-mail, post, phone, in person
  and generally not anonymous; the Commissioner's forms for a request and the complaints are Word files, and
  `data.poverenik.rs` has 16 CSV datasets (a CKAN API, all changed 21 Sep 2026; only the catalogue's columns
  were read, and it is read here already); the Anti-Corruption Agency has no citizen's channel on its pages. These
  are for the guides (a body, an address, a form), not for a list of what is on.

### What a program would meet

- **The year is missing** on Zavrni rukave and on the Mountaineering Association's calendar: a day without a
  year is not guessed (`when.py`'s rule), so such an entry has no day until the source writes one.
- **Hours are free text** at the Institute and the Red Cross of Belgrade ("9-15ч", "14-18č"), a PDF at Niš,
  calendar links at Vojvodina: four readers for one kind. The Institute's and the Red Cross of Belgrade's lists
  differ in places, so a municipality's drive can be on one and not the other: both would be shown as theirs.
- **`robots.txt`:** read for five of the sites. nvs.rs allows search and reference use and forbids training and
  names crawlers, among them ClaudeBot; a program of ours that lists a position with a link is reference use,
  and the page says so. itks.rs has none (404). Not read for the rest: before any site is read by a program, its
  `robots.txt` and terms are.
- **A person's contact** is public in NVS's API (a phone, a private e-mail): a position would be shown with the
  host's name and the link, never the contact (principle 4).
- **A fetch that summarises a page** was the agents' tool for several pages; every field named above that was
  not asked again here is second-hand until a reader of ours reads it.

### The page of actions, and the rule for its sources (decided 22 Nov 2026)

The maintainer, 22 Nov 2026: "we make a separate tab from the public debates; put all public actions for
improving the environment, giving blood, positive initiatives there"; and: "we may go outside the municipal sites
as long as the source is positive and publishes actions"; and, on news and social networks: "we can, as long as
we say it is the source".

- **A page of its own, "Akcije",** beside the debates' page: things to do, with a place and a day. Debates, public
  inspections and consultations stay where they were.
- **Who may be the source:** an institution, as before; and for this page also an organizer that is not one (an
  association, a group of citizens), news and a social network, as long as the row says that this is the source
  and links it. The organizer or the reporter is named on every row ("Извор: …"). Nothing from a source of this
  kind is a rule, a number or a deadline of the law, and no person's contact is carried (principle 4).
- **Not built, and why:** a social network's pages are not read by a program (they ask for a login, and their
  terms forbid it), so for now what is read is what a site publishes in the open. A news site is read when it
  has a feed worth reading; none has been added.
- **"Positive" is the maintainer's word,** for an action that does good to the place or to the people in it. The
  rule applied is the same for every organizer (principle 1): the organizer itself publishes the action, in a
  list of events or positions or in a post that names a day, open to anyone. What is open to anyone and what is
  closed (a drive for a firm's employees) is said when the organizer says it: the Institute for Blood Transfusion
  of Serbia marks such lines, and they are left out; where a source doesn't say, the page tells the reader to ask
  the organizer.
- **Open question (the maintainer's):** whether a call that is political is left out by its content, which is a
  judgement (principle 3), or only by the rule above. The one such source found, the drive of Zavrni rukave to
  remove political graffiti after the election, has no reader yet and is not on the page.

### What is read into `data/actions.json` (`ucestvuj actions`, by hand for now)

On 22 Nov 2026: 54 actions to come, 30 from the blood transfusion institute of Vojvodina, 21 from the Institute
for Blood Transfusion of Serbia (the closed ones left out), 3 from the volunteer service of Novi Sad. Each keeps
the kind (blood, volunteer, environment), who announces it, the place and venue, the title as the source wrote it
(the Institutes' lines have none: "Добровољно давање крви: <place>" is ours), the address of the announcement,
the day, the hours and, for a position, the deadline. Never a contact.

- **The institutes' lists are read each by its own form** (`actions.transfusion_vojvodina`, `transfusion_serbia`):
  calendar links, and a card per day with the hours as text. A source that doesn't answer is skipped.
- **The volunteer service's positions** are read through its public API, the fields about the action only
  (`actions.volunteer_service`); the hours are taken from its sentence only when it says them whole.
- **The municipalities' own posts** (the 51 WordPress sites) are searched for a call to give blood, to clean, to
  plant or to volunteer (`actions.of_municipality`): a title that says what it is and that it calls, not over,
  and a text that names a day from the post's own on. The first reading found 23 such posts, all of earlier
  years (the newest is of January 2026), so none is on the page: municipalities announce such actions
  rarely and mostly after the fact.
- **Environment actions: none on the page today.** No source found publishes a dated call to clean or to plant
  ahead of the day (the state's bodies publish news, the volunteer service's positions are event shifts). The
  kind is there, and the page says that there are few.
- **Only what is ahead is kept** when read; the page lists what ends today or later, the nearest day first.
- **Not read:** the Red Cross of Belgrade's list (the same lines as the Institute's, some differing), the plan
  of the Niš institute (a PDF a week), the Vojvodina volunteer centre's calendar (one past event), and Zavrni
  rukave (its days have no year; a weekday beside the day would settle it, and the political question above).

## Where the rest of what a citizen can take part in is

Not read yet; in the order of what each would add.

0. **An announcement's place and hour, and the days of the announcements read by title only** (the `ls.gov.rs`
   kind of content, 442 announcements, comes without a text and without a day; a text in an attached document
   is not opened).
1. **A topic's dates and documents on eKonsultacije** (its phases and methods): turns the list into "open until".
2. **The list pages behind the first page's links** on the sites that have no search to ask (`sites.json`), the
   `ls.gov.rs` category first, as its 15 sites are built alike.
3. **Public inspections of plans** are also announced by the body that makes the plan: the ministry in charge of
   construction for the republic's spatial plans, the province's secretariat, a city's planning institute.
4. **Environmental impact assessments**: the ministry of environmental protection, the province and the
   municipalities announce each study's public inspection and debate; the ministry is already the institution
   with most topics on eKonsultacije (107).
5. **The National Assembly's public hearings** and bills in procedure: Za ili Protiv reads the Assembly's site.
6. **A municipal assembly's sittings and agendas** (92 sites link them): when a decision is made, and on what.
7. **The statutes and the official gazettes** (43 and 52 sites link them): what each municipality's statute says
   about an initiative, an assembly and a debate, the second layer above.
8. **How requests for information end**, by body: the Commissioner's 16 other datasets (complaints, decisions),
   as counts and never as a ranking (principle 3).
