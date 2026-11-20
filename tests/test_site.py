"""The site built from the data in the repository: no source is asked."""

import datetime

from ucestvuj import site
from ucestvuj.translit import CYRILLIC, latin, latin_page, text_of


def test_the_site_builds_and_its_check_passes(tmp_path):
    out = tmp_path / "s"
    assert site.build(out, datetime.date(2026, 11, 21)) == []
    for page in ("index.html", "opstine.html", "drzava.html", "o-projektu.html"):
        assert (out / page).is_file() and (out / "cir" / page).is_file()
    home = (out / "index.html").read_text(encoding="utf-8")
    assert 'name="robots" content="noindex"' in home and "<script" not in home
    assert 'href="cir/index.html"' in home and 'href="https://zailiprotiv.rs/"' in home


def test_a_title_that_names_an_applicant_is_not_shown():
    named = {"title": "Јавни увид у студију пројекта инвеститора Петра Петровића из Села"}
    official = {"title": "Градоначелник Петровић на јавној расправи о буџету"}
    assert site.shown_title(named) is None
    assert site.shown_title(official) == official["title"]  # a public official, as the municipality wrote it


def test_municipalities_are_in_the_serbian_alphabet_by_their_own_name():
    names = ["Град Шабац", "Ћуприја", "Град Чачак", "Ада", "Љиг", "Градска општина Звездара", "Лесковац"]
    assert sorted(names, key=site.azbuka) == ["Ада", "Градска општина Звездара", "Лесковац", "Љиг", "Ћуприја", "Град Чачак", "Град Шабац"]


def test_the_latin_page_keeps_its_addresses_and_turns_its_words():
    page = '<a href="https://општина.рс/јавни-увид" title="Јавни увид">Јавни увид ЉУБОВИЈА</a>'
    turned = latin_page(page)
    assert 'href="https://општина.рс/јавни-увид"' in turned and 'title="Javni uvid"' in turned
    assert "Javni uvid LJUBOVIJA" in turned and not CYRILLIC.search(text_of(turned))
    assert latin("Љиг и ДЕТАЛЬНЕ") == "Ljig i DETALNE"
