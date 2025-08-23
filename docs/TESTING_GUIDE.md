# 🧪 Unified Content Creator System - Complete Testing Guide

## 📋 Overview

This guide covers comprehensive testing for the Unified Content Creator System, including unit tests, integration tests, performance tests, and end-to-end workflows.

## 🏗️ Testing Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Suite Structure                     │
├─────────────────────────────────────────────────────────────┤
│  🧪 Unit Tests          │  🔗 Integration Tests           │
│  • Individual tools     │  • Tool interactions            │
│  • MCP servers          │  • MCP server communication     │
│  • API endpoints        │  • End-to-end workflows         │
├─────────────────────────────────────────────────────────────┤
│  📊 Performance Tests   │  🎯 End-to-End Tests            │
│  • Load testing         │  • Complete user scenarios      │
│  • Stress testing       │  • Real-world use cases         │
│  • Benchmarking         │  • User acceptance testing      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start Testing

### Prerequisites

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx

# Install development dependencies
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run complete test suite
python scripts/test_complete_system.py

# Run with pytest
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/unit/ --cov=src --cov-report=term
pytest tests/integration/ --cov=src --cov-report=term
pytest tests/performance/ --cov=src --cov-report=term
```

## 🧪 Unit Testing

### Enhanced PPT Generator Tests

```python
# tests/unit/test_enhanced_ppt_generator.py
import pytest
from src.mcp_server_openai.tools.enhanced_ppt_generator import (
    EnhancedPPTGenerator, PPTRequest, PPTResponse
)

class TestEnhancedPPTGenerator:
    @pytest.fixture
    def generator(self):
        return EnhancedPPTGenerator()
    
    @pytest.fixture
    def sample_request(self):
        return PPTRequest(
            title="Test Presentation",
            brief="A test presentation for testing purposes",
            notes=["Note 1", "Note 2", "Note 3"],
            content_style="professional",
            language="en",
            slide_count=5
        )
    
    async def test_generate_ppt_basic(self, generator, sample_request):
        """Test basic PPT generation"""
        result = await generator.generate_ppt(sample_request)
        
        assert isinstance(result, PPTResponse)
        assert result.success is True
        assert result.file_path is not None
        assert result.slide_count == 5
        assert result.file_size > 0
    
    async def test_generate_ppt_with_custom_style(self, generator):
        """Test PPT generation with custom style"""
        request = PPTRequest(
            title="Creative Presentation",
            brief="A creative presentation",
            notes=["Creative note"],
            content_style="creative",
            language="en",
            slide_count=3
        )
        
        result = await generator.generate_ppt(request)
        assert result.success is True
        assert "creative" in result.file_path.lower()
    
    async def test_generate_ppt_error_handling(self, generator):
        """Test error handling for invalid requests"""
        request = PPTRequest(
            title="",
            brief="",
            notes=[],
            content_style="invalid",
            language="en",
            slide_count=0
        )
        
        result = await generator.generate_ppt(request)
        assert result.success is False
        assert "error" in result.message.lower()
```

### Enhanced Document Generator Tests

```python
# tests/unit/test_enhanced_document_generator.py
import pytest
from pathlib import Path
from src.mcp_server_openai.tools.enhanced_document_generator import (
    EnhancedDocumentGenerator, DocumentRequest, DocumentResult
)

