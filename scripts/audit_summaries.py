from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "items.json"

GENERIC_PHRASES = [
    "this article discusses",
    "this article says",
    "the article discusses",
    "the article says",
    "ai development in sarawak",
    "improving digital transformation",
    "working with partners on technology",
    "supports innovation and future growth",
    "highlighted the importance of ai",
]

HYPE_WORDS = [
    "revolutionary",
    "groundbreaking",
    "game-changing",
    "cutting-edge",
    "world-class",
]

STRATEGIC_TERMS = [
    "signalling",
    "signals",
    "signal",
    "positioning",
    "position itself",
    "positions",
    "frames",
    "linking",
    "moving",
    "shifting",
    "gives",
    "rollout",
    "roadmap",
    "adoption",
    "capability",
    "infrastructure",
    "public-service",
    "public-sector",
    "talent",
    "workforce",
    "pcds",
    "digital-economy",
    "regional ai",
]


@dataclass(frozen=True)
class SummaryIssue:
    item_id: str
    reason: str


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text))


def sentence_count(text: str) -> int:
    return len([part for part in re.split(r"[.!?]+\s*", text.strip()) if part])


def find_summary_issues(items: Iterable[dict]) -> list[SummaryIssue]:
    issues: list[SummaryIssue] = []
    for item in items:
        item_id = str(item.get("id", item.get("title", "unknown")))
        summary = str(item.get("summary", "")).strip()
        lowered = summary.lower()
        words = word_count(summary)
        if not 14 <= words <= 38:
            issues.append(SummaryIssue(item_id, f"word count {words} outside 14-38"))
        if sentence_count(summary) != 1:
            issues.append(SummaryIssue(item_id, "summary must be one sentence"))
        if any(phrase in lowered for phrase in GENERIC_PHRASES):
            issues.append(SummaryIssue(item_id, "generic wording detected"))
        if any(word in lowered for word in HYPE_WORDS):
            issues.append(SummaryIssue(item_id, "hype wording detected"))
        if summary.startswith(("This article", "The article")):
            issues.append(SummaryIssue(item_id, "do not start with article framing"))
        if not any(term in lowered for term in STRATEGIC_TERMS):
            issues.append(SummaryIssue(item_id, "missing clear strategic signal term"))
    return issues


def load_items(path: Path = DATA) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit(path: Path = DATA) -> int:
    items = load_items(path)
    issues = find_summary_issues(items)
    if not issues:
        print(f"Summary audit passed for {len(items)} items")
        return 0
    print("Summary audit failed:", file=sys.stderr)
    for issue in issues:
        print(f"- {issue.item_id}: {issue.reason}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify one-line Sarawak.News strategic article signals.")
    parser.add_argument("--items", type=Path, default=DATA, help="Path to items.json")
    args = parser.parse_args()
    return audit(args.items)


if __name__ == "__main__":
    raise SystemExit(main())
