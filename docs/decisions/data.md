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
| `announcements.json` | the municipalities' own sites | 1,530 announcements of public debates (688), public inspections (582) and early public inspections (260) from 49 municipalities; 1,088 with a day; 32 in the last 30 days, from 18 municipalities. |

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

## Where the rest of what a citizen can take part in is

Not read yet; in the order of what each would add.

0. **An announcement's own text** (21 Nov 2026): the day, the place and the deadline of a debate are in the
   text, not the title, so the site can say that a call was published and not whether it is still open. The
   WordPress sites give the text with the post; how a day is taken from free text, and who checks it, is the
   maintainer's decision (AGENTS.md).
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
