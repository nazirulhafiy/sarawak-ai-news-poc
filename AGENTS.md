# AGENTS.md

## Project
Sarawak AI News PoC: static proof-of-concept for a source-attributed regional AI intelligence brief.

## Rules
- Do not republish full article bodies.
- Maintain source URL, caveat, confidence, and why-it-matters fields for every item.
- Keep build dependency-free unless there is a clear reason to add tooling.
- Run `python3 -m unittest discover -s tests -v` before claiming changes work.
- Public publishing, newsletter sending, domain setup, or outreach requires Hafiy's explicit approval.

## Useful commands

```bash
python3 scripts/build.py
python3 scripts/ingest.py --limit-per-source 5
python3 -m unittest discover -s tests -v
python3 -m http.server 4173 -d dist
```
