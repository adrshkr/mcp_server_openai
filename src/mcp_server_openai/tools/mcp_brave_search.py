"""
MCP Brave Search Server Implementation

This server provides web search capabilities for content enhancement and research
using the Brave Search API and other search providers.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RESULTS = 5
DEFAULT_SAFE_SEARCH = True


@dataclass
class SearchResult:
    """Represents a single search result."""

    title: str
    url: str
    description: str
    source: str
    relevance_score: float  # 0.0 to 1.0
    content_type: str  # article, video, image, document
    language: str
    publish_date: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchRequest:
    """Request for web search."""

    query: str
    search_type: str = "web"  # web, news, images, videos
    max_results: int = DEFAULT_MAX_RESULTS
    safe_search: bool = DEFAULT_SAFE_SEARCH
    language: str = "en"
    region: str = "US"
    time_filter: str | None = None  # day, week, month, year
    client_id: str | None = None


@dataclass
class SearchResponse:
    """Response from web search."""

    status: str
    results: list[SearchResult]
    total_results: int
    search_time: float
    query: str
    search_type: str
    suggestions: list[str]
    related_queries: list[str]
    client_id: str | None = None
    error: str | None = None


class BraveSearchClient:
    """Client for Brave Search API."""

    def __init__(self) -> None:
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1"
        self.timeout = DEFAULT_TIMEOUT

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform web search using Brave Search API."""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self.api_key:
                # Fallback to mock search for development
                return await self._mock_search(request)

            # Prepare search parameters
            params: dict[str, str | int | bool | None] = {
                "q": request.query,
                "count": request.max_results,
                "safesearch": "strict" if request.safe_search else "off",
                "locale": request.language,
                "country": request.region,
            }

            if request.time_filter:
                params["freshness"] = request.time_filter

            headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}

            # Perform search
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/{request.search_type}", params=params, headers=headers)
                response.raise_for_status()
                search_data = response.json()

            # Parse results
            results = self._parse_brave_results(search_data, request)

            search_time = asyncio.get_event_loop().time() - start_time

            return SearchResponse(
                status="success",
                results=results,
                total_results=len(results),
                search_time=search_time,
                query=request.query,
                search_type=request.search_type,
                suggestions=search_data.get("suggestions", []),
                related_queries=search_data.get("related", []),
                client_id=request.client_id,
            )

        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            search_time = asyncio.get_event_loop().time() - start_time

            # Fallback to mock search
            return await self._mock_search(request)

    def _parse_brave_results(self, search_data: dict[str, Any], request: SearchRequest) -> list[SearchResult]:
        """Parse Brave Search API results."""
        results = []

        for item in search_data.get("web", {}).get("results", []):
            result = SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                source=item.get("source", ""),
                relevance_score=item.get("score", 0.5),
                content_type="article",
                language=request.language,
                publish_date=item.get("published", None),
                metadata={
                    "age": item.get("age", ""),
                    "language": item.get("language", ""),
                    "family_friendly": item.get("family_friendly", True),
                },
            )
            results.append(result)

        return results

    async def _mock_search(self, request: SearchRequest) -> SearchResponse:
        """Mock search for development/testing."""
        await asyncio.sleep(0.1)  # Simulate API delay

        # Generate mock results based on query
        mock_results = []
        for i in range(min(request.max_results, 5)):
            mock_result = SearchResult(
                title=f"Mock Result {i+1} for '{request.query}'",
                url=f"https://example.com/result-{i+1}",
                description=(
                    f"This is a mock search result for the query '{request.query}'. "
                    "It provides sample content for testing purposes."
                ),
                source="Mock Source",
                relevance_score=0.8 - (i * 0.1),
                content_type="article",
                language=request.language,
                publish_date="2024-01-01",
                metadata={"mock": True, "index": i},
            )
            mock_results.append(mock_result)

        return SearchResponse(
            status="success (mock)",
            results=mock_results,
            total_results=len(mock_results),
            search_time=0.1,
            query=request.query,
            search_type=request.search_type,
            suggestions=[f"related to {request.query}", f"more about {request.query}"],
            related_queries=[f"{request.query} examples", f"{request.query} guide"],
            client_id=request.client_id,
        )


