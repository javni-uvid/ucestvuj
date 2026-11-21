"""The site, built from data/ into static pages in the family's look (osnova/design/), in Cyrillic (cir/) and
Latin (the default). Written once in Cyrillic; the Latin edition is the same page turned letter by letter, its
addresses untouched. Nothing on a page comes from another server, and nothing needs a script.

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
from pathlib import Path

from ucestvuj.announcements import held
from ucestvuj.sites import REPORT
from ucestvuj.translit import CYRILLIC, latin_page, text_of

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
    return {"announcements": read("announcements.json"), "sites": read("sites.json"),
            "consultations": read("consultations.json"), "sources": read("sources.json"), "listed": listed}


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
</head>
<body>
<a class="skip" href="#sadrzaj">Прескочи на садржај</a>
{bar}
<header class="top">
  <a class="brand" href="{home}index.html">{NAME}</a>
  <nav aria-label="Сајт">
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


def item(a: dict, names: dict, with_place: bool = True) -> str:
    title = shown_title(a)
    words = (f'<a class="title" href="{esc(a["url"])}">{esc(title)}</a>' if title else
             f'<a class="title" href="{esc(a["url"])}">Наслов именује подносиоца; прочитајте га на сајту општине</a>')
    place = f'<a class="where" href="{{home}}opstina/{esc(a["code"])}.html">{esc(names[a["code"]])}</a>' if with_place else ""
    when = f'<span class="when">{day(a["day"])}</span>' if a["day"] else '<span class="when">без датума</span>'
    over = " · одржано" if held(a["title"]) else ""
    return f'<li>{when}{place}<span class="kind">{KIND[a["kind"]]}{over}</span>{words}</li>'


def topic(t: dict) -> str:
    return (f'<li><span class="when">до {day(t["until"])}</span><span class="where">{esc(t["institution"])}</span>'
            f'<span class="kind">{esc(t["phase"])}</span><a class="title" href="{esc(t["url"])}">{esc(t["title"])}</a></li>')


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
    called = [a for a in recent if not held(a["title"])]
    over = [a for a in recent if held(a["title"])]
    topics = data["consultations"]
    open_now = sorted((t for t in topics if t["open"] and t.get("until", "") >= today.isoformat()),
                      key=lambda t: (t["until"], t["institution"], t["title"]))
    stale = [t for t in topics if t["open"] and t.get("until", "") < today.isoformat()]
    sites = {s["code"]: s for s in data["sites"]}
    pages: dict[str, tuple[str, str, str]] = {}

    pages["index.html"] = ("Учествуј: где и када можеш да кажеш шта мислиш", ABOUT, f"""
