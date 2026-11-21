"""What a municipality announces on its own site that a citizen can take part in: public debates and public
inspections of plans. Read where a site offers a list a program can ask for:

- a WordPress site answers a search of its posts (`/wp-json/wp/v2/posts?search=…`), with each post's day; where
  the announcements are a kind of content of their own (the state's ls.gov.rs sites), its search of everything
  (`/wp-json/wp/v2/search`) finds them, without a day;
- any site with a feed gives its newest entries, kept when their title says what they are.

A site with neither is not read here (its first page's links are in sites.json). Only the title, the day, the
address and when what the announcement calls to is on (when.py) are kept; the text itself, which may name people
and give their addresses, is read and not kept, and stays on the municipality's site."""

import html
import re
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

from ucestvuj import web, when
from ucestvuj.translit import latin

ASKED = ("јавна расправа", "javna rasprava", "јавни увид", "javni uvid")
# What a title says the announcement is; the first that matches. Latin and Cyrillic, lower case.
KINDS = (
    ("early_inspection", re.compile(r"rani javni uvid|рани јавни увид")),
    ("inspection", re.compile(r"javn\w* uvid|јавн\w* увид")),
    ("debate", re.compile(r"javn\w* rasprav|јавн\w* расправ")),
)
# A title that says the debate or the inspection is over: news that it was held, or the report on it. Read in
# Latin, with or without the marks on the letters. "Извештај о стратешкој процени" is a document on inspection,
# not a report on one, so a report counts only when it is on a debate or an inspection.
_HELD = re.compile(r"odr[zž]an|sproveden|zavr[sš]en|obavljen|zapisnik"
                   r"|izve[sš]taj\w* (?:o|sa) (?:\w+ )?(?:ran\w+ )?javn\w+ (?:rasprav|uvid)")
_BUDGET = re.compile(r"budžet|budzet|буџет")
_TAGS = re.compile(r"<[^>]+>")


def kind(title: str) -> str:
    low = title.lower()
    return next((name for name, pattern in KINDS if pattern.search(low)), "")


# What an announcement is about, by its title's words; the first that matches. Read in Latin, lower case. A plan
# comes before the environment: a plan's inspection names its environmental report in the same title.
TOPICS = (
    ("budget", re.compile(r"bud[zž]et|buđet|rebalans|zavr[sš]n\w+ ra[cč]un")),
    ("taxes", re.compile(r"porez|taks|naknad|cen\w+ kvadratn")),
    ("plans", re.compile(r"regulacij|\bpdr\b|\bpgr\b|\bgup\b|prostorn\w+ plan|urbanisti|plansk\w+ dokument|komasacij|\bplan\w* detaljn|\bplan\w* generaln")),
    ("environment", re.compile(r"procen\w+ uticaja|[zž]ivotn\w+ sredin|za[sš]tit\w+ prirode|otpad|za[sš]ti[cć]en\w+ podru[cč]j")),
    ("development", re.compile(r"strategij|plan\w* razvoja|akcion\w+ plan|program\w* razvoja|srednjoro[cč]n|plan\w* javnog zdravlja")),
)


def topic(title: str) -> str:
    low = latin(title).lower()
    return next((name for name, pattern in TOPICS if pattern.search(low)), "other")


def held(title: str) -> bool:
    """Whether the title itself says the debate or the inspection was held. A title that doesn't say so may
    still be news of one: only the municipality's own page tells."""
    return bool(_HELD.search(latin(title).lower()))


def clean(text: str) -> str:
    return " ".join(html.unescape(_TAGS.sub(" ", text or "")).split())


def entry(title: str, url: str, day: str, via: str, text: str = "") -> dict | None:
    """One announcement, or nothing when its title doesn't say it is a debate or an inspection. Of its text only
    the periods and days it names are kept. The title is read with it: some say the period themselves."""
    title = clean(title)
    what = kind(title)
    if not what or not url.startswith("http"):
        return None
    return {"kind": what, "budget": bool(_BUDGET.search(title.lower())), "title": title, "day": day[:10], "url": url,
            "via": via, "when": when.read(f"{title}. {clean(text)}" if text else "", day)}


def from_wordpress(base: str) -> list[dict]:
    found = []
    for words in ASKED:
        q = urllib.parse.quote(words)
        asked = f"{base}wp-json/wp/v2/posts?search={q}&per_page=50&orderby=date&_fields=date,link,title"
        for fields in (",content", ""):  # with the text; a site that won't give 50 texts at once, without
            try:
                posts = web.get_json(asked + fields, timeout=40)
                found += [entry(p["title"]["rendered"], p["link"], p["date"], "wordpress posts",
                                p.get("content", {}).get("rendered", "")) for p in posts]
                break
            except Exception:
                pass  # a site that closed this door may still answer the next
        try:
            hits = web.get_json(f"{base}wp-json/wp/v2/search?search={q}&per_page=50&_fields=title,url", timeout=30)
            found += [entry(h["title"], h["url"], "", "wordpress search") for h in hits]
        except Exception:
            pass
    return [f for f in found if f]


def from_feed(feed: str) -> list[dict]:
    try:
        root = ET.fromstring(web.get(feed, timeout=30))
    except Exception:
        return []
    found = []
    for item in root.iter():
        tag = item.tag.rsplit("}", 1)[-1]
        if tag not in ("item", "entry"):
            continue
        parts = {child.tag.rsplit("}", 1)[-1]: child for child in item}
        link = parts.get("link")
        url = (link.text or link.get("href") or "").strip() if link is not None else ""
        when = next((parts[k].text or "" for k in ("pubDate", "published", "updated", "date") if k in parts), "")
        text = " ".join(parts[k].text or "" for k in ("encoded", "content", "description", "summary") if k in parts)
        found.append(entry(parts["title"].text if "title" in parts else "", url, day(when), "feed", text))
    return [f for f in found if f]


_MONTHS = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def day(when: str) -> str:
    """A feed's date as YYYY-MM-DD: RSS writes "Thu, 19 Nov 2026 10:00:00 +0000", Atom the ISO form."""
    when = (when or "").strip()
    rss = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", when)
    if rss and rss.group(2) in _MONTHS:
        return f"{rss.group(3)}-{_MONTHS[rss.group(2)]:02d}-{int(rss.group(1)):02d}"
    return when[:10] if re.match(r"\d{4}-\d{2}-\d{2}", when) else ""


def of_site(site: dict) -> list[dict]:
    """One municipality's announcements, each address once (the reading with a day wins, then the one whose
    text named more days), newest first."""
    if not site.get("answers"):
        return []
    base = f'{site["answers"]}://{site["domain"]}/'
    found = (from_wordpress(base) if site["system"] == "wordpress" else []) + (from_feed(site["feed"]) if site.get("feed") else [])
    best: dict[str, dict] = {}
    for f in found:
        weight = lambda e: (bool(e["day"]), len(e["when"]))
        if f["url"] not in best or weight(f) > weight(best[f["url"]]):
            best[f["url"]] = f
    rows = sorted(best.values(), key=lambda f: (f["day"], f["url"]), reverse=True)
    return [{"code": site["code"], "municipality": site["name"], **f} for f in rows]


def fetch(sites: list[dict], workers: int = 12) -> list[dict]:
    with ThreadPoolExecutor(workers) as pool:
        return [row for rows in pool.map(of_site, sites) for row in rows]
