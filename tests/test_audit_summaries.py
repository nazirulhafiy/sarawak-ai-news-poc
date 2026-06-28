import unittest

from scripts.audit_summaries import find_summary_issues


class AuditSummariesTest(unittest.TestCase):
    def test_flags_generic_summary_and_bad_word_count(self):
        items = [{"id": "x", "title": "X", "summary": "This article discusses AI development in Sarawak."}]
        issues = find_summary_issues(items)
        self.assertTrue(any("generic" in issue.reason for issue in issues))
        self.assertTrue(any("word count" in issue.reason for issue in issues))

    def test_accepts_specific_strategic_signal(self):
        items = [{
            "id": "x",
            "title": "Sarawak expands early intervention with AI screening",
            "summary": "Sarawak’s AI screening rollout gives the state a practical public-service use case for AI, focused on early childhood intervention across SeDidik centres.",
        }]
        self.assertEqual(find_summary_issues(items), [])

    def test_accepts_user_approved_short_strategic_signal(self):
        items = [{
            "id": "x",
            "title": "Sarawak explores AI Grid networks, satellite integration to power next-generation digital economy",
            "summary": "Sarawak’s AI Grid and satellite exploration points to a more distributed infrastructure strategy beyond conventional data centres.",
        }]
        self.assertEqual(find_summary_issues(items), [])

    def test_flags_multiple_sentences_and_hype_words(self):
        items = [{
            "id": "x",
            "title": "X",
            "summary": "Sarawak is launching a groundbreaking AI programme for public services. It is game-changing for future growth.",
        }]
        issues = find_summary_issues(items)
        self.assertTrue(any("one sentence" in issue.reason for issue in issues))
        self.assertTrue(any("hype" in issue.reason for issue in issues))


if __name__ == "__main__":
    unittest.main()