class TestEnhancedDocumentGenerator:
    @pytest.fixture
    def generator(self):
        return EnhancedDocumentGenerator()
    
    @pytest.fixture
    def sample_request(self):
        return DocumentRequest(
            title="Test Document",
            content="# Test Document\n\nThis is a test document.",
            output_format="html",
            template="professional",
            language="en",
            custom_css=None
        )
    
    async def test_generate_html_document(self, generator, sample_request):
        """Test HTML document generation"""
        result = await generator.generate_document(sample_request)
        
        assert isinstance(result, DocumentResult)
        assert result.success is True
        assert result.file_path is not None
        assert result.file_path.suffix == ".html"
        
        # Verify HTML content
        html_content = Path(result.file_path).read_text()
        assert "<html" in html_content
        assert "Test Document" in html_content
        assert "professional" in html_content
    
    async def test_generate_pdf_document(self, generator):
        """Test PDF document generation"""
        request = DocumentRequest(
            title="PDF Test",
            content="# PDF Test\n\nThis is a PDF test.",
            output_format="pdf",
            template="modern",
            language="en"
        )
        
        result = await generator.generate_document(request)
        assert result.success is True
        assert result.file_path.suffix == ".pdf"
    
    async def test_generate_docx_document(self, generator):
        """Test DOCX document generation"""
        request = DocumentRequest(
            title="DOCX Test",
            content="# DOCX Test\n\nThis is a DOCX test.",
            output_format="docx",
            template="professional",
            language="en"
        )
        
        result = await generator.generate_document(request)
        assert result.success is True
        assert result.file_path.suffix == ".docx"
    
    async def test_fallback_generation(self, generator):
        """Test fallback generation when primary method fails"""
        request = DocumentRequest(
            title="Fallback Test",
            content="# Fallback Test\n\nThis tests fallback generation.",
            output_format="pdf",
            template="modern",
            language="en"
        )
        
        # Mock primary generator failure
        generator.pandoc_generator = None
        
        result = await generator.generate_document(request)
        assert result.success is True
        assert "fallback" in result.message.lower()
```

### Enhanced Image Generator Tests

```python
# tests/unit/test_enhanced_image_generator.py
import pytest
from src.mcp_server_openai.tools.enhanced_image_generator import (
    EnhancedImageGenerator, ImageRequest, ImageResult
)

class TestEnhancedImageGenerator:
    @pytest.fixture
    def generator(self):
        return EnhancedImageGenerator()
    
    @pytest.fixture
    def sample_request(self):
        return ImageRequest(
            query="professional business meeting",
            content_type="content",
            style="professional",
            count=1,
            format="jpeg",
            quality="high",
            size="medium",
            provider="unsplash"
        )
    
    async def test_generate_image_unsplash(self, generator, sample_request):
        """Test image generation with Unsplash"""
        result = await generator.generate_image(sample_request)
        
        assert isinstance(result, ImageResult)
        assert result.success is True
        assert len(result.images) == 1
        assert result.images[0].provider == "unsplash"
        assert result.images[0].file_path is not None
    
    async def test_generate_image_stable_diffusion(self, generator):
        """Test image generation with Stable Diffusion"""
        request = ImageRequest(
            query="futuristic cityscape",
            content_type="creative",
            style="artistic",
            count=1,
            format="png",
            quality="high",
            size="large",
            provider="stable_diffusion"
        )
        
        result = await generator.generate_image(request)
        assert result.success is True
        assert result.images[0].provider == "stable_diffusion"
    
    async def test_generate_multiple_images(self, generator):
        """Test generation of multiple images"""
        request = ImageRequest(
            query="nature landscape",
            content_type="content",
            style="natural",
            count=3,
            format="jpeg",
            quality="medium",
            size="small",
            provider="pixabay"
        )
        
        result = await generator.generate_image(request)
        assert result.success is True
        assert len(result.images) == 3
        assert all(img.provider == "pixabay" for img in result.images)
```

### Enhanced Icon Generator Tests

```python
# tests/unit/test_enhanced_icon_generator.py
import pytest
from src.mcp_server_openai.tools.enhanced_icon_generator import (
    EnhancedIconGenerator, IconRequest, IconResult
)

