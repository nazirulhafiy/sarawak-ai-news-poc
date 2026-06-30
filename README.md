# Sarawak AI News PoC

Proof-of-concept for an AI-assisted regional intelligence brief tracking Sarawak-relevant AI, automation, digital economy, public-sector digital services, infrastructure, education, research, and workforce signals.

## What this project proves

- A small curated dataset can render into an Aligned-News-inspired briefing page: live line, sparse prose, large lead headline, short sections, and source links.
- Source attribution, caveats, and tags are first-class fields.
- A lightweight ingestion command can scan watched source pages, fetch candidate article pages, and produce candidate URLs for manual review.
- The project is hosted as a dependency-free static site on GitHub Pages at `https://ai.sarawak.news/`.
- Summarization/publication automation is intentionally deferred until source signal is validated.

## Run locally

```bash
python3 scripts/build.py
python3 -m http.server 4173 -d dist
# open http://127.0.0.1:4173
```

The design uses the reference site's measured 680 px page shell, 640 px content column, 48 px lead headline, and compact 14 px card padding. It keeps the approved content hierarchy, while confidence, caveats, and why-it-matters fields remain preserved in the generated item data.

## Production design source files

The production homepage uses:

- `site/style.css`
- `scripts/build.py` (compact renderer)
- `tests/test_build.py` (production SEO and layout checks)
- generated homepage output under `dist/`

## Live site

- Production URL: https://ai.sarawak.news/
- Hosting: GitHub Pages from `main`, generated files in `dist/`
- Custom-domain SEO is generated in `scripts/build.py` (`canonical`, Open Graph URL, robots, sitemap)
- Current public feed: 15 reviewed source-attributed stories with category filtering

## Candidate ingestion

```bash
python3 scripts/ingest.py --limit-per-source 5
# writes dist/candidates.json and dist/candidates.md
```

The ingestion command discovers candidates only. It now checks candidate article pages and keeps only items with both Sarawak relevance and concrete AI/digital-economy terms. Read the source article before adding anything to `data/items.json`.

## Weekly update flow

1. Run candidate discovery:
   ```bash
   python3 scripts/ingest.py --limit-per-source 5
   ```
2. Review candidate articles manually.
3. Add approved items to `data/items.json`.
4. Rebuild the site:
   ```bash
   python3 scripts/build.py
   ```
5. Run checks:
   ```bash
   python3 -m unittest discover -s tests -v
   python3 scripts/audit_dates.py
   python3 scripts/audit_summaries.py
   ```
6. Preview locally if needed:
   ```bash
   python3 -m http.server 4173 -d dist
   ```
7. Push to `main` so GitHub Pages redeploys.

## Test

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_dates.py
python3 scripts/audit_summaries.py
```

`audit_dates.py` compares every feed item date against the source article's own published metadata (`article:published_time`, `datePublished`, or byline date). Do not use site header dates, related-news dates, extractor summaries, URL guesses, or crawl dates as publication dates.

`audit_summaries.py` checks that each public one-line explanation is a single strategic signal, avoids generic/hype phrasing, and stays within the 22–38 word target.

## Project rules

- Do not republish full articles.
- Link prominently to original sources.
- Use original summaries and analysis.
- Mark caveats and confidence.
- Treat current data as PoC seed data, not a finished publication.

## Current status

Live public static brief. Candidate discovery exists, but public publishing remains manually reviewed: raw candidates, scoring, confidence notes, and summary decisions stay internal until approved and moved into `data/items.json`.

No scraper-to-summary pipeline, newsletter publishing, or external automation is live yet.
