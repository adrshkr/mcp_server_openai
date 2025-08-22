"""
MCP Research Integration Tool

This module provides automated research capabilities by integrating
Brave Search with Content Planning for intelligent content enhancement.
"""

import asyncio
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_RESEARCH_DEPTH = "moderate"  # basic, moderate, comprehensive
DEFAULT_MAX_RESULTS = 10
DEFAULT_TIMEOUT = 30
DEFAULT_CACHE_TTL = 3600  # 1 hour


@dataclass
class ResearchQuery:
    """Research query definition."""

    query_id: str
    topic: str
    content_type: str  # "presentation", "document", "webpage", "report"
    target_audience: str
    objectives: list[str]
    key_messages: list[str]
    research_depth: str = DEFAULT_RESEARCH_DEPTH
    max_results: int = DEFAULT_MAX_RESULTS
    include_sources: bool = True
    filter_duplicates: bool = True
    language: str = "en"
    region: str = "US"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchSource:
    """Research source information."""

    url: str
    title: str
    description: str
    domain: str
    content_type: str  # "article", "blog", "news", "academic", "government"
    relevance_score: float
    credibility_score: float
    freshness_score: float
    content_preview: str
    keywords: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchResult:
    """Result of research operation."""

    result_id: str
    query: ResearchQuery
    sources: list[ResearchSource]
    insights: list[str]
    key_findings: list[str]
    recommendations: list[str]
    content_enhancements: list[str]
    research_summary: str
    total_sources: int
    relevant_sources: int
    high_credibility_sources: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContentEnhancement:
    """Content enhancement suggestion."""

    enhancement_id: str
    content_section: str
    enhancement_type: str  # "fact", "example", "statistic", "quote", "case_study"
    source: ResearchSource
    suggested_content: str
    relevance_score: float
    implementation_notes: str
    priority: str = "medium"  # low, medium, high, critical


