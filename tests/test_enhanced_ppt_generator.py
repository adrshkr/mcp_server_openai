"""
Tests for enhanced PPT generator tool with Presenton API integration.

This test suite covers the enhanced PPT generator functionality including
LLM preprocessing, Presenton API integration, and error handling.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server_openai.tools.generators.enhanced_ppt_generator import (
    EnhancedPPTGenerator,
    LLMClient,
    PPTRequest,
    PPTResponse,
    PresentonAPIClient,
    create_enhanced_presentation,
)


class TestPPTRequest:
    """Test PPTRequest dataclass."""

    def test_ppt_request_creation(self):
        """Test creating a PPTRequest instance."""
        request = PPTRequest(
            notes=["Note 1", "Note 2"],
            brief="Test presentation",
            target_length="10 slides",
            model_type="gpt-4o",
            template_preference="professional",
            include_images=False,
            language="English",
            client_id="test_client",
        )

        assert request.notes == ["Note 1", "Note 2"]
        assert request.brief == "Test presentation"
        assert request.target_length == "10 slides"
        assert request.model_type == "gpt-4o"
        assert request.template_preference == "professional"
        assert request.include_images is False
        assert request.language == "English"
        assert request.client_id == "test_client"

    def test_ppt_request_defaults(self):
        """Test PPTRequest with default values."""
        request = PPTRequest(notes=["Note 1"], brief="Simple presentation", target_length="5 slides")

        assert request.model_type == "gpt-4o"
        assert request.template_preference == "auto"
        assert request.include_images is False
        assert request.language == "English"
        assert request.client_id is None


class TestPPTResponse:
    """Test PPTResponse dataclass."""

    def test_ppt_response_creation(self):
        """Test creating a PPTResponse instance."""
        response = PPTResponse(
            status="success",
            presentation_id="ppt_123",
            file_path="/path/to/presentation.pptx",
            draft_name="Test Presentation",
            template_used="professional",
            slides_count=10,
            processing_time_ms=1500.0,
            token_usage={"input": 100, "output": 200},
            client_id="test_client",
        )

        assert response.status == "success"
        assert response.presentation_id == "ppt_123"
        assert response.file_path == "/path/to/presentation.pptx"
        assert response.draft_name == "Test Presentation"
        assert response.template_used == "professional"
        assert response.slides_count == 10
        assert response.processing_time_ms == 1500.0
        assert response.token_usage == {"input": 100, "output": 200}
        assert response.client_id == "test_client"

    def test_ppt_response_error(self):
        """Test PPTResponse with error."""
        response = PPTResponse(
            status="error", error="Something went wrong", processing_time_ms=500.0, client_id="test_client"
        )

        assert response.status == "error"
        assert response.error == "Something went wrong"
        assert response.processing_time_ms == 500.0
        assert response.client_id == "test_client"


class TestLLMClient:
    """Test LLMClient class."""

    @pytest.fixture
    def llm_client(self):
        """Create LLMClient instance for testing."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-openai-key",
                "ANTHROPIC_API_KEY": "test-anthropic-key",
                "GOOGLE_API_KEY": "test-google-key",
            },
        ):
            return LLMClient()

    def test_llm_client_initialization(self, llm_client):
        """Test LLMClient initialization."""
        assert llm_client.openai_api_key == "test-openai-key"
        assert llm_client.anthropic_api_key == "test-anthropic-key"
        assert llm_client.google_api_key == "test-google-key"

    @pytest.mark.asyncio
    async def test_call_openai_success(self, llm_client):
        """Test successful OpenAI API call."""
        with patch("langchain_openai.ChatOpenAI") as mock_openai:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_response.usage_metadata = {"input_tokens": 50, "output_tokens": 25}
            mock_llm.invoke.return_value = mock_response
            mock_openai.return_value = mock_llm

            messages = [{"role": "user", "content": "Hello"}]
            result = await llm_client._call_openai("gpt-4o", messages, 0.2, 1000)

            assert len(result) == 4
            assert result[1] == "Test response"
            assert result[2] == 50  # input_tokens
            assert result[3] == 25  # output_tokens

    @pytest.mark.asyncio
    async def test_call_openai_with_schema(self, llm_client):
        """Test OpenAI API call with JSON schema."""
        with patch("langchain_openai.ChatOpenAI") as mock_openai:
            mock_llm = MagicMock()
            mock_llm.with_structured_output.return_value = mock_llm
            mock_raw_response = MagicMock()
            mock_raw_response.usage_metadata = {"input_tokens": 50, "output_tokens": 25}
            mock_llm.invoke.return_value = {"raw": mock_raw_response, "parsed": {"prompt": "Test", "n_slides": 5}}
            mock_openai.return_value = mock_llm

            messages = [{"role": "user", "content": "Hello"}]
            schema = {"type": "object"}
            result = await llm_client._call_openai("gpt-4o", messages, 0.2, 1000, schema)

            assert len(result) == 4
            assert result[1] == {"prompt": "Test", "n_slides": 5}
            assert result[2] == 50  # input_tokens
            assert result[3] == 25  # output_tokens

    @pytest.mark.asyncio
    async def test_call_anthropic_success(self, llm_client):
        """Test successful Anthropic API call."""
        with patch("langchain_anthropic.ChatAnthropic") as mock_anthropic:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_response.usage_metadata = {"input_tokens": 50, "output_tokens": 25}
            mock_llm.invoke.return_value = mock_response
            mock_anthropic.return_value = mock_llm

            messages = [{"role": "user", "content": "Hello"}]
            result = await llm_client._call_anthropic("claude-3-5-sonnet", messages, 0.2, 1000)

            assert len(result) == 4
            assert result[1] == "Test response"
            assert result[2] == 50  # input_tokens
            assert result[3] == 25  # output_tokens

    @pytest.mark.asyncio
    async def test_call_google_success(self, llm_client):
        """Test successful Google API call."""
        with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_google:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_response.usage_metadata = {"input_tokens": 50, "output_tokens": 25}
            mock_llm.invoke.return_value = mock_response
            mock_google.return_value = mock_llm

            messages = [{"role": "user", "content": "Hello"}]
            result = await llm_client._call_google("gemini-1.5-pro", messages, 0.2, 1000)

            assert len(result) == 4
            assert result[1] == "Test response"
            assert result[2] == 50  # input_tokens
            assert result[3] == 25  # output_tokens

    @pytest.mark.asyncio
    async def test_call_unknown_model(self, llm_client):
        """Test calling unknown model type."""
        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(ValueError, match="Unsupported model type: unknown"):
            await llm_client.chat_with_model("unknown", messages)


