"""Serbian Cyrillic to Latin, letter by letter (the other way is ambiguous: "nj" is њ in "konj" and нј in
"injekcija"), and a whole page turned without touching its addresses."""

import re

_PAIRS = dict(zip("абвгдђежзијклмнопрстћуфхцчш", "a b v g d đ e ž z i j k l m n o p r s t ć u f h c č š".split()))
_PAIRS.update({"љ": "lj", "њ": "nj", "џ": "dž"})
# Not Serbian, but they turn up in what the sources publish (a soft sign typed for a Latin letter, Roman numerals
# typed as І); without them a Latin page would keep Cyrillic letters. As javni-uvid/zailiprotiv turns them.
_PAIRS.update({"і": "i", "ї": "i", "є": "e", "ґ": "g", "й": "j", "ы": "y", "э": "e", "ё": "e", "ў": "u",
               "ю": "ju", "я": "ja", "щ": "šč", "ъ": "", "ь": ""})
_TAG = re.compile(r"(<[^>]+>)")
_SAID = re.compile(r'\b(content|aria-label|title|alt|placeholder)="([^"]*)"')
CYRILLIC = re.compile("[Ѐ-ӿ]")


def latin(text: str) -> str:
    """Љ, Њ and Џ become Lj, Nj, Dž, or LJ, NJ, DŽ inside a word in capitals."""
    out = []
    for i, ch in enumerate(text):
        low = ch.lower()
        if low not in _PAIRS:
            out.append(ch)
        elif ch == low:
            out.append(_PAIRS[low])
        else:
            nxt = text[i + 1] if i + 1 < len(text) else ""
            prev = text[i - 1] if i else ""
            shout = any(c.isalpha() and c == c.upper() and c != c.lower() for c in (nxt, prev))
            out.append(_PAIRS[low].upper() if shout else _PAIRS[low].capitalize())
    return "".join(out)


def latin_page(page: str) -> str:
    """The page's text and its said attributes in Latin; every address (href, src) as it was, since a
    municipality's address may hold Cyrillic letters."""
    parts = []
    for part in _TAG.split(page):
        if part.startswith("<"):
            parts.append(_SAID.sub(lambda m: f'{m.group(1)}="{latin(m.group(2))}"', part))
        else:
            parts.append(latin(part))
    return "".join(parts)


def text_of(page: str) -> str:
    """What a reader reads on a page: the text between its tags."""
    return "".join(p for p in _TAG.split(page) if not p.startswith("<"))
