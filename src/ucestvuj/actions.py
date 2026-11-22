"""Actions a person can join and that a body or an organizer announces on its own site: giving blood, volunteer
shifts, clean-ups and plantings. Not debates (announcements.py): these are things to do, with a place and a day.

The sources, each read by its own page's form (docs/decisions/data.md, "Other ways to take part"):

- the blood transfusion institute of Vojvodina: a list whose "add to calendar" links hold the day, the hours and
  the place;
- the Institute for Blood Transfusion of Serbia: a card per day, hours as text; an action marked as closed
  (employees only) is left out, since it is not for the public;
- the volunteer service of Novi Sad: a post type of its own with the days, the place and the deadline as fields;
  the host's phone and e-mail, which the same posts carry, are not read;
- the municipalities' own posts (the sites whose posts can be searched): a call to give blood, a clean-up, a
  planting or a volunteer action, kept only when its text names a day from the post's own on;
- the feeds of organizers and news sites listed in data/action_feeds.csv: the same rule for an entry, and the row
  says it is the organizer's news;
- the actions readers reported, checked and kept in data/actions_manual.json: the row says it is a reader's report.

Each action keeps the kind, who announces it, the place, the title as written, the address of the announcement
and the days; never a person's contact."""

import datetime
import html
import re
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

from ucestvuj import announcements, web, when
from ucestvuj.translit import latin

KINDS = ("blood", "volunteer", "environment")
MONTHS = {m: i + 1 for i, m in enumerate("јануар фебруар март април мај јун јул август септембар октобар новембар децембар".split())}
ZTKV = "https://www.transfuzija.rs/dobrovoljno-davanje-krvi/akcije-na-terenu/"
ITKS = "https://itks.rs/nedeljni-plan-ekipa.html"
NVS = "https://nvs.rs/wp-json/wp/v2/positions?per_page=50&_fields=date,link,title,meta"
ORGANIZERS = {"ztkv": "Завод за трансфузију крви Војводине", "itks": "Институт за трансфузију крви Србије",
              "nvs": "Новосадски волонтерски сервис"}


def action(kind: str, source: str, place: str, title: str, url: str, start: str, end: str = "", **more) -> dict:
    return {"kind": kind, "source": source, "organizer": ORGANIZERS.get(source, ""), "place": place, "title": title,
            "url": url, "start": start, "end": end or start, "time": "", "venue": "", "deadline": "", "code": "", "how": "", **more}


def _text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def _clock(hours: str) -> str:
    """9.30-14.30ч or 11-15ч as 9:30-14:30 / 11:00-15:00."""
    m = re.search(r"(\d{1,2})(?:[.:](\d{2}))?\s*[-–]\s*(\d{1,2})(?:[.:](\d{2}))?", hours)
    if not m:
        return ""
    return f"{int(m[1])}:{m[2] or '00'}–{int(m[3])}:{m[4] or '00'}"


def transfusion_vojvodina(page: str) -> list[dict]:
    """Every calendar link of the institute's list of field actions."""
    found = []
    for link in re.findall(r'https://calendar\.google\.com/calendar/render\?[^"\']+', page):
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(html.unescape(link)).query)
        dates = re.match(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})\d*/\d{4}\d{2}\d{2}T(\d{2})(\d{2})", (q.get("dates") or [""])[0])
        where = (q.get("location") or [""])[0]
        if not dates or not where:
            continue
        place, _, venue = where.partition(",")
        found.append(action("blood", "ztkv", place.strip(), "Добровољно давање крви: " + place.strip(), ZTKV,
                            f"{dates[1]}-{dates[2]}-{dates[3]}", venue=venue.strip(),
                            time=f"{int(dates[4])}:{dates[5]}–{int(dates[6])}:{dates[7]}"))
    return found


def transfusion_serbia(page: str) -> list[dict]:
    """A card of a day, and in it a line for each action: the municipality, the venue and the hours. A line marked
    as of the closed type (for employees only) is not read."""
    found = []
    for card in page.split("KARTICA DANA -")[1:]:
        day = re.search(r"(\d{1,2})\.\s*([а-я]+)\s+(\d{4})", _text(card.split("</h4>")[0]))
        if not day or day[2] not in MONTHS:
            continue
        iso = f"{day[3]}-{MONTHS[day[2]]:02d}-{int(day[1]):02d}"
        for icon, place, rest in re.findall(r'<img[^>]*images/(\w+)\.svg[^>]*>\s*(?:&nbsp;)?\s*<strong>([^<]*)</strong>(.*?)<br', card, re.S):
            if icon != "icondrop":
                continue
            hours = re.search(r"<b>([^<]*)</b>", rest)
            place = place.strip().rstrip(",").strip()
            found.append(action("blood", "itks", place, "Добровољно давање крви: " + place, ITKS, iso,
                                venue=_text(rest.split("<b>")[0]), time=_clock(hours[1]) if hours else ""))
    return found


