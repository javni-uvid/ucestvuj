"""The site, built from data/ into static pages in the family's look (osnova/design/), in Cyrillic (cir/) and
Latin (the default). Written once in Cyrillic; the Latin edition is the same page turned letter by letter, its
addresses untouched. Nothing on a page comes from another server, and nothing needs a script: the one script,
the site's own (static/site.js), only filters the first page's list, which is whole without it.

Pages: the first page (what is open now), the municipalities, a page for each municipality with
announcements, the state's consultations, and the project. A preview for the maintainer: the pages ask search
engines not to index them."""

import csv
import datetime
import hashlib
import html
import json
import re
import shutil
import unicodedata
from pathlib import Path

from ucestvuj import guide, when
from ucestvuj.announcements import held, topic as topic_of
from ucestvuj.sites import REPORT
from ucestvuj.translit import CYRILLIC, latin, latin_page, text_of

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DESIGN = ROOT / "osnova" / "design"
STATIC = Path(__file__).parent / "static"
URL = "https://javni-uvid.github.io/ucestvuj/"
REPO = "https://github.com/javni-uvid/ucestvuj"
NAME = "Учествуј"
ABOUT = ("Јавне расправе и јавни увиди које општине објављују, и консултације државних органа отворене за коментаре, "
         "свака са објавом саме институције.")
KIND = {"debate": "Јавна расправа", "inspection": "Јавни увид", "early_inspection": "Рани јавни увид"}
# What a period or a day in an announcement is of, as the words before it say (when.CUES).
WHAT = {"debate": "Јавна расправа", "inspection": "Јавни увид", "early_inspection": "Рани јавни увид", "session": "Јавна седница",
        "meeting": "Састанак или презентација", "remarks": "Примедбе", "": "У објави"}
TOPIC = {"budget": "Буџет", "taxes": "Порези, таксе и цене", "plans": "Урбанистички и просторни планови",
         "environment": "Животна средина", "development": "Стратегије и планови развоја", "other": "Остало"}
WHY = {"нема адресе": "адресу сајта ове општине још немамо", "не одговара": "сајт општине није одговорио кад смо га читали",
       "адреса нова, још није читана": "адреса сајта је нова и још није читана",
       "још не умемо": "објаве са сајта ове општине још не умемо да прочитамо"}
STATE = "rs"  # the place of what a body of the republic consults on
ACTION_REPORT = REPO + "/issues/new?template=akcija.yml"
ACTION = {"blood": "Давање крви", "volunteer": "Волонтирање", "environment": "Уређење и заштита околине"}
RECENT_DAYS = 30
# A title that names the one who asked for a plan or a study (an investor, an applicant) may name a private
# person; the site then shows the kind of announcement and links the municipality's own page for its words
# (AGENTS.md, principle 4). A public official in a title is kept as the municipality wrote it.
APPLICANT = re.compile(r"инвеститор|investitor|подносиоц|подносилац|podnosioc|podnosilac|носиоц[аи] пројект|nosioc[ai] projekt", re.I)
_AZBUKA = "абвгдђежзијклљмнњопрстћуфхцчџш"
_PREFIX = re.compile(r"^(?:Градска општина|Град)\s+")


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def day(iso: str) -> str:
    """2026-11-20 as 20. 11. 2026."""
    if not iso:
        return ""
    d = datetime.date.fromisoformat(iso[:10])
    return f"{d.day}. {d.month}. {d.year}."


def azbuka(name: str) -> tuple:
    """A municipality's place in the Serbian alphabet, by its own name ("Град Ниш" under Н)."""
    low = _PREFIX.sub("", name).lower()
    return tuple(_AZBUKA.index(c) if c in _AZBUKA else 100 + ord(c) for c in low), name


def shown_title(a: dict) -> str | None:
    """The announcement's title as the municipality wrote it, or nothing when it may name a private person."""
    return None if APPLICANT.search(a["title"]) else a["title"]


def load() -> dict:
    read = lambda name: json.loads((DATA / name).read_text(encoding="utf-8"))
    with (DATA / "municipal_sites.csv").open(encoding="utf-8", newline="") as f:
        listed = list(csv.DictReader(f))
    return {"announcements": read("announcements.json"), "actions": read("actions.json"), "sites": read("sites.json"),
            "consultations": read("consultations.json"), "laws": read("laws.json"), "sources": read("sources.json"), "listed": listed}


# ---- the frame of every page


MARK = ('<svg class="ju-mark" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3" '
        'fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="12" r="3.4" fill="currentColor"/></svg>')


