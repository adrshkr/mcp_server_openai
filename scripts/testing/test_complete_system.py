#!/usr/bin/env python3
"""
🚀 Complete Unified Content Creator System - Test Suite
This script tests all the latest tools and functionalities including:
- Enhanced PPT Generator
- Enhanced Document Generator (HTML, DOC, PDF)
- Enhanced Image Generator
- Enhanced Icon Generator
- MCP Servers (Sequential Thinking, Brave Search, Memory, Filesystem)
- Research Integration
- Content Validation
- Advanced Orchestration
- Unified Content Creator
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class CompleteSystemTester:
    """Comprehensive test suite for the Unified Content Creator System."""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    async def run_all_tests(self) -> bool:
        """Run all tests and return overall success status."""
        logger.info("🚀 Starting Complete Unified Content Creator System Tests")
        logger.info("=" * 60)

        # Test 1: Enhanced PPT Generator
        await self.test_enhanced_ppt_generator()

        # Test 2: Enhanced Document Generator
        await self.test_enhanced_document_generator()

        # Test 3: Enhanced Image Generator
        await self.test_enhanced_image_generator()

        # Test 4: Enhanced Icon Generator
        await self.test_enhanced_icon_generator()

        # Test 5: MCP Sequential Thinking
        await self.test_mcp_sequential_thinking()

        # Test 6: MCP Brave Search
        await self.test_mcp_brave_search()

        # Test 7: MCP Memory
        await self.test_mcp_memory()

        # Test 8: MCP Filesystem
        await self.test_mcp_filesystem()

        # Test 9: MCP Research Integration
        await self.test_mcp_research_integration()

        # Test 10: MCP Content Validation
        await self.test_mcp_content_validation()

        # Test 11: MCP Advanced Orchestration
        await self.test_mcp_advanced_orchestration()

        # Test 12: Unified Content Creator
        await self.test_unified_content_creator()

        # Test 13: Integration Tests
        await self.test_integration_workflows()

        # Test 14: Performance Tests
        await self.test_performance()

        # Test 15: Error Handling Tests
        await self.test_error_handling()

        return self.print_test_summary()

    async def test_enhanced_ppt_generator(self) -> None:
        """Test the Enhanced PPT Generator."""
        logger.info("📊 Testing Enhanced PPT Generator...")

        try:
            from mcp_server_openai.tools.enhanced_ppt_generator import create_enhanced_presentation

            # Test basic presentation creation
            result = await create_enhanced_presentation(
                notes=["Introduction to AI", "Machine Learning Basics", "Deep Learning Applications"],
                brief="A comprehensive overview of artificial intelligence",
                target_length="3 slides",
                template_preference="professional",
                include_images=True,
                language="English",
                client_id="test_client_001",
            )

            if result and hasattr(result, "file_path") and result.file_path:
                self.record_test("Enhanced PPT Generator - Basic Creation", True, f"Created: {result.file_path}")
            else:
                self.record_test("Enhanced PPT Generator - Basic Creation", False, "Failed to create presentation")

        except Exception as e:
            self.record_test("Enhanced PPT Generator", False, f"Error: {str(e)}")

    async def test_enhanced_document_generator(self) -> None:
        """Test the Enhanced Document Generator."""
        logger.info("📄 Testing Enhanced Document Generator...")

        try:
            from mcp_server_openai.tools.enhanced_document_generator import generate_document

            # Test HTML generation
            html_result = await generate_document(
                title="Test HTML Document",
                content="# Test Title\n\nThis is a test document with **bold** text.\n\n## Section 1\nContent for section 1.",
                output_format="html",
                template="professional",
            )

            if html_result.status == "success":
                self.record_test("Enhanced Document Generator - HTML", True, f"Generated: {html_result.file_path}")
            else:
                self.record_test("Enhanced Document Generator - HTML", False, f"Failed: {html_result.error_message}")

            # Test document generation
            doc_result = await generate_document(
                title="Test Document",
                content="# Test Title\n\nThis is a test document.\n\n## Section 1\nContent for section 1.",
                output_format="docx",
                template="professional",
            )

            if doc_result.status == "success":
                self.record_test("Enhanced Document Generator - DOCX", True, f"Generated: {doc_result.file_path}")
            else:
                self.record_test("Enhanced Document Generator - DOCX", False, f"Failed: {doc_result.error_message}")

        except Exception as e:
            self.record_test("Enhanced Document Generator", False, f"Error: {str(e)}")

    async def test_enhanced_image_generator(self) -> None:
        """Test the Enhanced Image Generator."""
        logger.info("🖼️ Testing Enhanced Image Generator...")

        try:
            from mcp_server_openai.tools.enhanced_image_generator import generate_image

            # Test image generation
            result = await generate_image(
                query="modern technology",
                content_type="presentation",
                style="professional",
                count=1,
                format="jpeg",
                quality="high",
                size="medium",
            )

            if result and hasattr(result, "url") and result.url:
                self.record_test("Enhanced Image Generator", True, f"Generated: {result.url}")
            else:
                self.record_test("Enhanced Image Generator", False, "Failed to generate image")

        except Exception as e:
            self.record_test("Enhanced Image Generator", False, f"Error: {str(e)}")

    async def test_enhanced_icon_generator(self) -> None:
        """Test the Enhanced Icon Generator."""
        logger.info("🎨 Testing Enhanced Icon Generator...")

        try:
            from mcp_server_openai.tools.enhanced_icon_generator import generate_icon

            # Test icon generation
            result = await generate_icon(query="technology", style="outline", size="medium", provider="lucide")

            if result and hasattr(result, "url") and result.url:
                self.record_test("Enhanced Icon Generator", True, f"Generated: {result.url}")
            else:
                self.record_test("Enhanced Icon Generator", False, "Failed to generate icon")

        except Exception as e:
            self.record_test("Enhanced Icon Generator", False, f"Error: {str(e)}")

    async def test_mcp_sequential_thinking(self) -> None:
        """Test the MCP Sequential Thinking Server."""
        logger.info("🧠 Testing MCP Sequential Thinking Server...")

        try:
            from mcp_server_openai.tools.mcp_sequential_thinking import SequentialThinkingEngine

            engine = SequentialThinkingEngine()

            # Test thinking process
            result = await engine.think_sequentially(
                {
                    "query": "How to create a business presentation?",
                    "context": "Business presentation for investors",
                    "depth": "moderate",
                }
            )

            if result and hasattr(result, "thinking_steps"):
                self.record_test(
                    "MCP Sequential Thinking", True, f"Generated {len(result.thinking_steps)} thinking steps"
                )
            else:
                self.record_test("MCP Sequential Thinking", False, "Failed to generate thinking steps")

        except Exception as e:
            self.record_test("MCP Sequential Thinking", False, f"Error: {str(e)}")

    async def test_mcp_brave_search(self) -> None:
        """Test the MCP Brave Search Server."""
        logger.info("🔍 Testing MCP Brave Search Server...")

        try:
            from mcp_server_openai.tools.mcp_brave_search import BraveSearchClient

            client = BraveSearchClient()

            # Test search functionality
            result = await client.search(
                {"query": "artificial intelligence trends 2024", "search_type": "web", "max_results": 5}
            )

            if result and hasattr(result, "results") and result.results:
                self.record_test("MCP Brave Search", True, f"Found {len(result.results)} results")
            else:
                self.record_test("MCP Brave Search", False, "Failed to perform search")

        except Exception as e:
            self.record_test("MCP Brave Search", False, f"Error: {str(e)}")

    async def test_mcp_memory(self) -> None:
        """Test the MCP Memory Server."""
        logger.info("💾 Testing MCP Memory Server...")

        try:
            from mcp_server_openai.tools.mcp_memory import MemoryServer

            server = MemoryServer()

            # Test memory operations
            content_id = await server.store_content(
                content_type="test",
                title="Test Content",
                content="This is test content for memory testing",
                metadata={"test": True},
            )

            if content_id:
                retrieved = await server.retrieve_content(content_id)
                if retrieved:
                    self.record_test("MCP Memory Server", True, f"Stored and retrieved content: {content_id}")
                else:
                    self.record_test("MCP Memory Server", False, "Failed to retrieve stored content")
            else:
                self.record_test("MCP Memory Server", False, "Failed to store content")

        except Exception as e:
            self.record_test("MCP Memory Server", False, f"Error: {str(e)}")

    async def test_mcp_filesystem(self) -> None:
        """Test the MCP Filesystem Server."""
        logger.info("📁 Testing MCP Filesystem Server...")

        try:
            from mcp_server_openai.tools.mcp_filesystem import FileSystemManager

            manager = FileSystemManager()

            # Test file operations
            test_content = "This is test content for filesystem testing"
            result = await manager.write_file(file_path="test_file.txt", content=test_content, overwrite=True)

            if result.status == "success":
                # Test read operation
                read_result = await manager.read_file("test_file.txt")
                if read_result.status == "success" and read_result.content == test_content:
                    self.record_test("MCP Filesystem Server", True, "File write and read successful")
                else:
                    self.record_test("MCP Filesystem Server", False, "File read failed")
            else:
                self.record_test("MCP Filesystem Server", False, f"File write failed: {result.error_message}")

        except Exception as e:
            self.record_test("MCP Filesystem Server", False, f"Error: {str(e)}")

    async def test_mcp_research_integration(self) -> None:
        """Test the MCP Research Integration Server."""
        logger.info("🔬 Testing MCP Research Integration Server...")

        try:
            from mcp_server_openai.tools.mcp_research_integration import ResearchIntegrationEngine

            engine = ResearchIntegrationEngine()

            # Test research integration
            result = await engine.conduct_automated_research(
                query="AI in healthcare", content_type="presentation", depth="moderate"
            )

            if result and hasattr(result, "research_id"):
                self.record_test("MCP Research Integration", True, f"Research completed: {result.research_id}")
            else:
                self.record_test("MCP Research Integration", False, "Failed to conduct research")

        except Exception as e:
            self.record_test("MCP Research Integration", False, f"Error: {str(e)}")

    async def test_mcp_content_validation(self) -> None:
        """Test the MCP Content Validation Server."""
        logger.info("✅ Testing MCP Content Validation Server...")

        try:
            from mcp_server_openai.tools.mcp_content_validation import ContentValidator

            validator = ContentValidator()

            # Test content validation
            test_content = "This is a test content for validation. It should pass basic checks."
            result = await validator.validate_content(
                {"content": test_content, "content_type": "document", "rules": ["readability", "grammar"]}
            )

            if result and hasattr(result, "validation_results"):
                self.record_test(
                    "MCP Content Validation",
                    True,
                    f"Validation completed with {len(result.validation_results)} results",
                )
            else:
                self.record_test("MCP Content Validation", False, "Failed to validate content")

        except Exception as e:
            self.record_test("MCP Content Validation", False, f"Error: {str(e)}")

    async def test_mcp_advanced_orchestration(self) -> None:
        """Test the MCP Advanced Orchestration Server."""
        logger.info("🎭 Testing MCP Advanced Orchestration Server...")

        try:
            from mcp_server_openai.tools.mcp_advanced_orchestration import AdvancedOrchestrationEngine

            engine = AdvancedOrchestrationEngine()

            # Test workflow creation
            workflow_id = await engine.create_workflow_definition(
                {
                    "name": "Test Workflow",
                    "description": "A test workflow for orchestration testing",
                    "steps": [{"type": "action", "name": "step1", "action": "test_action"}],
                }
            )

            if workflow_id:
                self.record_test("MCP Advanced Orchestration", True, f"Workflow created: {workflow_id}")
            else:
                self.record_test("MCP Advanced Orchestration", False, "Failed to create workflow")

        except Exception as e:
            self.record_test("MCP Advanced Orchestration", False, f"Error: {str(e)}")

    async def test_unified_content_creator(self) -> None:
        """Test the Unified Content Creator."""
        logger.info("🎯 Testing Unified Content Creator...")

        try:
            from mcp_server_openai.tools.unified_content_creator import create_unified_content

            # Test HTML content creation
            result = await create_unified_content(
                title="Test Unified Content",
                brief="Testing the unified content creation system",
                notes=["Feature 1: Content generation", "Feature 2: Multi-format support", "Feature 3: AI integration"],
                output_format="html",
                content_style="professional",
                include_images=True,
                include_icons=True,
            )

            if result.status == "success":
                self.record_test("Unified Content Creator - HTML", True, f"Created: {result.file_path}")
            else:
                self.record_test("Unified Content Creator - HTML", False, f"Failed: {result.error_message}")

            # Test document content creation
            doc_result = await create_unified_content(
                title="Test Document Content",
                brief="Testing document generation",
                notes=["Section 1: Introduction", "Section 2: Main content", "Section 3: Conclusion"],
                output_format="document",
                content_style="professional",
            )

            if doc_result.status == "success":
                self.record_test("Unified Content Creator - Document", True, f"Created: {doc_result.file_path}")
            else:
                self.record_test("Unified Content Creator - Document", False, f"Failed: {doc_result.error_message}")

        except Exception as e:
            self.record_test("Unified Content Creator", False, f"Error: {str(e)}")

    async def test_integration_workflows(self) -> None:
        """Test integration workflows between different components."""
        logger.info("🔗 Testing Integration Workflows...")

        try:
            # Test complete workflow: Research -> Planning -> Generation -> Validation
            from mcp_server_openai.tools.mcp_content_validation import ContentValidator
            from mcp_server_openai.tools.mcp_research_integration import ResearchIntegrationEngine
            from mcp_server_openai.tools.mcp_sequential_thinking import SequentialThinkingEngine
            from mcp_server_openai.tools.unified_content_creator import create_unified_content

            # Step 1: Research
            research_engine = ResearchIntegrationEngine()
            research_result = await research_engine.conduct_automated_research(
                query="digital transformation strategies", content_type="presentation", depth="moderate"
            )

            if not research_result:
                self.record_test("Integration Workflow", False, "Research step failed")
                return

            # Step 2: Planning
            thinking_engine = SequentialThinkingEngine()
            plan_result = await thinking_engine.think_sequentially(
                {
                    "query": "Create a presentation on digital transformation",
                    "context": "Based on research findings",
                    "depth": "moderate",
                }
            )

            if not plan_result:
                self.record_test("Integration Workflow", False, "Planning step failed")
                return

            # Step 3: Generation
            content_result = await create_unified_content(
                title="Digital Transformation Strategies",
                brief="Comprehensive guide to digital transformation",
                notes=[
                    "Strategy 1: Technology adoption",
                    "Strategy 2: Process optimization",
                    "Strategy 3: Culture change",
                ],
                output_format="html",
                content_style="professional",
            )

            if content_result.status != "success":
                self.record_test("Integration Workflow", False, "Generation step failed")
                return

            # Step 4: Validation
            validator = ContentValidator()
            validation_result = await validator.validate_content(
                {
                    "content": content_result.sections[0].content if content_result.sections else "Test content",
                    "content_type": "html",
                    "rules": ["readability", "seo"],
                }
            )

            if validation_result:
                self.record_test("Integration Workflow", True, "Complete workflow successful")
            else:
                self.record_test("Integration Workflow", False, "Validation step failed")

        except Exception as e:
            self.record_test("Integration Workflow", False, f"Error: {str(e)}")

    async def test_performance(self) -> None:
        """Test system performance."""
        logger.info("⚡ Testing System Performance...")

        try:
            from mcp_server_openai.tools.enhanced_document_generator import generate_document

            # Test HTML generation performance
            start_time = time.time()
            result = await generate_document(
                title="Performance Test Document",
                content="# Performance Test\n\nThis is a performance test document.\n\n## Section 1\nPerformance testing content.",
                output_format="html",
                template="minimalist",
            )
            end_time = time.time()

            generation_time = end_time - start_time

            if result.status == "success" and generation_time < 5.0:  # Should complete within 5 seconds
                self.record_test("Performance - HTML Generation", True, f"Completed in {generation_time:.2f}s")
            else:
                self.record_test("Performance - HTML Generation", False, f"Too slow: {generation_time:.2f}s")

        except Exception as e:
            self.record_test("Performance Testing", False, f"Error: {str(e)}")

    async def test_error_handling(self) -> None:
        """Test error handling capabilities."""
        logger.info("🛡️ Testing Error Handling...")

        try:
            from mcp_server_openai.tools.enhanced_document_generator import generate_document

            # Test with invalid parameters
            result = await generate_document(
                title="",  # Empty title
                content="",  # Empty content
                output_format="invalid_format",  # Invalid format
                template="invalid_template",  # Invalid template
            )

            # Should handle errors gracefully
            if result.status == "error" and result.error_message:
                self.record_test("Error Handling", True, "Gracefully handled invalid input")
            else:
                self.record_test("Error Handling", False, "Failed to handle invalid input")

        except Exception as e:
            self.record_test("Error Handling", False, f"Error: {str(e)}")

    def record_test(self, test_name: str, success: bool, message: str) -> None:
        """Record test result."""
        self.test_results.append({"test": test_name, "success": success, "message": message, "timestamp": time.time()})

        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")

    def print_test_summary(self) -> bool:
        """Print test summary and return overall success status."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)

        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{status} {result['test']}")
            if not result["success"]:
                logger.info(f"   └─ {result['message']}")

        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Total Time: {time.time() - self.start_time:.2f}s")

        if failed_tests == 0:
            logger.info("🎉 All tests passed! The system is working correctly.")
            return True
        else:
            logger.warning(f"⚠️ {failed_tests} tests failed. Please check the output above.")
            return False


async def main():
    """Main test runner."""
    tester = CompleteSystemTester()
    success = await tester.run_all_tests()

    if success:
        logger.info("🚀 All tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
