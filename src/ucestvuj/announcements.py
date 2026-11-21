"""What a municipality announces on its own site that a citizen can take part in: public debates and public
inspections of plans. Read where a site offers a list a program can ask for:

- a WordPress site answers a search of its posts (`/wp-json/wp/v2/posts?search=…`), with each post's day; where
  the announcements are a kind of content of their own (the state's ls.gov.rs sites), its search of everything
  (`/wp-json/wp/v2/search`) finds them, without a day;
- any site with a feed gives its newest entries, kept when their title says what they are.

A site with neither is not read here (its first page's links are in sites.json). Only the title, the day, the
address and the days the announcement's text names are kept; the text itself, which may name people and give
their addresses, is read and not kept, and stays on the municipality's site."""

import datetime
import html
import re
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

from ucestvuj import web
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


def held(title: str) -> bool:
    """Whether the title itself says the debate or the inspection was held. A title that doesn't say so may
    still be news of one: only the municipality's own page tells."""
    return bool(_HELD.search(latin(title).lower()))


_MONTHS_SR = ("januar", "februar", "mart", "april", "maj", "jun", "jul", "avgust", "septemb", "oktob", "novemb", "decemb")
# A day as the announcements write it: "28.10.2026.", "8. децембра 2026. године", and, in a range, without its
# year ("од 12. октобра до 23. новембра 2026."). Some sites' text has spaces inside a number ("2 0 . новембра
# 202 6 ."), so one space is let between the digits. Read in Latin, lower case.
_DATE = re.compile(r"(?<![\d./,:])(?P<d>[0-3]? ?\d) ?\. ?"
                   r"(?:(?P<m>[01]? ?\d) ?\. ?|(?P<name>" + "|".join(_MONTHS_SR) + r")[a-z]{0,3}(?![a-zčćžšđ])\.? ?)"
                   r"(?:(?P<y>20 ?\d ?\d)(?!\d))?")
_NEAR = 12  # how far a day without a year may stand from the dated day that ends its range ("... do ")
AHEAD = 400  # a day further than this after the announcement is not the debate's


def days(text: str, published: str) -> list[str]:
    """The days an announcement's text names, from the day it was published on: the debate, the session, the end
    of the inspection, the deadline for remarks. Which is which only the text says; the days before it (the
    decision's, the session's that adopted the draft) are left out. Nothing without the day of publication,
    and a day without a year counts only as the start of a range whose end has one."""
    if not published or not text:
        return []
    first = datetime.date.fromisoformat(published[:10])
    last = first + datetime.timedelta(days=AHEAD)
    found, after = set(), None  # `after`: the match that follows, as (start, year, month)
    for m in reversed(list(_DATE.finditer(latin(text).lower()))):
        digits = lambda s: int(s.replace(" ", ""))
        month = digits(m["m"]) if m["m"] else _MONTHS_SR.index(m["name"]) + 1
        if m["y"]:
            year = digits(m["y"])
        elif after and after[0] - m.end() <= _NEAR:
            year = after[1] - (month > after[2])  # "од 20. децембра до 15. јануара 2027."
        else:
            after = None
            continue
        after = (m.start(), year, month)
        try:
            day_ = datetime.date(year, month, digits(m["d"]))
        except ValueError:
            continue
        if first <= day_ <= last:
            found.add(day_.isoformat())
    return sorted(found)


def clean(text: str) -> str:
    return " ".join(html.unescape(_TAGS.sub(" ", text or "")).split())


def entry(title: str, url: str, day: str, via: str, text: str = "") -> dict | None:
    """One announcement, or nothing when its title doesn't say it is a debate or an inspection. Of its text only
    the days it names are kept."""
    title = clean(title)
    what = kind(title)
    if not what or not url.startswith("http"):
        return None
    return {"kind": what, "budget": bool(_BUDGET.search(title.lower())), "title": title, "day": day[:10], "url": url,
            "via": via, "days": days(clean(text), day)}


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
        weight = lambda e: (bool(e["day"]), len(e["days"]))
        if f["url"] not in best or weight(f) > weight(best[f["url"]]):
            best[f["url"]] = f
    rows = sorted(best.values(), key=lambda f: (f["day"], f["url"]), reverse=True)
    return [{"code": site["code"], "municipality": site["name"], **f} for f in rows]


def fetch(sites: list[dict], workers: int = 12) -> list[dict]:
    with ThreadPoolExecutor(workers) as pool:
        return [row for rows in pool.map(of_site, sites) for row in rows]
