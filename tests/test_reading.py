"""What is kept of each source, checked on small made-up answers: no test asks a source."""

import pytest

from ucestvuj import announcements, consultations, opendata, sites


def test_the_columns_that_name_people_never_reach_the_data():
    raw = ("Br.|Naziv organa|Kategorija|Prva klasifikacija|Druga klasifikacija|Adresa|Poštanski broj|Sedište|Veb adresa|Kontakt|Ovlašćena lica\n"
           "|REPUBLIČKI ORGANI|||||||||\n"
           "1|Opštinska uprava Ada|Opštine|Uprava||Trg oslobođenja 1|24430|Ada|www.ada.org.rs|024/1 x@ada.rs|Neko Neki\n").encode("utf-8-sig")
    rows = opendata.keep(opendata.table(raw), opendata.BODIES)
    assert rows == [{"name": "Opštinska uprava Ada", "category": "Opštine", "class_1": "Uprava", "class_2": "",
                     "address": "Trg oslobođenja 1", "post_code": "24430", "seat": "Ada", "web": "www.ada.org.rs"}]
    assert "Neko" not in str(rows) and "x@ada.rs" not in str(rows)
    assert not {"Kontakt", "Ovlašćena lica"} & set(opendata.BODIES.values())
    assert set(opendata.MUNICIPALITIES) == {"name", "address"}  # the mayors' and presidents' columns are not taken


def test_a_source_that_changed_its_columns_stops_the_reading():
    with pytest.raises(KeyError):
        opendata.keep([{"Naziv": "x"}], opendata.BODIES)


def test_a_topic_keeps_its_page_and_says_whether_it_is_open_and_local():
    raw = {"id": 7, "nameOfTopic": " Нацрт  закона ", "institutionName": "Министарство", "documentType": "Пропис",
           "fieldOfInterestName": "Развој ", "creationDate": "2026-11-06T13:25:59.000+00:00",
           "updatedAt": "2026-11-07T00:00:00.000+00:00", "currentPhaseName": "Јавна расправа", "currentPhaseId": 4,
           "phaseCreationDate": "2026-11-05T23:00:00.000+00:00", "activeMethodNames": "Обавештење: а; Прикупљање коментара: б",
           "hasActiveMethod": True, "endProcess": False, "jls": False}
    topic = consultations.topic(raw)
    assert topic["title"] == "Нацрт закона" and topic["open"] and not topic["local"]
    assert topic["url"] == "https://ekonsultacije.gov.rs/topicOfDiscussionPage/7/4"
    assert topic["active"] == ["Обавештење: а", "Прикупљање коментара: б"] and topic["created"] == "2026-11-06"
    with pytest.raises(KeyError):
        consultations.topic({"id": 1})


def test_a_sites_links_are_sorted_by_what_they_lead_to_in_both_scripts():
    page = ('<a href="/javne-rasprave/">Јавне расправе</a> <a href="/x">Javni uvid u nacrt plana</a>'
            '<a href="/b">Буџет</a> <a href="#top">Vrh</a> <a href="/vesti">Vesti</a>'
            '<meta name="generator" content="WordPress 6.5">')
    found = sites.links(page, "https://primer.rs/")
    assert found["debate"] == ["https://primer.rs/javne-rasprave/"]
    assert found["inspection"] == ["https://primer.rs/x"] and found["budget"] == ["https://primer.rs/b"]
    assert "https://primer.rs/vesti" not in str(found) and sites.system(page) == "wordpress"


def test_an_announcement_is_kept_only_when_its_title_says_what_it_is():
    early = announcements.entry("Рани јавни увид у план", "https://a.rs/1", "2026-11-19T10:00:00", "feed")
    assert early["kind"] == "early_inspection" and early["day"] == "2026-11-19" and not early["budget"]
    debate = announcements.entry("Javna rasprava o nacrtu odluke o <b>budžetu</b>", "https://a.rs/2", "", "wordpress search")
    assert debate["kind"] == "debate" and debate["budget"] and debate["title"] == "Javna rasprava o nacrtu odluke o budžetu"
    assert announcements.entry("Asfaltiranje ulice", "https://a.rs/3", "2026-01-01", "feed") is None
    assert announcements.day("Thu, 19 Nov 2026 10:00:00 +0000") == "2026-11-19"
    assert announcements.day("2026-11-19T10:00:00Z") == "2026-11-19" and announcements.day("juče") == ""


