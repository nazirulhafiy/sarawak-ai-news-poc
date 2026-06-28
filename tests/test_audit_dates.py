import unittest

from scripts.audit_dates import extract_published_date, find_date_mismatches


class AuditDatesTest(unittest.TestCase):
    def test_extracts_article_published_time_before_visible_header_dates(self):
        html = '''
        <html><head>
          <meta property="article:published_time" content="2025-11-12T19:09:48+08:00" />
        </head><body>
          <header>Sunday, 28 June, 2026</header>
          <h1>AI to transform Sarawak's economy</h1>
          <li>12 November 2025</li>
        </body></html>
        '''
        self.assertEqual(extract_published_date(html), "2025-11-12")

    def test_extracts_json_ld_date_published(self):
        html = '''
        <script type="application/ld+json">
        {"@type":"NewsArticle","datePublished":"2026-05-06T10:31:03+08:00"}
        </script>
        '''
        self.assertEqual(extract_published_date(html), "2026-05-06")

    def test_normalizes_utc_metadata_to_malaysia_publication_date(self):
        html = '<meta property="article:published_time" content="2026-03-31T16:27:26+00:00">'
        self.assertEqual(extract_published_date(html), "2026-04-01")

    def test_reports_feed_date_mismatch(self):
        items = [
            {"title": "Wrong", "url": "https://example.test/wrong", "date": "2026-06-28"},
            {"title": "Right", "url": "https://example.test/right", "date": "2026-05-20"},
        ]
        html_by_url = {
            "https://example.test/wrong": '<meta property="article:published_time" content="2026-05-06T10:31:03+08:00">',
            "https://example.test/right": '<meta property="article:published_time" content="2026-05-20T19:06:14+08:00">',
        }
        mismatches = find_date_mismatches(items, lambda url: html_by_url[url])
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0].expected, "2026-05-06")
        self.assertEqual(mismatches[0].actual, "2026-06-28")


if __name__ == "__main__":
    unittest.main()
