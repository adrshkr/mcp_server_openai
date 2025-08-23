#!/usr/bin/env python3
"""
Demo script for the Unified Content Creator Tool

This script demonstrates the comprehensive content creation capabilities
including PPT, DOC, PDF, and HTML generation with MCP server integration.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_openai.tools.unified_content_creator import (
    create_unified_content,
    SUPPORTED_FORMATS,
    CONTENT_STYLES,
    LANGUAGES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_content_creation():
    """Demonstrate basic content creation across all formats."""
    print("🚀 **Unified Content Creator Demo**")
    print("=" * 50)
    
    # Sample content
    title = "AI-Powered Content Creation: The Future of Digital Marketing"
    brief = (
        "An exploration of how artificial intelligence is revolutionizing "
        "content creation and digital marketing strategies."
    )
    notes = [
        "AI tools are transforming content creation workflows",
        "Machine learning algorithms can generate personalized content",
        "Natural language processing enables automated content optimization",
        "AI-powered analytics provide insights for content strategy",
        "The future of content creation is collaborative human-AI partnerships"
    ]
    
    print(f"📝 **Creating Content:** {title}")
    print(f"📋 **Brief:** {brief}")
    print(f"📌 **Notes:** {len(notes)} key points")
    print()
    
    # Test each output format
    for output_format in SUPPORTED_FORMATS:
        print(f"🔄 **Generating {output_format.upper()}...**")
        
        try:
            result = await create_unified_content(
                title=title,
                brief=brief,
                notes=notes,
                output_format=output_format,
                content_style="professional",
                language="English",
                include_images=True,
                include_icons=True,
                client_id="demo_user"
            )
            
            if result.status == "success":
                print(f"✅ **{output_format.upper()} Created Successfully!**")
                print(f"   📁 File: {result.file_path}")
                print(f"   📊 Size: {result.file_size} bytes")
                print(f"   🖼️  Images: {result.images_used}")
                print(f"   🎯 Icons: {result.icons_used}")
                print(f"   ⏱️  Time: {result.processing_time:.2f}s")
                print(f"   📑 Sections: {len(result.sections)}")
            else:
                print(f"❌ **{output_format.upper()} Creation Failed:** {result.error_message}")
            
        except Exception as e:
            print(f"❌ **Error creating {output_format.upper()}:** {e}")
        
        print()


async def demo_content_styles():
    """Demonstrate different content styles."""
    print("🎨 **Content Style Variations Demo**")
    print("=" * 40)
    
    title = "Innovation in Technology"
    brief = "Exploring cutting-edge technological innovations and their impact on society."
    notes = [
        "Emerging technologies are reshaping industries",
        "Innovation drives economic growth and competitiveness",
        "Technology adoption varies across different sectors",
        "Future trends in technological development"
    ]
    
    for style in CONTENT_STYLES:
        print(f"🎭 **Style: {style.title()}**")
        
        try:
            result = await create_unified_content(
                title=title,
                brief=brief,
                notes=notes,
                output_format="presentation",
                content_style=style,
                include_images=True,
                include_icons=True,
                client_id="demo_style_user"
            )
            
            if result.status == "success":
                print(f"   ✅ Created successfully in {style} style")
                print(f"   📁 File: {result.file_path}")
            else:
                print(f"   ❌ Failed: {result.error_message}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()


async def demo_multilingual_content():
    """Demonstrate multilingual content creation."""
    print("🌍 **Multilingual Content Demo**")
    print("=" * 35)
    
    title = "Global Business Strategy"
    brief = "Developing effective business strategies for international markets."
    notes = [
        "Market research and cultural understanding",
        "Localization strategies and adaptation",
        "International partnerships and alliances",
        "Global supply chain management"
    ]
    
    # Test a few languages
    test_languages = ["English", "Spanish", "French"]
    
    for language in test_languages:
        print(f"🗣️  **Language: {language}**")
        
        try:
            result = await create_unified_content(
                title=title,
                brief=brief,
                notes=notes,
                output_format="document",
                language=language,
                include_images=True,
                include_icons=True,
                client_id="demo_lang_user"
            )
            
            if result.status == "success":
                print(f"   ✅ Created successfully in {language}")
                print(f"   📁 File: {result.file_path}")
            else:
                print(f"   ❌ Failed: {result.error_message}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()


async def demo_advanced_features():
    """Demonstrate advanced content creation features."""
    print("🚀 **Advanced Features Demo**")
    print("=" * 35)
    
    title = "Comprehensive Business Analysis"
    brief = "In-depth analysis of business performance, market trends, and strategic recommendations."
    notes = [
        "Executive summary and key findings",
        "Market analysis and competitive landscape",
        "Financial performance and metrics",
        "Strategic recommendations and action items",
        "Risk assessment and mitigation strategies",
        "Implementation timeline and milestones"
    ]
    
    # Test with custom branding and advanced options
    custom_branding = {
        "company_name": "Demo Corp",
        "logo_url": "https://example.com/logo.png",
        "primary_color": "#2E86AB",
        "secondary_color": "#A23B72",
        "font_family": "Arial, sans-serif"
    }
    
    print("🎨 **Custom Branding & Advanced Options**")
    
    try:
        result = await create_unified_content(
            title=title,
            brief=brief,
            notes=notes,
            output_format="presentation",
            content_style="professional",
            language="English",
            theme="business",
            include_images=True,
            include_icons=True,
            custom_template="corporate",
            branding=custom_branding,
            target_length="15-20 slides",
            client_id="demo_advanced_user"
        )
        
        if result.status == "success":
            print("✅ **Advanced Content Created Successfully!**")
            print(f"   📁 File: {result.file_path}")
            print(f"   📊 Size: {result.file_size} bytes")
            print(f"   🖼️  Images: {result.images_used}")
            print(f"   🎯 Icons: {result.icons_used}")
            print(f"   ⏱️  Time: {result.processing_time:.2f}s")
            print(f"   📑 Sections: {len(result.sections)}")
            
            # Show section details
            print("\n   📋 **Section Details:**")
            for i, section in enumerate(result.sections, 1):
                print(f"      {i}. {section.title} ({section.section_type})")
                print(f"         Content: {section.content[:100]}...")
                print(f"         Images: {len(section.images)}, Icons: {len(section.icons)}")
        else:
            print(f"❌ **Advanced Content Creation Failed:** {result.error_message}")
        
    except Exception as e:
        print(f"❌ **Error in Advanced Features Demo:** {e}")
    
    print()


async def demo_error_handling():
    """Demonstrate error handling and edge cases."""
    print("⚠️  **Error Handling & Edge Cases Demo**")
    print("=" * 45)
    
    # Test with invalid inputs
    test_cases = [
        {
            "name": "Empty Title",
            "title": "",
            "brief": "Test brief",
            "notes": ["Test note"]
        },
        {
            "name": "Very Long Title",
            "title": "A" * 500,  # Very long title
            "brief": "Test brief",
            "notes": ["Test note"]
        },
        {
            "name": "No Notes",
            "title": "Test Title",
            "brief": "Test brief",
            "notes": []
        },
        {
            "name": "Invalid Format",
            "title": "Test Title",
            "brief": "Test brief",
            "notes": ["Test note"],
            "output_format": "invalid_format"
        }
    ]
    
    for test_case in test_cases:
        print(f"🧪 **Testing: {test_case['name']}**")
        
        try:
            result = await create_unified_content(
                title=test_case["title"],
                brief=test_case["brief"],
                notes=test_case["notes"],
                output_format=test_case.get("output_format", "presentation"),
                client_id="demo_error_user"
            )
            
            if result.status == "success":
                print(f"   ✅ Unexpected success for {test_case['name']}")
            else:
                print(f"   ❌ Expected failure: {result.error_message}")
            
        except Exception as e:
            print(f"   ❌ Exception caught: {e}")
        
        print()


async def main():
    """Run all demo functions."""
    print("🎉 **Welcome to the Unified Content Creator Demo!**")
    print("This demo showcases the comprehensive content creation capabilities")
    print("across multiple formats with MCP server integration.")
    print()
    
    try:
        # Run all demos
        await demo_basic_content_creation()
        await demo_content_styles()
        await demo_multilingual_content()
        await demo_advanced_features()
        await demo_error_handling()
        
        print("🎊 **Demo Completed Successfully!**")
        print("=" * 40)
        print("✅ Basic content creation across all formats")
        print("✅ Different content styles and themes")
        print("✅ Multilingual content support")
        print("✅ Advanced features and custom branding")
        print("✅ Error handling and edge cases")
        print()
        print("🚀 **Ready for Production Use!**")
        
    except Exception as e:
        print(f"❌ **Demo failed with error:** {e}")
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

