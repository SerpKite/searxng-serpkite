# SPDX-License-Identifier: AGPL-3.0-or-later
"""SerpKite web-search engine for independently managed SearXNG instances."""

import typing as t
from urllib.parse import urlparse

from searx.exceptions import SearxEngineAPIException
from searx.result_types import EngineResults
from searx.utils import html_to_text

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams

about = {
    "website": "https://serpkite.com",
    "wikidata_id": None,
    "official_api_documentation": "https://serpkite.com/docs",
    "use_official_api": True,
    "require_api_key": True,
    "results": "JSON",
}

api_key: str = ""
results_per_page: int = 10
categories = ["general", "web"]
paging = True
safesearch = True
time_range_support = True
base_url = "https://api.serpkite.com/v1/search"


def setup(_: dict[str, t.Any]) -> None:
    """Validate the instance configuration before accepting requests."""
    if not api_key:
        raise SearxEngineAPIException("A SerpKite API key is required")
    if results_per_page not in (10, 20, 30, 50, 100):
        raise ValueError("results_per_page must be 10, 20, 30, 50 or 100")


def request(query: str, params: "OnlineParams") -> None:
    """Build the request; SearXNG's network layer sends it."""
    body: dict[str, t.Any] = {
        "q": query,
        "num": results_per_page,
        "page": params["pageno"],
        "safe": "active" if params["safesearch"] else "off",
    }
    if params["time_range"]:
        body["time"] = params["time_range"]
    locale = params["searxng_locale"]
    if locale != "all":
        parts = locale.split("-")
        body["language"] = parts[0].lower()
        if len(parts) > 1 and len(parts[-1]) == 2:
            body["country"] = parts[-1].lower()
    params["url"] = base_url
    params["method"] = "POST"
    params["headers"]["Authorization"] = f"Bearer {api_key}"
    params["headers"]["Content-Type"] = "application/json"
    params["json"] = body


def response(resp: "SXNG_Response") -> EngineResults:
    """Map SerpKite's snake_case envelope to SearXNG web results."""
    data = resp.json()
    if data.get("error"):
        raise SearxEngineAPIException("SerpKite returned an API error")
    results = EngineResults()
    for item in data.get("results") or []:
        link = item.get("link") or ""
        parsed = urlparse(link)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            continue
        results.add(
            results.types.MainResult(
                url=link,
                title=html_to_text(item.get("title") or link),
                content=html_to_text(item.get("snippet") or ""),
            )
        )
    return results
