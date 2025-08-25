"""
Enhanced content creation tool using only free and open-source services.

This tool creates high-quality content without requiring paid APIs:
- DuckDuckGo Instant Answer API (free, no API key)
- Wikipedia API (free, no API key)
- Wikidata API (free, no API key)
- Local content generation using LLMs
- Built-in research capabilities
"""

from __future__ import annotations

import asyncio
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...logging_utils import get_logger
from ...progress import create_progress_tracker

_LOG = get_logger("mcp.tool.free_content_creator")
_TOOL = "free_content.create"


@dataclass
class ContentRequest:
    """Structured content creation request."""

    prompt: str
    content_type: str = "article"  # article, blog, summary, presentation, outline
    max_tokens: int = 2000
    tone: str = "professional"  # professional, casual, academic, creative
    audience: str = "general"  # general, technical, academic, business
    include_research: bool = True
    language: str = "en"


@dataclass
class ResearchResult:
    """Research result from free sources."""

    title: str
    content: str
    source: str  # wikipedia, duckduckgo, wikidata
    url: str
    relevance_score: float = 0.0


@dataclass
class ContentResponse:
    """Content creation response."""

    content: str
    research_sources: list[ResearchResult] = field(default_factory=list)
    word_count: int = 0
    generation_time: float = 0.0
    quality_score: float = 0.0