def _iso(text: str) -> str:
    """2026 11 29 as 2026-11-29."""
    m = re.fullmatch(r"\s*(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s*", text or "")
    return f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}" if m else ""


def _hours(text: str) -> str:
    """The hours a sentence names ("од 11 до 16 часова", "Od 14.00 do 20.00 časova"), or nothing."""
    low = latin(text).lower()
    # "od 8:00 do 14:00" needs no unit; "od 11 do 16" does ("časova"), or it may be days or ages
    m = (re.search(r"\bod\s+(\d{1,2})[.:](\d{2})\s*(?:do|-|–)\s*(\d{1,2})[.:](\d{2})", low)
         or re.search(r"\bod\s+(\d{1,2})()\s*(?:do|-|–)\s*(\d{1,2})()\s*(?:[cč]asov|[cč]\b|h\b)", low))
    return f"{int(m[1])}:{m[2] or '00'}–{int(m[3])}:{m[4] or '00'}" if m else ""


def volunteer_service(posts: list[dict]) -> list[dict]:
    """The volunteer service's positions. Only the fields about the action: the days, the place, the deadline, the
    hours; the contact fields are never read."""
    found = []
    for p in posts:
        meta = p.get("meta") or {}
        start = _iso(meta.get("_nvs_event_starts"))
        if not start:
            continue
        found.append(action("volunteer", "nvs", "Нови Сад", announcements.clean(p["title"]["rendered"]), p["link"], start,
                            _iso(meta.get("_nvs_event_ends")), venue=announcements.clean(meta.get("_nvs_location", "")),
                            deadline=_iso(meta.get("_nvs_application_deadline")),
                            time=_hours(announcements.clean(meta.get("_nvs_duration_info", "")))))
    return found


# What a municipality's post must say in its title to be a call to join, by kind; read in Latin, lower case.
CUES = {
    "blood": re.compile(r"\bkrvi\b|davao[cč]|davala[cč]"),
    "environment": re.compile(r"[cč]i[sš][cć]enj|pošumlj|posumlj|sadnj|sadnic|radn\w+ akcij|ekološk\w+ akcij|ure[dđ]enj\w+ (?:parka|dvori|okolin)|akcij\w+ (?:sakupljanja|prikupljanja)"),
    "volunteer": re.compile(r"volont"),
}
CALL = re.compile(r"poziv|akcij|obave[sš]tenj|najav|pridru[zž]|u[cč]estvuj|organizuj|zakazan|u toku|prijav|dobrodo[sš]li|pozivamo")
ASKED = {"blood": ("давање крви", "davanje krvi", "давалаца крви"), "environment": ("акција чишћења", "чишћење", "пошумљавање", "садња", "akcija čišćenja", "sadnja"),
         "volunteer": ("волонтерска акција", "волонтери", "volonterska akcija")}


def ahead(title: str, text: str, published: str) -> tuple[str, str] | None:
    """The start and the end of the nearest thing a post's text names from the post's own day on, or nothing."""
    items = [i for i in when.read(f"{title}. {text}", published) if i["from"] or i["to"]]
    days = [d for i in items for d in (i["from"], when.until(i)) if d and d >= published]
    if not days:
        return None
    item = next(i for i in items if min(days) in (i["from"], when.until(i)))
    return item["from"] or item["to"], when.until(item)


def kind_of(title: str) -> str:
    """What a title calls to, when it calls to something that isn't over: blood, environment or volunteer."""
    low = latin(title).lower()
    if not CALL.search(low) or announcements.held(title):
        return ""
    return next((k for k, cue in CUES.items() if cue.search(low)), "")