def family(script: str, home: str) -> tuple[str, str]:
    """The family's bar and footer block (osnova/design/family.html), with this site among the family's sites."""
    data = json.loads((DESIGN / "sites.json").read_text(encoding="utf-8"))
    fam = data["family"]
    me = {"id": "ucestvuj", "name": {"cyr": NAME, "lat": "Učestvuj"}, "about": {"cyr": ABOUT, "lat": ABOUT}}
    sites = [s for s in data["sites"] if s["id"] != "ucestvuj"] + [me]
    link = lambda s, extra="": (f'<a{extra} href="{esc(home)}">' if s is me else f'<a{extra} href="{esc(s["url"][script])}">')
    bar = (f'<nav class="ju-bar" aria-label="{esc(fam["name"][script])}"><div class="ju-bar-in">'
           f'<a class="ju-name" href="{esc(fam["url"][script])}">{MARK}{esc(fam["name"][script])}</a>'
           + "".join(link(s, ' aria-current="page"' if s is me else "") + esc(s["name"][script]) + "</a>" for s in sites)
           + "</div></nav>")
    items = "".join(f'<li>{link(s)}{esc(s["name"][script])}</a><span>{esc(s["about"][script])}</span></li>' for s in sites)
    foot = (f'<section class="ju-foot" aria-label="{esc(fam["name"][script])}"><h2><a href="{esc(fam["url"][script])}">'
            f'{MARK}{esc(fam["name"][script])}</a></h2><p>{esc(fam["promise"][script])} '
            f'<a href="{esc(fam["url"][script])}#nacela">{esc(fam["principles"][script])}</a></p><ul>{items}</ul></section>')
    return bar, foot


def frame(path: str, script: str, title: str, description: str, main: str, read: str, version: str) -> str:
    """A whole page. `path` is its place in the Latin edition ("opstina/70106.html"); `main` is written with
    {home} for the edition's first folder and {root} for the site's."""
    depth = path.count("/") + (script == "cyr")
    root = "../" * depth
    home = root + ("cir/" if script == "cyr" else "")
    twin = (root + "cir/" + path) if script == "lat" else (root + path)
    bar, foot = family(script, home + "index.html")
    main = main.replace("{home}", home).replace("{root}", root)
    page = f"""<!doctype html>
<html lang="@@LANG@@">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="referrer" content="no-referrer">
<link rel="icon" type="image/svg+xml" href="{root}znak.svg">
<link rel="stylesheet" href="{root}osnova.css?v={version}">
<link rel="stylesheet" href="{root}site.css?v={version}">
<script src="{root}site.js?v={version}" defer></script>
</head>
<body>
<a class="skip" href="#sadrzaj">Прескочи на садржај</a>
{bar}
<header class="top">
  <a class="brand" href="{home}index.html">{NAME}</a>
  <nav aria-label="Сајт">
    <a href="{home}index.html">Расправе</a>
    <a href="{home}akcije.html">Акције</a>
    <a href="{home}vodici.html">Водичи</a>
    <a href="{home}opstine.html">Општине</a>
    <a href="{home}drzava.html">Држава</a>
    <a href="{home}o-projektu.html">О пројекту</a>
    <a class="script-switch" href="{twin}" lang="@@LANG_OTHER@@" hreflang="@@LANG_OTHER@@">@@OTHER@@</a>
  </nav>
</header>
<p class="preview">Пробна верзија, за преглед. Подаци прочитани {esc(read)}</p>
<main id="sadrzaj">
{main}
</main>
<footer class="foot">
{foot}
<p class="fine">Без колачића, аналитике и ичега са других сервера. <a href="{REPO}">Код и подаци</a> · <a href="{REPO}/issues">Пријави грешку</a></p>
</footer>
</body>
</html>
"""
    if script == "lat":
        page = latin_page(page)
    for key, value in {"@@LANG@@": "sr-Latn" if script == "lat" else "sr-Cyrl",
                       "@@LANG_OTHER@@": "sr-Cyrl" if script == "lat" else "sr-Latn",
                       "@@OTHER@@": "Ћирилица" if script == "lat" else "Latinica"}.items():
        page = page.replace(key, value)
    return page


# ---- the pages' parts