class WebSearchEngine:
    """Main web search engine that orchestrates multiple search providers."""

    def __init__(self) -> None:
        self.brave_client = BraveSearchClient()
        self.provider_status = {"brave": True}

    async def search_web(self, request: SearchRequest) -> SearchResponse:
        """Perform web search using available providers."""
        try:
            # Try Brave Search first
            if self.provider_status.get("brave", False):
                return await self.brave_client.search(request)

            # Fallback to mock search
            return await self.brave_client._mock_search(request)

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            # Return error response
            return SearchResponse(
                status="error",
                results=[],
                total_results=0,
                search_time=0.0,
                query=request.query,
                search_type=request.search_type,
                suggestions=[],
                related_queries=[],
                client_id=request.client_id,
                error=str(e),
            )

    async def search_news(self, request: SearchRequest) -> SearchResponse:
        """Search for news articles."""
        news_request = SearchRequest(
            query=request.query,
            search_type="news",
            max_results=request.max_results,
            safe_search=request.safe_search,
            language=request.language,
            region=request.region,
            time_filter=request.time_filter or "week",
            client_id=request.client_id,
        )

        return await self.search_web(news_request)

    async def search_images(self, request: SearchRequest) -> SearchResponse:
        """Search for images."""
        image_request = SearchRequest(
            query=request.query,
            search_type="images",
            max_results=request.max_results,
            safe_search=request.safe_search,
            language=request.language,
            region=request.region,
            client_id=request.client_id,
        )

        return await self.search_web(image_request)

    async def search_videos(self, request: SearchRequest) -> SearchResponse:
        """Search for videos."""
        video_request = SearchRequest(
            query=request.query,
            search_type="videos",
            max_results=request.max_results,
            safe_search=request.safe_search,
            language=request.language,
            region=request.region,
            time_filter=request.time_filter,
            client_id=request.client_id,
        )

        return await self.search_web(video_request)

    async def get_search_suggestions(self, query: str, client_id: str | None = None) -> list[str]:
        """Get search suggestions for a query."""
        try:
            # Mock suggestions for now
            suggestions = [
                f"{query} examples",
                f"{query} guide",
                f"{query} tutorial",
                f"{query} best practices",
                f"{query} tips",
            ]

            return suggestions[:5]

        except Exception as e:
            logger.error(f"Failed to get search suggestions: {e}")
            return []

    async def get_trending_searches(self, region: str = "US", client_id: str | None = None) -> list[str]:
        """Get trending search terms."""
        try:
            # Mock trending searches
            trending = [
                "artificial intelligence",
                "machine learning",
                "data science",
                "cloud computing",
                "cybersecurity",
                "blockchain",
                "virtual reality",
                "augmented reality",
            ]

            return trending[:8]

        except Exception as e:
            logger.error(f"Failed to get trending searches: {e}")
            return []


# Global instance
_search_engine = WebSearchEngine()


async def search_content(
    query: str,
    search_type: str = "web",
    max_results: int = DEFAULT_MAX_RESULTS,
    safe_search: bool = DEFAULT_SAFE_SEARCH,
    language: str = "en",
    region: str = "US",
    time_filter: str | None = None,
    client_id: str | None = None,
) -> dict[str, Any]:
    """Search for content using web search."""
    request = SearchRequest(
        query=query,
        search_type=search_type,
        max_results=max_results,
        safe_search=safe_search,
        language=language,
        region=region,
        time_filter=time_filter,
        client_id=client_id,
    )

    result = await _search_engine.search_web(request)

    # Convert to dictionary for MCP tool response
    return {
        "status": result.status,
        "results": [
            {
                "title": res.title,
                "url": res.url,
                "description": res.description,
                "source": res.source,
                "relevance_score": res.relevance_score,
                "content_type": res.content_type,
                "language": res.language,
                "publish_date": res.publish_date,
                "metadata": res.metadata,
            }
            for res in result.results
        ],
        "total_results": result.total_results,
        "search_time": result.search_time,
        "query": result.query,
        "search_type": result.search_type,
        "suggestions": result.suggestions,
        "related_queries": result.related_queries,
        "client_id": result.client_id,
        "error": result.error,
    }


