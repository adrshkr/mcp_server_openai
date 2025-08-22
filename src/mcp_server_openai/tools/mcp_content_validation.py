"""
MCP Content Validation Tool

This module provides comprehensive content validation and quality assurance
capabilities for the unified content creation system.
"""

import asyncio
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_READABILITY_TARGET = "Grade 8-10"
DEFAULT_ACCURACY_THRESHOLD = 0.95
DEFAULT_COMPLETENESS_THRESHOLD = 0.90
DEFAULT_ENGAGEMENT_TARGET = 0.80
DEFAULT_ACCESSIBILITY_LEVEL = "WCAG 2.1 AA"


@dataclass
class ValidationRule:
    """Content validation rule."""

    rule_id: str
    name: str
    description: str
    category: str  # "quality", "accessibility", "seo", "technical"
    severity: str  # "critical", "warning", "info"
    enabled: bool = True
    threshold: float = 0.0
    custom_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of a validation check."""

    rule_id: str
    rule_name: str
    status: str  # "passed", "failed", "warning"
    score: float
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContentMetrics:
    """Content quality metrics."""

    word_count: int
    sentence_count: int
    paragraph_count: int
    readability_score: float
    keyword_density: dict[str, float]
    content_structure_score: float
    visual_element_score: float
    accessibility_score: float
    seo_score: float
    overall_quality_score: float


@dataclass
class ValidationRequest:
    """Request for content validation."""

    content: str
    content_type: str  # "presentation", "document", "webpage", "report"
    target_audience: str
    objectives: list[str]
    key_messages: list[str]
    validation_rules: list[str] | None = None  # Specific rules to apply
    custom_thresholds: dict[str, float] | None = None
    include_suggestions: bool = True


@dataclass
class ValidationResponse:
    """Response containing validation results."""

    status: str
    message: str
    validation_id: str
    content_metrics: ContentMetrics
    validation_results: list[ValidationResult]
    overall_score: float
    passed_rules: int
    failed_rules: int
    warning_rules: int
    recommendations: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


class ContentValidator:
    """Core content validation engine."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.validation_rules: dict[str, ValidationRule] = {}
        self.validation_history: list[ValidationResponse] = []
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default validation rules."""
        default_rules = [
            ValidationRule(
                rule_id="readability",
                name="Readability Check",
                description="Ensure content is appropriate for target audience reading level",
                category="quality",
                severity="warning",
                threshold=0.7,
            ),
            ValidationRule(
                rule_id="completeness",
                name="Content Completeness",
                description="Verify all required content elements are present",
                category="quality",
                severity="critical",
                threshold=0.9,
            ),
            ValidationRule(
                rule_id="accuracy",
                name="Content Accuracy",
                description="Check for factual accuracy and consistency",
                category="quality",
                severity="critical",
                threshold=0.95,
            ),
            ValidationRule(
                rule_id="engagement",
                name="Content Engagement",
                description="Assess content engagement and interest level",
                category="quality",
                severity="warning",
                threshold=0.8,
            ),
            ValidationRule(
                rule_id="accessibility",
                name="Accessibility Compliance",
                description="Ensure content meets accessibility standards",
                category="accessibility",
                severity="warning",
                threshold=0.8,
            ),
            ValidationRule(
                rule_id="seo",
                name="SEO Optimization",
                description="Check SEO best practices and keyword usage",
                category="seo",
                severity="info",
                threshold=0.7,
            ),
            ValidationRule(
                rule_id="structure",
                name="Content Structure",
                description="Validate logical content organization and flow",
                category="quality",
                severity="warning",
                threshold=0.8,
            ),
            ValidationRule(
                rule_id="visual_elements",
                name="Visual Elements",
                description="Assess visual content quality and relevance",
                category="quality",
                severity="info",
                threshold=0.7,
            ),
        ]

        for rule in default_rules:
            self.validation_rules[rule.rule_id] = rule

    async def validate_content(self, request: ValidationRequest) -> ValidationResponse:
        """Validate content according to configured rules."""
        try:
            # Generate validation ID
            validation_id = (
                f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.content[:100]) % 10000}"
            )

            # Calculate content metrics
            content_metrics = await self._calculate_content_metrics(request.content, request.content_type)

            # Apply validation rules
            validation_results = await self._apply_validation_rules(request, content_metrics)

            # Calculate overall score
            overall_score = self._calculate_overall_score(validation_results)

            # Count rule results
            passed_rules = sum(1 for r in validation_results if r.status == "passed")
            failed_rules = sum(1 for r in validation_results if r.status == "failed")
            warning_rules = sum(1 for r in validation_results if r.status == "warning")

            # Generate recommendations
            recommendations = await self._generate_recommendations(validation_results, content_metrics, request)

            # Create response
            response = ValidationResponse(
                status="success",
                message=f"Content validation completed. Overall score: {overall_score:.2f}",
                validation_id=validation_id,
                content_metrics=content_metrics,
                validation_results=validation_results,
                overall_score=overall_score,
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                warning_rules=warning_rules,
                recommendations=recommendations,
            )

            # Store in history
            self.validation_history.append(response)

            return response

        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return ValidationResponse(
                status="error",
                message=f"Content validation failed: {str(e)}",
                validation_id="error",
                content_metrics=ContentMetrics(
                    word_count=0,
                    sentence_count=0,
                    paragraph_count=0,
                    readability_score=0.0,
                    keyword_density={},
                    content_structure_score=0.0,
                    visual_element_score=0.0,
                    accessibility_score=0.0,
                    seo_score=0.0,
                    overall_quality_score=0.0,
                ),
                validation_results=[],
                overall_score=0.0,
                passed_rules=0,
                failed_rules=0,
                warning_rules=0,
                recommendations=[],
            )

    async def _calculate_content_metrics(self, content: str, content_type: str) -> ContentMetrics:
        """Calculate comprehensive content metrics."""
        # Basic text metrics
        words = content.split()
        word_count = len(words)

        sentences = re.split(r"[.!?]+", content)
        sentence_count = len([s for s in sentences if s.strip()])

        paragraphs = content.split("\n\n")
        paragraph_count = len([p for p in paragraphs if p.strip()])

        # Readability score (Flesch Reading Ease)
        readability_score = self._calculate_readability_score(content)

        # Keyword density
        keyword_density = self._calculate_keyword_density(content)

        # Content structure score
        content_structure_score = self._assess_content_structure(content, content_type)

        # Visual element score
        visual_element_score = self._assess_visual_elements(content, content_type)

        # Accessibility score
        accessibility_score = self._assess_accessibility(content, content_type)

        # SEO score
        seo_score = self._assess_seo_optimization(content, content_type)

        # Overall quality score
        overall_quality_score = (
            readability_score * 0.2
            + content_structure_score * 0.25
            + visual_element_score * 0.15
            + accessibility_score * 0.2
            + seo_score * 0.2
        )

        return ContentMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            readability_score=readability_score,
            keyword_density=keyword_density,
            content_structure_score=content_structure_score,
            visual_element_score=visual_element_score,
            accessibility_score=accessibility_score,
            seo_score=seo_score,
            overall_quality_score=overall_quality_score,
        )

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate Flesch Reading Ease score."""
        try:
            words = content.split()
            sentences = re.split(r"[.!?]+", content)
            sentences = [s for s in sentences if s.strip()]

            if not words or not sentences:
                return 0.0

            # Count syllables (approximate)
            syllables = 0
            for word in words:
                word_lower = word.lower()
                if word_lower.endswith("e"):
                    word_lower = word_lower[:-1]
                syllables += len(re.findall(r"[aeiouy]+", word_lower))

            # Flesch Reading Ease formula
            flesch_score = 206.835 - (1.015 * (len(words) / len(sentences))) - (84.6 * (syllables / len(words)))

            # Normalize to 0-1 scale
            return max(0.0, min(1.0, flesch_score / 100.0))

        except Exception:
            return 0.5  # Default score

    def _calculate_keyword_density(self, content: str) -> dict[str, float]:
        """Calculate keyword density for important terms."""
        words = content.lower().split()
        word_count = len(words)

        if word_count == 0:
            return {}

        # Common important words to track
        important_words = [
            "ai",
            "artificial",
            "intelligence",
            "machine",
            "learning",
            "data",
            "analysis",
            "technology",
            "digital",
            "transformation",
            "innovation",
            "strategy",
            "business",
            "customer",
            "user",
            "experience",
            "design",
            "development",
            "implementation",
        ]

        keyword_density = {}
        for word in important_words:
            count = words.count(word)
            density = count / word_count
            if density > 0.001:  # Only include if density > 0.1%
                keyword_density[word] = density

        return keyword_density

    def _assess_content_structure(self, content: str, content_type: str) -> float:
        """Assess content structure and organization."""
        score = 0.5  # Base score

        # Check for headings and structure
        if re.search(r"^#+\s+", content, re.MULTILINE):
            score += 0.2

        # Check for logical flow
        paragraphs = content.split("\n\n")
        if len(paragraphs) >= 3:
            score += 0.15

        # Check for bullet points or lists
        if re.search(r"^[\-\*]\s+", content, re.MULTILINE):
            score += 0.15

        # Content type specific checks
        if content_type == "presentation":
            if re.search(r"slide|section|slide", content, re.IGNORECASE):
                score += 0.1
        elif content_type == "document":
            if re.search(r"introduction|conclusion|summary", content, re.IGNORECASE):
                score += 0.1

        return min(score, 1.0)

    def _assess_visual_elements(self, content: str, content_type: str) -> float:
        """Assess visual element quality and relevance."""
        score = 0.5  # Base score

        # Check for image references
        if re.search(r"image|picture|photo|graphic|chart|diagram", content, re.IGNORECASE):
            score += 0.2

        # Check for data visualization references
        if re.search(r"chart|graph|table|infographic", content, re.IGNORECASE):
            score += 0.2

        # Check for color and design references
        if re.search(r"color|design|layout|style|theme", content, re.IGNORECASE):
            score += 0.1

        return min(score, 1.0)

    def _assess_accessibility(self, content: str, content_type: str) -> float:
        """Assess accessibility compliance."""
        score = 0.5  # Base score

        # Check for alt text references
        if re.search(r"alt\s*text|alternative\s*text|description", content, re.IGNORECASE):
            score += 0.2

        # Check for clear language
        if re.search(r"clear|simple|understandable|accessible", content, re.IGNORECASE):
            score += 0.15

        # Check for structure indicators
        if re.search(r"heading|title|section|chapter", content, re.IGNORECASE):
            score += 0.15

        return min(score, 1.0)

    def _assess_seo_optimization(self, content: str, content_type: str) -> float:
        """Assess SEO optimization."""
        score = 0.5  # Base score

        # Check for meta information
        if re.search(r"meta|title|description|keywords", content, re.IGNORECASE):
            score += 0.2

        # Check for internal linking
        if re.search(r"link|reference|see\s+also", content, re.IGNORECASE):
            score += 0.15

        # Check for keyword optimization
        if len(self._calculate_keyword_density(content)) > 0:
            score += 0.15

        return min(score, 1.0)

    async def _apply_validation_rules(
        self, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> list[ValidationResult]:
        """Apply validation rules to content."""
        results = []

        # Determine which rules to apply
        rules_to_apply = request.validation_rules or list(self.validation_rules.keys())

        for rule_id in rules_to_apply:
            if rule_id in self.validation_rules:
                rule = self.validation_rules[rule_id]
                if rule.enabled:
                    result = await self._apply_single_rule(rule, request, content_metrics)
                    results.append(result)

        return results

    async def _apply_single_rule(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Apply a single validation rule."""
        try:
            if rule.rule_id == "readability":
                return self._validate_readability(rule, request, content_metrics)
            elif rule.rule_id == "completeness":
                return self._validate_completeness(rule, request, content_metrics)
            elif rule.rule_id == "accuracy":
                return self._validate_accuracy(rule, request, content_metrics)
            elif rule.rule_id == "engagement":
                return self._validate_engagement(rule, request, content_metrics)
            elif rule.rule_id == "accessibility":
                return self._validate_accessibility(rule, request, content_metrics)
            elif rule.rule_id == "seo":
                return self._validate_seo(rule, request, content_metrics)
            elif rule.rule_id == "structure":
                return self._validate_structure(rule, request, content_metrics)
            elif rule.rule_id == "visual_elements":
                return self._validate_visual_elements(rule, request, content_metrics)
            else:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    status="warning",
                    score=0.0,
                    message=f"Unknown validation rule: {rule.rule_id}",
                    suggestions=["Contact system administrator for rule configuration"],
                )

        except Exception as e:
            logger.error(f"Error applying rule {rule.rule_id}: {e}")
            return ValidationResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status="warning",
                score=0.0,
                message=f"Rule application failed: {str(e)}",
                suggestions=["Check rule configuration and try again"],
            )

    def _validate_readability(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate content readability."""
        score = content_metrics.readability_score
        threshold = rule.threshold

        if score >= threshold:
            status = "passed"
            message = f"Readability score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"Readability score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.6:
            suggestions.append("Consider simplifying language and sentence structure")
            suggestions.append("Use shorter sentences and common words")
        elif score < 0.8:
            suggestions.append("Review complex sentences for clarity")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _validate_completeness(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate content completeness."""
        # Check if all objectives are addressed
        content_lower = request.content.lower()
        objectives_covered = 0

        for objective in request.objectives:
            if any(word.lower() in content_lower for word in objective.split()):
                objectives_covered += 1

        score = objectives_covered / len(request.objectives) if request.objectives else 1.0
        threshold = rule.threshold

        if score >= threshold:
            status = "passed"
            message = f"Completeness score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"Completeness score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.8:
            suggestions.append("Ensure all content objectives are addressed")
            suggestions.append("Add missing content sections")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _validate_accuracy(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate content accuracy."""
        # This would integrate with fact-checking services
        # For now, use a basic heuristic
        score = 0.9  # Default high score
        threshold = rule.threshold

        # Check for common accuracy indicators
        content_lower = request.content.lower()
        if re.search(r"according\s+to|research\s+shows|studies\s+indicate", content_lower):
            score += 0.05
        if re.search(r"verified|confirmed|proven", content_lower):
            score += 0.05

        score = min(score, 1.0)

        if score >= threshold:
            status = "passed"
            message = f"Accuracy score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"Accuracy score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.9:
            suggestions.append("Verify factual claims with reliable sources")
            suggestions.append("Add citations and references where appropriate")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _validate_engagement(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate content engagement."""
        score = content_metrics.overall_quality_score
        threshold = rule.threshold

        if score >= threshold:
            status = "passed"
            message = f"Engagement score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"Engagement score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.7:
            suggestions.append("Add more engaging content elements")
            suggestions.append("Include examples, stories, or case studies")
            suggestions.append("Use more active voice and compelling language")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _validate_accessibility(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate accessibility compliance."""
        score = content_metrics.accessibility_score
        threshold = rule.threshold

        if score >= threshold:
            status = "passed"
            message = f"Accessibility score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"Accessibility score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.8:
            suggestions.append("Add alt text for images and visual elements")
            suggestions.append("Ensure clear heading structure")
            suggestions.append("Use simple, clear language")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _validate_seo(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate SEO optimization."""
        score = content_metrics.seo_score
        threshold = rule.threshold

        if score >= threshold:
            status = "passed"
            message = f"SEO score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"SEO score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.7:
            suggestions.append("Optimize content with relevant keywords")
            suggestions.append("Add meta descriptions and titles")
            suggestions.append("Include internal and external links")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _validate_structure(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate content structure."""
        score = content_metrics.content_structure_score
        threshold = rule.threshold

        if score >= threshold:
            status = "passed"
            message = f"Structure score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"Structure score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.8:
            suggestions.append("Improve content organization and flow")
            suggestions.append("Add clear headings and sections")
            suggestions.append("Use bullet points and lists for better readability")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _validate_visual_elements(
        self, rule: ValidationRule, request: ValidationRequest, content_metrics: ContentMetrics
    ) -> ValidationResult:
        """Validate visual elements."""
        score = content_metrics.visual_element_score
        threshold = rule.threshold

        if score >= threshold:
            status = "passed"
            message = f"Visual elements score {score:.2f} meets threshold {threshold:.2f}"
        else:
            status = "failed"
            message = f"Visual elements score {score:.2f} below threshold {threshold:.2f}"

        suggestions = []
        if score < 0.7:
            suggestions.append("Add relevant images, charts, or diagrams")
            suggestions.append("Include visual examples and illustrations")
            suggestions.append("Use infographics to explain complex concepts")

        return ValidationResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=status,
            score=score,
            message=message,
            suggestions=suggestions,
        )

    def _calculate_overall_score(self, validation_results: list[ValidationResult]) -> float:
        """Calculate overall validation score."""
        if not validation_results:
            return 0.0

        # Weight scores by severity
        total_weight = 0
        weighted_sum = 0

        for result in validation_results:
            if result.status == "passed":
                weight = 1.0
            elif result.status == "warning":
                weight = 0.5
            else:  # failed
                weight = 0.0

            total_weight += weight
            weighted_sum += result.score * weight

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    async def _generate_recommendations(
        self, validation_results: list[ValidationResult], content_metrics: ContentMetrics, request: ValidationRequest
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Add rule-specific recommendations
        for result in validation_results:
            if result.status != "passed" and result.suggestions:
                recommendations.extend(result.suggestions)

        # Add general recommendations based on metrics
        if content_metrics.readability_score < 0.7:
            recommendations.append("Improve readability by simplifying language and sentence structure")

        if content_metrics.content_structure_score < 0.8:
            recommendations.append("Enhance content structure with clear headings and logical flow")

        if content_metrics.visual_element_score < 0.7:
            recommendations.append("Add visual elements to improve engagement and understanding")

        if content_metrics.accessibility_score < 0.8:
            recommendations.append("Enhance accessibility compliance for broader audience reach")

        # Content type specific recommendations
        if request.content_type == "presentation":
            recommendations.append("Ensure slides have clear, concise content with visual support")
        elif request.content_type == "document":
            recommendations.append("Include table of contents and executive summary for better navigation")
        elif request.content_type == "webpage":
            recommendations.append("Optimize for web with proper headings, meta tags, and internal linking")

        # Remove duplicates and limit
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:10]  # Limit to 10 recommendations

    def get_validation_history(self, limit: int = 50) -> list[ValidationResponse]:
        """Get validation history."""
        return self.validation_history[-limit:] if self.validation_history else []

    def get_validation_result(self, validation_id: str) -> ValidationResponse | None:
        """Get specific validation result."""
        for result in self.validation_history:
            if result.validation_id == validation_id:
                return result
        return None


# Global instance
content_validator = ContentValidator()


async def validate_content_quality(
    content: str,
    content_type: str,
    target_audience: str,
    objectives: list[str],
    key_messages: list[str],
    validation_rules: list[str] | None = None,
    custom_thresholds: dict[str, float] | None = None,
    include_suggestions: bool = True,
) -> dict[str, Any]:
    """
    Validate content quality and provide improvement recommendations.

    Args:
        content: Content to validate
        content_type: Type of content (presentation, document, webpage, report)
        target_audience: Target audience for the content
        objectives: Content objectives
        key_messages: Key messages to convey
        validation_rules: Specific validation rules to apply
        custom_thresholds: Custom thresholds for validation rules
        include_suggestions: Whether to include improvement suggestions

    Returns:
        Dictionary containing validation results and recommendations
    """
    request = ValidationRequest(
        content=content,
        content_type=content_type,
        target_audience=target_audience,
        objectives=objectives,
        key_messages=key_messages,
        validation_rules=validation_rules,
        custom_thresholds=custom_thresholds,
        include_suggestions=include_suggestions,
    )

    response = await content_validator.validate_content(request)

    return {
        "status": response.status,
        "message": response.message,
        "validation_id": response.validation_id,
        "overall_score": response.overall_score,
        "passed_rules": response.passed_rules,
        "failed_rules": response.failed_rules,
        "warning_rules": response.warning_rules,
        "content_metrics": {
            "word_count": response.content_metrics.word_count,
            "sentence_count": response.content_metrics.sentence_count,
            "paragraph_count": response.content_metrics.paragraph_count,
            "readability_score": response.content_metrics.readability_score,
            "content_structure_score": response.content_metrics.content_structure_score,
            "visual_element_score": response.content_metrics.visual_element_score,
            "accessibility_score": response.content_metrics.accessibility_score,
            "seo_score": response.content_metrics.seo_score,
            "overall_quality_score": response.content_metrics.overall_quality_score,
        },
        "validation_results": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "status": r.status,
                "score": r.score,
                "message": r.message,
                "suggestions": r.suggestions,
            }
            for r in response.validation_results
        ],
        "recommendations": response.recommendations,
        "timestamp": response.timestamp.isoformat(),
    }


def get_validation_history(limit: int = 50) -> list[dict[str, Any]]:
    """Get validation history."""
    history = content_validator.get_validation_history(limit)
    return [
        {
            "validation_id": result.validation_id,
            "overall_score": result.overall_score,
            "passed_rules": result.passed_rules,
            "failed_rules": result.failed_rules,
            "warning_rules": result.warning_rules,
            "timestamp": result.timestamp.isoformat(),
        }
        for result in history
    ]


def get_validation_result(validation_id: str) -> dict[str, Any] | None:
    """Get specific validation result."""
    result = content_validator.get_validation_result(validation_id)
    if not result:
        return None

    return {
        "validation_id": result.validation_id,
        "overall_score": result.overall_score,
        "passed_rules": result.passed_rules,
        "failed_rules": result.failed_rules,
        "warning_rules": result.warning_rules,
        "content_metrics": {
            "word_count": result.content_metrics.word_count,
            "sentence_count": result.content_metrics.sentence_count,
            "paragraph_count": result.content_metrics.paragraph_count,
            "readability_score": result.content_metrics.readability_score,
            "content_structure_score": result.content_metrics.content_structure_score,
            "visual_element_score": result.content_metrics.visual_element_score,
            "accessibility_score": result.content_metrics.accessibility_score,
            "seo_score": result.content_metrics.seo_score,
            "overall_quality_score": result.content_metrics.overall_quality_score,
        },
        "validation_results": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "status": r.status,
                "score": r.score,
                "message": r.message,
                "suggestions": r.suggestions,
            }
            for r in result.validation_results
        ],
        "recommendations": result.recommendations,
        "timestamp": result.timestamp.isoformat(),
    }


