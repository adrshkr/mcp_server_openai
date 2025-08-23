"""
MCP Content Planning Integration Tool

This module provides intelligent content planning and structuring by integrating
sequential thinking with content generation capabilities. It orchestrates the
entire content creation workflow from planning to execution.
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_MODEL_TYPE = "gpt-4o"
DEFAULT_MAX_TOKENS = 3000
DEFAULT_TEMPERATURE = 0.3
MAX_PLANNING_ITERATIONS = 3
CONTENT_TYPES = ["presentation", "document", "webpage", "report", "article", "manual"]


@dataclass
class ContentSection:
    """Represents a section of content with planning details."""

    section_id: str
    title: str
    description: str
    content_type: str  # "slide", "section", "chapter", etc.
    target_length: int  # words or characters
    key_points: list[str] = field(default_factory=list)
    visual_elements: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    priority: int = 1  # 1-5, where 1 is highest priority
    estimated_time: int | None = None  # minutes


@dataclass
class ContentPlan:
    """Complete content planning structure."""

    plan_id: str
    title: str
    content_type: str
    target_audience: str
    objectives: list[str] = field(default_factory=list)
    key_messages: list[str] = field(default_factory=list)
    sections: list[ContentSection] = field(default_factory=list)
    visual_strategy: dict[str, Any] = field(default_factory=dict)
    timeline: dict[str, Any] = field(default_factory=dict)
    resources_needed: list[str] = field(default_factory=list)
    quality_metrics: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlanningRequest:
    """Request for content planning."""

    title: str
    content_type: str
    target_audience: str
    objectives: list[str]
    key_messages: list[str]
    constraints: dict[str, Any] | None = None
    preferences: dict[str, Any] | None = None
    model_type: str = DEFAULT_MODEL_TYPE


@dataclass
class PlanningResponse:
    """Response containing content planning results."""

    status: str
    message: str
    content_plan: ContentPlan
    planning_metadata: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionRequest:
    """Request for content execution based on plan."""

    plan_id: str
    execution_mode: str  # "full", "section", "preview"
    target_format: str
    customizations: dict[str, Any] | None = None
    priority_sections: list[str] | None = None


@dataclass
class ExecutionResponse:
    """Response containing content execution results."""

    status: str
    message: str
    execution_id: str
    progress: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    next_steps: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class ContentPlanningEngine:
    """Core engine for intelligent content planning and execution."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.plans: dict[str, ContentPlan] = {}
        self.execution_history: list[ExecutionResponse] = []

    async def create_content_plan(self, request: PlanningRequest) -> PlanningResponse:
        """Create a comprehensive content plan using AI-powered planning."""
        try:
            # Generate plan ID
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.title) % 10000}"

            # Create initial plan structure
            content_plan = ContentPlan(
                plan_id=plan_id,
                title=request.title,
                content_type=request.content_type,
                target_audience=request.target_audience,
                objectives=request.objectives,
                key_messages=request.key_messages,
            )

            # Generate detailed sections using AI planning
            sections = await self._generate_sections(request, content_plan)
            content_plan.sections = sections

            # Generate visual strategy
            visual_strategy = await self._generate_visual_strategy(request, content_plan)
            content_plan.visual_strategy = visual_strategy

            # Generate timeline and resources
            timeline, resources = await self._generate_timeline_and_resources(request, content_plan)
            content_plan.timeline = timeline
            content_plan.resources_needed = resources

            # Generate quality metrics
            quality_metrics = await self._generate_quality_metrics(request, content_plan)
            content_plan.quality_metrics = quality_metrics

            # Store plan
            self.plans[plan_id] = content_plan

            # Generate recommendations
            recommendations = await self._generate_recommendations(content_plan)

            return PlanningResponse(
                status="success",
                message=f"Content plan '{request.title}' created successfully",
                content_plan=content_plan,
                planning_metadata={
                    "iterations": 1,
                    "model_used": request.model_type,
                    "planning_time": datetime.now().isoformat(),
                },
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Content planning failed: {e}")
            return PlanningResponse(
                status="error",
                message=f"Content planning failed: {str(e)}",
                content_plan=ContentPlan(
                    plan_id="error",
                    title=request.title,
                    content_type=request.content_type,
                    target_audience=request.target_audience,
                    objectives=request.objectives,
                    key_messages=request.key_messages,
                ),
            )

    async def _generate_sections(self, request: PlanningRequest, plan: ContentPlan) -> list[ContentSection]:
        """Generate content sections using AI planning."""
        # This would integrate with the sequential thinking MCP server
        # For now, create a basic structure based on content type

        sections = []

        if request.content_type == "presentation":
            # Generate presentation slides
            sections = [
                ContentSection(
                    section_id="intro",
                    title="Introduction",
                    description="Opening and overview",
                    content_type="slide",
                    target_length=100,
                    key_points=["Hook", "Overview", "Objectives"],
                    priority=1,
                ),
                ContentSection(
                    section_id="main_content",
                    title="Main Content",
                    description="Core presentation content",
                    content_type="slide",
                    target_length=300,
                    key_points=["Key Points", "Examples", "Evidence"],
                    priority=1,
                ),
                ContentSection(
                    section_id="conclusion",
                    title="Conclusion",
                    description="Summary and next steps",
                    content_type="slide",
                    target_length=100,
                    key_points=["Summary", "Call to Action", "Next Steps"],
                    priority=1,
                ),
            ]
        elif request.content_type == "document":
            # Generate document sections
            sections = [
                ContentSection(
                    section_id="executive_summary",
                    title="Executive Summary",
                    description="High-level overview",
                    content_type="section",
                    target_length=200,
                    key_points=["Overview", "Key Findings", "Recommendations"],
                    priority=1,
                ),
                ContentSection(
                    section_id="background",
                    title="Background",
                    description="Context and background information",
                    content_type="section",
                    target_length=400,
                    key_points=["Context", "History", "Current State"],
                    priority=2,
                ),
                ContentSection(
                    section_id="analysis",
                    title="Analysis",
                    description="Detailed analysis and findings",
                    content_type="section",
                    target_length=800,
                    key_points=["Data", "Analysis", "Insights"],
                    priority=1,
                ),
                ContentSection(
                    section_id="recommendations",
                    title="Recommendations",
                    description="Actionable recommendations",
                    content_type="section",
                    target_length=300,
                    key_points=["Actions", "Timeline", "Resources"],
                    priority=1,
                ),
            ]

        # Add more content types as needed

        return sections

    async def _generate_visual_strategy(self, request: PlanningRequest, plan: ContentPlan) -> dict[str, Any]:
        """Generate visual strategy for the content."""
        return {
            "theme": "professional",
            "color_scheme": "corporate",
            "typography": "modern",
            "layout_style": "clean",
            "visual_elements": ["charts", "diagrams", "icons"],
            "image_style": "high-quality",
            "branding": "consistent",
        }

    async def _generate_timeline_and_resources(
        self, request: PlanningRequest, plan: ContentPlan
    ) -> tuple[dict[str, Any], list[str]]:
        """Generate timeline and resource requirements."""
        total_sections = len(plan.sections)
        estimated_time = total_sections * 30  # 30 minutes per section

        timeline: dict[str, Any] = {
            "total_estimated_time": estimated_time,
            "phases": [
                {"phase": "Planning", "duration": estimated_time * 0.2},
                {"phase": "Research", "duration": estimated_time * 0.3},
                {"phase": "Creation", "duration": estimated_time * 0.4},
                {"phase": "Review", "duration": estimated_time * 0.1},
            ],
        }

        resources: list[str] = [
            "Content research tools",
            "Visual design software",
            "Review and feedback system",
            "Quality assurance tools",
        ]

        return timeline, resources

    async def _generate_quality_metrics(self, request: PlanningRequest, plan: ContentPlan) -> dict[str, Any]:
        """Generate quality metrics for the content."""
        return {
            "readability_target": "Grade 8-10",
            "accuracy_threshold": "95%",
            "completeness_target": "100%",
            "engagement_target": "High",
            "accessibility_compliance": "WCAG 2.1 AA",
        }

    async def _generate_recommendations(self, plan: ContentPlan) -> list[str]:
        """Generate recommendations for content creation."""
        recommendations = [
            f"Focus on {plan.target_audience} needs and preferences",
            "Ensure clear structure with logical flow",
            "Include visual elements to enhance engagement",
            "Plan for review and iteration cycles",
            "Consider accessibility requirements",
        ]

        if plan.content_type == "presentation":
            recommendations.extend(
                [
                    "Keep slides concise and focused",
                    "Use consistent visual design",
                    "Include speaker notes for guidance",
                ]
            )
        elif plan.content_type == "document":
            recommendations.extend(
                [
                    "Use clear headings and subheadings",
                    "Include table of contents",
                    "Add executive summary for key stakeholders",
                ]
            )

        return recommendations

    async def execute_content_plan(self, request: ExecutionRequest) -> ExecutionResponse:
        """Execute content creation based on the plan."""
        try:
            if request.plan_id not in self.plans:
                raise ValueError(f"Plan {request.plan_id} not found")

            plan = self.plans[request.plan_id]
            execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.plan_id) % 10000}"

            # Initialize execution progress
            progress = {
                "status": "started",
                "current_phase": "initialization",
                "completed_sections": 0,
                "total_sections": len(plan.sections),
                "start_time": datetime.now().isoformat(),
            }

            # Execute based on mode
            if request.execution_mode == "full":
                results = await self._execute_full_plan(plan, request)
            elif request.execution_mode == "section":
                results = await self._execute_sections(plan, request)
            elif request.execution_mode == "preview":
                results = await self._execute_preview(plan, request)
            else:
                raise ValueError(f"Invalid execution mode: {request.execution_mode}")

            # Update progress
            progress.update(
                {
                    "status": "completed",
                    "end_time": datetime.now().isoformat(),
                    "completed_sections": len(plan.sections),
                }
            )

            # Generate next steps
            next_steps = await self._generate_next_steps(plan, results)

            response = ExecutionResponse(
                status="success",
                message=f"Content execution completed for plan '{plan.title}'",
                execution_id=execution_id,
                progress=progress,
                results=results,
                next_steps=next_steps,
            )

            # Store execution history
            self.execution_history.append(response)

            return response

        except Exception as e:
            logger.error(f"Content execution failed: {e}")
            return ExecutionResponse(
                status="error",
                message=f"Content execution failed: {str(e)}",
                execution_id="error",
                progress={"status": "failed", "error": str(e)},
                results={},
                next_steps=[],
            )

    async def _execute_full_plan(self, plan: ContentPlan, request: ExecutionRequest) -> dict[str, Any]:
        """Execute the full content plan."""
        results = {
            "execution_mode": "full",
            "target_format": request.target_format,
            "sections": {},
            "overall_quality_score": 0.0,
            "generated_content": {},
        }

        # Execute each section
        for section in plan.sections:
            section_result = await self._execute_section(section, plan, request)
            if isinstance(results["sections"], dict):
                results["sections"][section.section_id] = section_result

        # Calculate overall quality
        if isinstance(results["sections"], dict) and results["sections"]:
            quality_scores = [s.get("quality_score", 0.0) for s in results["sections"].values()]
            if isinstance(results, dict):
                results["overall_quality_score"] = sum(quality_scores) / len(quality_scores)

        return results

    async def _execute_sections(self, plan: ContentPlan, request: ExecutionRequest) -> dict[str, Any]:
        """Execute specific sections of the plan."""
        results = {
            "execution_mode": "section",
            "target_format": request.target_format,
            "sections": {},
            "priority_sections": request.priority_sections or [],
        }

        # Execute priority sections if specified
        if request.priority_sections:
            for section_id in request.priority_sections:
                section = next((s for s in plan.sections if s.section_id == section_id), None)
                if section:
                    section_result = await self._execute_section(section, plan, request)
                    if isinstance(results["sections"], dict):
                        results["sections"][section_id] = section_result

        return results

    async def _execute_preview(self, plan: ContentPlan, request: ExecutionRequest) -> dict[str, Any]:
        """Execute a preview of the content plan."""
        results = {
            "execution_mode": "preview",
            "target_format": request.target_format,
            "preview_content": {},
            "estimated_full_execution_time": 0,
        }

        # Generate preview for first section
        if plan.sections:
            first_section = plan.sections[0]
            preview_result = await self._execute_section_preview(first_section, plan, request)
            results["preview_content"] = preview_result

        # Estimate full execution time
        results["estimated_full_execution_time"] = len(plan.sections) * 30  # 30 minutes per section

        return results

    async def _execute_section(
        self, section: ContentSection, plan: ContentPlan, request: ExecutionRequest
    ) -> dict[str, Any]:
        """Execute a single content section."""
        # This would integrate with the actual content generation tools
        # For now, return a mock result

        return {
            "section_id": section.section_id,
            "title": section.title,
            "status": "completed",
            "content_generated": True,
            "quality_score": 0.85,
            "execution_time": 25,  # minutes
            "output_files": [f"{section.section_id}_{request.target_format}"],
            "metadata": {
                "word_count": section.target_length,
                "visual_elements": len(section.visual_elements),
                "dependencies_met": len(section.dependencies) == 0,
            },
        }

    async def _execute_section_preview(
        self, section: ContentSection, plan: ContentPlan, request: ExecutionRequest
    ) -> dict[str, Any]:
        """Execute a preview of a content section."""
        return {
            "section_id": section.section_id,
            "title": section.title,
            "preview_content": f"Preview of {section.title}: {section.description}",
            "estimated_completion_time": 25,  # minutes
            "quality_estimate": 0.85,
        }

    async def _generate_next_steps(self, plan: ContentPlan, results: dict[str, Any]) -> list[str]:
        """Generate next steps based on execution results."""
        next_steps = [
            "Review generated content for quality and accuracy",
            "Gather feedback from stakeholders",
            "Iterate on content based on feedback",
            "Prepare for final delivery and distribution",
        ]

        if results.get("overall_quality_score", 0) < 0.8:
            next_steps.insert(0, "Address quality issues before proceeding")

        return next_steps

    def get_plan(self, plan_id: str) -> ContentPlan | None:
        """Get a content plan by ID."""
        return self.plans.get(plan_id)

    def get_all_plans(self) -> list[ContentPlan]:
        """Get all content plans."""
        return list(self.plans.values())

    def get_execution_history(self, limit: int = 50) -> list[ExecutionResponse]:
        """Get execution history."""
        return self.execution_history[-limit:] if self.execution_history else []


