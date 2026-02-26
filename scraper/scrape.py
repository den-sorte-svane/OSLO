# Minimal placeholder scraper (replace with full version later)

import json
from datetime import datetime
from pathlib import Path

DATA_PATH = Path("data/events.json")

def main():
    sample_event = {
        "id": "sample|https://example.com",
        "source": "sample",
        "venue": "Eksempel Venue",
        "title": "Eksempel Event",
        "start": datetime.now().isoformat(),
        "url": "https://example.com"
    }

    payload = {
        "generated_at": datetime.utcnow().isoformat(),
        "events": [sample_event]
    }

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
