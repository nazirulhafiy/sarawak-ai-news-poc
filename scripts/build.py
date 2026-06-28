from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DIST = ROOT / "dist"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def reviewed_items() -> list[dict]:
    items = load_json(DATA / "items.json")
    return [
        {
            "title": item["title"],
            "url": item["url"],
            "source": item["source"],
            "date": item["date"],
            "note": item["summary"],
        }
        for item in sorted(items, key=lambda row: row["date"], reverse=True)
        if item.get("date") and item.get("why_it_matters")
    ]


def load_feed_items() -> list[dict]:
    # Public feed uses reviewed editorial items only. Raw ingestion candidates
    # stay internal until date, relevance, and source quality are checked.
    return reviewed_items()


def render_signal(item: dict, index: int) -> str:
    date = f'<span class="date">{esc(item["date"])}</span>' if item.get("date") else ""
    return f"""
    <article class="signal-card">
      <div class="rank">{index}</div>
      <div class="signal-body">
        <p class="meta">{date}<span>{esc(item['source'])}</span></p>
        <h2><a href="{esc(item['url'])}" target="_blank" rel="noopener noreferrer">{esc(item['title'])}</a></h2>
        <p>{esc(item['note'])}</p>
      </div>
    </article>
    """


def render_index(items: list[dict]) -> str:
    feed = "\n".join(render_signal(item, index) for index, item in enumerate(items, 1))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI.Sarawak.News</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header class="topbar">
    <a class="brand" href="#">AI.SARAWAK.NEWS</a>
  </header>

  <main class="page">
    <p class="live-line">SUNDAY, JUNE 28, 2026 — UPDATED 11:05 AM</p>
    <header class="lede">
      <h1>Tracking Sarawak’s AI, technology, and future economy.</h1>
      <p>An independent news aggregator collecting important AI updates from Sarawak’s government, universities, businesses, and tech ecosystem.</p>
    </header>

    <section class="feed" aria-label="Latest intelligence signals">
      {feed}
    </section>
  </main>

  <footer>
    <p>Sarawak.News is an independent publication and is not affiliated with the Sarawak Government unless explicitly stated.</p>
  </footer>
</body>
</html>
"""


def build() -> None:
    items = load_feed_items()
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(render_index(items), encoding="utf-8")
    (DIST / "style.css").write_text((ROOT / "site" / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    (DIST / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    print(f"Built {DIST / 'index.html'} with {len(items)} feed items")


if __name__ == "__main__":
    build()