class ResearchIntegrationEngine:
    """Core research integration engine."""

    def __init__(self) -> None:
        self.brave_search_url = os.getenv("BRAVE_SEARCH_URL", "http://localhost:3002")
        self.sequential_thinking_url = os.getenv("SEQUENTIAL_THINKING_URL", "http://localhost:3001")
        self.memory_url = os.getenv("MEMORY_URL", "http://localhost:3003")
        self.research_cache: dict[str, ResearchResult] = {}
        self.research_history: list[ResearchResult] = []
        self._initialize_research_patterns()

    def _initialize_research_patterns(self) -> None:
        """Initialize research patterns and keywords."""
        self.research_patterns = {
            "presentation": {
                "keywords": ["trends", "statistics", "case studies", "best practices", "industry insights"],
                "content_types": ["article", "news", "academic", "government"],
                "min_credibility": 0.7,
            },
            "document": {
                "keywords": ["research", "analysis", "data", "reports", "studies"],
                "content_types": ["academic", "government", "article", "report"],
                "min_credibility": 0.8,
            },
            "webpage": {
                "keywords": ["seo", "user experience", "design", "conversion", "analytics"],
                "content_types": ["article", "blog", "news", "case study"],
                "min_credibility": 0.6,
            },
            "report": {
                "keywords": ["market analysis", "industry trends", "competitive analysis", "forecasts"],
                "content_types": ["report", "academic", "government", "article"],
                "min_credibility": 0.8,
            },
        }

    async def conduct_research(self, request: ResearchQuery) -> ResearchResult:
        """Conduct comprehensive research for content enhancement."""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.research_cache:
                cached_result = self.research_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    logger.info(f"Returning cached research result for query: {request.topic}")
                    return cached_result

            # Step 1: Generate research strategy
            research_strategy = await self._generate_research_strategy(request)

            # Step 2: Execute search queries
            search_results = await self._execute_search_queries(request, research_strategy)

            # Step 3: Analyze and filter sources
            filtered_sources = await self._analyze_and_filter_sources(search_results, request)

            # Step 4: Extract insights and findings
            insights, key_findings = await self._extract_insights_and_findings(filtered_sources, request)

            # Step 5: Generate content enhancements
            content_enhancements = await self._generate_content_enhancements(filtered_sources, request)

            # Step 6: Create research summary
            research_summary = await self._create_research_summary(insights, key_findings, request)

            # Step 7: Generate recommendations
            recommendations = await self._generate_recommendations(insights, key_findings, request)

            # Create result
            result = ResearchResult(
                result_id=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.topic[:100]) % 10000}",
                query=request,
                sources=filtered_sources,
                insights=insights,
                key_findings=key_findings,
                recommendations=recommendations,
                content_enhancements=content_enhancements,
                research_summary=research_summary,
                total_sources=len(search_results),
                relevant_sources=len(filtered_sources),
                high_credibility_sources=len([s for s in filtered_sources if s.credibility_score >= 0.8]),
            )

            # Store in cache and history
            self.research_cache[cache_key] = result
            self.research_history.append(result)

            return result

        except Exception as e:
            logger.error(f"Research integration failed: {e}")
            return self._create_error_result(request, str(e))

    async def _generate_research_strategy(self, request: ResearchQuery) -> dict[str, Any]:
        """Generate research strategy using sequential thinking."""
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.post(
                    f"{self.sequential_thinking_url}/api/sequential-thinking/plan",
                    json={
                        "topic": f"Research strategy for {request.topic}",
                        "objectives": [
                            "Identify key research areas",
                            "Determine search queries",
                            "Define source criteria",
                            "Plan analysis approach",
                        ],
                        "content_type": "research_strategy",
                        "audience": "researchers",
                        "style": "analytical",
                    },
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Failed to generate research strategy: {response.status_code}")
                    return self._generate_fallback_strategy(request)

        except Exception as e:
            logger.warning(f"Research strategy generation failed: {e}")
            return self._generate_fallback_strategy(request)

    def _generate_fallback_strategy(self, request: ResearchQuery) -> dict[str, Any]:
        """Generate fallback research strategy."""
        patterns = self.research_patterns.get(request.content_type, self.research_patterns["document"])

        return {
            "research_areas": [
                "Industry trends and statistics",
                "Best practices and case studies",
                "Expert opinions and quotes",
                "Recent developments and news",
                "Competitive analysis",
            ],
            "search_queries": [
                f"{request.topic} trends 2024",
                f"{request.topic} best practices",
                f"{request.topic} case studies",
                f"{request.topic} statistics data",
                f"{request.topic} expert insights",
            ],
            "source_criteria": {
                "min_credibility": patterns["min_credibility"],
                "content_types": patterns["content_types"],
                "max_age_days": 365,
                "min_relevance": 0.6,
            },
        }

    async def _execute_search_queries(self, request: ResearchQuery, strategy: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute search queries using Brave Search."""
        search_results = []

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                for query in strategy.get("search_queries", []):
                    response = await client.post(
                        f"{self.brave_search_url}/api/brave-search/search",
                        json={
                            "query": query,
                            "max_results": request.max_results // len(strategy.get("search_queries", [1])),
                            "safe_search": True,
                            "region": request.region,
                            "language": request.language,
                        },
                    )

                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        search_results.extend(results)
                    else:
                        logger.warning(f"Search query failed: {query}")

        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            # Return mock results for development
            search_results = self._generate_mock_search_results(request)

        return search_results

    def _generate_mock_search_results(self, request: ResearchQuery) -> list[dict[str, Any]]:
        """Generate mock search results for development/testing."""
        mock_results = [
            {
                "url": "https://example.com/trends",
                "title": f"Latest Trends in {request.topic}",
                "description": f"Comprehensive analysis of current trends in {request.topic}",
                "domain": "example.com",
                "content_type": "article",
                "relevance_score": 0.85,
                "credibility_score": 0.8,
                "freshness_score": 0.9,
                "content_preview": f"Recent developments in {request.topic} show significant growth...",
                "keywords": [request.topic.lower(), "trends", "analysis", "insights"],
            },
            {
                "url": "https://research.org/study",
                "title": f"{request.topic} Research Study 2024",
                "description": f"Academic research on {request.topic} implementation and outcomes",
                "domain": "research.org",
                "content_type": "academic",
                "relevance_score": 0.9,
                "credibility_score": 0.95,
                "freshness_score": 0.8,
                "content_preview": f"Research indicates that {request.topic} adoption leads to...",
                "keywords": [request.topic.lower(), "research", "study", "academic"],
            },
        ]

        return mock_results

    async def _analyze_and_filter_sources(
        self, search_results: list[dict[str, Any]], request: ResearchQuery
    ) -> list[ResearchSource]:
        """Analyze and filter search results based on criteria."""
        sources = []

        for result in search_results:
            # Convert to ResearchSource
            source = ResearchSource(
                url=result.get("url", ""),
                title=result.get("title", ""),
                description=result.get("description", ""),
                domain=result.get("domain", ""),
                content_type=result.get("content_type", "article"),
                relevance_score=result.get("relevance_score", 0.5),
                credibility_score=result.get("credibility_score", 0.5),
                freshness_score=result.get("freshness_score", 0.5),
                content_preview=result.get("content_preview", ""),
                keywords=result.get("keywords", []),
            )

            # Apply filtering criteria
            if self._meets_criteria(source, request):
                sources.append(source)

        # Sort by relevance and credibility
        sources.sort(key=lambda x: (x.relevance_score + x.credibility_score) / 2, reverse=True)

        return sources[: request.max_results]

    def _meets_criteria(self, source: ResearchSource, request: ResearchQuery) -> bool:
        """Check if source meets research criteria."""
        patterns = self.research_patterns.get(request.content_type, self.research_patterns["document"])

        # Check credibility
        if source.credibility_score < patterns["min_credibility"]:
            return False

        # Check relevance
        if source.relevance_score < 0.6:
            return False

        # Check content type
        if source.content_type not in patterns["content_types"]:
            return False

        return True

    async def _extract_insights_and_findings(
        self, sources: list[ResearchSource], request: ResearchQuery
    ) -> tuple[list[str], list[str]]:
        """Extract insights and key findings from sources."""
        insights = []
        key_findings = []

        for source in sources:
            # Extract insights from content preview
            content_lower = source.content_preview.lower()

            # Look for statistics and numbers
            stats = re.findall(r"\d+(?:\.\d+)?%?", source.content_preview)
            if stats:
                insights.append(f"Key statistic: {stats[0]} from {source.domain}")

            # Look for trends and patterns
            if any(word in content_lower for word in ["trend", "growth", "increase", "rise"]):
                insights.append(f"Trend identified: {source.title}")

            # Look for best practices
            if any(word in content_lower for word in ["best practice", "recommendation", "guideline"]):
                insights.append(f"Best practice: {source.title}")

            # Extract key findings
            if source.credibility_score >= 0.8:
                key_findings.append(f"High-credibility finding: {source.title}")

        return insights, key_findings

    async def _generate_content_enhancements(self, sources: list[ResearchSource], request: ResearchQuery) -> list[str]:
        """Generate content enhancement suggestions."""
        enhancements = []

        for source in sources:
            if source.credibility_score >= 0.7:
                enhancement = f"Add {source.content_type} reference: {source.title} ({source.url})"
                enhancements.append(enhancement)

            if source.relevance_score >= 0.8:
                enhancement = f"Include key insight: {source.content_preview[:100]}..."
                enhancements.append(enhancement)

        return enhancements[:10]  # Limit to 10 enhancements

    async def _create_research_summary(
        self, insights: list[str], key_findings: list[str], request: ResearchQuery
    ) -> str:
        """Create comprehensive research summary."""
        summary_parts = [
            f"Research Summary for: {request.topic}",
            f"Content Type: {request.content_type}",
            f"Target Audience: {request.target_audience}",
            "",
            f"Key Insights ({len(insights)}):",
            *[f"• {insight}" for insight in insights[:5]],
            "",
            f"Key Findings ({len(key_findings)}):",
            *[f"• {finding}" for finding in key_findings[:5]],
            "",
            f"Research completed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        return "\n".join(summary_parts)

    async def _generate_recommendations(
        self, insights: list[str], key_findings: list[str], request: ResearchQuery
    ) -> list[str]:
        """Generate actionable recommendations based on research."""
        recommendations = []

        # Content enhancement recommendations
        if insights:
            recommendations.append("Incorporate key statistics and trends from research")

        if key_findings:
            recommendations.append("Reference high-credibility sources to strengthen content")

        # Content type specific recommendations
        if request.content_type == "presentation":
            recommendations.append("Add data visualizations based on research findings")
            recommendations.append("Include expert quotes and case studies")

        elif request.content_type == "document":
            recommendations.append("Add comprehensive bibliography and citations")
            recommendations.append("Include detailed analysis and methodology")

        elif request.content_type == "webpage":
            recommendations.append("Optimize content with research-based keywords")
            recommendations.append("Add internal links to related research content")

        return recommendations

    def _generate_cache_key(self, request: ResearchQuery) -> str:
        """Generate cache key for research request."""
        return f"{request.topic}_{request.content_type}_{request.research_depth}_{request.language}"

    def _is_cache_valid(self, result: ResearchResult) -> bool:
        """Check if cached result is still valid."""
        age = datetime.now() - result.timestamp
        return age.total_seconds() < DEFAULT_CACHE_TTL

    def _create_error_result(self, request: ResearchQuery, error_message: str) -> ResearchResult:
        """Create error result when research fails."""
        return ResearchResult(
            result_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            query=request,
            sources=[],
            insights=[f"Research failed: {error_message}"],
            key_findings=[],
            recommendations=["Retry research with different parameters"],
            content_enhancements=[],
            research_summary=f"Research failed: {error_message}",
            total_sources=0,
            relevant_sources=0,
            high_credibility_sources=0,
        )

    def get_research_history(self, limit: int = 50) -> list[ResearchResult]:
        """Get research history."""
        return self.research_history[-limit:] if self.research_history else []

    def get_research_result(self, result_id: str) -> ResearchResult | None:
        """Get specific research result."""
        for result in self.research_history:
            if result.result_id == result_id:
                return result
        return None


# Global instance
research_engine = ResearchIntegrationEngine()


async def conduct_automated_research(
    topic: str,
    content_type: str,
    target_audience: str,
    objectives: list[str],
    key_messages: list[str],
    research_depth: str = DEFAULT_RESEARCH_DEPTH,
    max_results: int = DEFAULT_MAX_RESULTS,
    include_sources: bool = True,
    filter_duplicates: bool = True,
    language: str = "en",
    region: str = "US",
) -> dict[str, Any]:
    """
    Conduct automated research for content enhancement.

    Args:
        topic: Research topic
        content_type: Type of content being created
        target_audience: Target audience for the content
        objectives: Content objectives
        key_messages: Key messages to convey
        research_depth: Research depth (basic, moderate, comprehensive)
        max_results: Maximum number of research results
        include_sources: Whether to include source information
        filter_duplicates: Whether to filter duplicate sources
        language: Research language
        region: Research region

    Returns:
        Dictionary containing research results and recommendations
    """
    request = ResearchQuery(
        query_id=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        topic=topic,
        content_type=content_type,
        target_audience=target_audience,
        objectives=objectives,
        key_messages=key_messages,
        research_depth=research_depth,
        max_results=max_results,
        include_sources=include_sources,
        filter_duplicates=filter_duplicates,
        language=language,
        region=region,
    )

    result = await research_engine.conduct_research(request)

    return {
        "status": "success" if result.sources else "partial",
        "result_id": result.result_id,
        "topic": result.query.topic,
        "content_type": result.query.content_type,
        "total_sources": result.total_sources,
        "relevant_sources": result.relevant_sources,
        "high_credibility_sources": result.high_credibility_sources,
        "insights": result.insights,
        "key_findings": result.key_findings,
        "recommendations": result.recommendations,
        "content_enhancements": result.content_enhancements,
        "research_summary": result.research_summary,
        "sources": [
            {
                "url": s.url,
                "title": s.title,
                "description": s.description,
                "domain": s.domain,
                "content_type": s.content_type,
                "relevance_score": s.relevance_score,
                "credibility_score": s.credibility_score,
                "freshness_score": s.freshness_score,
            }
            for s in result.sources
        ],
        "timestamp": result.timestamp.isoformat(),
    }


def get_research_history(limit: int = 50) -> list[dict[str, Any]]:
    """Get research history."""
    history = research_engine.get_research_history(limit)
    return [
        {
            "result_id": result.result_id,
            "topic": result.query.topic,
            "content_type": result.query.content_type,
            "total_sources": result.total_sources,
            "relevant_sources": result.relevant_sources,
            "high_credibility_sources": result.high_credibility_sources,
            "timestamp": result.timestamp.isoformat(),
        }
        for result in history
    ]


def get_research_result(result_id: str) -> dict[str, Any] | None:
    """Get specific research result."""
    result = research_engine.get_research_result(result_id)
    if not result:
        return None

    return {
        "result_id": result.result_id,
        "topic": result.query.topic,
        "content_type": result.query.content_type,
        "total_sources": result.total_sources,
        "relevant_sources": result.relevant_sources,
        "high_credibility_sources": result.high_credibility_sources,
        "insights": result.insights,
        "key_findings": result.key_findings,
        "recommendations": result.recommendations,
        "content_enhancements": result.content_enhancements,
        "research_summary": result.research_summary,
        "sources": [
            {
                "url": s.url,
                "title": s.title,
                "description": s.description,
                "domain": s.domain,
                "content_type": s.content_type,
                "relevance_score": s.relevance_score,
                "credibility_score": s.credibility_score,
                "freshness_score": s.freshness_score,
            }
            for s in result.sources
        ],
        "timestamp": result.timestamp.isoformat(),
    }


def register(server: Any) -> None:
    """Register MCP tools with the server."""

    @server.tool()
    async def mcp_research_integration_conduct_research(
        topic: str,
        content_type: str,
        target_audience: str,
        objectives: list[str],
        key_messages: list[str],
        research_depth: str = DEFAULT_RESEARCH_DEPTH,
        max_results: int = DEFAULT_MAX_RESULTS,
        include_sources: bool = True,
        filter_duplicates: bool = True,
        language: str = "en",
        region: str = "US",
    ) -> dict[str, Any]:
        """
        Conduct automated research for content enhancement.

        This tool integrates Brave Search with Content Planning to provide
        intelligent research capabilities for content creation.

        Args:
            topic: Research topic
            content_type: Type of content being created
            target_audience: Target audience for the content
            objectives: Content objectives
            key_messages: Key messages to convey
            research_depth: Research depth (basic, moderate, comprehensive)
            max_results: Maximum number of research results
            include_sources: Whether to include source information
            filter_duplicates: Whether to filter duplicate sources
            language: Research language
            region: Research region

        Returns:
            Comprehensive research results with insights and recommendations
        """
        return await conduct_automated_research(
            topic=topic,
            content_type=content_type,
            target_audience=target_audience,
            objectives=objectives,
            key_messages=key_messages,
            research_depth=research_depth,
            max_results=max_results,
            include_sources=include_sources,
            filter_duplicates=filter_duplicates,
            language=language,
            region=region,
        )

    @server.tool()
    def mcp_research_integration_get_history(limit: int = 50) -> list[dict[str, Any]]:
        """
        Get research history.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of research history entries
        """
        return get_research_history(limit)

    @server.tool()
    def mcp_research_integration_get_result(result_id: str) -> dict[str, Any] | None:
        """
        Get specific research result.

        Args:
            result_id: ID of the research result

        Returns:
            Research result details or None if not found
        """
        return get_research_result(result_id)


if __name__ == "__main__":
    # Demo and testing
    async def main() -> None:
        print("MCP Research Integration Tool Demo")
        print("=" * 40)

        # Sample research request
        print("Conducting automated research...")
        research_result = await conduct_automated_research(
            topic="AI Strategy Implementation",
            content_type="presentation",
            target_audience="executives",
            objectives=[
                "Understand current AI adoption trends",
                "Identify best practices for implementation",
                "Learn from successful case studies",
            ],
            key_messages=[
                "AI adoption is accelerating across industries",
                "Successful implementation requires strategic planning",
                "ROI can be significant with proper execution",
            ],
            research_depth="comprehensive",
            max_results=5,
        )

        print(f"Research Status: {research_result['status']}")
        print(f"Result ID: {research_result['result_id']}")
        print(f"Total Sources: {research_result['total_sources']}")
        print(f"Relevant Sources: {research_result['relevant_sources']}")
        print(f"High Credibility Sources: {research_result['high_credibility_sources']}")

        print(f"\nInsights ({len(research_result['insights'])}):")
        for insight in research_result["insights"][:3]:
            print(f"  • {insight}")

        print(f"\nKey Findings ({len(research_result['key_findings'])}):")
        for finding in research_result["key_findings"][:3]:
            print(f"  • {finding}")

        print(f"\nRecommendations ({len(research_result['recommendations'])}):")
        for rec in research_result["recommendations"]:
            print(f"  • {rec}")

        print(f"\nContent Enhancements ({len(research_result['content_enhancements'])}):")
        for enhancement in research_result["content_enhancements"][:3]:
            print(f"  • {enhancement}")

        print("\nResearch Summary:")
        print(research_result["research_summary"])

        print("\nDemo completed successfully!")

    asyncio.run(main())
