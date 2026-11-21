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
    assert 'name="robots" content="noindex"' in home and home.count("<script") == 1 and "site.js?v=" in home
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


def test_a_municipality_says_what_is_read_of_it():
    seen = {"domain": "a.rs", "answers": "https"}
    assert site.state_of("", None, 0) == "нема адресе"
    assert site.state_of("b.rs", seen, 3) == "адреса нова, још није читана"  # the list changed since the last look
    assert site.state_of("a.rs", seen, 3) == "читамо" and site.state_of("a.rs", seen, 0) == "још не умемо"
    assert site.state_of("a.rs", {"domain": "a.rs", "answers": ""}, 0) == "не одговара"


def test_the_first_page_is_one_list_with_what_is_ahead_first(tmp_path):
    out = tmp_path / "s"
    site.build(out, datetime.date(2026, 11, 21))
    home = (out / "cir" / "index.html").read_text(encoding="utf-8")
    cards = home.split('<ol id="lista" class="cards">')[1].split("</ol>")[0].split('<li class="card"')[1:]
    days = [c.split('data-days="')[1].split('"')[0].split() for c in cards]
    nearest = [min((d for d in ds if d >= "2026-11-21"), default="") for ds in days]
    ahead = [n for n, c in zip(nearest, cards) if n and "data-held" not in c]
    assert ahead and nearest[:len(ahead)] == sorted(ahead)  # what is ahead leads, the nearest day first
    senta = next(c for c in cards if "Тиса" in c)
    assert 'data-place="80365"' in senta and 'data-topic="plans"' in senta and "<b>Јавни увид</b> од 30. 10. 2026. до 28. 11. 2026.</li>" in senta
    assert any('data-place="rs"' in c and 'data-kind="state"' in c for c in cards)  # the state's topics are in the same list
    assert any("data-held" in c and "одржано" in c for c in cards)
    # the choice is there for the script and hidden without it; every municipality can be chosen and says what is read of it
    assert '<form id="filter" class="filter" hidden' in home and home.count("<option value=") > 168
    assert 'id="m-80365" hidden' in home and "Зато њених објава овде засад нема" in home


def test_a_row_says_where_what_about_and_when():
    row = {"title": "Јавна расправа о Нацрту одлуке о буџету", "url": "https://a.rs/1", "code": "1", "kind": "debate", "day": "2026-11-01",
           "via": "wordpress posts", "when": [
               {"what": "debate", "from": "2026-11-01", "to": "2026-11-15", "days": 0, "hour": ""},
               {"what": "session", "from": "2026-11-16", "to": "2026-11-16", "days": 0, "hour": "13:00"},
               {"what": "remarks", "from": "", "to": "2026-11-15", "days": 0, "hour": ""},
               {"what": "inspection", "from": "2026-11-01", "to": "", "days": 30, "hour": ""},
               {"what": "", "from": "2026-12-20", "to": "2026-12-20", "days": 0, "hour": ""}]}
    shown = site.item(row, {"1": "Ђурђево"})
    for words in ("<b>Јавна расправа</b> од 1. 11. 2026. до 15. 11. 2026.", "<b>Јавна седница</b> 16. 11. 2026. у 13:00", "<b>Примедбе</b> до 15. 11. 2026.",
                  "<b>Јавни увид</b> од 1. 11. 2026., 30 дана", "<b>У објави</b> 20. 12. 2026."):
        assert f"<li>{words}</li>" in shown, words
    assert 'data-place="1"' in shown and 'data-kind="debate"' in shown and 'data-topic="budget"' in shown and "Буџет</span>" in shown
    # the filters' days: what is named, a start with its length to its last possible day; the unnamed day is not among them
    assert 'data-days="2026-11-01 2026-11-15 2026-11-16 2026-12-01"' in shown
    assert 'data-text="djurdjevo  javna rasprava o nacrtu odluke o budzetu"' in shown and "data-held" not in shown
    bare = site.item({**row, "when": [], "via": "wordpress search", "day": ""}, {"1": "Ада"}, False)
    assert "Објаву читамо само по наслову" in bare and "Без дана објаве" in bare and 'data-days=""' in bare
    assert "data-held" in site.item({**row, "title": "Одржана јавна расправа"}, {"1": "Ада"})


def test_only_the_sites_own_script_may_be_on_a_page():
    own = '<script src="../site.js?v=ab12cd34" defer></script>'
    assert site.check(own, "cyr") == []
    assert site.check(own + "<script>alert(1)</script>", "cyr") and site.check('<script src="https://x.rs/a.js"></script>', "cyr")
    assert site.check(own + '<a onclick="x()">a</a>', "cyr")
