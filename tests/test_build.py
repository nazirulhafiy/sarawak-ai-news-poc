import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BuildTest(unittest.TestCase):
    def test_seed_data_has_required_fields(self):
        items = json.loads((ROOT / "data" / "items.json").read_text())
        required = {"id", "date", "source", "url", "title", "section", "tags", "summary", "why_it_matters", "confidence"}
        self.assertGreaterEqual(len(items), 4)
        for item in items:
            self.assertTrue(required.issubset(item), item.get("id"))
            self.assertTrue(item["url"].startswith("https://"))
            self.assertLess(len(item["summary"]), 700)

    def test_build_outputs_aligned_style_static_site(self):
        result = subprocess.run([sys.executable, "scripts/build.py"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("Built", result.stdout)
        html = (ROOT / "dist" / "index.html").read_text()
        self.assertIn("Sarawak AI News", html)
        self.assertIn("LIVE —", html)
        self.assertIn("Make This Page Shorter", html)
        self.assertIn("How this PoC is built", html)
        self.assertIn("Source Watchlist", html)
        self.assertIn("Digital State: Sarawak adopts AI", html)
        self.assertTrue((ROOT / "dist" / "style.css").exists())
        self.assertTrue((ROOT / "dist" / "items.json").exists())


if __name__ == "__main__":
    unittest.main()