def period(p: dict) -> str:
    """One period or day of an announcement, as words: "од 30. 10. 2026. до 28. 11. 2026."."""
    if p["from"] and p["to"] == p["from"]:
        return day(p["from"]) + (f' у {p["hour"]}' if p["hour"] else "")
    if p["from"] and p["to"]:
        return f'од {day(p["from"])} до {day(p["to"])}'
    if p["to"]:
        return f'до {day(p["to"])}'
    return f'од {day(p["from"])}' + (f', {p["days"]} дана' if p["days"] else "")


def fold(text: str) -> str:
    """Words as the search compares them: Latin, lower case, no marks on the letters (site.js folds what is typed)."""
    low = latin(text).lower().replace("đ", "dj")
    return "".join(c for c in unicodedata.normalize("NFD", low) if not unicodedata.combining(c))


def card(place: str, where: str, by: str, kind: tuple[str, str], about: str, title: str, url: str, published: str,
         periods: list[tuple[str, str]], days: list[str], over: bool = False, none: str = "", source: str = "") -> str:
    """One row of a list, answering the reader's three questions in the same places every time: where (the
    municipality, or the republic and its body), what about (the kind, the topic, the title in the source's
    words, linked to the source) and when (each period or day with what it is of). Its data-* say the same to
    the filters (site.js); the row is whole without them."""
    chips = f'<span class="chip">{esc(kind[1])}</span>' + (f'<span class="chip">{TOPIC[about]}</span>' if about != "other" else "")
    chips += '<span class="chip over">одржано</span>' if over else ""
    lines = "".join(f"<li><b>{esc(what)}</b> {esc(words)}</li>" for what, words in periods)
    when_ = f'<ul class="when">{lines}</ul>' if lines else f'<p class="when none">{none}</p>'
    said = source or (f'Објављено {day(published)}' if published else "Без дана објаве")
    return (f'<li class="card" data-place="{esc(place)}" data-kind="{kind[0]}" data-topic="{about}" data-day="{published}" '
            f'data-days="{" ".join(days)}"{" data-held" if over else ""} data-text="{esc(fold(text_of(where) + " " + by + " " + title))}">'
            f'<div class="what"><p class="where">{where}{f"<span>{esc(by)}</span>" if by else ""}</p>'
            f'<a class="title" href="{esc(url)}">{esc(title)}</a><p class="chips">{chips}</p></div>'
            f'<div class="kada"><p class="next" hidden></p>{when_}<p class="pub">{said}</p></div></li>')


def item(a: dict, names: dict, with_place: bool = True) -> str:
    """A municipality's announcement as a row."""
    title = shown_title(a) or "Наслов именује подносиоца; прочитајте га на сајту општине"
    name = names[a["code"]]
    where = f'<a href="{{home}}opstina/{esc(a["code"])}.html">{esc(name)}</a>' if with_place else ""
    periods = a.get("when", [])
    days = sorted({d for p in periods if p["what"] for d in (p["from"], when.until(p)) if d})
    none = "Објаву читамо само по наслову" if a["via"] == "wordpress search" else "У тексту објаве нисмо нашли дан"
    return card(a["code"], where, "", (a["kind"], KIND[a["kind"]]), topic_of(a["title"]), title, a["url"], a["day"],
                [(WHAT[p["what"]], period(p)) for p in periods], days, held(a["title"]), none)


def place_key(place: str) -> str:
    """A place as the filter compares it: without "Град" or "Градска општина", folded."""
    return fold(_PREFIX.sub("", place)).replace(" ", "-")


def action_card(a: dict) -> str:
    """An action to join as a row: the place and the venue, the title as the organizer wrote it (linked to it), the
    day and the hours, and who announces it said as the source."""
    same = a["start"] == a["end"]
    words = day(a["start"]) if same else f'од {day(a["start"])} до {day(a["end"])}'
    words += f", {a['time']}" if a["time"] else ""
    periods = [(ACTION[a["kind"]], words)] + ([("Рок за пријаву", "до " + day(a["deadline"]))] if a["deadline"] else [])
    how = {"news": " (вести на њиховом сајту)", "report": " (пријава читаоца, проверена)"}.get(a.get("how", ""), "")
    where = esc(_PREFIX.sub("", a["place"])) if a["place"] else "Место је у објави"
    return card(place_key(a["place"]), where, a["venue"], (a["kind"], ACTION[a["kind"]]), "other",
                a["title"], a["url"], a["start"], periods, [d for d in (a["start"], a["end"]) if d],
                source="Извор: " + a["organizer"] + how)


