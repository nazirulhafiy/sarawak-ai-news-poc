import json
import subprocess
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BuildTest(unittest.TestCase):
    @staticmethod
    def updated_labels():
        value = json.loads((ROOT / "data" / "site.json").read_text())["last_updated"]
        updated = datetime.fromisoformat(value)
        time = updated.strftime("%I:%M %p").lstrip("0")
        current = f"{updated.strftime('%A, %B')} {updated.day}, {updated.year}, {time}".upper()
        compact = f"{updated.day} {updated.strftime('%b %Y').upper()} · {time} MYT"
        return value, current, compact

    def test_seed_data_has_required_fields(self):
        items = json.loads((ROOT / "data" / "items.json").read_text())
        required = {"id", "date", "source", "url", "title", "section", "tags", "summary", "why_it_matters", "confidence", "caveat"}
        self.assertGreaterEqual(len(items), 4)
        for item in items:
            self.assertTrue(required.issubset(item), item.get("id"))
            self.assertTrue(item["url"].startswith("https://"))
            self.assertLess(len(item["summary"]), 700)

    def test_build_outputs_aligned_style_static_site(self):
        result = subprocess.run([sys.executable, "scripts/build.py"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("Built", result.stdout)
        html = (ROOT / "dist" / "index.html").read_text()
        css = (ROOT / "dist" / "style.css").read_text()
        js = (ROOT / "dist" / "app.js").read_text()
        expected_items = len(json.loads((ROOT / "data" / "items.json").read_text()))
        self.assertIn("Sarawak.News", html)
        updated_iso, _, compact_updated = self.updated_labels()
        self.assertIn(f'<span class="updated-label">Last updated</span><time datetime="{updated_iso}">{compact_updated}</time>', html)
        self.assertLess(html.index('class="updated"'), html.index('id="brief-title"'))
        self.assertIn("Tracking Sarawak’s AI, news, policy, and future economy.", html)
        self.assertIn("An independent news aggregator collecting important AI updates from Sarawak’s government, universities, businesses, and tech ecosystem.", html)
        self.assertIn("Latest intelligence signals", html)
        self.assertIn("Sarawak.News is an independent publication", html)
        self.assertEqual(html.count('class="story-card"'), expected_items)
        self.assertEqual(html.count('class="story-section"'), expected_items)
        self.assertEqual(html.count('class="story-source-label"'), expected_items)
        self.assertEqual(html.count('class="category-filter-button'), 6)
        self.assertIn('data-category-filter hidden', html)
        self.assertIn('data-section="infrastructure"', html)
        self.assertIn('data-section-filter="all"', html)
        self.assertIn('data-section-filter="government-policy"', html)
        self.assertIn('<script src="app.js" defer></script>', html)
        self.assertIn('class="story-rank" aria-label="Chronological item 1">1</div>', html)
        self.assertIn('<time datetime="2026-06-24">24 Jun 2026</time>', html)
        self.assertIn('<meta name="description" content="AI Sarawak and Sarawak AI news, curated from Sarawak government, universities, businesses, infrastructure, and future-economy signals." />', html)
        self.assertIn('<meta name="google-site-verification" content="5Ro7_ZjEKgT00hwHzOx0paD1Cme1tLYEGdttr_CwHvo" />', html)
        self.assertIn('<meta name="robots" content="index,follow" />', html)
        self.assertIn('<meta property="og:title" content="AI.Sarawak.News" />', html)
        self.assertIn('<meta property="og:url" content="https://ai.sarawak.news/" />', html)
        self.assertIn('<meta name="twitter:card" content="summary_large_image" />', html)
        self.assertIn('<link rel="canonical" href="https://ai.sarawak.news/" />', html)
        self.assertIn('<title>AI.Sarawak.News</title>', html)
        self.assertNotIn("How This Is Built", html)
        self.assertNotIn("Sponsor This Brief", html)
        self.assertNotIn("Make This Brief Shorter", html)
        self.assertNotIn("Get this delivered to your inbox weekly", html)
        self.assertNotIn("Signal categories", html)
        self.assertNotIn("<nav", html)
        self.assertNotIn("Matched signal terms", html)
        self.assertIn('target="_blank"', html)
        self.assertIn("max-width: 680px", css)
        self.assertIn("grid-template-columns: 40px minmax(0, 1fr)", css)
        self.assertIn("font-size: 48px", css)
        self.assertIn("--canvas: #ffffff", css)
        self.assertIn("--card: #ffffff", css)
        self.assertIn("background: var(--card)", css)
        self.assertIn("background: var(--sarawak-black)", css)
        self.assertNotIn("-webkit-line-clamp", css)
        self.assertIn("--sarawak-red: #d22630", css)
        self.assertIn("--sarawak-yellow: #f7c948", css)
        self.assertIn("--sarawak-black: #111111", css)
        self.assertNotIn(".story-rank::after", css)
        self.assertIn(".category-filter-button.is-active", css)
        self.assertIn(".updated-label", css)
        self.assertIn(".updated time", css)
        self.assertIn("padding: 0 0 14px", css)
        self.assertIn("flex-wrap: nowrap", css)
        self.assertIn("overflow-x: auto", css)
        self.assertIn(".story-section", css)
        self.assertIn(".story-source", css)
        self.assertIn(".story-source-label", css)
        self.assertIn("background: var(--sarawak-yellow)", css)
        self.assertIn("color: var(--sarawak-black)", css)
        self.assertIn('applyFilter("all")', js)
        self.assertIn("story.hidden = !isVisible", js)
        for label in [">AI<", ">Tech<", ">PCDS 2030<", ">Policy<", ">Startups<", ">Energy<", ">Events<"]:
            self.assertNotIn(label, html)
        public_items = json.loads((ROOT / "dist" / "items.json").read_text())
        self.assertEqual(len(public_items), expected_items)
        self.assertTrue(all(item["date"] for item in public_items))
        public_titles = {item["title"] for item in public_items}
        self.assertIn("AI to transform Sarawak's economy, services, workforce productivity", public_titles)
        self.assertIn("Digital State: Sarawak adopts AI to address citizen needs", public_titles)
        self.assertIn("Sarawak Eyes Sovereign AI Infrastructure", public_titles)
        self.assertIn("Sarawak's AI future takes shape", public_titles)
        self.assertIn("Sarawak expands early intervention with AI screening", public_titles)
        self.assertNotIn("Sarawak Digital Economy Research Grant", public_titles)
        self.assertNotIn("Sarawak Digital Economy Research Grant", html)
        self.assertTrue(all(item.get("url") for item in public_items))
        self.assertTrue(all(item.get("why_it_matters") for item in public_items))
        self.assertTrue(all(item.get("confidence") for item in public_items))
        self.assertTrue(all(item.get("caveat") for item in public_items))

    def test_build_removes_alternative_route(self):
        alternative_dir = ROOT / "dist" / "alternative"
        alternative_dir.mkdir(parents=True, exist_ok=True)
        (alternative_dir / "legacy.html").write_text("stale alternative")

        subprocess.run([sys.executable, "scripts/build.py"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertFalse(alternative_dir.exists())


if __name__ == "__main__":
    unittest.main()