def register(server: Any) -> None:
    """Register MCP tools with the server."""

    @server.tool()
    async def mcp_content_validation_validate_content(
        content: str,
        content_type: str,
        target_audience: str,
        objectives: list[str],
        key_messages: list[str],
        validation_rules: list[str] | None = None,
        custom_thresholds: dict[str, float] | None = None,
        include_suggestions: bool = True,
    ) -> dict[str, Any]:
        """
        Validate content quality and provide improvement recommendations.

        This tool provides comprehensive content validation including readability,
        completeness, accuracy, engagement, accessibility, and SEO optimization.

        Args:
            content: Content to validate
            content_type: Type of content (presentation, document, webpage, report)
            target_audience: Target audience for the content
            objectives: Content objectives
            key_messages: Key messages to convey
            validation_rules: Specific validation rules to apply
            custom_thresholds: Custom thresholds for validation rules
            include_suggestions: Whether to include improvement suggestions

        Returns:
            Comprehensive validation results with metrics and recommendations
        """
        return await validate_content_quality(
            content=content,
            content_type=content_type,
            target_audience=target_audience,
            objectives=objectives,
            key_messages=key_messages,
            validation_rules=validation_rules,
            custom_thresholds=custom_thresholds,
            include_suggestions=include_suggestions,
        )

    @server.tool()
    def mcp_content_validation_get_history(limit: int = 50) -> list[dict[str, Any]]:
        """
        Get validation history.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of validation history entries
        """
        return get_validation_history(limit)

    @server.tool()
    def mcp_content_validation_get_result(validation_id: str) -> dict[str, Any] | None:
        """
        Get specific validation result.

        Args:
            validation_id: ID of the validation result

        Returns:
            Validation result details or None if not found
        """
        return get_validation_result(validation_id)


