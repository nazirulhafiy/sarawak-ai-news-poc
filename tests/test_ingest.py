import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import ingest


class IngestTest(unittest.TestCase):
    def test_scoring_prioritizes_sarawak_ai(self):
        score, matched = ingest.score_candidate("DayakDaily", "https://example.com/sarawak-ai-grid", "Sarawak explores AI Grid networks")
        self.assertGreaterEqual(score, 5)
        self.assertIn("sarawak", matched)
        self.assertIn("ai", matched)

    def test_ingest_cli_writes_candidates_from_mocked_page(self):
        html = """
        <html><title>Sarawak AI source</title>
        <a href="/sarawak-ai-grid">Sarawak explores AI Grid networks</a>
        <a href="/sports">Local sports update</a>
        </html>
        """
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "candidates.json"
            with mock.patch.object(ingest, "fetch", return_value=(200, html)), mock.patch.object(
                ingest, "load_sources", return_value=[{"name": "Mock Source", "url": "https://example.com", "tier": 1}]
            ):
                code = ingest.main(["--output", str(output), "--limit-per-source", "3"])
            self.assertEqual(code, 0)
            data = json.loads(output.read_text())
            self.assertTrue(any("AI Grid" in candidate["title"] for candidate in data))
            self.assertTrue(output.with_suffix(".md").exists())

    def test_ingest_help_runs(self):
        result = subprocess.run([sys.executable, "scripts/ingest.py", "--help"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("Discover candidate", result.stdout)


if __name__ == "__main__":
    unittest.main()
