"""
Enhanced PPT Generator Tool with Presenton API Integration.

This tool combines the power of our MCP server infrastructure with advanced
LLM preprocessing and the Presenton API for high-quality presentation generation.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from ...logging_utils import get_logger, log_accept, log_exception, log_response
from ...progress import create_progress_tracker

# Load environment variables
load_dotenv()

_LOG = get_logger("mcp.tool.enhanced_ppt_generator")
_TOOL = "enhanced_ppt.create"

# Configuration constants
DEFAULT_MODEL_TYPE = "gpt-4o"  # Primary default, falls back to gpt-4o-mini if not available
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TEMPERATURE = 0.2
SUPPORTED_TEMPLATES = ["classic", "general", "modern", "professional"]
SUPPORTED_LANGUAGES = ["English", "Spanish", "French", "German", "Chinese", "Japanese"]


@dataclass
class PPTRequest:
    """Structured PPT generation request."""

    notes: list[str]
    brief: str
    target_length: str
    model_type: str = DEFAULT_MODEL_TYPE
    template_preference: str = "auto"
    include_images: bool = False
    language: str = "English"
    client_id: str | None = None


@dataclass
class PPTResponse:
    """Structured PPT generation response."""

    status: str
    presentation_id: str | None = None
    file_path: str | None = None
    draft_name: str | None = None
    template_used: str | None = None
    slides_count: int | None = None
    file_size: int = 0
    processing_time_ms: float | None = None
    token_usage: dict[str, int] | None = None
    error: str | None = None
    client_id: str | None = None


class LLMClient:
    """Client for interacting with various LLM providers."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

    async def chat_with_model(
        self,
        model_type: str,
        messages: list[dict[str, str]],
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        json_schema: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, str]], Any, int, int]:
        """
        Invokes LLM API to chat with the model.

        Args:
            model_type: Type of model to use (gpt, claude, gemini)
            messages: List of message dictionaries
            temperature: Model temperature setting
            max_tokens: Maximum tokens for response
            json_schema: Optional JSON schema for structured output

        Returns:
            Tuple of (messages, response, input_tokens, output_tokens)
        """
        try:
            if model_type.startswith("gpt"):
                return await self._call_openai(model_type, messages, temperature, max_tokens, json_schema)
            elif model_type.startswith("claude"):
                return await self._call_anthropic(model_type, messages, temperature, max_tokens, json_schema)
            elif model_type.startswith("gemini"):
                return await self._call_google(model_type, messages, temperature, max_tokens, json_schema)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

        except Exception as e:
            _LOG.error(f"Error calling {model_type}: {e}")
            raise

    async def _call_openai(
        self,
        model_type: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        json_schema: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, str]], Any, int, int]:
        """Call OpenAI API."""
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=model_type, temperature=temperature, max_tokens=max_tokens, api_key=self.openai_api_key
            )

            if json_schema:
                llm = llm.with_structured_output(json_schema, include_raw=True)
                response = llm.invoke(messages)
                messages = messages + [response["raw"]]
                input_tokens = response["raw"].usage_metadata["input_tokens"]
                output_tokens = response["raw"].usage_metadata["output_tokens"]
                response = response["parsed"]
            else:
                response = llm.invoke(messages)
                messages = messages + [response]
                input_tokens = response.usage_metadata["input_tokens"]
                output_tokens = response.usage_metadata["output_tokens"]
                response = response.content

            return messages, response, input_tokens, output_tokens

        except ImportError as e:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai") from e

    async def _call_anthropic(
        self,
        model_type: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        json_schema: dict[str, Any] | None = None,
    ) -> tuple:
        """Call Anthropic API."""
        try:
            from langchain_anthropic import ChatAnthropic

            llm = ChatAnthropic(
                model=model_type,
                temperature=temperature,
                max_tokens=max_tokens,
                anthropic_api_key=self.anthropic_api_key,
            )

            if json_schema:
                llm = llm.with_structured_output(json_schema, include_raw=True)
                response = llm.invoke(messages)
                messages = messages + [response["raw"]]
                input_tokens = response["raw"].usage_metadata["input_tokens"]
                output_tokens = response["raw"].usage_metadata["output_tokens"]
                response = response["parsed"]
            else:
                response = llm.invoke(messages)
                messages = messages + [response]
                input_tokens = response.usage_metadata["input_tokens"]
                output_tokens = response.usage_metadata["output_tokens"]
                response = response.content

            return messages, response, input_tokens, output_tokens

        except ImportError as e:
            raise ImportError("langchain-anthropic not installed. Run: pip install langchain-anthropic") from e

    async def _call_google(
        self,
        model_type: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        json_schema: dict[str, Any] | None = None,
    ) -> tuple:
        """Call Google API."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=model_type, temperature=temperature, max_tokens=max_tokens, api_key=self.google_api_key
            )

            if json_schema:
                llm = llm.with_structured_output(json_schema, include_raw=True)
                response = llm.invoke(messages)
                messages = messages + [response["raw"]]
                input_tokens = response["raw"].usage_metadata["input_tokens"]
                output_tokens = response["raw"].usage_metadata["output_tokens"]
                response = response["parsed"]
            else:
                response = llm.invoke(messages)
                messages = messages + [response]
                input_tokens = response.usage_metadata["input_tokens"]
                output_tokens = response.usage_metadata["output_tokens"]
                response = response.content

            return messages, response, input_tokens, output_tokens

        except ImportError as e:
            raise ImportError("langchain-google-genai not installed. Run: pip install langchain-google-genai") from e


class PresentonAPIClient:
    """Client for interacting with the Presenton API."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("PRESENTON_API_URL", "http://localhost:5000")
        self.generate_endpoint = f"{self.base_url}/api/v1/ppt/presentation/generate"

    async def generate_presentation(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Generate presentation using Presenton API.

        Args:
            payload: API payload with prompt, n_slides, language, template, export_as

        Returns:
            API response with presentation_id and path
        """
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.generate_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Presenton API: {e}") from e

    async def download_presentation(self, ppt_path: str, draft_name: str) -> str:
        """
        Download the generated presentation.

        Args:
            ppt_path: Path returned from API
            draft_name: Name for the downloaded file

        Returns:
            Local file path where presentation was saved
        """
        try:
            download_url = f"{self.base_url}{ppt_path}"
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Create output directory
            output_dir = Path("output") / "presentations"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save file
            local_file_path = output_dir / f"{draft_name}.pptx"
            with open(local_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return str(local_file_path)

        except Exception as e:
            raise Exception(f"Error downloading presentation: {e}") from e


class EnhancedPPTGenerator:
    """Main class for enhanced PPT generation."""

    def __init__(self):
        self.llm_client = LLMClient()
        self.presenton_client = PresentonAPIClient()

    async def preprocess_for_presenton(self, request: PPTRequest) -> dict[str, Any]:
        """
        Preprocess inputs using LLM for structured JSON output.

        Args:
            request: PPT generation request

        Returns:
            Structured API arguments
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        notes_str = "\n".join(request.notes) if isinstance(request.notes, list) else request.notes
        parsed_slides = self._parse_max_slides(request.target_length) if request.target_length else None

        system_content = """
        You are an expert at preparing inputs for the Presenton PPT generation API.
        Analyze the provided notes, document brief, and length constraint.
        Output a JSON object with:
        - 'prompt': A refined, detailed prompt combining notes and brief into a logical structure without
        abbreviating, reducing, or summarizing it. Make good additions for refinement, such as suggesting
        slide outlines or enhancements for clarity and engagement. Only mention images or make the prompt
        image-friendly for Pixabay if the user explicitly requests images in the notes or brief. If no
        explicit requests for images, add instruction to not add any images.
        - 'n_slides': Integer (5-15). If a fixed number is provided in the length constraint, use that
        exactly. Otherwise, estimate based on content volume (e.g., short=6-8, long=12-15).
        - 'language': String (e.g., 'English').
        - 'template': String (choose one from: 'classic' for timeless/academic, 'general' for
        versatile/business, 'modern' for creative/startups, 'professional' for corporate/pitches—based
        on tone/content).
        - 'export_as': 'pptx'.
        - 'draft_name': String (3-4 words, logical PPT file name based on content, plain text without
        quotes/extensions).
        Ensure the prompt is engaging, organized, and image-friendly for Pixabay integration (if the user
        explicitly requests images in the notes or brief) and preserving all user-provided details verbatim.
        """

        # Include parsed_slides in user_content if available
        length_info = f"Length: {request.target_length}"
        if parsed_slides:
            length_info += f" (Fixed slides: {parsed_slides}—use this for 'n_slides')"

        # Add template preference if specified
        if request.template_preference != "auto":
            length_info += f"\nTemplate preference: {request.template_preference}"

        # Add image preference
        if request.include_images:
            length_info += "\nInclude images: Yes (make prompt image-friendly)"
        else:
            length_info += "\nInclude images: No (do not add any images)"

        user_content = f"Notes: {notes_str}\nBrief: {request.brief}\n{length_info}"

        messages = [SystemMessage(content=system_content), HumanMessage(content=user_content)]

        json_schema = {
            "name": "presenton_args",
            "schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "n_slides": {"type": "integer"},
                    "language": {"type": "string"},
                    "template": {"type": "string"},
                    "export_as": {"type": "string"},
                    "draft_name": {"type": "string"},
                },
                "required": ["prompt", "n_slides", "language", "template", "export_as", "draft_name"],
                "additionalProperties": False,
            },
        }

        _, api_args, input_tokens, output_tokens = await self.llm_client.chat_with_model(
            request.model_type,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            json_schema=json_schema,
        )

        return api_args, input_tokens, output_tokens

    def _parse_max_slides(self, target_length: str) -> int | None:
        """
        Parse or estimate the number of slides from target_length.

        Args:
            target_length: Target document length specification

        Returns:
            Estimated number of slides or None if cannot parse
        """
        if not target_length:
            return None

        # Try to extract specific slide count
        match = re.search(r"(\d+)\s*slides?", target_length, re.IGNORECASE)
        if match:
            slides = int(match.group(1))
            return max(5, min(15, slides))

        # Try to extract word count and estimate
        match = re.search(r"(\d+)\s*words?", target_length, re.IGNORECASE)
        if match:
            words = int(match.group(1))
            slides = max(5, min(15, words // 50))
            return slides

        # Try to extract character count and estimate
        match = re.search(r"(\d+)\s*characters?", target_length, re.IGNORECASE)
        if match:
            chars = int(match.group(1))
            slides = max(5, min(15, chars // 200))
            return slides

        return None

    async def generate_presentation(self, request: PPTRequest) -> PPTResponse:
        """
        Generate presentation using enhanced workflow.

        Args:
            request: PPT generation request

        Returns:
            PPT generation response
        """
        request_id = f"ppt-req-{int(time.time() * 1000)}"
        start_time = time.monotonic()

        # Create progress tracker
        progress = create_progress_tracker(_TOOL, request_id, total_steps=5)

        # Log request acceptance
        log_accept(
            _LOG,
            tool=_TOOL,
            client_id=request.client_id,
            request_id=request_id,
            payload={
                "notes_count": len(request.notes),
                "brief_length": len(request.brief),
                "target_length": request.target_length,
                "model_type": request.model_type,
            },
        )

        try:
            # Step 1: LLM preprocessing
            with progress.step_context("llm_preprocessing", {"model_type": request.model_type}):
                api_args, input_tokens, output_tokens = await self.preprocess_for_presenton(request)
                progress.update_progress(20.0, "LLM preprocessing completed")

            # Step 2: Validate and prepare API payload
            with progress.step_context("prepare_payload", {"template": api_args.get("template")}):
                payload = {
                    "prompt": api_args["prompt"],
                    "n_slides": api_args["n_slides"],
                    "language": api_args["language"],
                    "template": api_args["template"],
                    "export_as": api_args["export_as"],
                }
                progress.update_progress(40.0, "API payload prepared")

            # Step 3: Call Presenton API
            with progress.step_context("presenton_api", {"endpoint": "generate"}):
                api_response = await self.presenton_client.generate_presentation(payload)
                progress.update_progress(60.0, "Presenton API call completed")

            # Step 4: Download presentation
            with progress.step_context("download_presentation", {"draft_name": api_args["draft_name"]}):
                local_file_path = await self.presenton_client.download_presentation(
                    api_response["path"], api_args["draft_name"]
                )
                progress.update_progress(80.0, "Presentation downloaded")

            # Step 5: Finalize
            with progress.step_context("finalize", {"status": "success"}):
                progress.update_progress(100.0, "Presentation generation completed")

            # Calculate processing time
            processing_time_ms = (time.monotonic() - start_time) * 1000.0

            # Log successful completion
            log_response(
                _LOG,
                tool=_TOOL,
                request_id=request_id,
                status="ok",
                duration_ms=processing_time_ms,
                size=api_args.get("n_slides", 0),
            )

            progress.complete(
                "presentation_generated",
                {"status": "success", "slides_count": api_args.get("n_slides", 0), "file_path": local_file_path},
            )

            return PPTResponse(
                status="success",
                presentation_id=api_response.get("presentation_id"),
                file_path=local_file_path,
                draft_name=api_args["draft_name"],
                template_used=api_args["template"],
                slides_count=api_args.get("n_slides", 0),
                processing_time_ms=processing_time_ms,
                token_usage={"input": input_tokens, "output": output_tokens},
                client_id=request.client_id,
            )

        except Exception as exc:
            log_exception(_LOG, tool=_TOOL, request_id=request_id, exc=exc)
            processing_time_ms = (time.monotonic() - start_time) * 1000.0
            log_response(_LOG, tool=_TOOL, request_id=request_id, status="error", duration_ms=processing_time_ms)

            progress.complete("presentation_failed", {"status": "error", "error": str(exc)})

            return PPTResponse(
                status="error", error=str(exc), processing_time_ms=processing_time_ms, client_id=request.client_id
            )


# Global instance
_ppt_generator = EnhancedPPTGenerator()


async def create_enhanced_presentation(
    notes: list[str],
    brief: str,
    target_length: str,
    model_type: str = DEFAULT_MODEL_TYPE,
    template_preference: str = "auto",
    include_images: bool = False,
    language: str = "English",
    client_id: str | None = None,
    generator: EnhancedPPTGenerator | None = None,
) -> PPTResponse:
    """
    Create enhanced presentation using Presenton API with LLM preprocessing.

    Args:
        notes: List of content notes
        brief: Brief description of the presentation
        target_length: Target length specification
        model_type: LLM model to use for preprocessing
        template_preference: Template preference (auto, classic, general, modern, professional)
        include_images: Whether to include images
        language: Presentation language
        client_id: Client identifier for customization
        generator: Optional generator instance (for testing)

    Returns:
        PPT generation response
    """
    request = PPTRequest(
        notes=notes,
        brief=brief,
        target_length=target_length,
        model_type=model_type,
        template_preference=template_preference,
        include_images=include_images,
        language=language,
        client_id=client_id,
    )

    # Use provided generator for testing, otherwise use global instance
    ppt_generator = generator or _ppt_generator
    return await ppt_generator.generate_presentation(request)


def register(mcp: Any) -> None:
    """
    Register enhanced PPT generation tools on the provided FastMCP instance.
    """

    @mcp.tool(
        name="enhanced_ppt.create",
        description=(
            "Create enhanced PowerPoint presentations using Presenton API with LLM preprocessing "
            "for intelligent content structuring and optimization."
        ),
    )
    async def create_presentation(
        notes: list[str],
        brief: str,
        target_length: str,
        model_type: str = DEFAULT_MODEL_TYPE,
        template_preference: str = "auto",
        include_images: bool = False,
        language: str = "English",
        client_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create an enhanced PowerPoint presentation.

        Args:
            notes: List of content notes
            brief: Brief description of the presentation
            target_length: Target length specification (e.g., '10 slides', '800 words')
            model_type: LLM model to use for preprocessing
            template_preference: Template preference (auto, classic, general, modern, professional)
            include_images: Whether to include images
            language: Presentation language
            client_id: Client identifier for customization

        Returns:
            Dictionary with presentation metadata and file path
        """
        result = await create_enhanced_presentation(
            notes=notes,
            brief=brief,
            target_length=target_length,
            model_type=model_type,
            template_preference=template_preference,
            include_images=include_images,
            language=language,
            client_id=client_id,
        )

        return {
            "status": result.status,
            "presentation_id": result.presentation_id,
            "file_path": result.file_path,
            "draft_name": result.draft_name,
            "template_used": result.template_used,
            "slides_count": result.slides_count,
            "processing_time_ms": result.processing_time_ms,
            "token_usage": result.token_usage,
            "error": result.error,
            "client_id": result.client_id,
        }

    @mcp.tool(
        name="enhanced_ppt.analyze",
        description="Analyze content and suggest optimal PPT structure using LLM preprocessing.",
    )
    async def analyze_content(
        notes: list[str],
        brief: str,
        target_length: str,
        model_type: str = DEFAULT_MODEL_TYPE,
        client_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Analyze content and suggest PPT structure.

        Args:
            notes: List of content notes
            brief: Brief description of the presentation
            target_length: Target length specification
            model_type: LLM model to use for analysis
            client_id: Client identifier for customization

        Returns:
            Analysis results with suggested structure
        """
        try:
            request = PPTRequest(
                notes=notes, brief=brief, target_length=target_length, model_type=model_type, client_id=client_id
            )

            api_args, input_tokens, output_tokens = await _ppt_generator.preprocess_for_presenton(request)

            return {
                "status": "success",
                "suggested_structure": {
                    "prompt": api_args["prompt"],
                    "n_slides": api_args["n_slides"],
                    "template": api_args["template"],
                    "language": api_args["language"],
                },
                "token_usage": {"input": input_tokens, "output": output_tokens},
                "client_id": client_id,
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "client_id": client_id}

    @mcp.tool(
        name="enhanced_ppt.templates", description="Get available presentation templates and their characteristics."
    )
    async def get_templates() -> dict[str, Any]:
        """
        Get available presentation templates.

        Returns:
            Dictionary with template information
        """
        return {
            "status": "success",
            "templates": {
                "classic": {
                    "description": "Timeless, academic presentations",
                    "best_for": ["Research", "Academic", "Traditional business"],
                    "characteristics": ["Clean lines", "Professional fonts", "Subtle colors"],
                },
                "general": {
                    "description": "Versatile, business presentations",
                    "best_for": ["Business meetings", "General presentations", "Corporate"],
                    "characteristics": ["Balanced design", "Professional appearance", "Wide compatibility"],
                },
                "modern": {
                    "description": "Creative, startup presentations",
                    "best_for": ["Startups", "Creative projects", "Innovation"],
                    "characteristics": ["Bold colors", "Modern fonts", "Dynamic layouts"],
                },
                "professional": {
                    "description": "Corporate, pitch presentations",
                    "best_for": ["Executive presentations", "Investor pitches", "Corporate reports"],
                    "characteristics": ["Sophisticated design", "High-end appearance", "Executive appeal"],
                },
            },
        }
