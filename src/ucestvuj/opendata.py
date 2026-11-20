"""The institutions' own datasets on data.gov.rs: the bodies a letter can be sent to, the cities and
municipalities, and what local government is responsible for.

Two of the files name people (the bodies' authorised persons and contacts; the mayors, assembly presidents and
heads of administration). The project names no one (AGENTS.md, principle 4): those columns are dropped here, as
the file is read, and never reach `data/`."""

import csv
import hashlib
import io
from pathlib import Path

from ucestvuj import web

API = "https://data.gov.rs/api/1/datasets/?organization={org}&page_size=100"
COMMISSIONER = "58590b21cbe3c816ac018e67"  # Повереник за информације од јавног значаја и заштиту података о личности
MINISTRY = "5f61fe6f7de272429326be60"      # Министарство државне управе и локалне самоуправе

# What is kept of each file: the output's column, and the source's column it comes from. Anything not listed is
# dropped; the columns with a person's name, phone or e-mail are not listed.
BODIES = {
    "name": "Naziv organa", "category": "Kategorija", "class_1": "Prva klasifikacija",
    "class_2": "Druga klasifikacija", "address": "Adresa", "post_code": "Poštanski broj", "seat": "Sedište",
    "web": "Veb adresa",
}
MUNICIPALITIES = {"name": "Назив јединице локалне самоуправе", "address": "Адреса јединице локалне самоуправе"}
TASKS = {
    "area": "ОБЛАСТ", "sub_area": "ПОДОБЛАСТ", "task": "ПОСАО", "legal_basis": "ПРАВНИ ОСНОВ",
    "level": "НИВО ВЛАСТИ", "body": "НАДЛЕЖНИ ОРГАН", "kind": "ВРСТА ПОСЛА",
}


def resource(org: str, title: str, fmt: str = "csv") -> dict:
    """The dataset of `org` whose title contains `title`: its page, its file of `fmt`, when it was last changed."""
    for dataset in web.get_json(API.format(org=org))["data"]:
        if title in dataset["title"]:
            for r in dataset["resources"]:
                if (r.get("format") or "").lower() == fmt:
                    return {"title": dataset["title"].strip(), "page": dataset.get("page", ""), "url": r["url"],
                            "modified": (r.get("last_modified") or dataset.get("last_modified") or "")[:10]}
    raise LookupError(f"no {fmt} resource titled like {title!r} at organization {org}")


def table(raw: bytes) -> list[dict]:
    """A CSV as rows by column name. The delimiter is the one the header uses most (the catalogue uses "|")."""
    text = raw.decode("utf-8-sig")
    head = text.split("\n", 1)[0]
    delimiter = max("|;,\t", key=head.count)
    return list(csv.DictReader(io.StringIO(text), delimiter=delimiter))


def keep(rows: list[dict], columns: dict[str, str]) -> list[dict]:
    """Only the named columns, under the project's names, cells trimmed; rows without a first value, and the
    file's own headings, dropped."""
    missing = [src for src in columns.values() if rows and src not in rows[0]]
    if missing:
        raise KeyError(f"the source no longer has the columns {missing}; it has {list(rows[0])}")
    out = [{name: " ".join((row.get(src) or "").split()) for name, src in columns.items()} for row in rows]
    first = next(iter(columns))
    # A row with a name and nothing else is a heading inside the file ("REPUBLIČKI ORGANI"), not an entry.
    return [r for r in out if r[first] and (len(columns) == 1 or any(v for k, v in r.items() if k != first))]


def write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fetch(data: Path) -> dict:
    """Read the three files and write them to `data/`. Returns what was read, for `data/sources.json`."""
    read = {}
    for name, org, title, columns in (
        ("bodies", COMMISSIONER, "Каталог органа", BODIES),
        ("municipalities", MINISTRY, "Контакт подаци", MUNICIPALITIES),
        ("tasks", MINISTRY, "Изворни и поверени", TASKS),
    ):
        found = resource(org, title)
        raw = web.get(found["url"], timeout=120)
        rows = keep(table(raw), columns)
        write(data / f"{name}.csv", rows)
        read[name] = {**found, "sha256": hashlib.sha256(raw).hexdigest(), "rows": len(rows), "kept": list(columns)}
    return read
