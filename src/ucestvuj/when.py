"""When what an announcement calls to is on, read from its text: the period of a debate or an inspection, the day
and hour of a session, the last day for remarks.

A text is read in four steps, each by words and none by guessing:

1. every day written whole is found ("28.10.2026.", "8. децембра 2026. године"); a day without its year counts
   only as the start of a range whose end has one ("од 12. октобра до 23. новембра 2026.", "од 2. до 23.
   новембра 2026.");
2. two days joined by "до" are one period; a day after "до" or "закључно са" is an end, a day after "од" or
   "почев од" a start (with "у трајању од 30 дана" beside it, a start and a length: the end is not counted out);
3. a day alone may have its hour ("у 13 часова");
4. each gets the name of what the words just before it speak of (a public inspection, a debate, a session, a
   meeting, remarks), or none; a period or a day with no name is kept as "in the announcement", a bare start or
   end with no name is not, and what a period of the same thing already says is not said twice.

What ended before the announcement was published is left out: the session that adopted the draft, the decision's
day. Only these few fields are kept; the text itself, which may name people, is not."""

import datetime
import re

from ucestvuj.translit import latin

MONTHS = ("januar", "februar", "mart", "april", "maj", "jun", "jul", "avgust", "septemb", "oktob", "novemb", "decemb")
# One space is let inside a number: some sites' text has them ("2 0 . новембра 202 6 .").
_DATE = re.compile(r"(?<![\d./,:])(?P<d>[0-3]? ?\d) ?\. ?"
                   r"(?:(?P<m>[01]? ?\d) ?\. ?|(?P<name>" + "|".join(MONTHS) + r")[a-z]{0,3}(?![a-zčćžšđ])\.? ?)"
                   r"(?:(?P<y>20 ?\d ?\d)(?!\d))?")
_YEAR_WORD = r"(?:\.?\s*(?:godine|god\b\.?|g\.))?"
# Between the two days of a period: "... 2026. године до ...", "... – ...".
_TO = re.compile(r"^[\s.,]*" + _YEAR_WORD + r"[\s.,]*(?:pa\s+)?(?:do|–|—|-|zaključno\s+sa)\s*(?:dana\s*)?$")
# Just before a day that ends its period ("од 2. до 23. новембра"): the period's first day, the number alone.
_FIRST = re.compile(r"(?<![\d./,:])([0-3]?\d)\s?\.\s*(?:do|–|—|-)\s*$")
_AND = re.compile(r"^[\s.,]*" + _YEAR_WORD + r"[\s.,]*(?:i\s+)?$")  # between the days of a list
_END = re.compile(r"(?:\bdo|zaključno\s+sa|najkasnije)\s*(?:dana\s*)?$")
_START = re.compile(r"(?:\bod|počev|počinje|počev\s+od)\s*(?:dana\s*)?$")
_LENGTH = re.compile(r"u\s+trajanju\s+od\s+(\d ?\d?)\s*(?:\([a-zčćžšđ]+\)\s*)?d\s?ana")
_HOUR = re.compile(r"^[\s.,]*" + _YEAR_WORD + r"[\s.,]*(?:\([a-zčćžšđ]+\)[\s,]*)?(?:,?\s*sa\s+početkom\s*)?(?:u|od)\s+"
                   r"([0-2]?\d)(?:\s?[:.,]\s?([0-5]\d))?\s*(?:časova|čas\b|sati|sata|h\b)")
# What the words before a day speak of; the nearest to the day wins.
CUES = (
    ("early_inspection", re.compile(r"ran\w+\s+javn\w+\s+uvid")),
    ("inspection", re.compile(r"javn\w+\s+uvid|izla\w+\s+na\s+javni\s+uvid")),
    ("debate", re.compile(r"javn\w+\s+rasprav")),
    ("session", re.compile(r"javn\w+\s+sednic")),
    ("meeting", re.compile(r"okrugl\w+\s+sto|otvoren\w+\s+sastan|javn\w+\s+prezentacij|javn\w+\s+tribin|javn\w+\s+slušanj")),
    ("remarks", re.compile(r"primedb|sugestij")),
)
# A body named after what it runs is not that thing: "јавна седница Комисије за јавни увид" is a session.
_BODY = re.compile(r"komisij\w+\s+za\s+(?:\w+\s+)?javn\w+\s+(?:uvid|rasprav)\w*")
# Just before a day that is not the announcement's own: the day a newspaper printed the notice ("оглас, Вечерње
# новости од 06.08.2024."), or a day that the announcement says was changed ("уместо како је раније било објављено
# у среду 15. априла"). Read in Latin, lower case, in the last words before the day.
_NOT_OURS = re.compile(r"novosti|ve[cč]ernj|dnevn\w+\s+list|umesto|ranije|prethodno\s+(?:bilo\s+)?objavljen")
_NEAR = 12    # how far a day without a year may stand from the dated day that ends its range
_BEFORE = 260  # how far back the words that name a day are looked for
AHEAD = 400    # a day further than this after the announcement is not this announcement's
MOST = 8       # an announcement with more periods than this is a schedule; the rest is in its text


def _number(text: str) -> int:
    return int(text.replace(" ", ""))


