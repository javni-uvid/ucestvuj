"""The stylesheet and the pages' frame keep to the design rules (docs/decisions/site.md, "Design rules")."""

import datetime
import re
from pathlib import Path

import ucestvuj
from ucestvuj import site

STATIC = Path(ucestvuj.__file__).parent / "static"
CSS = (STATIC / "site.css").read_text(encoding="utf-8")
FAMILY = (site.DESIGN / "osnova.css").read_text(encoding="utf-8")


def test_letter_sizes_are_the_familys_scale():
    """Rule 1: every size is a step of the one scale (osnova.css), whether set alone or in the shorthand."""
    sizes = {v.strip() for v in re.findall(r"font-size:\s*([^;}]+)", CSS)}
    sizes |= {m for m in re.findall(r"font:\s*(?:\d{3}\s+)?([^/;}\s]+)", CSS)}
    assert sizes and all(re.fullmatch(r"var\(--ju-t-(\d|h1)\)", v) for v in sizes), sizes
    steps = dict(re.findall(r"--ju-t-(\w+):\s*([^;]+);", FAMILY))
    assert steps["3"] == "1rem" and "font: var(--ju-t-3)/1.55 var(--ju-sans)" in CSS  # body text is 16 px


def test_the_site_declares_no_colour_or_font_of_its_own():
    """Rule 2: every colour and both fonts are the family's values; no colour here carries a meaning."""
    assert not re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", CSS)
    used = set(re.findall(r"(?:color|background|border[\w-]*|outline):[^;}]*?var\(--([\w-]+)\)", CSS))
    assert used <= {"ju-bg", "ju-fg", "ju-muted", "ju-line", "ju-card"}, used
    assert "font-family" not in CSS and set(re.findall(r"var\(--(ju-(?:serif|sans))\)", CSS)) == {"ju-serif", "ju-sans"}


def _contrast(a: str, b: str) -> float:
    def lum(h: str) -> float:
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_text_and_controls_have_contrast_in_both_themes():
    """WCAG 2.2 AA from the family's values as this site uses them: ink and grey text on the page and on the
    cards 4.5:1, a form control's edge (the grey) 3:1, in the light theme and both ways to the dark one."""
    tokens = lambda block: dict(re.findall(r"--(ju-(?:bg|fg|muted|line|card)):\s*(#[0-9a-fA-F]{6})", block))
    light = tokens(FAMILY[FAMILY.index(":root {"):FAMILY.index("@media (prefers-color-scheme: dark)")])
    system = tokens(FAMILY[FAMILY.index("@media (prefers-color-scheme: dark)"):FAMILY.index(':root[data-theme="dark"]')])
    chosen = tokens(FAMILY[FAMILY.index(':root[data-theme="dark"]'):FAMILY.index(".ju-bar")])
    assert system == chosen and len(light) == len(system) == 5
    for name, t in (("light", light), ("dark", system)):
        for fg in ("ju-fg", "ju-muted"):
            for bg in ("ju-bg", "ju-card"):
                assert _contrast(t[fg], t[bg]) >= 4.5, (name, fg, bg, round(_contrast(t[fg], t[bg]), 2))
        assert _contrast(t["ju-muted"], t["ju-bg"]) >= 3


def test_keyboard_reach_and_things_to_press():
    """Rules 6 and 8: the keyboard's place is outlined in ink, the first Tab skips to the page, and what is
    pressed is 44 px high."""
    assert re.search(r":focus-visible\s*\{\s*outline:\s*3px solid var\(--ju-fg\)", CSS)
    page = site.frame("index.html", "cyr", "t", "d", "<p>x</p>", "", "v")
    assert '<a class="skip" href="#sadrzaj">' in page and '<main id="sadrzaj">' in page
    for pressed in (".top nav a", ".filter select, .filter input, .filter button", ".filter summary"):
        rule = CSS[CSS.index(pressed + " {"):]
        assert "min-height: 44px" in rule[:rule.index("}")], pressed
    assert "animation" not in CSS and "transition" not in CSS  # nothing moves


def test_every_page_is_whole_without_the_script(tmp_path):
    """Rule 8: the script only filters. The list, each row's days and the way to every municipality are in the
    page itself; what the script shows is hidden until it runs."""
    out = tmp_path / "s"
    site.build(out, datetime.date(2026, 11, 21))
    home = (out / "index.html").read_text(encoding="utf-8")
    assert home.count('<li class="card"') > 20 and "od 30. 10. 2026. do 28. 11. 2026." in home
    assert '<form id="filter" class="filter" hidden' in home and 'class="next" hidden' in home
    assert 'href="opstine.html"' in home and "<noscript" not in home
    js = (STATIC / "site.js").read_text(encoding="utf-8")
    for sends_or_stores in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "document.cookie", "http"):
        assert sends_or_stores not in js, sends_or_stores  # principle 5, and what the pages promise


def test_fonts_are_served_from_the_site():
    """Principle 5: the stylesheets name no other host, and every font file they name is in the family's folder
    with its licence."""
    assert "http" not in CSS + FAMILY
    for name in re.findall(r"url\(fonts/([^)]+)\)", FAMILY):
        assert (site.DESIGN / "fonts" / name).exists(), name
    assert (site.DESIGN / "fonts" / "OFL-Literata.txt").exists()