class TestEnhancedIconGenerator:
    @pytest.fixture
    def generator(self):
        return EnhancedIconGenerator()
    
    @pytest.fixture
    def sample_request(self):
        return IconRequest(
            query="business",
            style="professional",
            size="medium",
            format="svg",
            provider="lucide"
        )
    
    async def test_generate_icon_lucide(self, generator, sample_request):
        """Test icon generation with Lucide"""
        result = await generator.generate_icon(sample_request)
        
        assert isinstance(result, IconResult)
        assert result.success is True
        assert len(result.icons) == 1
        assert result.icons[0].provider == "lucide"
        assert result.icons[0].file_path.suffix == ".svg"
    
    async def test_generate_icon_iconify(self, generator):
        """Test icon generation with Iconify"""
        request = IconRequest(
            query="technology",
            style="modern",
            size="large",
            format="png",
            provider="iconify"
        )
        
        result = await generator.generate_icon(request)
        assert result.success is True
        assert result.icons[0].provider == "iconify"
    
    async def test_generate_icon_filtering(self, generator):
        """Test icon filtering and selection"""
        request = IconRequest(
            query="arrow",
            style="minimal",
            size="small",
            format="svg",
            provider="lucide"
        )
        
        result = await generator.generate_icon(request)
        assert result.success is True
        assert "arrow" in result.icons[0].file_path.name.lower()
```

## 🔗 Integration Testing

### MCP Server Integration Tests

```python
# tests/integration/test_mcp_integration.py
import pytest
import asyncio
from src.mcp_server_openai.tools.mcp_sequential_thinking import MCPSequentialThinkingClient
from src.mcp_server_openai.tools.mcp_brave_search import MCPBraveSearchClient
from src.mcp_server_openai.tools.mcp_memory import MCPMemoryClient

class TestMCPIntegration:
    @pytest.fixture
    async def mcp_clients(self):
        """Initialize MCP clients"""
        clients = {
            'sequential_thinking': MCPSequentialThinkingClient(),
            'brave_search': MCPBraveSearchClient(),
            'memory': MCPMemoryClient()
        }
        
        # Initialize connections
        for client in clients.values():
            await client.initialize()
        
        yield clients
        
        # Cleanup
        for client in clients.values():
            await client.close()
    
    async def test_sequential_thinking_workflow(self, mcp_clients):
        """Test complete sequential thinking workflow"""
        # Create content plan
        plan = await mcp_clients['sequential_thinking'].create_content_plan(
            title="AI in Healthcare",
            brief="Presentation about AI applications in healthcare",
            target_audience="Healthcare professionals",
            duration_minutes=30
        )
        
        assert plan.success is True
        assert len(plan.sections) > 0
        
        # Store plan in memory
        memory_result = await mcp_clients['memory'].store_content(
            content_id="plan_001",
            content_type="content_plan",
            content=plan.dict(),
            metadata={"title": "AI in Healthcare", "created_at": "2024-01-01"}
        )
        
        assert memory_result.success is True
        
        # Retrieve and verify plan
        retrieved_plan = await mcp_clients['memory'].retrieve_content("plan_001")
        assert retrieved_plan.success is True
        assert retrieved_plan.content["title"] == "AI in Healthcare"
    
    async def test_research_integration_workflow(self, mcp_clients):
        """Test research integration workflow"""
        # Search for relevant information
        search_results = await mcp_clients['brave_search'].search_web(
            query="AI healthcare applications 2024",
            max_results=5
        )
        
        assert search_results.success is True
        assert len(search_results.results) > 0
        
        # Store research results
        research_id = "research_001"
        memory_result = await mcp_clients['memory'].store_content(
            content_id=research_id,
            content_type="research",
            content=search_results.dict(),
            metadata={"query": "AI healthcare applications 2024", "date": "2024-01-01"}
        )
        
        assert memory_result.success is True
        
        # Use research for content enhancement
        enhanced_content = await mcp_clients['sequential_thinking'].enhance_content_with_research(
            content_plan_id="plan_001",
            research_id=research_id
        )
        
        assert enhanced_content.success is True
        assert len(enhanced_content.enhanced_sections) > 0
```

### Unified Content Creator Integration Tests

```python
# tests/integration/test_unified_content_creator.py
import pytest
from src.mcp_server_openai.tools.unified_content_creator import (
    UnifiedContentCreator, UnifiedContentRequest, UnifiedContentResult
)