def test_a_title_says_when_the_debate_was_held():
    for title in ("Одржана јавна расправа о нацрту буџета", "ИЗВЕШТАЈ О СПРОВЕДЕНОЈ ЈАВНОЈ РАСПРАВИ О НАЦРТУ ОДЛУКЕ",
                  "Odrzana javna rasprava", "Извештај са јавне расправе", "Извештај о обављеном раном јавном увиду"):
        assert announcements.held(title), title
    for title in ("ЈАВНИ ПОЗИВ ЗА УЧЕШЋЕ У ЈАВНОЈ РАСПРАВИ О НАЦРТУ ОДЛУКЕ О БУЏЕТУ", "Јавна расправа",
                  "Обавештење о терминима одржавања јавне седнице комисије за јавни увид",
                  "Оглас за јавни увид у Нацрт плана и Извештај о стратешкој процени утицаја плана на животну средину"):
        assert not announcements.held(title), title


def test_a_new_copy_of_the_list_says_what_it_changed():
    row = lambda code, name, domain: {"municipality_code": code, "name": name, "domain": domain}
    old = [row("1", "Ада", "ada.org.rs"), row("2", "Ариље", ""), row("3", "Бор", "bor.rs"), row("4", "Стара", "s.rs")]
    new = [row("1", "Ада", "ada.org.rs"), row("2", "Ариље", "arilje.org.rs"), row("3", "Бор", ""), row("5", "Нова", "n.rs")]
    assert sites.changes(old, new) == ["Ариље: no address -> arilje.org.rs", "Бор: bor.rs -> no address",
                                       "Нова: added, n.rs", "Стара: left out"]
    assert sites.table('municipality_code,name,domain,note\n1,Ада,ada.org.rs,"a, b"\n')[0]["note"] == "a, b"


def test_the_days_an_announcement_names_are_read_from_its_text():
    days = announcements.days
    # the session that adopted the draft is before the announcement; a range's first day takes its end's year
    text = ("на седници одржаној 22.09.2026. године, утврдила Нацрт. 1. ЈАВНИ УВИД обавиће се од 12. октобра до "
            "23. новембра 2026. године, сваког радног дана од 9 до 18 часова. 2. ЈАВНА СЕДНИЦА одржаће се "
            "8. децембра 2026. године у 13 часова (сала на 20. спрату). Закон („Службени гласник РС”, бр. 72/09, 9/20)")
    assert days(text, "2026-10-29") == ["2026-11-23", "2026-12-08"]
    assert days("одржаће се од 28.10.2026. до 11.11.2026. године, а седница 12.11.2026. године у 11,00 часова",
                "2026-10-28") == ["2026-10-28", "2026-11-11", "2026-11-12"]
    assert days("Javna rasprava traje od 20. decembra do 15. januara 2027. godine", "2026-12-18") == ["2026-12-20", "2027-01-15"]
    assert days("почев од дана 2 0 . новембра 202 6 . године до дана 4 . децембра 202 6. године", "2026-11-20") == ["2026-11-20", "2026-12-04"]
    # a day without a year is not guessed; an amount, a time and a law's number are not days
    assert days("трајала је од 28.октобра до 11.новембра, у 10:00, износ 1.250.000,00, члана 4., 7. и 8. Одлуке, 31.11.2026.", "2026-10-28") == []
    assert days("Јавни увид траје до 1. децембра 2026. године", "") == [] and days("", "2026-11-01") == []
    assert days("рок је 1.12.2029.", "2026-11-01") == []  # too far ahead to be this announcement's


def test_an_announcement_keeps_the_days_of_its_text_and_not_the_text():
    a = announcements.entry("Јавни позив за јавну расправу", "https://a.rs/1", "2026-11-01T08:00:00", "wordpress posts",
                            "<p>Примедбе на мејл господина Петра Петровића, p@a.rs, до 15.11.2026. године.</p>")
    assert a["days"] == ["2026-11-15"] and "Петр" not in str(a) and "p@a.rs" not in str(a)
    assert announcements.entry("Јавна расправа", "https://a.rs/2", "", "wordpress search")["days"] == []
