# Sarawak AI News PoC

Proof-of-concept for an AI-assisted regional intelligence brief tracking Sarawak-relevant AI, automation, digital economy, public-sector digital services, infrastructure, education, research, and workforce signals.

## What this PoC proves

- A small curated dataset can render into an Aligned-News-inspired briefing page: live line, sparse prose, large lead headline, short sections, and source links.
- Source attribution, caveats, and tags are first-class fields.
- A lightweight ingestion command can scan watched source pages, fetch candidate article pages, and produce candidate URLs for manual review.
- The project can be hosted as a static site later without a backend.
- Summarization/publication automation is intentionally deferred until source signal is validated.

## Run locally

```bash
python3 scripts/build.py
python3 -m http.server 4173 -d dist
# open http://127.0.0.1:4173
```

## Candidate ingestion

```bash
python3 scripts/ingest.py --limit-per-source 5
# writes dist/candidates.json and dist/candidates.md
```

The ingestion command discovers candidates only. It now checks candidate article pages and keeps only items with both Sarawak relevance and concrete AI/digital-economy terms. Read the source article before adding anything to `data/items.json`.

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Project rules

- Do not republish full articles.
- Link prominently to original sources.
- Use original summaries and analysis.
- Mark caveats and confidence.
- Treat current data as PoC seed data, not a finished publication.

## Current status

PoC only. Candidate discovery exists; no live publishing, scraper-to-summary pipeline, or LLM automation yet.
