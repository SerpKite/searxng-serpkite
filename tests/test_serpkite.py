import unittest
from unittest.mock import Mock, patch

import serpkite
from searx.exceptions import SearxEngineAPIException


class SerpKiteTests(unittest.TestCase):
    def params(self, **overrides):
        return {
            "pageno": 2,
            "safesearch": 2,
            "time_range": "week",
            "searxng_locale": "en-GB",
            "headers": {},
            **overrides,
        }

    def test_request_auth_paging_and_filters(self):
        params = self.params()
        with patch.object(serpkite, "api_key", "test-key"):
            serpkite.request("test query", params)
        self.assertEqual(params["url"], "https://api.serpkite.com/v1/search")
        self.assertEqual(params["method"], "POST")
        self.assertEqual(params["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(
            params["json"],
            {
                "q": "test query",
                "num": 10,
                "page": 2,
                "safe": "active",
                "time": "week",
                "language": "en",
                "country": "gb",
            },
        )
        self.assertNotIn("test-key", params["url"])

    def test_all_locale_and_unfiltered_search(self):
        params = self.params(searxng_locale="all", time_range="", safesearch=0)
        serpkite.request("test", params)
        self.assertEqual(
            params["json"], {"q": "test", "num": 10, "page": 2, "safe": "off"}
        )

    def test_setup_requires_key(self):
        with patch.object(serpkite, "api_key", ""):
            with self.assertRaises(SearxEngineAPIException):
                serpkite.setup({})

    def test_setup_rejects_unsupported_page_size(self):
        with (
            patch.object(serpkite, "api_key", "test-key"),
            patch.object(serpkite, "results_per_page", 11),
        ):
            with self.assertRaises(ValueError):
                serpkite.setup({})

    def test_setup_accepts_supported_page_size(self):
        with (
            patch.object(serpkite, "api_key", "test-key"),
            patch.object(serpkite, "results_per_page", 10),
        ):
            serpkite.setup({})

    def test_results_and_html_cleanup(self):
        resp = Mock()
        resp.json.return_value = {
            "request": {},
            "results": [
                {
                    "title": "<b>Example</b>",
                    "link": "https://example.com",
                    "snippet": "A <i>result</i>.",
                }
            ],
            "meta": {},
        }
        results = serpkite.response(resp)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, "https://example.com")
        self.assertEqual(results[0].title, "Example")
        self.assertEqual(results[0].content, "A result.")

    def test_missing_and_unsafe_links_are_skipped(self):
        resp = Mock()
        resp.json.return_value = {
            "results": [
                {"title": "No URL"},
                {"link": "javascript:alert(1)"},
                {"link": "https://example.com"},
            ]
        }
        results = serpkite.response(resp)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "https://example.com")
        self.assertEqual(results[0].content, "")

    def test_empty_results(self):
        for body in ({"results": []}, {"results": None}):
            resp = Mock()
            resp.json.return_value = body
            self.assertEqual(serpkite.response(resp), [])

    def test_errors_do_not_expose_response_text(self):
        resp = Mock()
        resp.json.return_value = {
            "error": {"code": "unauthorized", "message": "private query or credential"}
        }
        with self.assertRaisesRegex(
            SearxEngineAPIException, "SerpKite returned an API error"
        ) as error:
            serpkite.response(resp)
        self.assertNotIn("private", str(error.exception))


if __name__ == "__main__":
    unittest.main()
