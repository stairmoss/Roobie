"""
Roobie Search Tools
Local web search without API keys using DuckDuckGo HTML scraping.
"""

import re
import json
import requests
from typing import List, Dict
from urllib.parse import quote_plus, urljoin


class SearchTools:
    """Web search using DuckDuckGo HTML (no API key required)."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def web_search(self, query: str, max_results: int = 8) -> Dict:
        """Search the web using DuckDuckGo HTML (no API)."""
        results = []

        # Method 1: DuckDuckGo HTML
        try:
            ddg_results = self._search_ddg_html(query, max_results)
            if ddg_results:
                results.extend(ddg_results)
        except Exception:
            pass

        # Method 2: DuckDuckGo Lite
        if not results:
            try:
                lite_results = self._search_ddg_lite(query, max_results)
                if lite_results:
                    results.extend(lite_results)
            except Exception:
                pass

        # Method 3: Try SearXNG if available
        if not results:
            try:
                searx = self._search_searxng(query, max_results)
                if searx:
                    results.extend(searx)
            except Exception:
                pass

        if not results:
            return {
                "success": False,
                "query": query,
                "results": [],
                "error": "No search results found. Check network connection."
            }

        return {
            "success": True,
            "query": query,
            "results": results[:max_results],
            "count": len(results[:max_results])
        }

    def _search_ddg_html(self, query: str, max_results: int) -> List[Dict]:
        """Search DuckDuckGo HTML version."""
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        r = requests.get(url, headers=self.HEADERS, timeout=15)
        r.raise_for_status()

        results = []
        # Parse result blocks
        # DuckDuckGo HTML has results in <div class="result"> blocks
        result_pattern = re.compile(
            r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            re.DOTALL
        )

        for match in result_pattern.finditer(r.text):
            url_raw = match.group(1)
            title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
            snippet = re.sub(r'<[^>]+>', '', match.group(3)).strip()

            # DuckDuckGo wraps URLs through a redirect
            actual_url = url_raw
            if "uddg=" in url_raw:
                url_match = re.search(r'uddg=([^&]+)', url_raw)
                if url_match:
                    from urllib.parse import unquote
                    actual_url = unquote(url_match.group(1))

            if title and actual_url:
                results.append({
                    "title": title,
                    "url": actual_url,
                    "snippet": snippet,
                    "source": "duckduckgo"
                })

            if len(results) >= max_results:
                break

        return results

    def _search_ddg_lite(self, query: str, max_results: int) -> List[Dict]:
        """Search DuckDuckGo Lite version (even more lightweight)."""
        url = f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}"
        r = requests.get(url, headers=self.HEADERS, timeout=15)
        r.raise_for_status()

        results = []
        # Parse lite version
        link_pattern = re.compile(
            r'<a[^>]*rel="nofollow"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            re.DOTALL
        )
        snippet_pattern = re.compile(
            r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>',
            re.DOTALL
        )

        links = link_pattern.findall(r.text)
        snippets = snippet_pattern.findall(r.text)

        for i, (url_raw, title_raw) in enumerate(links):
            title = re.sub(r'<[^>]+>', '', title_raw).strip()
            snippet = ""
            if i < len(snippets):
                snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()

            if title and url_raw and url_raw.startswith("http"):
                results.append({
                    "title": title,
                    "url": url_raw,
                    "snippet": snippet,
                    "source": "duckduckgo-lite"
                })

            if len(results) >= max_results:
                break

        return results

    def _search_searxng(self, query: str, max_results: int) -> List[Dict]:
        """Try local SearXNG instance as fallback."""
        try:
            params = {
                "q": query,
                "format": "json",
                "categories": "general",
                "language": "en",
            }
            r = requests.get("http://localhost:8080/search", params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return [
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "source": "searxng"
                    }
                    for item in data.get("results", [])[:max_results]
                ]
        except Exception:
            pass
        return []

    def fetch_url(self, url: str, max_chars: int = 5000) -> Dict:
        """Fetch and extract text content from a URL."""
        try:
            r = requests.get(url, headers=self.HEADERS, timeout=15)
            r.raise_for_status()

            # Basic HTML to text
            text = re.sub(r'<script[^>]*>.*?</script>', '', r.text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()

            return {
                "success": True,
                "url": url,
                "content": text[:max_chars],
                "length": len(text)
            }
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}