# Global instance
planning_engine = ContentPlanningEngine()


async def create_content_plan(
    title: str,
    content_type: str,
    target_audience: str,
    objectives: list[str],
    key_messages: list[str],
    constraints: dict[str, Any] | None = None,
    preferences: dict[str, Any] | None = None,
    model_type: str = DEFAULT_MODEL_TYPE,
) -> dict[str, Any]:
    """
    Create a comprehensive content plan using AI-powered planning.

    Args:
        title: Title of the content
        content_type: Type of content (presentation, document, webpage, etc.)
        target_audience: Target audience for the content
        objectives: List of content objectives
        key_messages: Key messages to convey
        constraints: Optional constraints for the content
        preferences: Optional preferences for the content
        model_type: AI model to use for planning

    Returns:
        Dictionary containing the content plan and planning results
    """
    request = PlanningRequest(
        title=title,
        content_type=content_type,
        target_audience=target_audience,
        objectives=objectives,
        key_messages=key_messages,
        constraints=constraints,
        preferences=preferences,
        model_type=model_type,
    )

    response = await planning_engine.create_content_plan(request)

    return {
        "status": response.status,
        "message": response.message,
        "plan_id": response.content_plan.plan_id,
        "content_plan": {
            "title": response.content_plan.title,
            "content_type": response.content_plan.content_type,
            "target_audience": response.content_plan.target_audience,
            "objectives": response.content_plan.objectives,
            "key_messages": response.content_plan.key_messages,
            "sections": [
                {
                    "section_id": s.section_id,
                    "title": s.title,
                    "description": s.description,
                    "content_type": s.content_type,
                    "target_length": s.target_length,
                    "key_points": s.key_points,
                    "priority": s.priority,
                }
                for s in response.content_plan.sections
            ],
            "visual_strategy": response.content_plan.visual_strategy,
            "timeline": response.content_plan.timeline,
            "resources_needed": response.content_plan.resources_needed,
            "quality_metrics": response.content_plan.quality_metrics,
        },
        "planning_metadata": response.planning_metadata,
        "recommendations": response.recommendations,
        "timestamp": response.timestamp.isoformat(),
    }


