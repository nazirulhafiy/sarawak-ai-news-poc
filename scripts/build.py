from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DIST = ROOT / "dist"

SECTION_FILTERS = (
    ("Government & Policy", "Policy"),
    ("Education & Workforce", "Education"),
    ("Infrastructure", "Infrastructure"),
    ("Research & Universities", "Research"),
    ("Public Services", "Public Services"),
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def format_story_date(value: str) -> str:
    date = datetime.strptime(value, "%Y-%m-%d")
    return f"{date.day} {date.strftime('%b %Y')}"


def last_updated() -> tuple[str, str, str]:
    value = load_json(DATA / "site.json")["last_updated"]
    updated = parse_datetime(value)
    time = updated.strftime("%I:%M %p").lstrip("0")
    current = f"{updated.strftime('%A, %B')} {updated.day}, {updated.year}, {time}".upper()
    compact = f"{updated.day} {updated.strftime('%b %Y').upper()} · {time} MYT"
    return value, current, compact


def reviewed_items() -> list[dict]:
    items = load_json(DATA / "items.json")
    return [
        {
            "id": item["id"],
            "title": item["title"],
            "url": item["url"],
            "source": item["source"],
            "date": item["date"],
            "section": item["section"],
            "tags": item["tags"],
            "note": item["summary"],
            "why_it_matters": item["why_it_matters"],
            "confidence": item["confidence"],
            "caveat": item["caveat"],
        }
        for item in sorted(items, key=lambda row: row["date"], reverse=True)
        if item.get("date") and item.get("why_it_matters")
    ]


def load_feed_items() -> list[dict]:
    # Public feed uses reviewed editorial items only. Raw ingestion candidates
    # stay internal until date, relevance, and source quality are checked.
    return reviewed_items()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def render_compact_signal(item: dict, index: int) -> str:
    caveat = ""
    if str(item["confidence"]).lower() != "high":
        caveat = f'<p class="story-caveat"><strong>Source note:</strong> {esc(item["caveat"])}</p>'
    return f"""
    <article class="story-card" id="{slug(item['id'])}" data-section="{slug(item['section'])}">
      <div class="story-rank" aria-label="Chronological item {index}">{index}</div>
      <div class="story-body">
        <p class="story-meta-row">
          <time datetime="{esc(item['date'])}">{esc(format_story_date(item['date']))}</time>
          <span class="story-source"><span class="story-source-label">{esc(item['source'])}</span></span>
          <span class="story-section">{esc(item['section'])}</span>
        </p>
        <h2><a href="{esc(item['url'])}" target="_blank" rel="noopener noreferrer">{esc(item['title'])}</a></h2>
        <p class="story-summary">{esc(item['note'])}</p>
        {caveat}
      </div>
    </article>
    """


def render_category_filter(items: list[dict]) -> str:
    counts = {section: sum(item["section"] == section for item in items) for section, _ in SECTION_FILTERS}
    buttons = [
        f'<button type="button" class="category-filter-button is-active" data-section-filter="all" '
        f'data-filter-label="All stories" aria-pressed="true">All '
        f'<span class="category-filter-count" aria-hidden="true">{len(items)}</span></button>'
    ]
    buttons.extend(
        f'<button type="button" class="category-filter-button" data-section-filter="{slug(section)}" '
        f'data-filter-label="{esc(section)}" aria-pressed="false">{esc(label)} '
        f'<span class="category-filter-count" aria-hidden="true">{counts[section]}</span></button>'
        for section, label in SECTION_FILTERS
        if counts[section]
    )
    return f"""
    <section class="category-filter" aria-labelledby="category-filter-title" data-category-filter hidden>
      <p class="category-filter-title" id="category-filter-title">Browse by category</p>
      <div class="category-filter-options">
        {' '.join(buttons)}
      </div>
      <p class="visually-hidden" data-filter-status aria-live="polite">Showing all {len(items)} stories</p>
    </section>
    """


def render_compact_body(items: list[dict]) -> str:
    feed = "\n".join(render_compact_signal(item, index) for index, item in enumerate(items, 1))
    category_filter = render_category_filter(items)
    updated_iso, _, updated_compact = last_updated()

    return f"""<body>
  <a class="skip-link" href="#content">Skip to content</a>

  <header class="bar">
    <a class="brand" href="/">AI.SARAWAK.NEWS</a>
  </header>

  <main id="content">
    <header class="brief">
      <p class="updated"><span class="updated-label">Last updated</span><time datetime="{esc(updated_iso)}">{esc(updated_compact)}</time></p>
      <h1 id="brief-title">Tracking Sarawak’s AI, news, policy, and future economy.</h1>
      <p class="brief-deck">An independent news aggregator collecting important AI updates from Sarawak’s government, universities, businesses, and tech ecosystem.</p>
    </header>

    {category_filter}

    <section class="story-list" aria-label="Latest intelligence signals" data-story-list>
      {feed}
    </section>
  </main>

  <footer>
    <p>Sarawak.News is an independent publication and is not affiliated with the Sarawak Government unless explicitly stated.</p>
  </footer>
</body>"""


def render_index(items: list[dict]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="AI Sarawak and Sarawak AI news, curated from Sarawak government, universities, businesses, infrastructure, and future-economy signals." />
  <meta name="google-site-verification" content="5Ro7_ZjEKgT00hwHzOx0paD1Cme1tLYEGdttr_CwHvo" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="AI.Sarawak.News" />
  <meta property="og:description" content="A curated Sarawak AI intelligence brief tracking government, universities, businesses, infrastructure, and future-economy signals." />
  <meta property="og:url" content="https://ai.sarawak.news/" />
  <meta property="og:site_name" content="AI.Sarawak.News" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="AI.Sarawak.News" />
  <meta name="twitter:description" content="A curated Sarawak AI intelligence brief tracking government, universities, businesses, infrastructure, and future-economy signals." />
  <link rel="canonical" href="https://ai.sarawak.news/" />
  <title>AI.Sarawak.News</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>" />
  <link rel="stylesheet" href="style.css" />
  <script src="app.js" defer></script>
</head>
{render_compact_body(items)}
</html>
"""


def build() -> None:
    items = load_feed_items()
    DIST.mkdir(exist_ok=True)
    alternative_dir = DIST / "alternative"
    if alternative_dir.exists():
        shutil.rmtree(alternative_dir)
    (DIST / "index.html").write_text(render_index(items), encoding="utf-8")
    compact_css = (ROOT / "site" / "style.css").read_text(encoding="utf-8")
    (DIST / "style.css").write_text(compact_css, encoding="utf-8")
    (DIST / "app.js").write_text((ROOT / "site" / "app.js").read_text(encoding="utf-8"), encoding="utf-8")
    (DIST / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://ai.sarawak.news/sitemap.xml\n", encoding="utf-8")
    (DIST / "sitemap.xml").write_text("""<?xml version='1.0' encoding='UTF-8'?>
<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>
  <url>
    <loc>https://ai.sarawak.news/</loc>
  </url>
</urlset>
""", encoding="utf-8")
    print(f"Built {DIST / 'index.html'} with {len(items)} feed items")


if __name__ == "__main__":
    build()