class TestUnifiedContentCreator:
    @pytest.fixture
    async def creator(self):
        """Initialize unified content creator"""
        creator = UnifiedContentCreator()
        await creator.initialize()
        yield creator
        await creator.cleanup()
    
    @pytest.fixture
    def sample_request(self):
        return UnifiedContentRequest(
            title="AI in Modern Business",
            brief="Comprehensive overview of AI applications in business",
            notes=[
                "Machine learning applications",
                "Automation benefits",
                "Future trends"
            ],
            output_format="html",
            content_style="professional",
            language="en",
            include_images=True,
            include_icons=True,
            research_depth="comprehensive"
        )
    
    async def test_complete_content_creation_workflow(self, creator, sample_request):
        """Test complete content creation workflow"""
        result = await creator.create_unified_content(sample_request)
        
        assert isinstance(result, UnifiedContentResult)
        assert result.success is True
        assert result.content_type == "html"
        assert result.file_path is not None
        
        # Verify content components
        assert result.content_plan is not None
        assert result.research_results is not None
        assert result.generated_content is not None
        
        if sample_request.include_images:
            assert result.images is not None
            assert len(result.images) > 0
        
        if sample_request.include_icons:
            assert result.icons is not None
            assert len(result.icons) > 0
    
    async def test_cross_format_content_generation(self, creator):
        """Test content generation across different formats"""
        formats = ["html", "pdf", "docx", "pptx"]
        
        for format_type in formats:
            request = UnifiedContentRequest(
                title=f"Test {format_type.upper()}",
                brief=f"Test content in {format_type} format",
                notes=["Test note"],
                output_format=format_type,
                content_style="professional",
                language="en",
                include_images=False,
                include_icons=False
            )
            
            result = await creator.create_unified_content(request)
            assert result.success is True
            assert result.content_type == format_type
            assert result.file_path.suffix == f".{format_type}"
    
    async def test_content_validation_integration(self, creator, sample_request):
        """Test content validation integration"""
        # Enable validation
        sample_request.validate_content = True
        
        result = await creator.create_unified_content(sample_request)
        assert result.success is True
        assert result.validation_results is not None
        
        # Check validation scores
        validation = result.validation_results
        assert validation.content_quality_score >= 0.7
        assert validation.readability_score >= 0.7
        assert validation.seo_score >= 0.7
```

## 📊 Performance Testing

### Load Testing

```python
# tests/performance/test_load_performance.py
import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from src.mcp_server_openai.tools.unified_content_creator import UnifiedContentCreator

