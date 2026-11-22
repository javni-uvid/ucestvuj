"""What is kept of each source, checked on small made-up answers: no test asks a source."""

import pytest

from ucestvuj import actions, announcements, consultations, opendata, sites, when


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


def test_an_announcement_keeps_when_it_is_on_and_not_its_text():
    a = announcements.entry("Јавни позив за јавну расправу", "https://a.rs/1", "2026-11-01T08:00:00", "wordpress posts",
                            "<p>Примедбе на мејл господина Петра Петровића, p@a.rs, до 15.11.2026. године.</p>")
    assert a["when"] == [{"what": "remarks", "from": "", "to": "2026-11-15", "days": 0, "hour": ""}]
    assert "Петр" not in str(a) and "p@a.rs" not in str(a)
    assert announcements.entry("Јавна расправа", "https://a.rs/2", "", "wordpress search")["when"] == []
    # a title that says the period itself is read with the text
    titled = announcements.entry("Јавна расправа о буџету у периоду од 2. до 23. новембра 2026. године", "https://a.rs/3",
                                 "2026-11-02", "feed", "Позивамо грађане.")
    assert [(p["what"], p["from"], p["to"]) for p in titled["when"]] == [("debate", "2026-11-02", "2026-11-23")]


def short(text, published):
    return [(p["what"], p["from"], p["to"], p["days"], p["hour"]) for p in when.read(text, published)]


def test_a_period_keeps_both_its_ends_and_what_it_is_of():
    # Senta, 4 Nov 2026: the inspection began before the announcement and is still one period
    senta = ("Јавни увид одржаће се у згради Градске куће у Сенти, Главни трг бр. 1, канцеларија бр. 23 (I спрат), у трајању "
             "од 30 дана, од 30. октобра до 28. новембра 2026. године, сваког радног дана од 10 до 13 часова")
    assert short(senta, "2026-11-04") == [("inspection", "2026-10-30", "2026-11-28", 0, "")]
    # the session that adopted the draft is over; the inspection and the session to come are named apart
    beograd = ("на седници одржаној 22.09.2026. године, утврдила Нацрт. 1. ЈАВНИ УВИД обавиће се од 12. октобра до "
               "23. новембра 2026. године, сваког радног дана од 9 до 18 часова. 2. ЈАВНА СЕДНИЦА Комисије за планове, "
               "одржаће се 8. децембра 2026. године у 13 часова (сала на 20. спрату). („Службени гласник РС”, бр. 72/09, 9/20)")
    assert short(beograd, "2026-10-29") == [("inspection", "2026-10-12", "2026-11-23", 0, ""), ("session", "2026-12-08", "2026-12-08", 0, "13:00")]
    vlasotince = ("Јавна расправа о Нацрту одлуке одржаће се од 28.10.2026. до 11.11.2026. године. Примедбе и сугестије "
                  "достављају се поштом. У оквиру спровођења јавне расправе одржаће се јавна седница 12.11.2026. године у сали "
                  "Скупштине са почетком у 11,00 часова")
    assert short(vlasotince, "2026-10-28") == [("debate", "2026-10-28", "2026-11-11", 0, ""), ("session", "2026-11-12", "2026-11-12", 0, "")]
    assert short("Javna rasprava traje od 20. decembra do 15. januara 2027. godine", "2026-12-18") == [("debate", "2026-12-20", "2027-01-15", 0, "")]
    assert short("Јавна расправа ће трајати почев од дана 2 0 . новембра 202 6 . године до дана 4 . децембра 202 6. године",
                 "2026-11-20") == [("debate", "2026-11-20", "2026-12-04", 0, "")]


def test_an_end_a_start_and_a_day_alone_are_told_apart():
    assert short("Јавни увид траје до 1. децембра 2026. године, до када се могу доставити примедбе", "2026-11-20") == [
        ("inspection", "", "2026-12-01", 0, "")]
    # a length is kept as the text gives it; the last day is not counted out
    assert short("Јавни увид у Нацрт Плана, одржаће се у трајању од 3 0 дана и то почев од 30 .10.2026 . Наведени плански документ",
                 "2026-10-30") == [("inspection", "2026-10-30", "", 30, "")]
    assert short("биће представљен на Округлом столу, који ће се одржати у среду 30.11.2026. године у Сечњу, у сали у 12:00 часова",
                 "2026-11-03") == [("meeting", "2026-11-30", "2026-11-30", 0, "")]
    assert short("Отворени састанак ће се одржати дана 28.10.2026. године у 10 часова. Одлука се примењује од 1.1.2027.", "2026-10-22") == [
        ("meeting", "2026-10-28", "2026-10-28", 0, "10:00")]  # a bare start nothing names may be anything: not kept
    # the days of a list are of one thing; a period's end said again is said once; remarks are their own
    assert short("јавне седнице Комисије за јавни увид одржати 27.08.2026., 28.08.2026. и 29.08.2026. године у амфитеатру",
                 "2026-08-01") == [("session", f"2026-08-{d}", f"2026-08-{d}", 0, "") for d in (27, 28, 29)]
    assert short("Јавна расправа спровешће се од 2. новембра 2026. године до 23. новембра 2026. године. Предлози у току трајања "
                 "јавне расправе, закључно са 23. новембром 2026. године. Примедбе се достављају до 23.11.2026. године.",
                 "2026-11-02") == [("debate", "2026-11-02", "2026-11-23", 0, ""), ("remarks", "", "2026-11-23", 0, "")]
    assert short("Седница одбора биће 5.11.2026. године у 10 часова", "2026-11-01") == [("", "2026-11-05", "2026-11-05", 0, "10:00")]
    # a day without a year is not guessed; an amount, a time and a law's number are not days; a wrong day is none
    assert short("трајала је од 28.октобра до 11.новембра, у 10:00, износ 1.250.000,00, члана 4., 7. и 8. Одлуке, 31.11.2026.", "2026-10-28") == []
    assert short("Јавни увид траје до 1. децембра 2026. године", "") == [] and short("", "2026-11-01") == []
    assert short("рок је 1.12.2029.", "2026-11-01") == []  # too far ahead to be this announcement's


