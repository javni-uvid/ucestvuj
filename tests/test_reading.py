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