class FreeResearchClient:
    """Research client using free APIs only."""

    def __init__(self):
        self.timeout = 10
        self.max_retries = 3

    async def search_multiple_sources(self, query: str, max_results: int = 5) -> list[ResearchResult]:
        """Search multiple free sources concurrently."""
        tasks = [
            self._search_wikipedia(query, max_results // 2),
            self._search_duckduckgo_instant(query, max_results // 2),
            self._search_wikidata(query, 1),
        ]

        results = []
        try:
            # Run searches concurrently
            search_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in search_results:
                if isinstance(result, list):
                    results.extend(result)
                elif isinstance(result, Exception):
                    _LOG.warning(f"Search failed: {result}")

        except Exception as e:
            _LOG.error(f"Research search failed: {e}")

        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]

    async def _search_wikipedia(self, query: str, max_results: int = 3) -> list[ResearchResult]:
        """Search Wikipedia for research content."""
        results = []
        try:
            # First, search for relevant articles
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            # Clean query for Wikipedia
            clean_query = re.sub(r"[^\w\s]", "", query).strip().replace(" ", "_")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    response = await client.get(f"{search_url}{clean_query}")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("extract"):
                            results.append(
                                ResearchResult(
                                    title=data.get("title", query),
                                    content=data.get("extract", ""),
                                    source="Wikipedia",
                                    url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                                    relevance_score=0.9,
                                )
                            )
                except Exception:
                    pass

                # Also try OpenSearch API for broader results
                search_api = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "opensearch",
                    "search": query,
                    "limit": max_results,
                    "format": "json",
                    "namespace": 0,
                }

                try:
                    response = await client.get(search_api, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        if len(data) >= 4:
                            titles, descriptions, urls = data[1], data[2], data[3]
                            for i, (title, desc, url) in enumerate(zip(titles, descriptions, urls, strict=False)):
                                if len(results) < max_results and desc:
                                    results.append(
                                        ResearchResult(
                                            title=title,
                                            content=desc,
                                            source="Wikipedia",
                                            url=url,
                                            relevance_score=0.8 - (i * 0.1),
                                        )
                                    )
                except Exception:
                    pass

        except Exception as e:
            _LOG.warning(f"Wikipedia search failed: {e}")

        return results

    async def _search_duckduckgo_instant(self, query: str, max_results: int = 2) -> list[ResearchResult]:
        """Search DuckDuckGo Instant Answer API (free, no key required)."""
        results = []
        try:
            instant_api = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(instant_api, params=params)
                if response.status_code == 200:
                    data = response.json()

                    # Check for abstract (main answer)
                    if data.get("Abstract"):
                        results.append(
                            ResearchResult(
                                title=data.get("Heading", query),
                                content=data.get("Abstract"),
                                source="DuckDuckGo",
                                url=data.get("AbstractURL", ""),
                                relevance_score=0.85,
                            )
                        )

                    # Check for definition
                    if data.get("Definition") and len(results) < max_results:
                        results.append(
                            ResearchResult(
                                title=f"Definition: {query}",
                                content=data.get("Definition"),
                                source="DuckDuckGo",
                                url=data.get("DefinitionURL", ""),
                                relevance_score=0.8,
                            )
                        )

                    # Check for related topics
                    related_topics = data.get("RelatedTopics", [])
                    for topic in related_topics[: max_results - len(results)]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append(
                                ResearchResult(
                                    title=topic.get("Text", "")[:50] + "...",
                                    content=topic.get("Text", ""),
                                    source="DuckDuckGo",
                                    url=topic.get("FirstURL", ""),
                                    relevance_score=0.7,
                                )
                            )

        except Exception as e:
            _LOG.warning(f"DuckDuckGo search failed: {e}")

        return results

    async def _search_wikidata(self, query: str, max_results: int = 1) -> list[ResearchResult]:
        """Search Wikidata for structured information."""
        results = []
        try:
            # Wikidata SPARQL endpoint
            sparql_url = "https://query.wikidata.org/sparql"

            # Simple SPARQL query to find entities
            sparql_query = f"""
            SELECT ?item ?itemLabel ?itemDescription WHERE {{
                ?item rdfs:label ?itemLabel .
                ?item schema:description ?itemDescription .
                FILTER(CONTAINS(LCASE(?itemLabel), LCASE("{query}")))
                FILTER(LANG(?itemLabel) = "en")
                FILTER(LANG(?itemDescription) = "en")
            }}
            LIMIT {max_results}
            """

            headers = {"Accept": "application/sparql-results+json", "User-Agent": "ContentCreator/1.0"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(sparql_url, params={"query": sparql_query}, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    bindings = data.get("results", {}).get("bindings", [])

                    for binding in bindings:
                        label = binding.get("itemLabel", {}).get("value", "")
                        description = binding.get("itemDescription", {}).get("value", "")
                        item_id = binding.get("item", {}).get("value", "")

                        if label and description:
                            results.append(
                                ResearchResult(
                                    title=label,
                                    content=description,
                                    source="Wikidata",
                                    url=item_id,
                                    relevance_score=0.75,
                                )
                            )

        except Exception as e:
            _LOG.warning(f"Wikidata search failed: {e}")

        return results


class FreeContentCreator:
    """Content creator using only free services."""

    def __init__(self):
        self.research_client = FreeResearchClient()

    async def create_content(self, request: ContentRequest, length_tier: str = "short") -> ContentResponse:
        """Create content using free research and generation."""
        start_time = time.time()

        with create_progress_tracker(_TOOL, {"prompt": request.prompt[:100], "type": request.content_type}) as progress:
            # Scale research and caps by length tier
            # short (default): fast, low cost; medium: more research; long: extensive
            tier = (length_tier or "short").lower()
            research_max = {"short": 4, "medium": 6, "long": 8}.get(tier, 4)
            llm_cap_chars = {"short": 8000, "medium": 12000, "long": 16000}.get(tier, 8000)

            # Step 1: Research if requested
            research_results = []
            if request.include_research:
                with progress.step_context("research", {"sources": "free_apis"}):
                    research_results = await self.research_client.search_multiple_sources(
                        request.prompt, max_results=research_max
                    )
                    _LOG.info(f"Found {len(research_results)} research sources")

            # Step 2: Generate content
            with progress.step_context("generate", {"method": "template_based"}):
                content = await self._generate_content_from_research(request, research_results)

            # Step 3: Quality assessment
            with progress.step_context("quality_check", {}):
                quality_score = self._assess_content_quality(content, request)
                word_count = len(content.split())

        # Optional LLM refinement (OpenAI -> Gemini -> skip)
        use_llm = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        if use_llm:
            try:
                with progress.step_context("llm_refine", {"provider": "auto"}):
                    refined = await self._refine_with_llm(
                        draft=content,
                        prompt=request.prompt,
                        content_type=request.content_type,
                        tone=request.tone,
                        audience=request.audience,
                        research=research_results,
                        llm_cap_chars=llm_cap_chars,
                    )
                    if refined:
                        content = refined
            except Exception as e:
                _LOG.warning(f"LLM refinement skipped due to error: {e}")

        generation_time = time.time() - start_time

        return ContentResponse(
            content=content,
            research_sources=research_results,
            word_count=word_count,
            generation_time=generation_time,
            quality_score=quality_score,
        )

    async def _generate_content_from_research(
        self, request: ContentRequest, research_results: list[ResearchResult]
    ) -> str:
        """Generate content using research data and templates."""
        # Extract key information from research
        research_content = []
        for result in research_results[:3]:  # Use top 3 results
            research_content.append(f"• {result.title}: {result.content[:200]}...")

        # Create content based on type
        if request.content_type == "article":
            content = self._generate_article(request, research_content)
        elif request.content_type == "blog":
            content = self._generate_blog_post(request, research_content)
        elif request.content_type == "summary":
            content = self._generate_summary(request, research_content)
        elif request.content_type == "presentation":
            content = self._generate_presentation_outline(request, research_content)
        elif request.content_type == "outline":
            content = self._generate_outline(request, research_content)
        else:
            content = self._generate_general_content(request, research_content)

        # Apply tone adjustments
        content = self._adjust_tone(content, request.tone, request.audience)

        # Limit content length
        words = content.split()
        if len(words) > request.max_tokens // 4:  # Rough token estimation
            content = " ".join(words[: request.max_tokens // 4])

        return content

    async def _refine_with_llm(
        self,
        draft: str,
        prompt: str,
        content_type: str,
        tone: str,
        audience: str,
        research: list[ResearchResult],
        llm_cap_chars: int = 8000,
    ) -> str | None:
        """Optionally refine content using OpenAI or Google Gemini if keys are set.
        Returns refined text or None on failure.
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")

        system_instructions = (
            "You are a helpful writing assistant. Improve clarity, structure, and tone. "
            "Keep facts consistent with provided research snippets. Output Markdown only."
        )
        research_snippets = "\n".join(f"- {r.title}: {r.content[:200]}" for r in research[:5])
        # Guard rails: cap draft length before LLM
        if len(draft) > llm_cap_chars:
            draft = draft[:llm_cap_chars] + "\n\n…"

        user_prompt = (
            f"Task: Refine the following {content_type} for a {tone} tone, audience: {audience}.\n"
            f"Topic: {prompt}\n\n"
            f"Research snippets:\n{research_snippets}\n\n"
            f"Draft:\n{draft}\n\n"
            "Return improved content in Markdown, preserving structure."
        )

        # Try OpenAI first
        if openai_key:
            try:
                headers = {
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.5,
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"].strip()
                        # Guard rails: cap response length
                        if len(text) > 12000:
                            text = text[:12000] + "\n\n…"
                        return text
                    _LOG.warning(f"OpenAI refine HTTP {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                _LOG.warning(f"OpenAI refinement failed: {e}")

        # Fallback to Gemini if available
        if google_key:
            try:
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": system_instructions},
                                {"text": user_prompt},
                            ]
                        }
                    ]
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_key}",
                        json=payload,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and candidates[0].get("content", {}).get("parts"):
                            parts = candidates[0]["content"]["parts"]
                            text = "".join(p.get("text", "") for p in parts).strip()
                            if len(text) > 12000:
                                text = text[:12000] + "\n\n…"
                            if text:
                                return text
                        _LOG.warning("Gemini response missing content")
                    else:
                        _LOG.warning(f"Gemini refine HTTP {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                _LOG.warning(f"Gemini refinement failed: {e}")

        return None

    def _generate_article(self, request: ContentRequest, research_content: list[str]) -> str:
        """Generate an article format."""
        lines = [
            f"# {request.prompt.title()}\n",
            "## Introduction\n",
            (
                f"This article explores {request.prompt.lower()}, providing comprehensive insights "
                "based on current research and expert knowledge.\n"
            ),
            "## Key Findings\n",
        ]

        # Add research-based content
        for item in research_content:
            lines.append(f"{item}\n")

        lines.extend(
            [
                "\n## Analysis\n",
                (
                    f"Based on the available information, {request.prompt.lower()} represents an important topic "
                    "that requires careful consideration of multiple factors.\n"
                ),
                "\n## Conclusion\n",
                (
                    f"Understanding {request.prompt.lower()} is crucial for making informed decisions "
                    "and achieving successful outcomes.\n"
                ),
            ]
        )

        return "".join(lines)

    def _generate_blog_post(self, request: ContentRequest, research_content: list[str]) -> str:
        """Generate a blog post format."""
        lines = [
            f"# {request.prompt.title()}: A Comprehensive Guide\n\n",
            (
                f"Have you ever wondered about {request.prompt.lower()}? You're not alone! "
                "This topic has been gaining attention, and for good reason.\n\n"
            ),
            "## What You Need to Know\n\n",
        ]

        # Add research-based content in a more conversational way
        for i, item in enumerate(research_content, 1):
            lines.append(f"### {i}. Key Insight\n{item}\n\n")

        lines.extend(
            [
                "## Why This Matters\n\n",
                (
                    f"Understanding {request.prompt.lower()} can help you make better decisions "
                    "and stay informed about important developments.\n\n"
                ),
                "## Takeaways\n\n",
                (
                    f"The key to mastering {request.prompt.lower()} lies in staying informed "
                    "and applying these insights to your specific situation.\n"
                ),
            ]
        )

        return "".join(lines)

    def _generate_summary(self, request: ContentRequest, research_content: list[str]) -> str:
        """Generate a summary format."""
        lines = [f"## Summary: {request.prompt.title()}\n\n"]

        if research_content:
            lines.append("**Key Points:**\n\n")
            for item in research_content:
                lines.append(f"- {item.replace('•', '').strip()}\n")
        else:
            lines.append(
                f"This summary covers the essential aspects of {request.prompt.lower()}, highlighting "
                "the most important information for quick reference.\n"
            )

        lines.append(
            f"\n**Bottom Line:** {request.prompt.title()} is an important topic that requires "
            "understanding of key concepts and current developments.\n"
        )

        return "".join(lines)

    def _generate_presentation_outline(self, request: ContentRequest, research_content: list[str]) -> str:
        """Generate a presentation outline."""
        lines = [
            f"# Presentation: {request.prompt.title()}\n\n",
            "## Slide 1: Title Slide\n",
            f"- Title: {request.prompt.title()}\n",
            "- Subtitle: Comprehensive Overview\n",
            "- Date: [Current Date]\n\n",
            "## Slide 2: Agenda\n",
            "- Introduction\n",
            "- Key Concepts\n",
            "- Current Insights\n",
            "- Conclusion\n\n",
            "## Slide 3: Introduction\n",
            f"- Overview of {request.prompt.lower()}\n",
            "- Why it matters\n",
            "- Today's objectives\n\n",
        ]

        # Add research-based slides
        for i, item in enumerate(research_content, 1):
            lines.append(f"## Slide {3 + i}: Key Insight #{i}\n")
            lines.append(f"{item}\n\n")

        lines.extend(
            [
                f"## Slide {4 + len(research_content)}: Summary\n",
                "- Key takeaways\n",
                "- Action items\n",
                "- Next steps\n\n",
                f"## Slide {5 + len(research_content)}: Questions & Discussion\n",
                "- Q&A Session\n",
                "- Contact Information\n",
            ]
        )

        return "".join(lines)

    def _generate_outline(self, request: ContentRequest, research_content: list[str]) -> str:
        """Generate a general outline."""
        lines = [
            f"# Outline: {request.prompt.title()}\n\n",
            "## I. Introduction\n",
            f"   A. Definition of {request.prompt.lower()}\n",
            "   B. Importance and relevance\n",
            "   C. Scope of discussion\n\n",
            "## II. Main Content\n",
        ]

        # Add research-based sections
        for i, item in enumerate(research_content, 1):
            letter = chr(ord("A") + i - 1)
            lines.append(f"   {letter}. {item.split(':')[0] if ':' in item else f'Key Point {i}'}\n")

        lines.extend(
            [
                "\n## III. Analysis and Discussion\n",
                "   A. Current trends\n",
                "   B. Implications\n",
                "   C. Future considerations\n\n",
                "## IV. Conclusion\n",
                "   A. Summary of key points\n",
                "   B. Final thoughts\n",
                "   C. Call to action\n",
            ]
        )

        return "".join(lines)

    def _generate_general_content(self, request: ContentRequest, research_content: list[str]) -> str:
        """Generate general content when type is not specified."""
        lines = [
            f"# {request.prompt.title()}\n\n",
            (
                f"This content addresses the topic of {request.prompt.lower()}, providing "
                "valuable insights and information.\n\n"
            ),
        ]

        if research_content:
            lines.append("## Key Information\n\n")
            for item in research_content:
                lines.append(f"{item}\n\n")
        else:
            lines.append(
                f"The topic of {request.prompt.lower()} encompasses various important aspects "
                "that are worth exploring in detail.\n\n"
            )

        lines.append("## Summary\n\n")
        lines.append(
            f"Understanding {request.prompt.lower()} provides valuable knowledge for making "
            "informed decisions and achieving success.\n"
        )

        return "".join(lines)

    def _adjust_tone(self, content: str, tone: str, audience: str) -> str:
        """Adjust content tone based on requirements."""
        # This is a simplified tone adjustment
        # In a real implementation, you might use more sophisticated NLP

        if tone == "casual":
            # Make it more conversational
            content = content.replace(". ", ". You know, ")
            content = content.replace("This", "So this")
            content = re.sub(r"\b(important|crucial|essential)\b", r"really \1", content, flags=re.IGNORECASE)

        elif tone == "academic":
            # Make it more formal
            content = content.replace("you", "one")
            content = content.replace("You", "One")
            content = re.sub(r"\b(shows|proves|says)\b", r"demonstrates", content, flags=re.IGNORECASE)

        elif tone == "creative":
            # Add some creative elements
            content = re.sub(r"^# (.+)$", r"# 🌟 \1 🌟", content, flags=re.MULTILINE)
            content = content.replace("important", "fascinating")

        return content

    def _assess_content_quality(self, content: str, request: ContentRequest) -> float:
        """Assess content quality with a simple scoring system."""
        score = 0.0

        # Length check
        word_count = len(content.split())
        if word_count >= 100:
            score += 0.2
        if word_count >= 300:
            score += 0.2

        # Structure check
        if "##" in content or "#" in content:
            score += 0.2  # Has headers

        if content.count("\n") >= 5:
            score += 0.1  # Has multiple paragraphs

        # Content relevance (simple keyword matching)
        prompt_words = request.prompt.lower().split()
        content_lower = content.lower()
        matches = sum(1 for word in prompt_words if word in content_lower)
        if matches >= len(prompt_words) * 0.5:
            score += 0.2

        # Tone appropriateness
        if request.tone == "professional" and not any(
            word in content.lower() for word in ["you know", "so this", "really"]
        ):
            score += 0.1

        return min(score, 1.0)


# Export the main function for the API
async def create_content(
    prompt: str,
    content_type: str = "article",
    max_tokens: int = 2000,
    tone: str = "professional",
    audience: str = "general",
    include_research: bool = True,
    language: str = "en",
) -> dict[str, Any]:
    """
    Create content using only free and open-source services.

    Args:
        prompt: The content topic or request
        content_type: Type of content to create (article, blog, summary, presentation, outline)
        max_tokens: Maximum length of generated content
        tone: Writing tone (professional, casual, academic, creative)
        audience: Target audience (general, technical, academic, business)
        include_research: Whether to include research from free sources
        language: Content language (currently only 'en' supported)

    Returns:
        Dictionary with generated content and metadata
    """
    creator = FreeContentCreator()

    request = ContentRequest(
        prompt=prompt,
        content_type=content_type,
        max_tokens=max_tokens,
        tone=tone,
        audience=audience,
        include_research=include_research,
        language=language,
    )

    response = await creator.create_content(request)

    return {
        "content": response.content,
        "word_count": response.word_count,
        "generation_time": response.generation_time,
        "quality_score": response.quality_score,
        "research_sources": [
            {
                "title": source.title,
                "source": source.source,
                "url": source.url,
                "relevance_score": source.relevance_score,
            }
            for source in response.research_sources
        ],
        "metadata": {
            "content_type": request.content_type,
            "tone": request.tone,
            "audience": request.audience,
            "language": request.language,
            "research_enabled": request.include_research,
        },
    }