def test_what_is_ahead_is_the_nearest_day_still_to_come():
    period = {"what": "inspection", "from": "2026-10-30", "to": "2026-11-28", "days": 0, "hour": ""}
    session = {"what": "session", "from": "2026-12-08", "to": "2026-12-08", "days": 0, "hour": "13:00"}
    started = {"what": "inspection", "from": "2026-10-30", "to": "", "days": 30, "hour": ""}
    assert when.ahead([period, session], "2026-11-21") == "2026-11-28" and when.ahead([period, session], "2026-11-29") == "2026-12-08"
    assert when.ahead([period], "2026-11-29") == "" and when.ahead([], "2026-11-21") == ""
    assert when.ahead([started], "2026-11-21") == "2026-11-29" and when.ahead([started], "2026-11-30") == ""
    assert when.ahead([{**session, "what": ""}], "2026-11-21") == ""  # a day nothing names is shown, not counted


def test_a_title_says_what_the_announcement_is_about():
    for title, about in (("ЈАВНИ ПОЗИВ ЗА УЧЕШЋЕ У ЈАВНОЈ РАСПРАВИ О НАЦРТУ ОДЛУКЕ О БУЏЕТУ", "budget"),
                         ("Javna rasprava o drugom rebalansu budzeta", "budget"),
                         ("Јавна расправа о Нацрту одлуке о локалним комуналним таксама", "taxes"),
                         ("Јавни увид у Нацрт ПДР соларне електране и Извештај о стратешкој процени утицаја на животну средину", "plans"),
                         ("Рани јавни увид поводом израде Плана генералне регулације", "plans"),
                         ("Јавни увид Студије о процени утицаја на животну средину пројекта", "environment"),
                         ("Јавна расправа о Локалном акционом плану за младе", "development"),
                         ("Јавна расправа", "other")):
        assert announcements.topic(title) == about, title


def test_a_blood_drive_is_read_from_the_calendar_links_of_the_institute_of_vojvodina():
    page = ('<a href="https://calendar.google.com/calendar/render?action=TEMPLATE&#038;text=Dobrovoljno%20davanje%20krvi%20%E2%80%94%20Ruma'
            '&#038;dates=20261120T080000/20261120T120000&#038;ctz=Europe/Belgrade&#038;location=Ruma%2C%20Kulturni%20centar">+</a>')
    [drive] = actions.transfusion_vojvodina(page)
    assert (drive["kind"], drive["place"], drive["venue"], drive["start"], drive["time"]) == ("blood", "Ruma", "Kulturni centar", "2026-11-20", "8:00–12:00")


def test_the_institute_of_serbia_lists_a_card_a_day_and_a_closed_action_is_left_out():
    page = ('<!-- KARTICA DANA --><h4><strong>Недеља, </strong> 22. новембар 2026.</h4><div class="card__title">'
            '<img src="images/icondrop.svg" width="24px" alt="x"/>&nbsp;<strong> Шабац, </strong> Рибари <b> 9.30-13ч </b><br/>'
            '<img src="images/upozorenje.svg" width="24px" alt="x"/>&nbsp;<strong> Нови Београд, </strong> Comtrade <b> 09-13ч </b><br/>'
            '</div><!-- KRAJ KARTICE DANA -->')
    [drive] = actions.transfusion_serbia(page)
    assert (drive["place"], drive["venue"], drive["start"], drive["time"]) == ("Шабац", "Рибари", "2026-11-22", "9:30–13:00")


def test_a_volunteer_position_keeps_its_days_and_never_the_hosts_contact():
    post = {"link": "https://nvs.rs/volontiraj/x/", "title": {"rendered": "OBRT fest &#8211; razmena"},
            "meta": {"_nvs_event_starts": "2026 11 29", "_nvs_event_ends": "2026 11 29", "_nvs_location": "OC OPENS",
                     "_nvs_application_deadline": "2026 11 27", "_nvs_duration_info": "Од 14.00 до 20.00 часова - једна смена", "_nvs_contact_phone": "0692019016", "_nvs_contact_email": "x@gmail.com"}}
    [position] = actions.volunteer_service([post, {"link": "https://nvs.rs/volontiraj/y/", "title": {"rendered": "bez dana"}, "meta": {}}])
    assert (position["start"], position["deadline"], position["venue"], position["title"], position["time"]) == ("2026-11-29", "2026-11-27", "OC OPENS", "OBRT fest – razmena", "14:00–20:00")
    assert actions._hours("Догађај ће трајати од 11 до 16 часова. Уколико број волонтера") == "11:00–16:00" and actions._hours("jedna smena") == ""
    assert "0692019016" not in str(position) and "gmail" not in str(position)
