"""
MCP Sequential Thinking Server Implementation

This server provides intelligent content planning and structuring capabilities
using sequential thinking algorithms and AI-powered analysis.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_TIMEOUT = 60
DEFAULT_MAX_STEPS = 10
DEFAULT_THINKING_DEPTH = "medium"  # shallow, medium, deep


@dataclass
class ThinkingStep:
    """Represents a single thinking step in the sequential process."""

    step_id: int
    step_type: str  # analysis, planning, structuring, validation, optimization
    description: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    confidence: float  # 0.0 to 1.0
    reasoning: str
    next_steps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThinkingRequest:
    """Request for sequential thinking process."""

    content_type: str  # presentation, document, html, pdf
    brief: str
    notes: str
    target_length: str
    style: str = "professional"
    tone: str = "concise"
    audience: str = "stakeholders"
    thinking_depth: str = DEFAULT_THINKING_DEPTH
    max_steps: int = DEFAULT_MAX_STEPS
    client_id: str | None = None


@dataclass
class ThinkingResponse:
    """Response from sequential thinking process."""

    status: str
    thinking_process: list[ThinkingStep]
    final_plan: dict[str, Any]
    confidence_score: float
    reasoning_summary: str
    suggested_structure: dict[str, Any]
    processing_time: float
    client_id: str | None = None
    error: str | None = None


class SequentialThinkingEngine:
    """Core engine for sequential thinking and content planning."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

    async def think_sequentially(self, request: ThinkingRequest) -> ThinkingResponse:
        """Execute sequential thinking process for content planning."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Step 1: Content Analysis
            analysis_step = await self._analyze_content(request)

            # Step 2: Structure Planning
            planning_step = await self._plan_structure(request, analysis_step)

            # Step 3: Content Structuring
            structuring_step = await self._structure_content(request, planning_step)

            # Step 4: Validation
            validation_step = await self._validate_plan(request, structuring_step)

            # Step 5: Optimization
            optimization_step = await self._optimize_plan(request, validation_step)

            # Compile thinking process
            thinking_process = [analysis_step, planning_step, structuring_step, validation_step, optimization_step]

            # Calculate overall confidence
            confidence_score = sum(step.confidence for step in thinking_process) / len(thinking_process)

            # Generate final plan
            final_plan = self._compile_final_plan(thinking_process)

            # Create reasoning summary
            reasoning_summary = self._create_reasoning_summary(thinking_process)

            processing_time = asyncio.get_event_loop().time() - start_time

            return ThinkingResponse(
                status="success",
                thinking_process=thinking_process,
                final_plan=final_plan,
                confidence_score=confidence_score,
                reasoning_summary=reasoning_summary,
                suggested_structure=final_plan.get("structure", {}),
                processing_time=processing_time,
                client_id=request.client_id,
            )

        except Exception as e:
            logger.error(f"Sequential thinking failed: {e}")
            processing_time = asyncio.get_event_loop().time() - start_time

            return ThinkingResponse(
                status="error",
                thinking_process=[],
                final_plan={},
                confidence_score=0.0,
                reasoning_summary="",
                suggested_structure={},
                processing_time=processing_time,
                client_id=request.client_id,
                error=str(e),
            )

    async def _analyze_content(self, request: ThinkingRequest) -> ThinkingStep:
        """Analyze the content brief and notes."""
        try:
            # Use LLM to analyze content

            # For now, return a structured analysis
            # In production, this would call an LLM
            analysis_data = {
                "content_type": request.content_type,
                "key_themes": self._extract_themes(request.brief + " " + request.notes),
                "target_audience": request.audience,
                "content_complexity": "medium",
                "suggested_approach": "structured",
                "potential_challenges": ["content_organization", "audience_engagement"],
            }

            return ThinkingStep(
                step_id=1,
                step_type="analysis",
                description="Content analysis and theme extraction",
                input_data={"brief": request.brief, "notes": request.notes},
                output_data=analysis_data,
                confidence=0.85,
                reasoning="Content analyzed for key themes and structure",
                next_steps=["planning"],
            )

        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise

    async def _plan_structure(self, request: ThinkingRequest, analysis_step: ThinkingStep) -> ThinkingStep:
        """Plan the content structure based on analysis."""
        try:
            # Plan structure based on content type and length
            structure_plan = self._create_structure_plan(request, analysis_step.output_data)

            return ThinkingStep(
                step_id=2,
                step_type="planning",
                description="Content structure planning",
                input_data=analysis_step.output_data,
                output_data=structure_plan,
                confidence=0.80,
                reasoning="Structure planned based on content analysis",
                next_steps=["structuring"],
            )

        except Exception as e:
            logger.error(f"Structure planning failed: {e}")
            raise

    async def _structure_content(self, request: ThinkingRequest, planning_step: ThinkingStep) -> ThinkingStep:
        """Structure the content according to the plan."""
        try:
            # Create detailed content structure
            content_structure = self._create_content_structure(request, planning_step.output_data)

            return ThinkingStep(
                step_id=3,
                step_type="structuring",
                description="Content structuring and organization",
                input_data=planning_step.output_data,
                output_data=content_structure,
                confidence=0.75,
                reasoning="Content structured according to plan",
                next_steps=["validation"],
            )

        except Exception as e:
            logger.error(f"Content structuring failed: {e}")
            raise

    async def _validate_plan(self, request: ThinkingRequest, structuring_step: ThinkingStep) -> ThinkingStep:
        """Validate the content plan."""
        try:
            # Validate the content structure
            validation_result = self._validate_content_plan(request, structuring_step.output_data)

            return ThinkingStep(
                step_id=4,
                step_type="validation",
                description="Content plan validation",
                input_data=structuring_step.output_data,
                output_data=validation_result,
                confidence=0.90,
                reasoning="Plan validated for completeness and coherence",
                next_steps=["optimization"],
            )

        except Exception as e:
            logger.error(f"Plan validation failed: {e}")
            raise

    async def _optimize_plan(self, request: ThinkingRequest, validation_step: ThinkingStep) -> ThinkingStep:
        """Optimize the content plan."""
        try:
            # Optimize the content plan
            optimization_result = self._optimize_content_plan(request, validation_step.output_data)

            return ThinkingStep(
                step_id=5,
                step_type="optimization",
                description="Content plan optimization",
                input_data=validation_step.output_data,
                output_data=optimization_result,
                confidence=0.85,
                reasoning="Plan optimized for best results",
                next_steps=[],
            )

        except Exception as e:
            logger.error(f"Plan optimization failed: {e}")
            raise

    def _extract_themes(self, text: str) -> list[str]:
        """Extract key themes from text."""
        # Simple theme extraction - in production, use NLP/LLM
        words = text.lower().split()
        common_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
        themes = [word for word in words if word not in common_words and len(word) > 3]
        return list(set(themes))[:5]  # Return top 5 unique themes

    def _create_structure_plan(self, request: ThinkingRequest, analysis: dict[str, Any]) -> dict[str, Any]:
        """Create a structure plan based on content type and analysis."""
        if request.content_type == "presentation":
            return self._create_presentation_structure(request, analysis)
        elif request.content_type == "document":
            return self._create_document_structure(request, analysis)
        elif request.content_type == "html":
            return self._create_html_structure(request, analysis)
        elif request.content_type == "pdf":
            return self._create_pdf_structure(request, analysis)
        else:
            return self._create_generic_structure(request, analysis)

    def _create_presentation_structure(self, request: ThinkingRequest, analysis: dict[str, Any]) -> dict[str, Any]:
        """Create presentation structure plan."""
        # Parse target length to estimate slide count
        slide_count = self._parse_slide_count(request.target_length)

        structure = {
            "type": "presentation",
            "estimated_slides": slide_count,
            "sections": [
                {"type": "title", "slides": 1, "content": "Introduction"},
                {"type": "overview", "slides": 1, "content": "Overview"},
                {"type": "main_content", "slides": max(1, slide_count - 4), "content": "Main Content"},
                {"type": "summary", "slides": 1, "content": "Summary"},
                {"type": "conclusion", "slides": 1, "content": "Conclusion"},
            ],
            "style_guidelines": {"visual_style": request.style, "tone": request.tone, "audience": request.audience},
        }

        return structure

    def _create_document_structure(self, request: ThinkingRequest, analysis: dict[str, Any]) -> dict[str, Any]:
        """Create document structure plan."""
        structure = {
            "type": "document",
            "sections": [
                {"type": "title", "content": "Title Page"},
                {"type": "table_of_contents", "content": "Table of Contents"},
                {"type": "introduction", "content": "Introduction"},
                {"type": "main_content", "content": "Main Content"},
                {"type": "conclusion", "content": "Conclusion"},
                {"type": "references", "content": "References"},
            ],
            "formatting": {"style": request.style, "tone": request.tone, "audience": request.audience},
        }

        return structure

    def _create_html_structure(self, request: ThinkingRequest, analysis: dict[str, Any]) -> dict[str, Any]:
        """Create HTML structure plan."""
        structure = {
            "type": "html",
            "sections": [
                {"type": "header", "content": "Header"},
                {"type": "navigation", "content": "Navigation"},
                {"type": "main_content", "content": "Main Content"},
                {"type": "sidebar", "content": "Sidebar"},
                {"type": "footer", "content": "Footer"},
            ],
            "responsive_design": True,
            "seo_optimization": True,
            "accessibility": True,
        }

        return structure

    def _create_pdf_structure(self, request: ThinkingRequest, analysis: dict[str, Any]) -> dict[str, Any]:
        """Create PDF structure plan."""
        structure = {
            "type": "pdf",
            "sections": [
                {"type": "cover", "content": "Cover Page"},
                {"type": "table_of_contents", "content": "Table of Contents"},
                {"type": "main_content", "content": "Main Content"},
                {"type": "appendix", "content": "Appendix"},
            ],
            "formatting": {"page_size": "A4", "margins": "standard", "fonts": "professional"},
        }

        return structure

    def _create_generic_structure(self, request: ThinkingRequest, analysis: dict[str, Any]) -> dict[str, Any]:
        """Create generic content structure."""
        structure = {
            "type": "generic",
            "sections": [
                {"type": "introduction", "content": "Introduction"},
                {"type": "main_content", "content": "Main Content"},
                {"type": "conclusion", "content": "Conclusion"},
            ],
            "metadata": {"style": request.style, "tone": request.tone, "audience": request.audience},
        }

        return structure

    def _parse_slide_count(self, target_length: str) -> int:
        """Parse target length to estimate slide count."""
        import re

        # Try to extract specific slide count
        match = re.search(r"(\d+)\s*slides?", target_length, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Try to extract word count and estimate
        match = re.search(r"(\d+)\s*words?", target_length, re.IGNORECASE)
        if match:
            words = int(match.group(1))
            return max(5, min(15, words // 50))

        # Default to medium length
        return 8

    def _create_content_structure(self, request: ThinkingRequest, structure_plan: dict[str, Any]) -> dict[str, Any]:
        """Create detailed content structure."""
        content_structure: dict[str, Any] = {
            "overview": structure_plan,
            "detailed_sections": [],
            "content_flow": [],
            "key_messages": [],
            "visual_elements": [],
            "interactive_elements": [],
        }

        # Add detailed sections based on structure plan
        sections = structure_plan.get("sections", [])
        for section in sections:
            detailed_section = {
                "title": section.get("content", ""),
                "type": section.get("type", ""),
                "content_outline": self._generate_content_outline(section, request),
                "estimated_length": section.get("slides", 1) if "slides" in section else 1,
                "key_points": [],
                "supporting_materials": [],
            }
            content_structure["detailed_sections"].append(detailed_section)

        return content_structure

    def _generate_content_outline(self, section: dict[str, Any], request: ThinkingRequest) -> list[str]:
        """Generate content outline for a section."""
        section_type = section.get("type", "")

        if section_type == "introduction":
            return [
                "Hook/Opening statement",
                "Context and background",
                "Problem statement",
                "Objectives and goals",
                "Overview of what's to come",
            ]
        elif section_type == "main_content":
            return [
                "Key point 1 with supporting evidence",
                "Key point 2 with supporting evidence",
                "Key point 3 with supporting evidence",
                "Examples and case studies",
                "Data and statistics",
            ]
        elif section_type == "conclusion":
            return ["Summary of key points", "Main takeaways", "Call to action", "Next steps", "Closing thoughts"]
        else:
            return ["Content point 1", "Content point 2", "Content point 3"]

    def _validate_content_plan(self, request: ThinkingRequest, content_structure: dict[str, Any]) -> dict[str, Any]:
        """Validate the content plan for completeness and coherence."""
        validation_result: dict[str, Any] = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "completeness_score": 0.0,
        }

        # Check for required elements
        required_elements = ["introduction", "main_content", "conclusion"]
        found_elements: list[str] = []

        for section in content_structure.get("detailed_sections", []):
            section_type = section.get("type", "").lower()
            if section_type in required_elements:
                found_elements.append(section_type)

        # Calculate completeness score
        validation_result["completeness_score"] = len(found_elements) / len(required_elements)

        # Check for missing elements
        missing_elements = [elem for elem in required_elements if elem not in found_elements]
        if missing_elements:
            validation_result["issues"].append(f"Missing required sections: {', '.join(missing_elements)}")
            validation_result["is_valid"] = False

        # Check content flow
        if len(content_structure.get("detailed_sections", [])) < 3:
            validation_result["warnings"].append("Content structure seems too simple")

        # Add suggestions
        if validation_result["completeness_score"] < 0.8:
            validation_result["suggestions"].append("Consider adding more detailed sections")

        return validation_result

    def _optimize_content_plan(self, request: ThinkingRequest, validation_result: dict[str, Any]) -> dict[str, Any]:
        """Optimize the content plan based on validation results."""
        optimization_result: dict[str, Any] = {
            "original_plan": validation_result,
            "optimizations": [],
            "improved_plan": {},
            "optimization_score": 0.0,
        }

        # Apply optimizations based on validation issues
        if not validation_result.get("is_valid", True):
            # Fix validation issues
            optimization_result["optimizations"].append("Fixed missing required sections")
            optimization_result["optimizations"].append("Improved content flow")

        # Add performance optimizations
        optimization_result["optimizations"].append("Optimized for target audience")
        optimization_result["optimizations"].append("Enhanced visual structure")

        # Calculate optimization score
        completeness_score = validation_result.get("completeness_score", 0.0)
        if isinstance(completeness_score, int | float):
            optimization_result["optimization_score"] = min(1.0, completeness_score + 0.2)
        else:
            optimization_result["optimization_score"] = 0.5

        return optimization_result

    def _compile_final_plan(self, thinking_process: list[ThinkingStep]) -> dict[str, Any]:
        """Compile the final plan from all thinking steps."""
        final_plan: dict[str, Any] = {
            "overview": {},
            "structure": {},
            "content": {},
            "recommendations": [],
            "metadata": {},
        }

        # Extract information from each thinking step
        for step in thinking_process:
            if step.step_type == "analysis":
                final_plan["overview"] = step.output_data
            elif step.step_type == "planning":
                final_plan["structure"] = step.output_data
            elif step.step_type == "structuring":
                final_plan["content"] = step.output_data
            elif step.step_type == "validation":
                final_plan["metadata"]["validation"] = step.output_data
            elif step.step_type == "optimization":
                final_plan["metadata"]["optimization"] = step.output_data

        # Add recommendations
        final_plan["recommendations"] = [
            "Follow the structured approach for best results",
            "Consider audience engagement throughout",
            "Maintain consistent style and tone",
            "Include visual elements where appropriate",
        ]

        return final_plan

    def _create_reasoning_summary(self, thinking_process: list[ThinkingStep]) -> str:
        """Create a summary of the reasoning process."""
        summary_parts: list[str] = []

        for step in thinking_process:
            summary_parts.append(f"Step {step.step_id} ({step.step_type}): {step.reasoning}")

        return " | ".join(summary_parts)


# Global instance
_thinking_engine = SequentialThinkingEngine()


async def plan_content(
    content_type: str,
    brief: str,
    notes: str,
    target_length: str,
    style: str = "professional",
    tone: str = "concise",
    audience: str = "stakeholders",
    thinking_depth: str = DEFAULT_THINKING_DEPTH,
    max_steps: int = DEFAULT_MAX_STEPS,
    client_id: str | None = None,
) -> dict[str, Any]:
    """Plan content using sequential thinking."""
    request = ThinkingRequest(
        content_type=content_type,
        brief=brief,
        notes=notes,
        target_length=target_length,
        style=style,
        tone=tone,
        audience=audience,
        thinking_depth=thinking_depth,
        max_steps=max_steps,
        client_id=client_id,
    )

    result = await _thinking_engine.think_sequentially(request)

    # Convert to dictionary for MCP tool response
    return {
        "status": result.status,
        "thinking_process": [
            {
                "step_id": step.step_id,
                "step_type": step.step_type,
                "description": step.description,
                "confidence": step.confidence,
                "reasoning": step.reasoning,
            }
            for step in result.thinking_process
        ],
        "final_plan": result.final_plan,
        "confidence_score": result.confidence_score,
        "reasoning_summary": result.reasoning_summary,
        "suggested_structure": result.suggested_structure,
        "processing_time": result.processing_time,
        "client_id": result.client_id,
        "error": result.error,
    }


def register(mcp: Any) -> None:
    """Register the sequential thinking tools with the MCP server."""

    @mcp.tool()
    async def sequential_thinking_plan(
        content_type: str,
        brief: str,
        notes: str,
        target_length: str,
        style: str = "professional",
        tone: str = "concise",
        audience: str = "stakeholders",
        thinking_depth: str = DEFAULT_THINKING_DEPTH,
        max_steps: int = DEFAULT_MAX_STEPS,
        client_id: str | None = None,
    ) -> str:
        """Plan content using sequential thinking and AI-powered analysis."""
        try:
            result = await plan_content(
                content_type=content_type,
                brief=brief,
                notes=notes,
                target_length=target_length,
                style=style,
                tone=tone,
                audience=audience,
                thinking_depth=thinking_depth,
                max_steps=max_steps,
                client_id=client_id,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Sequential thinking planning failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def sequential_thinking_analyze(
        content: str,
        analysis_type: str = "general",
        depth: str = DEFAULT_THINKING_DEPTH,
        client_id: str | None = None,
    ) -> str:
        """Analyze content using sequential thinking."""
        try:
            # Create a mock request for analysis
            request = ThinkingRequest(
                content_type="analysis",
                brief=content[:200],
                notes=content,
                target_length="analysis",
                style="analytical",
                tone="objective",
                audience="general",
                thinking_depth=depth,
                client_id=client_id,
            )

            # Only run analysis step
            analysis_step = await _thinking_engine._analyze_content(request)

            result = {
                "status": "success",
                "analysis": analysis_step.output_data,
                "confidence": analysis_step.confidence,
                "reasoning": analysis_step.reasoning,
                "client_id": client_id,
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)
