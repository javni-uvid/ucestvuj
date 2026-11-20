"""Asking a source: little, slowly, and saying who asks (osnova/work.md, "The outside")."""

import json
import time
import urllib.error
import urllib.request

# The form well-behaved robots use: some servers answer nothing to an agent that does not begin this way
# (ekonsultacije.gov.rs, 20 Nov 2026: an empty answer to a plain name). It still says who asks and where to find us.
AGENT = "Mozilla/5.0 (compatible; javni-uvid-ucesce/0.1; +https://github.com/javni-uvid)"
_last: dict[str, float] = {}


def get(url: str, *, data: bytes | None = None, headers: dict | None = None, timeout: int = 40, wait: float = 1.0) -> bytes:
    """The body at `url`. Waits `wait` seconds between two requests to the same host."""
    host = urllib.request.urlparse(url).netloc
    since = time.monotonic() - _last.get(host, 0)
    if since < wait:
        time.sleep(wait - since)
    request = urllib.request.Request(url, data=data, headers={"User-Agent": AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as answer:
            return answer.read()
    finally:
        _last[host] = time.monotonic()


def get_json(url: str, **kw):
    return json.loads(get(url, **kw).decode("utf-8-sig"))


def post_json(url: str, body: dict, **kw):
    """A read that the source's own public page makes as a POST (a filter in the body)."""
    raw = get(url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"}, **kw)
    return json.loads(raw.decode("utf-8"))
