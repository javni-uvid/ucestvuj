"""Commands. Each reads one source and writes what it found under data/, with a line in data/sources.json
saying where it came from and when."""

import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def save(path: Path, value) -> None:
    """JSON a person can read and git can diff: one entry per line for a list of entries."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, list):
        text = "[\n" + ",\n".join(json.dumps(v, ensure_ascii=False, sort_keys=True) for v in value) + "\n]\n"
    else:
        text = json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def note(name: str, what: dict) -> None:
    """Where a file under data/ came from, and the day it was read."""
    path = DATA / "sources.json"
    sources = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    sources[name] = {**what, "read": datetime.date.today().isoformat()}
    save(path, sources)


def opendata(_args) -> None:
    from ucestvuj import opendata as source
    for name, what in source.fetch(DATA).items():
        note(name, what)
        print(f'{name}: {what["rows"]} rows from "{what["title"]}" (changed {what["modified"]})')


def consultations(_args) -> None:
    from ucestvuj import consultations as source
    found = source.fetch()
    save(DATA / "consultations.json", found["topics"])
    save(DATA / "consultation_institutions.json", found["institutions"])
    topics = found["topics"]
    note("consultations", {"url": source.BASE, "topics": len(topics), "open": sum(t["open"] for t in topics),
                           "local": sum(t["local"] for t in topics),
                           "institutions": len(found["institutions"]),
                           "local_institutions": sum(i["local"] for i in found["institutions"])})
    print(f'consultations: {len(topics)} topics, {sum(t["open"] for t in topics)} open, '
          f'{sum(t["local"] for t in topics)} of municipalities')


def sites_list(_args) -> None:
    from ucestvuj import sites as source
    changed = source.bring(DATA / "municipal_sites.csv")
    for line in changed:
        print("list:", line)
    print(f"list: {len(changed)} changed")


def sites(_args) -> None:
    from ucestvuj import sites as source
    seen = source.survey(DATA / "municipal_sites.csv")
    save(DATA / "sites.json", seen)
    up = [s for s in seen if s["answers"]]
    note("sites", {"list": "javni-uvid/izborna-analiza data/municipal_sites.csv", "sites": len(seen), "answer": len(up)})
    print(f"sites: {len(up)} of {len(seen)} answer")


def announcements(_args) -> None:
    from ucestvuj import announcements as source
    seen = json.loads((DATA / "sites.json").read_text(encoding="utf-8"))
    found = source.fetch(seen)
    save(DATA / "announcements.json", found)
    note("announcements", {"from": "the municipalities' own sites (data/sites.json)", "announcements": len(found),
                           "municipalities": len({f["code"] for f in found})})
    print(f'announcements: {len(found)} from {len({f["code"] for f in found})} municipalities')


def actions(args) -> None:
    from ucestvuj import actions as source
    seen = json.loads((DATA / "sites.json").read_text(encoding="utf-8"))
    path = DATA / "actions.json"
    before = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    found = source.fetch(seen, before, municipalities=not args.quick)
    save(DATA / "actions.json", found)
    by = {s: sum(a["source"] == s for a in found) for s in sorted({a["source"] for a in found})}
    note("actions", {"from": "the blood transfusion institutes, the volunteer service of Novi Sad and the municipalities' own posts",
                     "actions": len(found), "by_source": by})
    print(f"actions: {len(found)} {by}")


def site(args) -> None:
    from ucestvuj import site as source
    wrong = source.build(Path(args.out))
    for w in wrong:
        print("site:", w, file=sys.stderr)
    if wrong:
        raise SystemExit(1)
    print(f"site: {args.out}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="ucestvuj", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    for name, run, about in (
        ("opendata", opendata, "the bodies, the municipalities and local government's tasks, from data.gov.rs"),
        ("consultations", consultations, "every topic on eKonsultacije"),
        ("list", sites_list, "the municipalities' sites: izborna-analiza's list, copied (says what changed)"),
        ("sites", sites, "what each municipality's own site is and links to"),
        ("announcements", announcements, "public debates and inspections the municipalities announce on their sites"),
    ):
        commands.add_parser(name, help=about).set_defaults(run=run)
    quick = commands.add_parser("actions", help="actions to join: blood drives, volunteer shifts, clean-ups and plantings (after `sites`)")
    quick.add_argument("--quick", action="store_true", help="only the institutes' pages and the volunteer service; the municipalities' rows stay")
    quick.set_defaults(run=actions)
    build = commands.add_parser("site", help="build the site from data/ (fails on a page that loads from elsewhere)")
    build.add_argument("--out", default="_site")
    build.set_defaults(run=site)
    args = parser.parse_args()
    args.run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
