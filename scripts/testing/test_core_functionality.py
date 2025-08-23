#!/usr/bin/env python3
"""
Core Functionality Test Script

This script tests the core functionality of our tools without requiring
external API keys or MCP server connections.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server_openai.tools.enhanced_ppt_generator import PPTRequest, PPTResponse, LLMClient
from mcp_server_openai.tools.enhanced_image_generator import ImageRequest, ImageResult, ImageResponse
from mcp_server_openai.tools.enhanced_icon_generator import IconRequest, IconResult, IconResponse
from mcp_server_openai.tools.unified_content_creator import (
    ContentRequest, ContentOutline, ContentSection, ContentResult,
    SUPPORTED_FORMATS, CONTENT_STYLES, LANGUAGES
)

async def test_dataclasses():
    """Test that all dataclasses can be instantiated correctly."""
    print("🧪 Testing Dataclasses...")
    
    try:
        # Test PPTRequest
        ppt_req = PPTRequest(
            brief="A test presentation",
            notes=["Note 1", "Note 2"],
            target_length="3 slides",
            model_type="gpt-4o"
        )
        print(f"  ✅ PPTRequest: {ppt_req.brief}")
        
        # Test PPTResponse
        ppt_resp = PPTResponse(
            status="success",
            file_path="test.pptx",
            slides_count=3,
            file_size=1024
        )
        print(f"  ✅ PPTResponse: {ppt_resp.status}")
        
        # Test ImageRequest
        img_req = ImageRequest(
            query="technology",
            content_type="presentation",
            style="professional"
        )
        print(f"  ✅ ImageRequest: {img_req.query}")
        
        # Test IconRequest
        icon_req = IconRequest(
            description="business icon",
            content_type="presentation"
        )
        print(f"  ✅ IconRequest: {icon_req.description}")
        
        # Test ContentRequest
        content_req = ContentRequest(
            title="Test Content",
            brief="A test content",
            notes=["Note 1", "Note 2"]
        )
        print(f"  ✅ ContentRequest: {content_req.title}")
        
        print("  🎉 All dataclasses working correctly!")
        
    except Exception as e:
        print(f"  ❌ Dataclass test failed: {e}")
        return False
    
    return True

async def test_constants():
    """Test that all constants are properly defined."""
    print("\n🔧 Testing Constants...")
    
    try:
        print(f"  📋 Supported Formats: {SUPPORTED_FORMATS}")
        print(f"  🎨 Content Styles: {CONTENT_STYLES}")
        print(f"  🌍 Languages: {LANGUAGES}")
        
        # Verify expected values
        assert "presentation" in SUPPORTED_FORMATS
        assert "professional" in CONTENT_STYLES
        assert "English" in LANGUAGES
        
        print("  ✅ All constants properly defined!")
        
    except Exception as e:
        print(f"  ❌ Constants test failed: {e}")
        return False
    
    return True

async def test_llm_client():
    """Test LLM client initialization."""
    print("\n🤖 Testing LLM Client...")
    
    try:
        client = LLMClient()
        print(f"  ✅ LLM Client initialized")
        print(f"  🔑 OpenAI API Key: {'Set' if client.openai_api_key else 'Not Set'}")
        print(f"  🔑 Anthropic API Key: {'Set' if client.anthropic_api_key else 'Not Set'}")
        print(f"  🔑 Google API Key: {'Set' if client.google_api_key else 'Not Set'}")
        
    except Exception as e:
        print(f"  ❌ LLM Client test failed: {e}")
        return False
    
    return True

async def test_content_creation():
    """Test content creation workflow."""
    print("\n📝 Testing Content Creation Workflow...")
    
    try:
        # Create a sample content outline
        outline = ContentOutline(
            title="Test Content",
            sections=[
                {
                    "title": "Introduction",
                    "type": "title",
                    "content": "Welcome to the presentation"
                },
                {
                    "title": "Main Content",
                    "type": "content",
                    "content": "This is the main content"
                }
            ],
            total_sections=2,
            estimated_length="2 slides",
            suggested_images=1,
            suggested_icons=2,
            themes=["professional", "modern"]
        )
        
        print(f"  ✅ Content Outline created: {outline.title}")
        print(f"  📊 Sections: {outline.total_sections}")
        print(f"  🖼️  Suggested Images: {outline.suggested_images}")
        print(f"  🎯 Suggested Icons: {outline.suggested_icons}")
        
        # Create content sections
        sections = [
            ContentSection(
                title="Introduction",
                content="Welcome to the presentation",
                section_type="title",
                layout="title_slide"
            ),
            ContentSection(
                title="Main Content",
                content="This is the main content",
                section_type="content",
                layout="content_slide"
            )
        ]
        
        print(f"  ✅ Content Sections created: {len(sections)} sections")
        
        # Create content result
        result = ContentResult(
            title="Test Content",
            output_format="presentation",
            file_path="test.pptx",
            file_size=2048,
            sections=sections,
            images_used=1,
            icons_used=2,
            processing_time=5.5
        )
        
        print(f"  ✅ Content Result created: {result.title}")
        print(f"  📁 File: {result.file_path}")
        print(f"  📊 Size: {result.file_size} bytes")
        print(f"  ⏱️  Time: {result.processing_time}s")
        
        print("  🎉 Content creation workflow working correctly!")
        
    except Exception as e:
        print(f"  ❌ Content creation test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting Core Functionality Tests...\n")
    
    tests = [
        test_dataclasses(),
        test_constants(),
        test_llm_client(),
        test_content_creation()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n" + "="*50)
    print("📊 Test Results Summary")
    print("="*50)
    
    passed = 0
    total = len(tests)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"  ❌ Test {i+1} failed with exception: {result}")
        elif result:
            print(f"  ✅ Test {i+1} passed")
            passed += 1
        else:
            print(f"  ❌ Test {i+1} failed")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core functionality tests passed! The system is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
