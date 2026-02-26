from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
from dateutil import tz

DATA_PATH = Path("data/events.json")
OSLO_TZ = tz.gettz("Europe/Oslo")


@dataclass(frozen=True)
class Event:
    id: str
    source: str
    venue: str
    title: str
    start: str
    url: str


def load_previous() -> Dict[str, Any]:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {"generated_at": None, "events": []}


def save(events: List[Event]) -> None:
    payload = {
        "generated_at": datetime.now(tz=tz.UTC).isoformat(),
        "events": [asdict(e) for e in sorted(events, key=lambda x: x.start)],
    }
    DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def diff_and_merge(prev_events, new_events):
    prev_by_id = {e["id"]: e for e in prev_events}
    out = []

    for e in new_events:
        old = prev_by_id.get(e.id)
        if old is None:
            out.append(e)
            continue

        changed = any(old.get(k) != getattr(e, k)
                      for k in ["title", "start", "venue", "url"])

        out.append(e if changed else Event(**old))

    return out


def parse_parkteatret() -> List[Event]:
    url = "https://www.parkteatret.no/program"
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "lxml")

    events = []

    for h2 in soup.select("h2"):
        title = h2.get_text(strip=True)
        if not title:
            continue

        a = h2.find("a")
        event_url = a["href"] if a and a.has_attr("href") else url
        if event_url.startswith("/"):
            event_url = "https://www.parkteatret.no" + event_url

        text_block = h2.parent.get_text(" ", strip=True)

        m_date = re.search(r"(\\d{2})\\.(\\d{2})\\.(\\d{2})", text_block)
        if not m_date:
            continue

        dd, mm, yy = map(int, m_date.groups())
        year = 2000 + yy

        m_time = re.search(r"(\\d{1,2}):(\\d{2})", text_block)
        hh, mi = (int(m_time.group(1)), int(m_time.group(2))) if m_time else (19, 0)

        dt = datetime(year, mm, dd, hh, mi, tzinfo=OSLO_TZ)

        events.append(Event(
            id=f"parkteatret|{event_url}",
            source="parkteatret",
            venue="Parkteatret",
            title=title,
            start=dt.isoformat(),
            url=event_url
        ))

    return events


def main():
    prev = load_previous()
    new_events = parse_parkteatret()
    merged = diff_and_merge(prev.get("events", []), new_events)
    save(merged)


if __name__ == "__main__":
    main()
