"""The cities' and municipalities' own web sites: where a municipality announces its public debates, public
inspections of plans, calls and sittings. There is no common form, so the first reading only finds out what each
site is: whether it answers, what it runs on, whether it has a feed, and which of its first page's links lead to
what a citizen can take part in. One request per site.

The list of sites is javni-uvid/izborna-analiza's (`data/municipal_sites.csv`: the domain of each electoral
commission's e-mail in RIK's address book), copied to `data/municipal_sites.csv`."""

import csv
import html
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ucesce import web

# What a link's words say it leads to. Latin and Cyrillic, without the endings, lower case.
KINDS = {
    "debate": ("javn[aeiou] rasprav", "јавн[аеиоу] расправ", "javne-rasprave", "javna-rasprava"),
    "inspection": ("javni uvid", "јавни увид", "rani javni uvid", "рани јавни увид", "javni-uvid"),
    "consultation": ("konsultacij", "консултациј", "anket", "анкет"),
    "budget": ("budžet", "budzet", "буџет"),
    "call": ("javni poziv", "јавни позив", "konkurs", "конкурс", "javni-pozivi"),
    "assembly": ("sednic", "седниц", "skupštin", "skupstin", "скупштин"),
    "local_community": ("mesn[ae] zajednic", "месн[ае] заједниц", "mesne-zajednice"),
    "information": ("informator", "информатор", "informacije od javnog", "информације од јавног"),
    "gazette": ("službeni list", "sluzbeni list", "службени лист", "službeni glasnik", "службени гласник", "sluzbeni-list"),
    "statute": ("statut", "статут"),
    "plans": ("urbanistič", "урбанистич", "planska dokument", "планска документ", "prostorni plan", "просторни план"),
    "petition": ("peticij", "петициј", "inicijativ", "иницијатив", "predlozi građana", "предлози грађана"),
}
_KIND = {kind: re.compile("|".join(words)) for kind, words in KINDS.items()}
_A = re.compile(r'<a\b[^>]*?\bhref\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', re.S | re.I)
_TAGS = re.compile(r"<[^>]+>")
_FEED = re.compile(r'<link\b[^>]*type=["\']application/(?:rss|atom)\+xml["\'][^>]*>', re.I)
_HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)
_GENERATOR = re.compile(r'<meta\b[^>]*name=["\']generator["\'][^>]*content=["\']([^"\']+)["\']', re.I)


def decode(raw: bytes) -> str:
    for encoding in ("utf-8", "cp1250", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def system(page: str) -> str:
    """What the site runs on, as far as its first page says."""
    low = page.lower()
    generator = _GENERATOR.search(page)
    if "wp-content/" in low or "api.w.org" in low or (generator and "wordpress" in generator.group(1).lower()):
        return "wordpress"
    if "/media/jui/" in low or "joomla" in low:
        return "joomla"
    if "drupal" in low:
        return "drupal"
    return (generator.group(1).split()[0].lower() if generator else "") or "other"


def links(page: str, base: str) -> dict[str, list[str]]:
    """The first page's links by what they lead to: kind -> addresses, each once, in the page's order."""
    found: dict[str, list[str]] = {}
    for href, inner in _A.findall(page):
        words = " ".join(html.unescape(_TAGS.sub(" ", inner)).split()).lower()
        target = urllib.parse.urljoin(base, html.unescape(href.strip()))
        if not target.startswith("http"):
            continue
        hay = words + " " + urllib.parse.unquote(target).lower()
        for kind, pattern in _KIND.items():
            if pattern.search(hay) and target not in found.setdefault(kind, []):
                found[kind].append(target)
    return found


def look(domain: str) -> dict:
    """One site: does it answer, what it runs on, its feed, and its first page's links by kind."""
    for scheme in ("https", "http"):
        url = f"{scheme}://{domain}/"
        try:
            page = decode(web.get(url, timeout=25, wait=0))
        except Exception as error:  # a site that doesn't answer is a finding, not a failure of the run
            reason = type(error).__name__
            continue
        feed = _FEED.search(page)
        feed_url = urllib.parse.urljoin(url, html.unescape(_HREF.search(feed.group(0)).group(1))) if feed and _HREF.search(feed.group(0)) else ""
        return {"answers": scheme, "system": system(page), "feed": feed_url, "links": links(page, url), "size": len(page)}
    return {"answers": "", "system": "", "feed": "", "links": {}, "size": 0, "error": reason}


def survey(sites_csv: Path, workers: int = 12) -> list[dict]:
    """Every municipality's site looked at once, in the list's order."""
    with sites_csv.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("domain")]
    with ThreadPoolExecutor(workers) as pool:
        seen = list(pool.map(lambda r: look(r["domain"]), rows))
    return [{"code": r["municipality_code"], "name": r["name"], "domain": r["domain"], **s} for r, s in zip(rows, seen)]