<h1>Где и када можеш да кажеш шта мислиш</h1>
<p class="lead">Јавне расправе и јавни увиди које општине објављују на својим сајтовима, и консултације државних органа отворене за коментаре. Сваки ред води на објаву саме институције.</p>
<h2>У општинама: позиви и огласи, последњих {RECENT_DAYS} дана</h2>
<p class="count">{len(called)} објава из {len({a["code"] for a in called})} општина, најновије прво. Дан је дан објаве, не дан расправе: рок и место су у самој објави, а ми засад читамо само наслов. Објаве читамо са сајтова {len(by_code)} општина од {len(names)}; <a href="{{home}}opstine.html">којих и зашто</a>.</p>
<ol class="items">{"".join(item(a, names) for a in called)}</ol>
<h2>У општинама: одржано</h2>
<p class="count">{len(over)} објава чији наслов каже да је расправа или увид одржан: вест о томе или извештај.</p>
<ol class="items">{"".join(item(a, names) for a in over)}</ol>
<h2>Држава: отворено за коментаре</h2>
<p class="count">{len(open_now)} тема на порталу еКонсултације, по року.</p>
<ol class="items">{"".join(topic(t) for t in open_now)}</ol>
<p><a href="{{home}}drzava.html">Шта је још на порталу</a></p>
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
            parts.append(f'<h2>{year or "Без датума"}</h2><ol class="items">{"".join(item(a, names, False) for a in years[year])}</ol>')
        link = f'<a href="{esc(site["answers"])}://{esc(site["domain"])}/">{esc(site["domain"])}</a>' if site else ""
        pages[f"opstina/{code}.html"] = (f"{names[code]}: јавне расправе и јавни увиди — Учествуј",
                                         f"Јавне расправе и јавни увиди које {names[code]} објављује на свом сајту.", f"""
<p class="crumbs"><a href="{{home}}opstine.html">Општине</a></p>
<h1>{esc(names[code])}</h1>
<p class="lead">{len(found)} објава о јавним расправама и јавним увидима са сајта {link}, најновије прво.</p>
<p class="note">Наслови су речи општине. „Одржано“ стоји уз објаву чији наслов каже да је расправа или увид одржан; и објава без те ознаке може бити вест, а не позив: прочитајте је на сајту општине. Наслов који именује подносиоца захтева (инвеститора) не преносимо.</p>
{"".join(parts)}
""")

    pages["drzava.html"] = ("Држава: консултације и јавне расправе — Учествуј", "Консултације и јавне расправе државних органа на порталу еКонсултације.", f"""
<h1>Држава</h1>
<p class="lead">Консултације и јавне расправе државних органа о прописима и планским документима, са портала <a href="https://ekonsultacije.gov.rs/">еКонсултације</a>.</p>
<h2>Отворено за коментаре</h2>
<p class="count">{len(open_now)} тема чија фаза траје, по року.</p>
<ol class="items">{"".join(topic(t) for t in open_now)}</ol>
<h2>Шта још има на порталу</h2>
<p>Портал води {len(topics)} тема. Још {len(stale)} није означено као завршено, а ниједна њихова фаза не траје: рок је прошао или фаза није ни отворена. Сматрамо отвореном само тему чија фаза траје данас, по датумима самог портала.</p>
<p>Општине су на порталу регистроване, али на њему готово ништа не објављују; њихове расправе су на њиховим сајтовима (<a href="{{home}}opstine.html">Општине</a>).</p>
""")

    sources = data["sources"]
    srows = []
    for key, label in (("announcements", "Сајтови општина"), ("consultations", "еКонсултације"), ("bodies", "Каталог органа јавне власти, Повереник"),
                       ("municipalities", "Контакт подаци општина, министарство"), ("tasks", "Послови локалне самоуправе, министарство")):
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
<li><b>Отворено је оно чија фаза траје данас,</b> по датумима самог портала.</li>
<li><b>Списак општинских сајтова је један,</b> заједнички са Изборним подацима: адреса нађена или исправљена тамо стиже и овде.</li>
</ul>
<h2>Шта још није овде</h2>
<ul>
<li>Водичи кроз то како се учествује (збор грађана, грађанска иницијатива, јавна расправа, захтев за информације од јавног значаја), сваки корак са чланом закона на коме почива.</li>
<li>Општине чије објаве још не умемо да прочитамо, и рокови општинских расправа: објава их наводи у тексту, а ми засад читамо само наслов.</li>
<li>Јавни увиди у планове које објављују министарство, покрајина и заводи за урбанизам, и процене утицаја на животну средину.</li>
</ul>
<p>Грешку пријавите на <a href="{REPO}/issues">GitHub-у</a>.</p>
""")

    if out.exists():
        shutil.rmtree(out)
    (out / "cir").mkdir(parents=True)
    shutil.copy(DESIGN / "osnova.css", out / "osnova.css")
    shutil.copytree(DESIGN / "fonts", out / "fonts")
    for f in STATIC.iterdir():
        shutil.copy(f, out / f.name)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    version = hashlib.sha256((DESIGN / "osnova.css").read_bytes() + (STATIC / "site.css").read_bytes()).hexdigest()[:8]
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
    if "<script" in page:
        wrong.append("a script; the site has none")
    loads = re.findall(r'<(?:img|iframe|source|video|audio|embed|object)\b[^>]*\b(?:src|data)="([^"]*)"', page)
    loads += re.findall(r'<link\b[^>]*\bhref="([^"]*)"', page)
    wrong += [f"loads from another server: {a}" for a in loads if re.match(r"(?:[a-z]+:)?//", a)]
    if script == "lat":
        left = CYRILLIC.findall(text_of(page).replace("Ћирилица", ""))
        if left:
            wrong.append("Cyrillic letters on the Latin page: " + "".join(sorted(set(left))))
    if len(page.encode("utf-8")) > 1_000_000:
        wrong.append("over 1 MB")
    return wrong