class TestPresentonAPIClient:
    """Test PresentonAPIClient class."""

    @pytest.fixture
    def api_client(self):
        """Create PresentonAPIClient instance for testing."""
        return PresentonAPIClient("https://test-api.com")

    def test_api_client_initialization(self, api_client):
        """Test PresentonAPIClient initialization."""
        assert api_client.base_url == "https://test-api.com"
        assert api_client.generate_endpoint == "https://test-api.com/api/v1/ppt/presentation/generate"

    def test_api_client_default_url(self):
        """Test PresentonAPIClient with default URL."""
        with patch.dict(os.environ, {"PRESENTON_API_URL": "https://default-api.com"}):
            client = PresentonAPIClient()
            assert client.base_url == "https://default-api.com"

    @pytest.mark.asyncio
    async def test_generate_presentation_success(self, api_client):
        """Test successful presentation generation."""
        with patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"presentation_id": "ppt_123", "path": "/path/to/ppt"}
            mock_post.return_value = mock_response

            payload = {"prompt": "Test", "n_slides": 5}
            result = await api_client.generate_presentation(payload)

            assert result["presentation_id"] == "ppt_123"
            assert result["path"] == "/path/to/ppt"

    @pytest.mark.asyncio
    async def test_generate_presentation_error(self, api_client):
        """Test presentation generation with error."""
        with patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.requests.post") as mock_post:
            from requests.exceptions import RequestException

            mock_post.side_effect = RequestException("API Error")

            payload = {"prompt": "Test", "n_slides": 5}

            with pytest.raises(Exception, match="Error calling Presenton API: API Error"):
                await api_client.generate_presentation(payload)

    @pytest.mark.asyncio
    async def test_download_presentation_success(self, api_client):
        """Test successful presentation download."""
        with patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b"test content"]
            mock_get.return_value = mock_response

            with patch("pathlib.Path.mkdir"), patch("builtins.open", create=True):
                result = await api_client.download_presentation("/path/to/ppt", "test_presentation")

                assert "test_presentation.pptx" in result
                # Use Path to handle cross-platform path separators
                assert "output" in result and "presentations" in result


