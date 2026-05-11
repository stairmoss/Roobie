"""
Roobie Research Engine
Local research using SearXNG and crawl4ai for competitor analysis,
UI inspiration, SEO opportunities, and design trends.
"""

import json
import re
import requests
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from rich.console import Console

console = Console()


class ResearchEngine:
    """Research engine using SearXNG + crawl4ai for local-first web research."""

    def __init__(self, settings):
        self.settings = settings
        self.searxng_url = settings.research.searxng_url
        self.max_results = settings.research.max_search_results
        self.timeout = settings.research.research_timeout

    def research(self, query: str, max_results: int = None) -> List[Dict]:
        """Run a research query using SearXNG."""
        max_results = max_results or self.max_results
        results = []

        # Try SearXNG first
        searx_results = self._search_searxng(query, max_results)
        if searx_results:
            results.extend(searx_results)

        # Crawl top results for deeper analysis if crawl4ai available
        if self.settings.research.crawl4ai_enabled and results:
            for i, r in enumerate(results[:3]):
                url = r.get("url", "")
                if url:
                    crawled = self._crawl_url(url)
                    if crawled:
                        results[i]["crawled_content"] = crawled

        return results

    def research_competitors(self, niche: str, max_results: int = 5) -> List[Dict]:
        """Research competitor websites in a niche."""
        queries = [
            f"best {niche} websites 2024",
            f"{niche} website design inspiration",
            f"top {niche} landing pages",
        ]

        all_results = []
        for q in queries:
            results = self._search_searxng(q, max_results)
            if results:
                all_results.extend(results)

        # Deduplicate by URL
        seen = set()
        unique = []
        for r in all_results:
            url = r.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(r)

        return unique[:max_results * 2]

    def research_seo(self, topic: str) -> Dict:
        """Research SEO opportunities for a topic."""
        results = self._search_searxng(f"{topic} SEO keywords strategy", 5)
        return {
            "topic": topic,
            "results": results or [],
            "suggested_keywords": self._extract_keywords(results or []),
        }

    def research_design_trends(self, style: str = "modern") -> List[Dict]:
        """Research current design trends."""
        queries = [
            f"{style} web design trends 2024",
            f"{style} UI design patterns",
        ]
        results = []
        for q in queries:
            r = self._search_searxng(q, 5)
            if r:
                results.extend(r)
        return results

    def _search_searxng(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search using local SearXNG instance."""
        try:
            params = {
                "q": query,
                "format": "json",
                "categories": "general",
                "language": "en",
                "pageno": 1,
            }
            r = requests.get(
                f"{self.searxng_url}/search",
                params=params,
                timeout=self.timeout,
            )
            if r.status_code == 200:
                data = r.json()
                results = []
                for item in data.get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "summary": item.get("content", ""),
                        "source": "searxng",
                        "engine": item.get("engine", ""),
                    })
                return results
        except requests.ConnectionError:
            console.print("[yellow]⚠️ SearXNG not available (run locally on port 8080)[/yellow]")
        except Exception as e:
            console.print(f"[yellow]⚠️ SearXNG error: {e}[/yellow]")
        return []

    def _crawl_url(self, url: str) -> Optional[str]:
        """Crawl a URL using crawl4ai or requests fallback."""
        # Try crawl4ai first
        try:
            from crawl4ai import WebCrawler
            crawler = WebCrawler()
            crawler.warmup()
            result = crawler.run(url=url)
            if result.success:
                return result.markdown[:5000]  # Limit content size
        except ImportError:
            pass
        except Exception:
            pass

        # Fallback to basic requests
        try:
            headers = {"User-Agent": "Roobie/1.0 (Research Bot)"}
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                # Basic HTML to text extraction
                text = re.sub(r'<[^>]+>', ' ', r.text)
                text = re.sub(r'\s+', ' ', text).strip()
                return text[:3000]
        except Exception:
            pass

        return None

    def _extract_keywords(self, results: List[Dict]) -> List[str]:
        """Extract potential keywords from search results."""
        text = " ".join(r.get("title", "") + " " + r.get("summary", "") for r in results)
        # Simple keyword extraction: most frequent meaningful words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        stop_words = {"this", "that", "with", "from", "have", "been", "were", "your",
                      "will", "about", "more", "their", "which", "when", "what", "there",
                      "also", "into", "best", "most", "than", "only", "some", "other"}
        word_counts = {}
        for w in words:
            if w not in stop_words:
                word_counts[w] = word_counts.get(w, 0) + 1
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [w for w, c in sorted_words[:20]]
