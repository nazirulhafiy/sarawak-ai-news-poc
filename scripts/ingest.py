from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "dist" / "candidates.json"

KEYWORDS = [
    "sarawak",
    "ai",
    "artificial intelligence",
    "machine learning",
    "digital economy",
    "data centre",
    "data center",
    "sovereign ai",
    "ai grid",
    "cloud",
    "smart city",
    "iot",
    "5g",
    "satellite",
    "automation",
    "robotic",
    "sains",
    "sdec",
    "saic",
    "deepSAR",
    "dayang",
    "centexs",
]

@dataclass
class Candidate:
    source: str
    source_url: str
    url: str
    title: str
    score: int
    matched_keywords: list[str]
    status: str = "candidate"
    error: str | None = None


def load_sources() -> list[dict]:
    return json.loads((DATA / "sources.json").read_text(encoding="utf-8"))


def fetch(url: str, timeout: int = 12) -> tuple[int, str]:
    req = Request(url, headers={"User-Agent": "SarawakAINewsPoC/0.1 (+manual validation)"})
    with urlopen(req, timeout=timeout) as response:  # nosec: PoC reads configured public URLs only
        raw = response.read(800_000)
        charset = response.headers.get_content_charset() or "utf-8"
        return response.status, raw.decode(charset, errors="replace")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def page_title(body: str, fallback: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.I | re.S)
    return clean_text(match.group(1)) if match else fallback


def links_from_page(base_url: str, body: str) -> Iterable[tuple[str, str]]:
    for match in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", body, flags=re.I | re.S):
        href, label = match.groups()
        url = urljoin(base_url, href.split("#", 1)[0])
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        title = clean_text(label) or url
        if len(title) < 4:
            continue
        yield url, title[:180]


def keyword_matches(haystack: str) -> list[str]:
    matches: list[str] = []
    for kw in KEYWORDS:
        pattern = r"\bai\b" if kw.lower() == "ai" else re.escape(kw.lower())
        if re.search(pattern, haystack):
            matches.append(kw)
    return matches


def score_candidate(source_name: str, url: str, title: str) -> tuple[int, list[str]]:
    del source_name  # source names often include the query text; do not let that inflate relevance.
    parsed = urlparse(url)
    generic_titles = {"read more", "about us", "business", "home", "news", "contact", "privacy policy"}
    normalized_title = title.strip().lower()
    if (
        normalized_title in generic_titles
        or normalized_title.startswith("http")
        or "facebook" in normalized_title
        or "/category/" in parsed.path
        or re.search(r"/page/\d+", parsed.path)
        or normalized_title.startswith("you searched for")
        or "search results" in normalized_title
    ):
        return 0, []

    haystack = f"{parsed.path} {title}".lower()
    matched = keyword_matches(haystack)
    score = len(matched)
    if "sarawak" in matched:
        score += 2
    if any(kw in matched for kw in ["ai", "artificial intelligence", "saic", "sovereign ai", "ai grid"]):
        score += 2
    return max(score, 0), matched


def discover(limit_per_source: int, min_score: int = 4) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen_urls: set[str] = set()
    for source in load_sources():
        source_name = source["name"]
        source_url = source["url"]
        try:
            status, body = fetch(source_url)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            candidates.append(Candidate(source_name, source_url, source_url, source_name, 0, [], "error", str(exc)))
            continue

        landing_title = page_title(body, source_name)
        # Landing/search pages are source-health checks, not publishable article candidates.
        _landing_score, _landing_matches = score_candidate(source_name, source_url, landing_title)

        source_candidates: list[Candidate] = []
        source_seen: set[str] = set()
        for url, title in links_from_page(source_url, body):
            if url in seen_urls or url in source_seen:
                continue
            score, matched = score_candidate(source_name, url, title)
            if score >= min_score:
                source_seen.add(url)
                source_candidates.append(Candidate(source_name, source_url, url, title, score, matched, f"http {status}"))

        for candidate in sorted(source_candidates, key=lambda c: (-c.score, c.title))[:limit_per_source]:
            seen_urls.add(candidate.url)
            candidates.append(candidate)
        time.sleep(0.2)
    return sorted(candidates, key=lambda c: (-c.score, c.source, c.title))


def write_outputs(candidates: list[Candidate], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = [candidate.__dict__ for candidate in candidates]
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md = output.with_suffix(".md")
    rows = ["# Candidate URLs", "", "Generated for manual review. Do not publish candidates without reading the source article.", "", "| Score | Source | Title | URL | Status |", "| ---: | --- | --- | --- | --- |"]
    for c in candidates:
        rows.append(f"| {c.score} | {c.source} | {c.title.replace('|', '/')} | {c.url} | {c.status} |")
    md.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover candidate Sarawak AI News URLs from configured source pages.")
    parser.add_argument("--limit-per-source", type=int, default=5)
    parser.add_argument("--min-score", type=int, default=4)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    candidates = discover(args.limit_per_source, args.min_score)
    write_outputs(candidates, args.output)
    errors = sum(1 for c in candidates if c.status == "error")
    print(f"Wrote {len(candidates)} candidates to {args.output} ({errors} source errors)")
    return 0 if candidates else 2


if __name__ == "__main__":
    raise SystemExit(main())