class TestEnhancedPPTGenerator:
    """Test EnhancedPPTGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create EnhancedPPTGenerator instance for testing."""
        return EnhancedPPTGenerator()

    def test_generator_initialization(self, generator):
        """Test EnhancedPPTGenerator initialization."""
        assert generator.llm_client is not None
        assert generator.presenton_client is not None

    def test_parse_max_slides_specific_count(self, generator):
        """Test parsing specific slide count."""
        result = generator._parse_max_slides("10 slides")
        assert result == 10

    def test_parse_max_slides_word_count(self, generator):
        """Test parsing word count."""
        result = generator._parse_max_slides("500 words")
        assert result == 10  # 500 // 50

    def test_parse_max_slides_character_count(self, generator):
        """Test parsing character count."""
        result = generator._parse_max_slides("1000 characters")
        assert result == 5  # 1000 // 200

    def test_parse_max_slides_invalid(self, generator):
        """Test parsing invalid length specification."""
        result = generator._parse_max_slides("invalid")
        assert result is None

    def test_parse_max_slides_none(self, generator):
        """Test parsing None length specification."""
        result = generator._parse_max_slides(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_preprocess_for_presenton(self, generator):
        """Test content preprocessing."""
        with patch.object(generator.llm_client, "chat_with_model") as mock_chat:
            mock_chat.return_value = (
                [],  # messages
                {
                    "prompt": "Test prompt",
                    "n_slides": 8,
                    "template": "professional",
                    "language": "English",
                    "export_as": "pptx",
                    "draft_name": "Test Presentation",
                },
                100,  # input_tokens
                50,  # output_tokens
            )

            request = PPTRequest(notes=["Note 1", "Note 2"], brief="Test brief", target_length="8 slides")

            result = await generator.preprocess_for_presenton(request)

            assert len(result) == 3
            api_args, input_tokens, output_tokens = result
            assert api_args["prompt"] == "Test prompt"
            assert api_args["n_slides"] == 8
            assert api_args["template"] == "professional"
            assert input_tokens == 100
            assert output_tokens == 50

    @pytest.mark.asyncio
    async def test_generate_presentation_success(self, generator):
        """Test successful presentation generation."""
        with (
            patch.object(generator, "preprocess_for_presenton") as mock_preprocess,
            patch.object(generator.presenton_client, "generate_presentation") as mock_generate,
            patch.object(generator.presenton_client, "download_presentation") as mock_download,
        ):
            mock_preprocess.return_value = (
                {
                    "prompt": "Test",
                    "n_slides": 8,
                    "template": "professional",
                    "language": "English",
                    "export_as": "pptx",
                    "draft_name": "Test",
                },
                100,
                50,
            )
            mock_generate.return_value = {"presentation_id": "ppt_123", "path": "/path/to/ppt"}
            mock_download.return_value = "/local/path/test.pptx"

            request = PPTRequest(notes=["Note 1"], brief="Test brief", target_length="8 slides")

            result = await generator.generate_presentation(request)

            assert result.status == "success"
            assert result.presentation_id == "ppt_123"
            assert result.file_path == "/local/path/test.pptx"
            assert result.slides_count == 8
            assert result.template_used == "professional"

    @pytest.mark.asyncio
    async def test_generate_presentation_error(self, generator):
        """Test presentation generation with error."""
        with patch.object(generator, "preprocess_for_presenton") as mock_preprocess:
            mock_preprocess.side_effect = Exception("Preprocessing failed")

            request = PPTRequest(notes=["Note 1"], brief="Test brief", target_length="8 slides")

            result = await generator.generate_presentation(request)

            assert result.status == "error"
            assert "Preprocessing failed" in result.error


class TestCreateEnhancedPresentation:
    """Test create_enhanced_presentation function."""

    @pytest.mark.asyncio
    @patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.EnhancedPPTGenerator")
    async def test_create_enhanced_presentation_success(self, mock_generator_class):
        """Test successful presentation creation."""
        mock_generator = AsyncMock()
        mock_generator.generate_presentation.return_value = PPTResponse(
            status="success",
            presentation_id="ppt_123",
            file_path="/path/to/presentation.pptx",
            draft_name="Test Presentation",
            template_used="professional",
            slides_count=8,
            processing_time_ms=1500.0,
            token_usage={"input": 100, "output": 50},
            client_id="test_client",
        )
        mock_generator_class.return_value = mock_generator

        result = await create_enhanced_presentation(
            notes=["Note 1", "Note 2"],
            brief="Test brief",
            target_length="8 slides",
            model_type="gpt-4o",
            template_preference="professional",
            include_images=False,
            language="English",
            client_id="test_client",
            generator=mock_generator,
        )

        assert result.status == "success"
        assert result.presentation_id == "ppt_123"
        assert result.file_path == "/path/to/presentation.pptx"
        assert result.slides_count == 8
        assert result.template_used == "professional"
        assert result.client_id == "test_client"

    @pytest.mark.asyncio
    @patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.EnhancedPPTGenerator")
    async def test_create_enhanced_presentation_error(self, mock_generator_class):
        """Test presentation creation with error."""
        mock_generator = AsyncMock()
        mock_generator.generate_presentation.return_value = PPTResponse(
            status="error", error="Generation failed", processing_time_ms=500.0, client_id="test_client"
        )
        mock_generator_class.return_value = mock_generator

        result = await create_enhanced_presentation(
            notes=["Note 1"],
            brief="Test brief",
            target_length="5 slides",
            client_id="test_client",
            generator=mock_generator,
        )

        assert result.status == "error"
        assert "Generation failed" in result.error
        assert result.client_id == "test_client"


class TestIntegration:
    """Integration tests for the enhanced PPT generator."""

    @pytest.mark.asyncio
    async def test_full_workflow_mock(self):
        """Test the complete workflow with mocked dependencies."""
        # Create test request
        request = PPTRequest(
            notes=["Topic: AI Strategy", "Market analysis", "Implementation plan"],
            brief="Create a presentation about AI strategy implementation",
            target_length="8 slides",
            model_type="gpt-4o",
            template_preference="professional",
            client_id="integration_test",
        )

        # Mock the entire workflow
        with (
            patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.LLMClient") as mock_llm_class,
            patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.PresentonAPIClient") as mock_api_class,
            patch("mcp_server_openai.tools.generators.enhanced_ppt_generator.create_progress_tracker"),
        ):
            # Mock LLM client
            mock_llm = AsyncMock()
            mock_llm.chat_with_model.return_value = (
                [],  # messages
                {
                    "prompt": "AI Strategy Implementation",
                    "n_slides": 8,
                    "template": "professional",
                    "language": "English",
                    "export_as": "pptx",
                    "draft_name": "AI Strategy",
                },
                150,  # input_tokens
                75,  # output_tokens
            )
            mock_llm_class.return_value = mock_llm

            # Mock API client
            mock_api = AsyncMock()
            mock_api.generate_presentation.return_value = {"presentation_id": "ppt_int_123", "path": "/api/path/to/ppt"}
            mock_api.download_presentation.return_value = "/local/path/ai_strategy.pptx"
            mock_api_class.return_value = mock_api

            # Create generator and run workflow
            generator = EnhancedPPTGenerator()
            result = await generator.generate_presentation(request)

            # Verify results
            assert result.status == "success"
            assert result.presentation_id == "ppt_int_123"
            assert result.file_path == "/local/path/ai_strategy.pptx"
            assert result.slides_count == 8
            assert result.template_used == "professional"
            assert result.client_id == "integration_test"
            assert result.token_usage["input"] == 150
            assert result.token_usage["output"] == 75