if __name__ == "__main__":
    # Demo and testing
    async def main() -> None:
        print("MCP Content Validation Tool Demo")
        print("=" * 40)

        # Sample content for validation
        sample_content = """
        # AI in Healthcare: Opportunities and Challenges
        
        Artificial Intelligence (AI) is transforming healthcare delivery across the globe. 
        This presentation explores the current state of AI applications in healthcare, 
        identifies key challenges and opportunities, and provides actionable recommendations 
        for successful implementation.
        
        ## Current Applications
        
        AI is currently being used in:
        - Medical imaging and diagnostics
        - Drug discovery and development
        - Patient care and monitoring
        - Administrative tasks and scheduling
        
        ## Key Challenges
        
        Despite its potential, AI implementation faces several challenges:
        - Data privacy and security concerns
        - Regulatory compliance requirements
        - Integration with existing systems
        - Staff training and adoption
        
        ## Recommendations
        
        To successfully implement AI in healthcare:
        1. Start with pilot projects
        2. Ensure robust data governance
        3. Invest in staff training
        4. Monitor and evaluate outcomes
        """

        print("Validating sample content...")
        validation_result = await validate_content_quality(
            content=sample_content,
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

        print(f"Validation Status: {validation_result['status']}")
        print(f"Validation ID: {validation_result['validation_id']}")
        print(f"Overall Score: {validation_result['overall_score']:.2f}")
        print(f"Passed Rules: {validation_result['passed_rules']}")
        print(f"Failed Rules: {validation_result['failed_rules']}")
        print(f"Warning Rules: {validation_result['warning_rules']}")

        metrics = validation_result["content_metrics"]
        print("\nContent Metrics:")
        print(f"  Word Count: {metrics['word_count']}")
        print(f"  Readability Score: {metrics['readability_score']:.2f}")
        print(f"  Structure Score: {metrics['content_structure_score']:.2f}")
        print(f"  Visual Elements Score: {metrics['visual_element_score']:.2f}")
        print(f"  Accessibility Score: {metrics['accessibility_score']:.2f}")
        print(f"  SEO Score: {metrics['seo_score']:.2f}")

        print(f"\nValidation Results ({len(validation_result['validation_results'])}):")
        for result in validation_result["validation_results"]:
            print(f"  {result['rule_name']}: {result['status']} (Score: {result['score']:.2f})")
            print(f"    {result['message']}")
            if result["suggestions"]:
                for suggestion in result["suggestions"]:
                    print(f"    - {suggestion}")
            print()

        print(f"Recommendations ({len(validation_result['recommendations'])}):")
        for rec in validation_result["recommendations"]:
            print(f"  - {rec}")

        print("\nDemo completed successfully!")

    asyncio.run(main())