class TestLoadPerformance:
    @pytest.fixture
    async def creator(self):
        creator = UnifiedContentCreator()
        await creator.initialize()
        yield creator
        await creator.cleanup()
    
    async def test_concurrent_content_generation(self, creator):
        """Test concurrent content generation performance"""
        request = UnifiedContentRequest(
            title="Performance Test",
            brief="Testing concurrent generation performance",
            notes=["Test note 1", "Test note 2"],
            output_format="html",
            content_style="professional",
            language="en",
            include_images=False,
            include_icons=False
        )
        
        # Test with different concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        results = {}
        
        for concurrency in concurrency_levels:
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = [creator.create_unified_content(request) for _ in range(concurrency)]
            results_list = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calculate metrics
            success_count = sum(1 for r in results_list if r.success)
            avg_time = total_time / concurrency
            
            results[concurrency] = {
                'total_time': total_time,
                'avg_time': avg_time,
                'success_rate': success_count / concurrency,
                'throughput': concurrency / total_time
            }
            
            print(f"Concurrency {concurrency}: {results[concurrency]}")
        
        # Performance assertions
        assert results[1]['success_rate'] == 1.0, "Single request should always succeed"
        assert results[5]['success_rate'] >= 0.8, "5 concurrent requests should have 80%+ success rate"
        assert results[10]['success_rate'] >= 0.7, "10 concurrent requests should have 70%+ success rate"
    
    async def test_memory_usage_under_load(self, creator):
        """Test memory usage under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate multiple content pieces
        request = UnifiedContentRequest(
            title="Memory Test",
            brief="Testing memory usage",
            notes=["Memory test note"],
            output_format="html",
            content_style="professional",
            language="en"
        )
        
        for i in range(10):
            await creator.create_unified_content(request)
            
            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory
            
            print(f"Request {i+1}: Memory increase: {memory_increase:.2f} MB")
            
            # Memory should not increase excessively
            assert memory_increase < 100, f"Memory increase {memory_increase} MB exceeds 100 MB limit"
    
    async def test_response_time_distribution(self, creator):
        """Test response time distribution"""
        request = UnifiedContentRequest(
            title="Response Time Test",
            brief="Testing response time distribution",
            notes=["Response time test note"],
            output_format="html",
            content_style="professional",
            language="en"
        )
        
        # Collect response times
        response_times = []
        for _ in range(20):
            start_time = time.time()
            result = await creator.create_unified_content(request)
            end_time = time.time()
            
            if result.success:
                response_times.append(end_time - start_time)
        
        # Calculate statistics
        mean_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        std_dev = statistics.stdev(response_times)
        
        print(f"Response Time Statistics:")
        print(f"  Mean: {mean_time:.2f}s")
        print(f"  Median: {median_time:.2f}s")
        print(f"  Std Dev: {std_dev:.2f}s")
        print(f"  Min: {min(response_times):.2f}s")
        print(f"  Max: {max(response_times):.2f}s")
        
        # Performance assertions
        assert mean_time < 30, f"Mean response time {mean_time}s exceeds 30s limit"
        assert max(response_times) < 60, f"Max response time {max(response_times)}s exceeds 60s limit"
        assert std_dev < mean_time * 0.5, f"Response time variance too high"
```

### Stress Testing

```python
# tests/performance/test_stress_performance.py
import pytest
import asyncio
import time
from src.mcp_server_openai.tools.unified_content_creator import UnifiedContentCreator

class TestStressPerformance:
    @pytest.fixture
    async def creator(self):
        creator = UnifiedContentCreator()
        await creator.initialize()
        yield creator
        await creator.cleanup()
    
    async def test_extended_usage_stability(self, creator):
        """Test system stability under extended usage"""
        request = UnifiedContentRequest(
            title="Stability Test",
            brief="Testing system stability",
            notes=["Stability test note"],
            output_format="html",
            content_style="professional",
            language="en"
        )
        
        # Run for extended period
        start_time = time.time()
        success_count = 0
        total_count = 0
        
        while time.time() - start_time < 300:  # 5 minutes
            try:
                result = await creator.create_unified_content(request)
                total_count += 1
                
                if result.success:
                    success_count += 1
                
                # Small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error during stress test: {e}")
                continue
        
        # Calculate success rate
        success_rate = success_count / total_count if total_count > 0 else 0
        
        print(f"Stress Test Results:")
        print(f"  Total requests: {total_count}")
        print(f"  Successful requests: {success_count}")
        print(f"  Success rate: {success_rate:.2%}")
        
        # Stability assertions
        assert success_rate >= 0.8, f"Success rate {success_rate:.2%} below 80% threshold"
        assert total_count >= 50, f"Total requests {total_count} below 50 minimum"
    
    async def test_error_recovery(self, creator):
        """Test system recovery after errors"""
        # Create invalid request to trigger error
        invalid_request = UnifiedContentRequest(
            title="",
            brief="",
            notes=[],
            output_format="invalid",
            content_style="invalid",
            language="invalid"
        )
        
        # Trigger error
        error_result = await creator.create_unified_content(invalid_request)
        assert error_result.success is False
        
        # Verify system can recover and handle valid requests
        valid_request = UnifiedContentRequest(
            title="Recovery Test",
            brief="Testing system recovery",
            notes=["Recovery test note"],
            output_format="html",
            content_style="professional",
            language="en"
        )
        
        recovery_result = await creator.create_unified_content(valid_request)
        assert recovery_result.success is True, "System should recover from errors"
```

## 🎯 End-to-End Testing

### Complete User Scenarios

```python
# tests/e2e/test_user_scenarios.py
import pytest
from pathlib import Path
from src.mcp_server_openai.tools.unified_content_creator import UnifiedContentCreator

class TestUserScenarios:
    @pytest.fixture
    async def creator(self):
        creator = UnifiedContentCreator()
        await creator.initialize()
        yield creator
        await creator.cleanup()
    
    async def test_business_presentation_workflow(self, creator):
        """Test complete business presentation workflow"""
        # Step 1: Create comprehensive business presentation
        business_request = UnifiedContentRequest(
            title="Digital Transformation Strategy",
            brief="Comprehensive strategy for digital transformation in enterprise",
            notes=[
                "Current state assessment",
                "Technology roadmap",
                "Implementation timeline",
                "Success metrics",
                "Risk mitigation"
            ],
            output_format="pptx",
            content_style="executive",
            language="en",
            include_images=True,
            include_icons=True,
            research_depth="comprehensive",
            validate_content=True
        )
        
        business_result = await creator.create_unified_content(business_request)
        assert business_result.success is True
        assert business_result.content_type == "pptx"
        
        # Step 2: Generate supporting documentation
        doc_request = UnifiedContentRequest(
            title="Digital Transformation Strategy - Detailed Report",
            brief="Detailed report supporting the presentation",
            notes=business_request.notes,
            output_format="pdf",
            content_style="executive",
            language="en",
            include_images=True,
            include_icons=True,
            research_depth="comprehensive"
        )
        
        doc_result = await creator.create_unified_content(doc_request)
        assert doc_result.success is True
        assert doc_result.content_type == "pdf"
        
        # Step 3: Generate web version
        web_request = UnifiedContentRequest(
            title="Digital Transformation Strategy - Web Version",
            brief="Web-optimized version of the strategy",
            notes=business_request.notes,
            output_format="html",
            content_style="modern",
            language="en",
            include_images=True,
            include_icons=True,
            research_depth="comprehensive"
        )
        
        web_result = await creator.create_unified_content(web_request)
        assert web_result.success is True
        assert web_result.content_type == "html"
        
        # Verify all outputs exist and are accessible
        outputs = [business_result, doc_result, web_result]
        for output in outputs:
            assert Path(output.file_path).exists()
            assert Path(output.file_path).stat().st_size > 0
        
        print(f"Business presentation workflow completed successfully:")
        print(f"  Presentation: {business_result.file_path}")
        print(f"  Report: {doc_result.file_path}")
        print(f"  Web version: {web_result.file_path}")
    
    async def test_educational_content_workflow(self, creator):
        """Test complete educational content workflow"""
        # Step 1: Create educational presentation
        edu_request = UnifiedContentRequest(
            title="Introduction to Machine Learning",
            brief="Comprehensive introduction to machine learning concepts",
            notes=[
                "What is Machine Learning",
                "Types of Machine Learning",
                "Real-world Applications",
                "Getting Started",
                "Resources and Tools"
            ],
            output_format="pptx",
            content_style="educational",
            language="en",
            include_images=True,
            include_icons=True,
            research_depth="comprehensive"
        )
        
        edu_result = await creator.create_unified_content(edu_request)
        assert edu_result.success is True
        
        # Step 2: Generate study guide
        guide_request = UnifiedContentRequest(
            title="Machine Learning Study Guide",
            brief="Comprehensive study guide for machine learning",
            notes=edu_request.notes,
            output_format="docx",
            content_style="educational",
            language="en",
            include_images=True,
            include_icons=True
        )
        
        guide_result = await creator.create_unified_content(guide_request)
        assert guide_result.success is True
        
        # Step 3: Generate interactive HTML version
        interactive_request = UnifiedContentRequest(
            title="Interactive Machine Learning Guide",
            brief="Interactive web-based learning guide",
            notes=edu_request.notes,
            output_format="html",
            content_style="interactive",
            language="en",
            include_images=True,
            include_icons=True
        )
        
        interactive_result = await creator.create_unified_content(interactive_request)
        assert interactive_result.success is True
        
        print(f"Educational content workflow completed successfully:")
        print(f"  Presentation: {edu_result.file_path}")
        print(f"  Study Guide: {guide_result.file_path}")
        print(f"  Interactive Guide: {interactive_result.file_path}")
    
    async def test_marketing_campaign_workflow(self, creator):
        """Test complete marketing campaign workflow"""
        # Step 1: Create campaign presentation
        campaign_request = UnifiedContentRequest(
            title="Q4 Product Launch Campaign",
            brief="Comprehensive marketing campaign for new product launch",
            notes=[
                "Campaign Overview",
                "Target Audience",
                "Marketing Channels",
                "Content Strategy",
                "Timeline and Milestones",
                "Success Metrics"
            ],
            output_format="pptx",
            content_style="marketing",
            language="en",
            include_images=True,
            include_icons=True,
            research_depth="comprehensive"
        )
        
        campaign_result = await creator.create_unified_content(campaign_request)
        assert campaign_result.success is True
        
        # Step 2: Generate marketing materials
        materials_request = UnifiedContentRequest(
            title="Marketing Materials Package",
            brief="Complete package of marketing materials",
            notes=campaign_request.notes,
            output_format="pdf",
            content_style="marketing",
            language="en",
            include_images=True,
            include_icons=True
        )
        
        materials_result = await creator.create_unified_content(materials_request)
        assert materials_result.success is True
        
        # Step 3: Generate landing page
        landing_request = UnifiedContentRequest(
            title="Product Launch Landing Page",
            brief="High-converting landing page for product launch",
            notes=campaign_request.notes,
            output_format="html",
            content_style="conversion",
            language="en",
            include_images=True,
            include_icons=True
        )
        
        landing_result = await creator.create_unified_content(landing_request)
        assert landing_result.success is True
        
        print(f"Marketing campaign workflow completed successfully:")
        print(f"  Campaign Presentation: {campaign_result.file_path}")
        print(f"  Marketing Materials: {materials_result.file_path}")
        print(f"  Landing Page: {landing_result.file_path}")
```

## 🔧 Test Configuration

### Pytest Configuration

```ini
# pytest.ini
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    e2e: End-to-end tests
    slow: Slow running tests
    mcp: MCP server tests
```

### Test Environment Setup

```python
# tests/conftest.py
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture(autouse=True)
def setup_test_environment(temp_dir, monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("OUTPUT_DIR", str(temp_dir))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # Mock API keys for testing
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
```

## 📊 Test Reporting

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Generate XML coverage report for CI/CD
pytest tests/ --cov=src --cov-report=xml

# Generate coverage report with specific thresholds
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=85
```

### Performance Reports

```bash
# Run performance tests with timing
pytest tests/performance/ -v --durations=10

# Generate performance profile
python -m cProfile -o profile.prof scripts/test_complete_system.py

# Analyze profile
python -c "import pstats; p = pstats.Stats('profile.prof'); p.sort_stats('cumulative').print_stats(20)"
```

### Test Results Summary

```bash
# Run tests and generate summary
python scripts/test_complete_system.py --summary

# Run specific test categories
python scripts/test_complete_system.py --category=unit
python scripts/test_complete_system.py --category=integration
python scripts/test_complete_system.py --category=performance
python scripts/test_complete_system.py --category=e2e
```

## 🚀 Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=src --cov-report=xml --cov-fail-under=80
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ --cov=src --cov-report=xml
    
    - name: Run performance tests
      run: |
        pytest tests/performance/ -v --durations=10
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

## 📚 Additional Resources

- **Test Data**: `tests/data/` - Sample content and test files
- **Test Utilities**: `tests/utils/` - Helper functions and mocks
- **Performance Benchmarks**: `tests/benchmarks/` - Performance baseline tests
- **Test Documentation**: `docs/testing/` - Detailed testing documentation

---

**Happy Testing! 🧪**
