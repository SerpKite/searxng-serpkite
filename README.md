# SerpKite for SearXNG

An independently maintained drop-in web-search engine for SearXNG. Maintained by the SerpKite team. This is an optional downstream integration; it is not part of the upstream SearXNG catalog.

## Install

1. Get an API key at https://app.serpkite.com. Use a dedicated key with a monthly credit limit.
2. Copy `serpkite.py` into your SearXNG installation's `searx/engines/` directory. For a container, mount the file at `/usr/local/searxng/searx/engines/serpkite.py`; confirm that location against your image.
3. Merge the engine block from `settings.example.yml` into your instance's `settings.yml`. Set `api_key` privately. Keep your configured file out of version control.
4. Restart your SearXNG instance. Use `!skt your query` or enable SerpKite in search preferences.

```yaml
engines:
  - name: serpkite
    engine: serpkite
    shortcut: skt
    api_key: "YOUR_SERPKITE_API_KEY"
    results_per_page: 10
    inactive: false
```

Your instance sends requests to `https://api.serpkite.com/v1/search` with a Bearer header. Query text stays out of the URL. The engine maps SerpKite's own `results` envelope to SearXNG results, skips invalid links, and strips HTML from titles and snippets. It supports paging, language/region, SafeSearch and day/week/month/year filters.

Each live page uses SerpKite credits. Supported result depths are 10, 20, 30, 50 and 100; deeper requests cost more. Read https://serpkite.com/pricing and https://serpkite.com/docs before changing the depth. Credits never expire; failed and empty searches are free. This integration is opt-in because a hosted search provider receives the query and authenticates requests to your account.

## Test

The engine was tested against SearXNG commit `d48c4b555421e824342c51d68482dd0898e54d0f` (2026-10-04). With that checkout and its requirements installed:

```bash
PYTHONPATH=/path/to/searxng:$PWD python -m unittest discover -s tests -v
```

Nine tests cover payload/authentication, filters, configuration validation, result mapping, empty results, unsafe links, and private error text. They use SearXNG's real result types and send no network requests.

## Support and license

Source: AGPL-3.0-or-later, compatible with SearXNG. The hosted SerpKite API is proprietary.

Docs: https://serpkite.com/docs · Support/security: support@serpkite.com

This downstream repository was developed with Codex. No AI-generated issue or PR was submitted upstream; SearXNG requires human-authored contributions.

Google is a trademark of Google LLC; SerpKite is not affiliated with Google.