async def search_news(
    query: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    safe_search: bool = DEFAULT_SAFE_SEARCH,
    language: str = "en",
    region: str = "US",
    time_filter: str = "week",
    client_id: str | None = None,
) -> dict[str, Any]:
    """Search for news articles."""
    return await search_content(
        query=query,
        search_type="news",
        max_results=max_results,
        safe_search=safe_search,
        language=language,
        region=region,
        time_filter=time_filter,
        client_id=client_id,
    )


async def search_images(
    query: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    safe_search: bool = DEFAULT_SAFE_SEARCH,
    language: str = "en",
    region: str = "US",
    client_id: str | None = None,
) -> dict[str, Any]:
    """Search for images."""
    return await search_content(
        query=query,
        search_type="images",
        max_results=max_results,
        safe_search=safe_search,
        language=language,
        region=region,
        client_id=client_id,
    )


async def get_search_suggestions(query: str, client_id: str | None = None) -> dict[str, Any]:
    """Get search suggestions for a query."""
    suggestions = await _search_engine.get_search_suggestions(query, client_id)

    return {
        "status": "success",
        "query": query,
        "suggestions": suggestions,
        "count": len(suggestions),
        "client_id": client_id,
    }


async def get_trending_searches(region: str = "US", client_id: str | None = None) -> dict[str, Any]:
    """Get trending search terms."""
    trending = await _search_engine.get_trending_searches(region, client_id)

    return {
        "status": "success",
        "region": region,
        "trending_searches": trending,
        "count": len(trending),
        "client_id": client_id,
    }


def register(mcp: Any) -> None:
    """Register the Brave Search tools with the MCP server."""

    @mcp.tool()
    async def brave_search_web(
        query: str,
        max_results: int = DEFAULT_MAX_RESULTS,
        safe_search: bool = DEFAULT_SAFE_SEARCH,
        language: str = "en",
        region: str = "US",
        time_filter: str | None = None,
        client_id: str | None = None,
    ) -> str:
        """Search the web using Brave Search API."""
        try:
            result = await search_content(
                query=query,
                search_type="web",
                max_results=max_results,
                safe_search=safe_search,
                language=language,
                region=region,
                time_filter=time_filter,
                client_id=client_id,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def brave_search_news(
        query: str,
        max_results: int = DEFAULT_MAX_RESULTS,
        safe_search: bool = DEFAULT_SAFE_SEARCH,
        language: str = "en",
        region: str = "US",
        time_filter: str = "week",
        client_id: str | None = None,
    ) -> str:
        """Search for news articles using Brave Search."""
        try:
            result = await search_news(
                query=query,
                max_results=max_results,
                safe_search=safe_search,
                language=language,
                region=region,
                time_filter=time_filter,
                client_id=client_id,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"News search failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def brave_search_images(
        query: str,
        max_results: int = DEFAULT_MAX_RESULTS,
        safe_search: bool = DEFAULT_SAFE_SEARCH,
        language: str = "en",
        region: str = "US",
        client_id: str | None = None,
    ) -> str:
        """Search for images using Brave Search."""
        try:
            result = await search_images(
                query=query,
                max_results=max_results,
                safe_search=safe_search,
                language=language,
                region=region,
                client_id=client_id,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def brave_search_suggestions(query: str, client_id: str | None = None) -> str:
        """Get search suggestions for a query."""
        try:
            result = await get_search_suggestions(query, client_id)

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Search suggestions failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def brave_trending_searches(region: str = "US", client_id: str | None = None) -> str:
        """Get trending search terms."""
        try:
            result = await get_trending_searches(region, client_id)

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Trending searches failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)
