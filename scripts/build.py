from __future__ import annotations

import html
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DIST = ROOT / "dist"

SECTION_ORDER = [
    "Government & Policy",
    "Infrastructure",
    "Education & Workforce",
    "Research & Universities",
    "Business & Startups",
]


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def prose_block(item: dict) -> str:
    tags = " · ".join(item.get("tags", [])[:4])
    caveat = item.get("caveat")
    caveat_html = f'<p class="caveat">Caveat: {esc(caveat)}</p>' if caveat else ""
    return f"""
    <article class="signal" id="{esc(item['id'])}">
      <p class="source-line">{esc(item['source'])} · {esc(item['date'])}</p>
      <h3><a href="{esc(item['url'])}" rel="noopener noreferrer">{esc(item['title'])}</a></h3>
      <p class="tag-line">{esc(tags)}</p>
      <p>{esc(item['summary'])}</p>
      <p><strong>Why it matters:</strong> {esc(item['why_it_matters'])}</p>
      {caveat_html}
    </article>
    """


def render_index(items: list[dict], sources: list[dict]) -> str:
    section_counts = Counter(item["section"] for item in items)
    tag_counts = Counter(tag for item in items for tag in item.get("tags", []))
    generated = datetime.now().strftime("%A, %B %-d, %Y — Updated %-I:%M %p")

    sections = []
    grouped = []
    for section in SECTION_ORDER:
        section_items = sorted(
            [item for item in items if item["section"] == section],
            key=lambda item: item["date"],
            reverse=True,
        )
        if not section_items:
            continue
        grouped.append((section_items[0]["date"], section, section_items))
    for _, section, section_items in sorted(grouped, key=lambda row: row[0], reverse=True):
        body = "\n".join(prose_block(item) for item in section_items)
        sections.append(f"<section class=\"story-section\"><h2>{esc(section)}</h2>{body}</section>")

    source_links = "".join(
        f'<li><a href="{esc(src["url"])}">{esc(src["name"])}</a> <span>Tier {esc(src["tier"])} · {esc(src["expected_yield"])}</span></li>'
        for src in sorted(sources, key=lambda s: (s["tier"], s["name"]))
    )
    tag_links = "".join(f"<span>{esc(tag)} × {count}</span>" for tag, count in tag_counts.most_common(10))
    section_line = " · ".join(f"{name}: {count}" for name, count in section_counts.items())

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sarawak AI News — PoC Brief</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <nav class="topbar">
    <a class="brand" href="#">Sarawak AI News</a>
    <a href="#brief">Brief</a>
    <a href="#sources">Sources</a>
    <a href="items.json">Data</a>
  </nav>

  <main id="brief" class="page">
    <p class="live-line">LIVE — {esc(generated)}</p>
    <p class="edition">Sarawak signal brief</p>

    <header class="lede">
      <h1>Sarawak’s AI Stack Is Becoming Visible</h1>
      <p>This is no longer just digital-economy branding.</p>
      <p>Sarawak’s AI story is starting to resolve into institutions, infrastructure, public services, talent, and applied sector projects.</p>
      <p>The open question is whether the signal is weekly enough to justify a standing brief.</p>
    </header>

    <section class="story-section">
      <h2>The pattern</h2>
      <p>Sarawak AI is not showing up as one product launch.</p>
      <p>It is showing up as a stack: public-service assistants, sovereign infrastructure, agency coordination, research partnerships, and workforce readiness.</p>
      <p>The important question is whether these signals repeat every week.</p>
    </section>

    {''.join(sections)}

    <section id="how-built" class="about-box">
      <h2>How this PoC is built</h2>
      <p>Seed data is stored in JSON, rendered into a static page, and checked by unit tests. Candidate ingestion is intentionally manual-review first: it discovers URLs from watched sources, but does not summarize or publish them automatically.</p>
      <p>{esc(section_line)}</p>
      <div class="tag-cloud">{tag_links}</div>
    </section>

    <section id="sources" class="source-box">
      <h2>Source Watchlist</h2>
      <p>{len(sources)} sources watched. Every headline should link back to the original source.</p>
      <ol>{source_links}</ol>
    </section>
  </main>

  <footer>
    Built as a private PoC. Source-attributed summaries only. No full-article republication.
  </footer>
</body>
</html>
"""


def build() -> None:
    items = sorted(load_json("items.json"), key=lambda item: item["date"], reverse=True)
    sources = load_json("sources.json")
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(render_index(items, sources), encoding="utf-8")
    (DIST / "style.css").write_text((ROOT / "site" / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    (DIST / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    print(f"Built {DIST / 'index.html'} with {len(items)} items and {len(sources)} sources")


if __name__ == "__main__":
    build()
