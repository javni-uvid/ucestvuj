"""The text of a law, as the Official Gazette's register prints it (principles 2 and 6).

The register's page (pravno-informacioni-sistem.rs) is a script; the script's own calls go to `reg.` + the same
host + `/api/`. `GetLawActTimeline?guid=` lists a law's versions with the day each took effect and
`viewAct/<guid>?lawActId=<version>` is the consolidated text of one version as an HTML page. Both are the page's
own public calls, not a documented API (docs/decisions/data.md, "The text of the laws").

What is kept per article: its number, the heading the register gives it, its paragraphs word for word, and the
amendment notes that stand under it. Nothing is paraphrased.
"""

import html
import re

from ucestvuj import web

API = "https://reg.pravno-informacioni-sistem.rs/api/"
PAGE = "https://pravno-informacioni-sistem.rs/reg/viewAct/"

# The laws the guides rest on: key, the register's guid of the act. More are added when a guide needs them.
LAWS = {
    "access": {"guid": "0b7f7931-f230-45cf-b550-a1495539249d"},  # Law on Free Access to Information of Public Importance
}

# "Члан 12." and, for an article added later, "Члан 28а" (no full stop)
_ARTICLE = re.compile(r"\n[ \t]*Члан[ \t]+(\d+[а-џ]?)\.?[ \t]*\n")
_END = re.compile(r"\n[ \t]*ОДРЕДБЕ КОЈЕ НИСУ УНЕТЕ")
_NOTE = re.compile(r"^\*+\s*Службени гласник[^\n]*$", re.M)


def plain(page: str) -> str:
    """The page as lines of text: no markup, no style, one space between words."""
    page = re.sub(r"(?is)<(script|style).*?</\1>", "", page)
    page = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", page)
    text = html.unescape(re.sub(r"<[^>]+>", "", page)).replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", text)


def _is_heading(paragraph: str) -> bool:
    """A line between two articles that names the next one or the part it opens: not a sentence (no full stop,
    semicolon or colon at its end), or a part's number and name ("II ИСКЉУЧЕЊЕ И ОГРАНИЧЕЊЕ ...")."""
    return bool(re.match(r"[IVX]+ [А-ЯЂЈЉЊЋЏ ,-]{6,}$", paragraph)) or not paragraph.endswith((".", ";", ":", ",", "”", '"'))


def articles(text: str) -> list[dict]:
    """The articles of a consolidated text, in order. The provisions the register leaves out of the consolidated
    text (what its footer lists of earlier amending acts) are not read."""
    end = _END.search(text)
    text = text[:end.start()] if end else text
    parts = _ARTICLE.split(text)
    found = []
    before = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", parts[0])]
    opening = []
    while before and (not before[-1] or _is_heading(before[-1])):  # what stands between the title block and article 1
        opening.insert(0, before.pop())
    heading = " · ".join(h for h in opening if h)
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        notes = [n.lstrip("* ").strip() for n in _NOTE.findall(body)]
        body = _NOTE.sub("", body)
        paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body)]
        paragraphs = [p for p in paragraphs if p]
        next_heading = []
        while paragraphs and _is_heading(paragraphs[-1]):  # these name the next article (or the part)
            next_heading.insert(0, paragraphs.pop())
        found.append({"number": parts[i], "heading": heading, "paragraphs": paragraphs, "notes": notes})
        heading = " · ".join(next_heading)
    return found


def fetch(key: str) -> dict:
    """One law, in its version now in force: the register's text read into articles."""
    guid = LAWS[key]["guid"]
    versions = web.get_json(f"{API}GetLawActTimeline?guid={guid}")
    now = max(versions, key=lambda v: v["versionApplicationDate"])
    page = web.get(f"{API}viewAct/{guid}?lawActId={now['id']}", timeout=60).decode("utf-8-sig")
    text = plain(page)
    head = text[:text.find("Члан")]
    title = re.search(r"ЗАКОН\s+([^\n]+)\n", head)
    gazette = re.search(r"“Службени гласник РС”,.*?\d{4}\.\s*(?:\n|$)", head, re.S)
    return {
        "title": ("Закон " + title.group(1).strip()) if title else "",
        "gazette": re.sub(r"\s+", " ", gazette.group(0)).strip() if gazette else "",
        "in_force_from": now["versionApplicationDate"][:10],
        "url": PAGE + guid,
        "articles": articles(text),
    }