def of_feed(feed: dict) -> list[dict]:
    """The entries of an organizer's feed that call to join something and name a day ahead."""
    try:
        root = ET.fromstring(web.get(feed["url"], timeout=40))
    except Exception:
        return []
    found = []
    for entry in root.iter():
        if entry.tag.rsplit("}", 1)[-1] not in ("item", "entry"):
            continue
        parts = {child.tag.rsplit("}", 1)[-1]: child for child in entry}
        link = parts.get("link")
        url = ((link.text or link.get("href") or "") if link is not None else "").strip()
        title = announcements.clean(parts["title"].text if "title" in parts else "")
        published = announcements.day(next((parts[k].text or "" for k in ("pubDate", "published", "updated", "date") if k in parts), ""))
        kind = kind_of(title)
        if not (kind and url.startswith("http") and published):
            continue
        text = announcements.clean(" ".join(parts[k].text or "" for k in ("encoded", "content", "description", "summary") if k in parts))
        days = ahead(title, text, published)
        if days:
            found.append(action(kind, "feed", feed.get("place", ""), title, url, days[0], days[1],
                                organizer=feed["organizer"], how="news", published=published))
    return found


def reported(rows: list[dict]) -> list[dict]:
    """The actions readers reported and a person checked, from data/actions_manual.json. A row without a kind, an
    organizer, a title, an address or a day is not taken."""
    found = []
    for r in rows:
        if r.get("kind") in KINDS and r.get("organizer") and r.get("title") and str(r.get("url", "")).startswith("http") and r.get("start"):
            found.append(action(r["kind"], "report", r.get("place", ""), r["title"], r["url"], r["start"], r.get("end", ""),
                                organizer=r["organizer"], how="report", venue=r.get("venue", ""), time=r.get("time", "")))
    return found


def of_municipality(site: dict) -> list[dict]:
    """A municipality's posts that call to give blood, to clean, to plant or to volunteer, with the days the post's
    text names from its own day on. A post whose title says it is over, or whose text names no day ahead, is not
    kept: there would be no day to give."""
    if not site.get("answers") or site.get("system") != "wordpress":
        return []
    base = f'{site["answers"]}://{site["domain"]}/'
    best: dict[str, dict] = {}
    for kind, words in ASKED.items():
        for w in words:
            try:
                posts = web.get_json(f"{base}wp-json/wp/v2/posts?search={urllib.parse.quote(w)}&per_page=20&orderby=date&_fields=date,link,title,content", timeout=40)
            except Exception:
                continue
            for p in posts:
                title = announcements.clean(p["title"]["rendered"])
                low = latin(title).lower()
                if not CUES[kind].search(low) or not CALL.search(low) or announcements.held(title):
                    continue
                days = ahead(title, announcements.clean(p["content"]["rendered"]), p["date"][:10])
                if days:
                    best[p["link"]] = action(kind, "municipality", site["name"], title, p["link"], days[0], days[1],
                                             organizer=site["name"], code=site["code"], published=p["date"][:10])
    return list(best.values())


def fetch(sites: list[dict], previous: list[dict] = (), municipalities: bool = True, feeds: list[dict] = (),
          manual: list[dict] = (), workers: int = 12) -> list[dict]:
    """The sources read once. `municipalities=False` reads only the three pages of the institutes and the
    service (the quick reading: three requests); the municipalities' rows are then those of `previous`.
    A source that does not answer, or answers a page from which nothing could be read, keeps its rows of
    `previous` that are still ahead: a page that changed its form must not empty the site."""
    found, read_ok = [], set()
    for name, read in (("ztkv", lambda: transfusion_vojvodina(web.get(ZTKV, timeout=40).decode("utf-8", "replace"))),
                       ("itks", lambda: transfusion_serbia(web.get(ITKS, timeout=40).decode("utf-8", "replace"))),
                       ("nvs", lambda: volunteer_service(web.get_json(NVS, timeout=40)))):
        try:
            rows = read()
        except Exception:
            continue
        if rows:
            found += rows
            read_ok.add(name)
    if municipalities:
        with ThreadPoolExecutor(workers) as pool:
            found += [a for rows in pool.map(of_municipality, sites) for a in rows]
        read_ok.add("municipality")
    for feed in feeds:  # a feed that gives nothing today gives nothing: its entries are the latest ten
        found += of_feed(feed)
    found += reported(manual)
    read_ok |= {"feed", "report"}
    found += [a for a in previous if a["source"] not in read_ok]
    today = datetime.date.today().isoformat()
    found = [a for a in found if a["end"] >= today]  # what is over is not kept
    unique = {(a["source"], a["place"], a["start"], a["url"], a["title"]): a for a in found}
    return sorted(unique.values(), key=lambda a: (a["start"], a["kind"], a["place"], a["title"]))
