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
