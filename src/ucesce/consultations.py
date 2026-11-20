"""eKonsultacije (ekonsultacije.gov.rs): the state's portal of consultations and public debates.

The portal's own public page lists the topics by asking its server with a filter; this asks the same way, for
every topic, open and finished, of the republic's bodies and of cities and municipalities. The address is not
documented, so a change of the portal can break this: `fetch` fails loudly when an answer has not the fields it
keeps. Read on 20 Nov 2026: 675 topics of the republic's bodies (181 open), and 4 of municipalities, none open,
although 148 municipalities are registered there. The portal is the source for what the republic consults on,
and not for what a municipality does."""

from ucesce import web

BASE = "https://ekonsultacije.gov.rs"
TOPICS = BASE + "/api/topicOfDiscussion/findAllFillteredTopicsOfDiscussionAnonUser"
INSTITUTIONS = BASE + "/api/institution/findAllActiveWithoutSuperAdminInstitution"
PAGE = 100
KEPT = ("id", "nameOfTopic", "institutionName", "documentType", "fieldOfInterestName", "creationDate", "updatedAt",
        "currentPhaseName", "currentPhaseId", "phaseCreationDate", "activeMethodNames", "hasActiveMethod",
        "endProcess", "jls")


def topic(raw: dict) -> dict:
    """One topic as the project keeps it: the portal's fields under plain names, and the topic's own page."""
    missing = [k for k in KEPT if k not in raw]
    if missing:
        raise KeyError(f"eKonsultacije's answer has no {missing}; it has {sorted(raw)}")
    return {
        "id": raw["id"],
        "title": " ".join(raw["nameOfTopic"].split()),
        "institution": raw["institutionName"].strip(),
        "local": bool(raw["jls"]),
        "document": raw["documentType"],
        "field": (raw["fieldOfInterestName"] or "").strip(),
        "phase": raw["currentPhaseName"],
        "phase_since": (raw["phaseCreationDate"] or "")[:10],
        "open": not raw["endProcess"],
        "active": [m.strip() for m in (raw["activeMethodNames"] or "").split(";") if m.strip()],
        "created": (raw["creationDate"] or "")[:10],
        "updated": (raw["updatedAt"] or "")[:10],
        "url": f'{BASE}/topicOfDiscussionPage/{raw["id"]}/{raw["currentPhaseId"]}',
    }


def fetch() -> dict:
    """Every topic on the portal, by id, and the institutions registered there."""
    topics = {}
    for ended in (False, True):
        for local in (False, True):
            page, got = 0, 0  # "start" is the number of the page, not of the first row (found by asking)
            while True:
                answer = web.post_json(TOPICS, {
                    "start": page, "size": PAGE, "globalFilter": "",
                    "filters": [{"id": "endProcess", "value": ended}, {"id": "isJLS", "value": local}],
                    "sorting": [{"id": "updatedAt", "desc": True}],
                })
                for raw in answer["content"]:
                    topics[raw["id"]] = topic(raw)
                got += len(answer["content"])
                page += 1
                if answer["last"] or not answer["content"]:
                    break
            if got != answer["totalElements"]:  # a change of the portal's paging must not pass for fewer topics
                raise ValueError(f"eKonsultacije says {answer['totalElements']} topics (ended={ended}, local={local}), read {got}")
    institutions = sorted(
        ({"name": i["institutionName"].strip(), "local": bool(i["jls"])} for i in web.get_json(INSTITUTIONS)),
        key=lambda i: (i["local"], i["name"]),
    )
    return {"topics": [topics[k] for k in sorted(topics)], "institutions": institutions}