def _days(text: str) -> list[tuple[int, int, datetime.date]]:
    """Every day the text names whole, as (where it starts, where it ends, the day), in the text's order."""
    found, after = [], None  # `after`: the match that follows, as (start, year, month)
    for m in reversed(list(_DATE.finditer(text))):
        month = _number(m["m"]) if m["m"] else MONTHS.index(m["name"]) + 1
        if m["y"]:
            year = _number(m["y"])
        elif after and after[0] - m.end() <= _NEAR:
            year = after[1] - (month > after[2])  # "од 20. децембра до 15. јануара 2027."
        else:
            after = None
            continue
        after = (m.start(), year, month)
        try:
            found.append((m.start(), m.end(), datetime.date(year, month, _number(m["d"]))))
        except ValueError:
            after = None
    return found[::-1]


def _what(before: str) -> str:
    """What the words before a day speak of: the cue nearest to the day."""
    best, at = "", -1
    before = _BODY.sub(lambda m: " " * len(m.group()), before)
    for name, pattern in CUES:
        for m in pattern.finditer(before):
            if m.start() > at or (m.start() == at and name == "early_inspection"):
                best, at = name, m.start()
    # "рани јавни увид" also reads as "јавни увид" a word later: the longer name is the one meant
    early = CUES[0][1].search(before[max(0, at - 12):]) if best == "inspection" else None
    return "early_inspection" if early else best


def read(text: str, published: str) -> list[dict]:
    """The periods and days a text names, in its order: {"what", "from", "to", "days", "hour"}. A period has
    both ends; a day alone has the same day in both; an end has no "from", a start no "to" (and "days" when the
    text says how long). Nothing without the day of publication, which tells what was over before it."""
    if not published or not text:
        return []
    text = latin(text).lower()
    first = datetime.date.fromisoformat(published[:10])
    last = first + datetime.timedelta(days=AHEAD)
    days = _days(text)
    out, i, cut, listed = [], 0, 0, ""
    while i < len(days):
        start, end, day = days[i]
        before = text[max(cut, start - _BEFORE):start]
        if _NOT_OURS.search(before[-70:]):
            i, cut = i + 1, end
            continue
        item = {"what": _what(before), "from": "", "to": "", "days": 0, "hour": ""}
        if i + 1 < len(days) and _TO.match(text[end:days[i + 1][0]]):
            start2, end2, day2 = days[i + 1]
            item["from"], item["to"], closes, i = day, day2, end2, i + 1
        elif (alone := _FIRST.search(before)) and 1 <= int(alone.group(1)) < day.day:
            item["from"], item["to"], closes = day.replace(day=int(alone.group(1))), day, end
        elif _END.search(before):
            item["to"], closes = day, end
        elif _START.search(before):
            length = _LENGTH.search(before[-90:]) or _LENGTH.match(text[end:end + 60].lstrip(" .,"))
            item["from"], item["days"], closes = day, (_number(length.group(1)) if length else 0), end
        else:
            hour = _HOUR.match(text[end:end + 70])
            item["from"], item["to"], closes = day, day, end
            if hour and int(hour.group(1)) < 24:
                item["hour"] = f"{int(hour.group(1))}:{hour.group(2) or '00'}"
        if not item["what"] and listed and _AND.match(text[cut:start]):
            item["what"] = listed  # "27.08.2025., 28.08.2025. и 29.08.2025.": the days of one thing
        i, cut, listed = i + 1, closes, item["what"]
        # over before the announcement, or not this announcement's at all
        until = item["to"] or item["from"] + datetime.timedelta(days=item["days"])
        if until < first or (item["from"] or item["to"]) > last or (item["from"] and item["to"] and item["from"] > item["to"]):
            continue
        # a start or an end the words don't name is as likely the day a decision takes effect as anything
        if not item["what"] and not (item["from"] and item["to"]):
            continue
        item["from"], item["to"] = (d.isoformat() if d else "" for d in (item["from"], item["to"]))
        if item not in out:
            out.append(item)
    return [p for p in out if not _said(p, out)][:MOST]


def _said(item: dict, items: list[dict]) -> bool:
    """Whether a period of the same thing already says this: its end again ("закључно са 23. новембром"), or
    its first day alone. A day nothing names is also said by any item that has it."""
    if item["from"] and item["to"] and item["from"] != item["to"]:
        return False
    day = item["to"] or item["from"]
    return any(other is not item and (other["what"] == item["what"] or not item["what"]) and other["from"] != other["to"]
               and other["from"] and other["to"] and day in (other["from"], other["to"]) and not item["hour"] for other in items)


def until(item: dict) -> str:
    """The last day an item may still be under way: its end, or its start and the length the text gives."""
    if item["to"]:
        return item["to"]
    return (datetime.date.fromisoformat(item["from"]) + datetime.timedelta(days=item["days"])).isoformat()


def ahead(items: list[dict], today: str) -> str:
    """The nearest day, today or later, on which something an announcement names starts, is on or ends; nothing
    when all of it is over. A day the words don't name is shown and not counted: it may be anything."""
    days = [d for item in items if item["what"] for d in (item["from"], until(item)) if d and d >= today]
    return min(days, default="")