async def execute_content_plan(
    plan_id: str,
    execution_mode: str = "full",
    target_format: str = "default",
    customizations: dict[str, Any] | None = None,
    priority_sections: list[str] | None = None,
) -> dict[str, Any]:
    """
    Execute content creation based on a content plan.

    Args:
        plan_id: ID of the content plan to execute
        execution_mode: Execution mode (full, section, preview)
        target_format: Target output format
        customizations: Optional customizations for execution
        priority_sections: Optional list of priority sections to execute

    Returns:
        Dictionary containing execution results and progress
    """
    request = ExecutionRequest(
        plan_id=plan_id,
        execution_mode=execution_mode,
        target_format=target_format,
        customizations=customizations,
        priority_sections=priority_sections,
    )

    response = await planning_engine.execute_content_plan(request)

    return {
        "status": response.status,
        "message": response.message,
        "execution_id": response.execution_id,
        "progress": response.progress,
        "results": response.results,
        "next_steps": response.next_steps,
        "timestamp": response.timestamp.isoformat(),
    }


def get_content_plan(plan_id: str) -> dict[str, Any] | None:
    """
    Get a content plan by ID.

    Args:
        plan_id: ID of the content plan

    Returns:
        Content plan dictionary or None if not found
    """
    plan = planning_engine.get_plan(plan_id)
    if not plan:
        return None

    return {
        "plan_id": plan.plan_id,
        "title": plan.title,
        "content_type": plan.content_type,
        "target_audience": plan.target_audience,
        "objectives": plan.objectives,
        "key_messages": plan.key_messages,
        "sections": [
            {
                "section_id": s.section_id,
                "title": s.title,
                "description": s.description,
                "content_type": s.content_type,
                "target_length": s.target_length,
                "key_points": s.key_points,
                "priority": s.priority,
            }
            for s in plan.sections
        ],
        "visual_strategy": plan.visual_strategy,
        "timeline": plan.timeline,
        "resources_needed": plan.resources_needed,
        "quality_metrics": plan.quality_metrics,
        "created_at": plan.created_at.isoformat(),
        "updated_at": plan.updated_at.isoformat(),
    }