def topic(t: dict) -> str:
    """A topic a body of the republic consults on, as a row: open until its phase under way ends."""
    under_way = [p for p in t.get("phases", []) if p["active"]]
    start = under_way[-1]["start"] if under_way else ""
    words = f'од {day(start)} до {day(t["until"])}' if start else f'до {day(t["until"])}'
    return card(STATE, "Република Србија", t["institution"], ("state", "Консултације државе"), topic_of(t["title"]), t["title"], t["url"],
                t.get("phase_since") or t["created"], [(t["phase"], words)], [d for d in (start, t["until"]) if d])


def state_of(domain: str, site: dict | None, found: int) -> str:
    """What is read of a municipality. `domain` is the list's address, `site` what the last look at it found."""
    if not domain:
        return "нема адресе"
    if site is None or site["domain"] != domain:
        return "адреса нова, још није читана"
    if not site["answers"]:
        return "не одговара"
    if found:
        return "читамо"
    return "још не умемо"


def build(out: Path, today: datetime.date | None = None) -> list[str]:
    """Write the site to `out`. Returns what is wrong with it; nothing when it may be published."""
    today = today or datetime.date.today()
    data = load()
    names = {r["municipality_code"]: r["name"] for r in data["listed"]}
    domains = {r["municipality_code"]: r["domain"] for r in data["listed"]}
    by_code: dict[str, list] = {}
    seen_urls: set[tuple] = set()
    for a in sorted(data["announcements"], key=lambda a: (a["day"], a["url"]), reverse=True):
        if (a["code"], a["url"]) not in seen_urls:
            seen_urls.add((a["code"], a["url"]))
            by_code.setdefault(a["code"], []).append(a)
    read = data["sources"].get("announcements", {}).get("read", "")
    read = day(read) if read else ""
    since = (today - datetime.timedelta(days=RECENT_DAYS)).isoformat()
    recent = sorted((a for rows in by_code.values() for a in rows if a["day"] >= since),
                    key=lambda a: (a["day"], azbuka(names[a["code"]])), reverse=True)
    # Ahead: an announcement not said to be over whose text names today or a later day, the nearest such day first.
    ahead_of = lambda a: when.ahead(a.get("when", []), today.isoformat())
    ahead = sorted((a for rows in by_code.values() for a in rows if ahead_of(a) and not held(a["title"])),
                   key=lambda a: (ahead_of(a), azbuka(names[a["code"]]), a["url"]))
    called = [a for a in recent if not held(a["title"]) and not ahead_of(a)]
    over = [a for a in recent if held(a["title"])]
    topics = data["consultations"]
    open_now = sorted((t for t in topics if t["open"] and t.get("until", "") >= today.isoformat()),
                      key=lambda t: (t["until"], t["institution"], t["title"]))
    stale = [t for t in topics if t["open"] and t.get("until", "") < today.isoformat()]
    sites = {s["code"]: s for s in data["sites"]}
    pages: dict[str, tuple[str, str, str]] = {}

    # The first page: one list. What is ahead first, the nearest day first (the municipalities' and the state's
    # together), then the other announcements of the last 30 days, newest first.
    rows_ahead = sorted([(ahead_of(a), azbuka(names[a["code"]]), item(a, names)) for a in ahead]
                        + [(min(d for d in (t["until"],) if d), azbuka(t["institution"]), topic(t)) for t in open_now])
    rest = called + over
    rest.sort(key=lambda a: (a["day"], azbuka(names[a["code"]])), reverse=True)
    cards = [r[2] for r in rows_ahead] + [item(a, names) for a in rest]
    options, notes = [], []
    for code, name in sorted(names.items(), key=lambda kv: azbuka(kv[1])):
        found, domain, s = by_code.get(code, []), domains[code], sites.get(code)
        options.append(f'<option value="{code}">{esc(name)}</option>')
        own = f' Сајт општине: <a href="https://{esc(domain)}/">{esc(domain)}</a>.' if domain else ""
        if found:
            notes.append(f'<p id="m-{code}" hidden>{esc(name)}: читамо објаве са сајта општине, {len(found)} до сада. '
                         f'<a href="{{home}}opstina/{code}.html">Све објаве ове општине</a>, и оне старије.</p>')
        else:
            notes.append(f'<p id="m-{code}" hidden>{esc(name)}: {WHY[state_of(domain, s, 0)]}. Зато њених објава овде засад нема; то није оцена општине.{own}</p>')
    notes.append(f'<p id="m-{STATE}" hidden>Државни органи: теме отворене за коментаре на порталу еКонсултације. <a href="{{home}}drzava.html">Шта је још на порталу</a>.</p>')
    pages["index.html"] = ("Учествуј: где и када можеш да кажеш шта мислиш", ABOUT, f"""
<h1>Где и када можеш да кажеш шта мислиш</h1>
<p class="lead">Јавне расправе и јавни увиди које општине објављују на својим сајтовима, и консултације државних органа отворене за коментаре. Уз сваку: где је, о чему је и када. Наслов води на објаву саме институције.</p>
<form id="filter" class="filter" hidden aria-label="Избор објава">
<label>Место <select name="mesto"><option value="">Сва места</option><option value="{STATE}">Република Србија (државни органи)</option>{"".join(options)}</select></label>
<details><summary>Време, врста, тема, реч</summary><div>
<label>Када <select name="kada"><option value="ahead">Траје или тек почиње</option><option value="week">Нешто почиње или истиче за 7 дана</option><option value="recent">Објављено у последњих {RECENT_DAYS} дана</option></select></label>
<label>Врста <select name="vrsta"><option value="">Све врсте</option>{"".join(f'<option value="{k}">{v}</option>' for k, v in KIND.items())}<option value="state">Консултације државе</option></select></label>
<label>Тема <select name="tema"><option value="">Све теме</option>{"".join(f'<option value="{k}">{v}</option>' for k, v in TOPIC.items())}</select></label>
<label>Реч у наслову <input type="search" name="rec" placeholder="нпр. соларна, вртић, порез"></label>
<button type="reset">Поништи избор</button>
</div></details>
</form>
<div id="reci" hidden><span data-k="found">Објава:</span><span data-k="next">Следећи дан:</span><span data-k="today">данас</span><span data-k="tomorrow">сутра</span><span data-k="in">за</span><span data-k="day">дан</span><span data-k="days">дана</span></div>
<p id="broj" class="count" aria-live="polite">{len(rows_ahead)} објава у којима нешто траје или тек почиње, по најближем дану, па још {len(rest)} објава из последњих {RECENT_DAYS} дана, најновије прво.</p>
<div id="mesta" class="note">{"".join(notes)}</div>
<p id="nema" class="note" hidden>Нема објава за овај избор.</p>
<ol id="lista" class="cards">{"".join(cards)}</ol>
<p class="count">Тражите акцију, не расправу (давање крви, волонтирање, чишћење, сађење)? <a href="{{home}}akcije.html">Акције</a>. Периоде и дане програм чита из текста објаве, са оним на шта се по речима објаве односе; тему и врсту из наслова. Место одржавања пише у објави. Објаве читамо са сајтова {len(by_code)} општина од {len(names)}; <a href="{{home}}opstine.html">којих и зашто</a>. <a href="{{home}}o-projektu.html">Како читамо</a>.</p>
""")

    # The page of actions: what is still to come, the nearest day first.
    todo = sorted((a for a in data["actions"] if a["end"] >= today.isoformat()), key=lambda a: (a["start"], a["kind"], a["place"], a["title"]))
    places = sorted({(place_key(a["place"]), _PREFIX.sub("", a["place"])) for a in todo if a["place"]}, key=lambda p: azbuka(p[1]))
    by_kind = {k: sum(1 for a in todo if a["kind"] == k) for k in ACTION}
    pages["akcije.html"] = ("Акције: давање крви, волонтирање, уређење околине — Учествуј", "Акције у којима можеш да учествујеш: давање крви, волонтерске акције, чишћење и сађење.", f"""
<h1>Акције у којима можеш да учествујеш</h1>
<p class="lead">Давање крви, волонтерске смене, чишћење и сађење: оно што организатор сам објављује, са местом и даном. Уз сваку је означено ко је објављује; наслов води на његову објаву.</p>
<form id="filter" class="filter" hidden aria-label="Избор акција">
<label>Место <select name="mesto"><option value="">Сва места</option>{"".join(f'<option value="{k}">{esc(n)}</option>' for k, n in places)}</select></label>
<details><summary>Време, врста, реч</summary><div>
<label>Када <select name="kada"><option value="ahead">Од данас надаље</option><option value="week">Почиње или истиче за 7 дана</option></select></label>
<label>Врста <select name="vrsta"><option value="">Све врсте</option>{"".join(f'<option value="{k}">{v}</option>' for k, v in ACTION.items())}</select></label>
<label>Реч <input type="search" name="rec" placeholder="нпр. крв, парк, маратон"></label>
<button type="reset">Поништи избор</button>
</div></details>
</form>
<div id="reci" hidden><span data-k="found">Акција:</span><span data-k="next">Следећи дан:</span><span data-k="today">данас</span><span data-k="tomorrow">сутра</span><span data-k="in">за</span><span data-k="day">дан</span><span data-k="days">дана</span></div>
<p id="broj" class="count" aria-live="polite">{len(todo)} акција од данас надаље: {by_kind["blood"]} давања крви, {by_kind["volunteer"]} волонтерских, {by_kind["environment"]} за уређење и заштиту околине.</p>
<div id="mesta" class="note"></div>
<p id="nema" class="note" hidden>Нема акција за овај избор.</p>
<ol id="lista" class="cards">{"".join(action_card(a) for a in todo)}</ol>
<p class="count">Сваку акцију објављује организатор на свом сајту, и то је њен извор: завод за трансфузију, Новосадски волонтерски сервис или општина. Дан и сате програм чита са те странице. Нису све акције отворене за свакога: нека организује фирма или установа за своје запослене, па место и услове проверите код организатора. Акција за уређење околине има мало, јер их организатори ретко објављују унапред. Знате акцију коју овде нема? <a href="{ACTION_REPORT}">Пријавите је</a> са везом на објаву организатора: проверимо је и додамо уз извор. <a href="{{home}}o-projektu.html">Како читамо</a>.</p>
""")

    rows = []
    for code, name in sorted(names.items(), key=lambda kv: azbuka(kv[1])):
        site, found = sites.get(code), by_code.get(code, [])
        last = next((a["day"] for a in found if a["day"]), "")
        label = f'<a href="{{home}}opstina/{code}.html">{esc(name)}</a>' if found else esc(name)
        domain = domains[code]
        scheme = site["answers"] if site and site["domain"] == domain and site["answers"] else "https"
        link = f'<a href="{scheme}://{esc(domain)}/">{esc(domain)}</a>' if domain else ""
        rows.append(f"<tr><th scope=\"row\">{label}</th><td class=\"num\">{len(found) or ''}</td><td>{day(last)}</td>"
                    f"<td>{state_of(domain, site, len(found))}</td><td>{link}</td></tr>")
    pages["opstine.html"] = ("Општине: јавне расправе и јавни увиди — Учествуј", "Шта која општина објављује на свом сајту, по азбуци.", f"""
<h1>Општине</h1>
<p class="lead">Шта општине објављују на својим сајтовима о јавним расправама и јавним увидима, по азбуци.</p>
<p>Општински сајтови немају заједнички облик. Читамо оне које можемо да питамо програмом (претрага сајта, фид). „Још не умемо“ значи да сајт одговара, али његове објаве засад не умемо да прочитамо; „не одговара“ да сајт није одговорио; „нема адресе“ да адресу сајта још немамо. То није оцена општине: многе објављују на страницама које још не умемо да прочитамо.</p>
<p>Списак сајтова је заједнички са <a href="https://izbornipodaci.rs/">Изборним подацима</a>. Знате адресу које овде нема, или је нека погрешна? <a href="{REPORT}">Пријавите је</a>: исправка стиже на оба сајта.</p>
<div class="scroll"><table class="sites">
<thead><tr><th scope="col">Општина</th><th scope="col" class="num">Објаве</th><th scope="col">Последња</th><th scope="col">Стање</th><th scope="col">Сајт</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table></div>
""")

    for code, found in by_code.items():
        site = sites.get(code)
        years: dict[str, list] = {}
        for a in found:
            years.setdefault(a["day"][:4] or "", []).append(a)
        parts = []
        for year in sorted(years, reverse=True):
            parts.append(f'<h2>{year or "Без датума"}</h2><ol class="cards">{"".join(item(a, names, False) for a in years[year])}</ol>')
        link = f'<a href="{esc(site["answers"])}://{esc(site["domain"])}/">{esc(site["domain"])}</a>' if site else ""
        pages[f"opstina/{code}.html"] = (f"{names[code]}: јавне расправе и јавни увиди — Учествуј",
                                         f"Јавне расправе и јавни увиди које {names[code]} објављује на свом сајту.", f"""
<p class="crumbs"><a href="{{home}}opstine.html">Општине</a></p>
<h1>{esc(names[code])}</h1>
<p class="lead">{len(found)} објава о јавним расправама и јавним увидима са сајта {link}, најновије прво.</p>
<p class="note">Наслови су речи општине. Периоде и дане испод наслова програм чита из текста објаве; „У објави“ стоји уз дан за који из речи око њега није јасно на шта се односи. „Одржано“ стоји уз објаву чији наслов каже да је расправа или увид одржан; и објава без те ознаке може бити вест, а не позив: прочитајте је на сајту општине. Наслов који именује подносиоца захтева (инвеститора) не преносимо.</p>
{"".join(parts)}
""")

    pages["drzava.html"] = ("Држава: консултације и јавне расправе — Учествуј", "Консултације и јавне расправе државних органа на порталу еКонсултације.", f"""
<h1>Држава</h1>
<p class="lead">Консултације и јавне расправе државних органа о прописима и планским документима, са портала <a href="https://ekonsultacije.gov.rs/">еКонсултације</a>.</p>
<h2>Отворено за коментаре</h2>
<p class="count">{len(open_now)} тема чија фаза траје, по року.</p>
<ol class="cards">{"".join(topic(t) for t in open_now)}</ol>
<h2>Шта још има на порталу</h2>
<p>Портал води {len(topics)} тема. Још {len(stale)} није означено као завршено, а ниједна њихова фаза не траје: рок је прошао или фаза није ни отворена. Сматрамо отвореном само тему чија фаза траје данас, по датумима самог портала.</p>
<p>Општине су на порталу регистроване, али на њему готово ништа не објављују; њихове расправе су на њиховим сајтовима (<a href="{{home}}opstine.html">Општине</a>).</p>
""")

    sources = data["sources"]
    srows = []
    for key, label in (("announcements", "Сајтови општина"), ("consultations", "еКонсултације"), ("bodies", "Каталог органа јавне власти, Повереник"),
                       ("municipalities", "Контакт подаци општина, министарство"), ("tasks", "Послови локалне самоуправе, министарство"), ("laws", "Закони: регистар Службеног гласника"), ("actions", "Акције: заводи за трансфузију, волонтерски сервис, општине")):
        s = sources.get(key)
        if s:
            where = f'<a href="{esc(s.get("page") or s.get("url") or "")}">{esc(s.get("title") or label)}</a>' if (s.get("page") or s.get("url")) else esc(label)
            srows.append(f"<tr><th scope=\"row\">{esc(label)}</th><td>{where}</td><td>{day(s['read'])}</td></tr>")
    pages["o-projektu.html"] = ("О пројекту — Учествуј", "Шта је Учествуј, одакле су подаци и по којим правилима ради.", f"""
<h1>О пројекту</h1>
<p class="lead">Учествуј показује где и када човек може да учествује у одлукама тамо где живи: јавне расправе, јавни увиди, консултације. Део је <a href="https://javni-uvid.github.io/osnova/">Јавног увида</a> и држи се његових начела.</p>
<h2>Одакле су подаци</h2>
<div class="scroll"><table><thead><tr><th scope="col">Шта</th><th scope="col">Извор</th><th scope="col">Прочитано</th></tr></thead><tbody>{"".join(srows)}</tbody></table></div>
<h2>Правила</h2>
<ul>
<li><b>Иста правила за сваку општину.</b> Општине су по азбуци; ниједна се не оцењује, ниједна се не рангира.</li>
<li><b>Сваки ред води на објаву саме институције.</b> Сајт не преписује објаве, само њихов наслов, дан и адресу.</li>
<li><b>Наслов је речи општине,</b> пренет како је написан; на латиничком издању пресловљен. Јавни функционер у наслову остаје како га је општина навела. Наслов који именује подносиоца захтева (инвеститора, носиоца пројекта) не преносимо, јер може именовати приватно лице: уместо њега стоји веза ка објави.</li>
<li><b>Одржано је оно за шта наслов то каже</b> („одржана“, „извештај о спроведеној јавној расправи“). Остале објаве су позиви и огласи, а понека и вест коју наслов не одаје.</li>
<li><b>Када је шта, читамо из текста објаве, а текст не преносимо.</b> Програм налази периоде („од … до …“), рокове („до …“) и дане са часом, и уз сваки ставља оно о чему говоре речи испред њега: јавни увид, јавна расправа, јавна седница, примедбе. Где то из речи није јасно, пише само „У објави“. Дан написан без године не узима, а трајање („30 дана од …“) не прерачунава у крајњи дан. Оно што се завршило пре објаве не наводи. Нађете ли погрешан дан, пријавите га.</li>
<li><b>Тему и врсту читамо из наслова,</b> по речима („буџет“, „план детаљне регулације“, „процена утицаја“). Наслов који не каже тему стоји под „Остало“.</li>
<li><b>Акције објављује организатор, и то је њихов извор.</b> На страници „Акције“ уз сваку пише ко је објављује и наслов води на његову објаву. То нису само институције: може и удружење или група грађана, ако сама објављује акцију којој може да се придружи сваки човек, а ту могућност је одлучио одржавалац 22. 11. 2026. (вести и друштвене мреже такође могу бити извор, ако се тако означе; програм их данас не чита). Иста правила за сваког организатора. Лични подаци (телефон, мејл) се не преносе. Акцију затвореног типа (за запослене једне фирме) не преносимо кад сам организатор то каже; кад не каже, место и услове проверите код њега.</li>
<li><b>Отворено је оно чија фаза траје данас,</b> по датумима самог портала.</li>
<li><b>Избор на првој страни ради у вашем прегледачу.</b> Једна скрипта, наша, сакрива редове које нисте тражили и рачуна колико је дана до следећег дана у објави. Ништа не чува на уређају и ништа никуд не шаље; без ње је списак цео.</li>
<li><b>Списак општинских сајтова је један,</b> заједнички са Изборним подацима: адреса нађена или исправљена тамо стиже и овде.</li>
</ul>
<h2>Шта још није овде</h2>
<ul>
<li>Водичи кроз остале начине да се учествује (грађанска иницијатива, збор грађана, јавна расправа): <a href="{{home}}vodici.html">два су написана</a> (захтев за информације од јавног значаја; грађанска иницијатива и збор грађана), сваки корак са чланом закона на коме почива. Јавна расправа чека статуте општина.</li>
<li>Општине чије објаве још не умемо да прочитамо, и место расправе: објава га наводи у тексту, а ми из њега читамо само када је шта.</li>
<li>Јавни увиди у планове које објављују министарство, покрајина и заводи за урбанизам, и процене утицаја на животну средину.</li>
</ul>
<p>Грешку пријавите на <a href="{REPO}/issues">GitHub-у</a>.</p>
""")

    pages["zahtev.html"] = guide.page(data["laws"]["access"], data["laws"]["procedure"])
    pages["inicijativa.html"] = guide.initiative_page(data["laws"]["local"])
    pages["vodici.html"] = guide.index_page()

    if out.exists():
        shutil.rmtree(out)
    (out / "cir").mkdir(parents=True)
    shutil.copy(DESIGN / "osnova.css", out / "osnova.css")
    shutil.copytree(DESIGN / "fonts", out / "fonts")
    for f in STATIC.iterdir():
        shutil.copy(f, out / f.name)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    version = hashlib.sha256((DESIGN / "osnova.css").read_bytes() + (STATIC / "site.css").read_bytes()
                             + (STATIC / "site.js").read_bytes()).hexdigest()[:8]
    wrong = []
    for path, (title, description, main) in pages.items():
        for script in ("lat", "cyr"):
            text = frame(path, script, title, description, main, read, version)
            where = out / ("cir/" if script == "cyr" else "") / path
            where.parent.mkdir(parents=True, exist_ok=True)
            where.write_text(text, encoding="utf-8", newline="\n")
            wrong += [f"{where.relative_to(out).as_posix()}: {w}" for w in check(text, script)]
    return wrong


def check(page: str, script: str) -> list[str]:
    wrong = []
    if "@@" in page or "{home}" in page or "{root}" in page:
        wrong.append("a placeholder was left in")
    # One script, the site's own file: nothing written into a page, nothing from another server.
    if re.sub(r'<script src="(?:\.\./)*site\.js\?v=\w+" defer></script>', "", page, count=1).count("<script") or re.search(r"\son[a-z]+=", page):
        wrong.append("a script other than the site's own file")
    loads = re.findall(r'<(?:img|iframe|source|video|audio|embed|object)\b[^>]*\b(?:src|data)="([^"]*)"', page)
    loads += re.findall(r'<link\b[^>]*\bhref="([^"]*)"', page) + re.findall(r'<script\b[^>]*\bsrc="([^"]*)"', page)
    wrong += [f"loads from another server: {a}" for a in loads if re.match(r"(?:[a-z]+:)?//", a)]
    if script == "lat":
        left = CYRILLIC.findall(text_of(page).replace("Ћирилица", ""))
        if left:
            wrong.append("Cyrillic letters on the Latin page: " + "".join(sorted(set(left))))
    if len(page.encode("utf-8")) > 1_000_000:
        wrong.append("over 1 MB")
    return wrong