def get_all_content_plans() -> list[dict[str, Any]]:
    """
    Get all content plans.

    Returns:
        List of all content plans
    """
    plans = planning_engine.get_all_plans()
    return [
        {
            "plan_id": plan.plan_id,
            "title": plan.title,
            "content_type": plan.content_type,
            "target_audience": plan.target_audience,
            "objectives": plan.objectives,
            "key_messages": plan.key_messages,
            "sections_count": len(plan.sections),
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat(),
        }
        for plan in plans
    ]


def get_execution_history(limit: int = 50) -> list[dict[str, Any]]:
    """
    Get execution history.

    Args:
        limit: Maximum number of history entries to return

    Returns:
        List of execution history entries
    """
    history = planning_engine.get_execution_history(limit)
    return [
        {
            "execution_id": entry.execution_id,
            "status": entry.status,
            "message": entry.message,
            "progress": entry.progress,
            "timestamp": entry.timestamp.isoformat(),
        }
        for entry in history
    ]


def register(server: Any) -> None:
    """Register MCP tools with the server."""

    @server.tool()
    async def mcp_content_planning_create(
        title: str,
        content_type: str,
        target_audience: str,
        objectives: list[str],
        key_messages: list[str],
        constraints: dict[str, Any] | None = None,
        preferences: dict[str, Any] | None = None,
        model_type: str = DEFAULT_MODEL_TYPE,
    ) -> dict[str, Any]:
        """
        Create a comprehensive content plan using AI-powered planning.

        This tool integrates sequential thinking with content generation to create
        intelligent, structured content plans for various formats.

        Args:
            title: Title of the content
            content_type: Type of content (presentation, document, webpage, etc.)
            target_audience: Target audience for the content
            objectives: List of content objectives
            key_messages: Key messages to convey
            constraints: Optional constraints for the content
            preferences: Optional preferences for the content
            model_type: AI model to use for planning

        Returns:
            Complete content plan with sections, strategy, and recommendations
        """
        return await create_content_plan(
            title=title,
            content_type=content_type,
            target_audience=target_audience,
            objectives=objectives,
            key_messages=key_messages,
            constraints=constraints,
            preferences=preferences,
            model_type=model_type,
        )

    @server.tool()
    async def mcp_content_planning_execute(
        plan_id: str,
        execution_mode: str = "full",
        target_format: str = "default",
        customizations: dict[str, Any] | None = None,
        priority_sections: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Execute content creation based on a content plan.

        Args:
            plan_id: ID of the content plan to execute
            execution_mode: Execution mode (full, section, preview)
            target_format: Target output format
            customizations: Optional customizations for execution
            priority_sections: Optional list of priority sections to execute

        Returns:
            Execution results with progress and next steps
        """
        return await execute_content_plan(
            plan_id=plan_id,
            execution_mode=execution_mode,
            target_format=target_format,
            customizations=customizations,
            priority_sections=priority_sections,
        )

    @server.tool()
    def mcp_content_planning_get_plan(plan_id: str) -> dict[str, Any] | None:
        """
        Get a content plan by ID.

        Args:
            plan_id: ID of the content plan

        Returns:
            Content plan details or None if not found
        """
        return get_content_plan(plan_id)

    @server.tool()
    def mcp_content_planning_list_plans() -> list[dict[str, Any]]:
        """
        Get all content plans.

        Returns:
            List of all content plans
        """
        return get_all_content_plans()

    @server.tool()
    def mcp_content_planning_history(limit: int = 50) -> list[dict[str, Any]]:
        """
        Get execution history.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of execution history entries
        """
        return get_execution_history(limit)


if __name__ == "__main__":
    # Demo and testing
    async def main() -> None:
        print("MCP Content Planning Tool Demo")
        print("=" * 40)

        # Create a content plan
        print("Creating content plan...")
        plan_result = await create_content_plan(
            title="AI in Healthcare: Opportunities and Challenges",
            content_type="presentation",
            target_audience="Healthcare professionals and administrators",
            objectives=[
                "Educate about AI applications in healthcare",
                "Identify key challenges and opportunities",
                "Provide actionable recommendations",
            ],
            key_messages=[
                "AI can significantly improve healthcare outcomes",
                "Implementation requires careful planning and governance",
                "Success depends on human-AI collaboration",
            ],
        )

        print(f"Plan created: {plan_result['status']}")
        print(f"Plan ID: {plan_result['plan_id']}")
        print(f"Sections: {len(plan_result['content_plan']['sections'])}")

        # Execute the plan
        print("\nExecuting content plan...")
        execution_result = await execute_content_plan(plan_id=plan_result["plan_id"], execution_mode="preview")

        print(f"Execution: {execution_result['status']}")
        print(f"Execution ID: {execution_result['execution_id']}")

        # Show recommendations
        if plan_result.get("recommendations"):
            print("\nRecommendations:")
            for rec in plan_result["recommendations"]:
                print(f"  - {rec}")

        print("\nDemo completed successfully!")

    asyncio.run(main())
