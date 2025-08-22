#!/usr/bin/env python3
"""
Demo script for the Enhanced PPT Generator with Presenton API integration.

This script demonstrates how to use the enhanced PPT generator to create
high-quality PowerPoint presentations with LLM preprocessing and intelligent
content structuring.
"""

import asyncio
import json
import sys
from pathlib import Path
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_openai.tools.enhanced_ppt_generator import (
    create_enhanced_presentation,
    PPTRequest,
    EnhancedPPTGenerator
)


async def demo_basic_usage():
    """Demonstrate basic usage of the enhanced PPT generator."""
    print("🚀 Enhanced PPT Generator Demo")
    print("=" * 50)

    # Create a sample PPT request
    request = PPTRequest(
        notes=[
            "Topic: Digital Transformation Strategy",
            "Current state assessment and gap analysis",
            "Technology roadmap and implementation plan",
            "Change management and stakeholder engagement",
            "Success metrics and ROI projections",
            "Risk mitigation and contingency planning"
        ],
        brief="Create a strategic presentation for our digital transformation initiative, highlighting key milestones, technology investments, and expected business outcomes.",
        target_length="8 slides",
        model_type="gpt-4o",
        template_preference="professional",
        include_images=False,
        language="English",
        client_id="demo_client"
    )

    print(f"📋 PPT Request:")
    print(f"   Brief: {request.brief}")
    print(f"   Notes: {len(request.notes)} points")
    print(f"   Target Length: {request.target_length}")
    print(f"   Model: {request.model_type}")
    print(f"   Template: {request.template_preference}")
    print(f"   Images: {'Yes' if request.include_images else 'No'}")
    print(f"   Language: {request.language}")
    print()

    try:
        # Generate the presentation
        print("🔄 Generating enhanced presentation...")
        result = await create_enhanced_presentation(
            notes=request.notes,
            brief=request.brief,
            target_length=request.target_length,
            model_type=request.model_type,
            template_preference=request.template_preference,
            include_images=request.include_images,
            language=request.language,
            client_id=request.client_id
        )

        if result.status == "success":
            print("✅ Presentation generated successfully!")
            print(f"   📁 File path: {result.file_path}")
            print(f"   📊 Slides created: {result.slides_count}")
            print(f"   🎨 Template used: {result.template_used}")
            print(f"   📝 Draft name: {result.draft_name}")
            print(f"   ⏱️  Processing time: {result.processing_time_ms:.2f}ms")
            print(f"   🧠 Token usage: {result.token_usage}")
            print(f"   🆔 Presentation ID: {result.presentation_id}")
        else:
            print("❌ Presentation generation failed!")
            print(f"   Error: {result.error}")

    except Exception as e:
        print(f"❌ Error during presentation generation: {e}")


async def demo_content_analysis():
    """Demonstrate content analysis capabilities."""
    print("\n🔍 Content Analysis Demo")
    print("=" * 30)

    generator = EnhancedPPTGenerator()
    
    # Test content analysis
    request = PPTRequest(
        notes=[
            "Topic: Sustainable Business Practices",
            "Environmental impact assessment",
            "Green technology implementation",
            "Stakeholder engagement strategies",
            "Long-term sustainability goals"
        ],
        brief="Analyze our business practices and suggest a presentation structure for communicating our sustainability initiatives to investors and customers.",
        target_length="10 slides",
        model_type="gpt-4o",
        client_id="analysis_client"
    )

    try:
        print("🧠 Analyzing content for optimal structure...")
        api_args, input_tokens, output_tokens = await generator.preprocess_for_presenton(request)
        
        print("✅ Content analysis completed!")
        print(f"   📝 Suggested prompt length: {len(api_args['prompt'])} characters")
        print(f"   📊 Recommended slides: {api_args['n_slides']}")
        print(f"   🎨 Suggested template: {api_args['template']}")
        print(f"   🌍 Language: {api_args['language']}")
        print(f"   📄 Export format: {api_args['export_as']}")
        print(f"   🏷️  Draft name: {api_args['draft_name']}")
        print(f"   🧠 Token usage: {input_tokens} input, {output_tokens} output")
        
    except Exception as e:
        print(f"❌ Content analysis failed: {e}")


async def demo_template_selection():
    """Demonstrate template selection capabilities."""
    print("\n🎨 Template Selection Demo")
    print("=" * 30)

    # Test different template preferences
    templates = ["classic", "general", "modern", "professional"]
    
    for template in templates:
        print(f"\n🔍 Testing '{template}' template...")
        
        request = PPTRequest(
            notes=[
                "Topic: Product Launch Strategy",
                "Market research and competitive analysis",
                "Product features and benefits",
                "Marketing and go-to-market strategy",
                "Sales projections and revenue targets"
            ],
            brief=f"Create a product launch presentation using the {template} template style.",
            target_length="6 slides",
            model_type="gpt-4o",
            template_preference=template,
            client_id="template_client"
        )

        try:
            result = await create_enhanced_presentation(
                notes=request.notes,
                brief=request.brief,
                target_length=request.target_length,
                model_type=request.model_type,
                template_preference=request.template_preference,
                client_id=request.client_id
            )
            
            if result.status == "success":
                print(f"   ✅ {template.title()} template successful")
                print(f"      📊 Slides: {result.slides_count}")
                print(f"      ⏱️  Time: {result.processing_time_ms:.2f}ms")
            else:
                print(f"   ❌ {template.title()} template failed: {result.error}")
                
        except Exception as e:
            print(f"   ❌ {template.title()} template error: {e}")


async def demo_multilingual_support():
    """Demonstrate multilingual support."""
    print("\n🌍 Multilingual Support Demo")
    print("=" * 30)

    languages = ["English", "Spanish", "French"]
    
    for language in languages:
        print(f"\n🔍 Testing {language} language...")
        
        request = PPTRequest(
            notes=[
                "Topic: International Market Expansion",
                "Market entry strategy and localization",
                "Cultural considerations and adaptation",
                "Regulatory compliance requirements",
                "Partnership and distribution channels"
            ],
            brief=f"Create a presentation about international market expansion in {language}.",
            target_length="8 slides",
            model_type="gpt-4o",
            language=language,
            client_id="multilingual_client"
        )

        try:
            result = await create_enhanced_presentation(
                notes=request.notes,
                brief=request.brief,
                target_length=request.target_length,
                model_type=request.model_type,
                language=request.language,
                client_id=request.client_id
            )
            
            if result.status == "success":
                print(f"   ✅ {language} presentation successful")
                print(f"      📊 Slides: {result.slides_count}")
                print(f"      🎨 Template: {result.template_used}")
            else:
                print(f"   ❌ {language} presentation failed: {result.error}")
                
        except Exception as e:
            print(f"   ❌ {language} presentation error: {e}")


async def demo_configuration():
    """Demonstrate configuration options."""
    print("\n⚙️  Configuration Demo")
    print("=" * 30)

    # Show configuration file location
    config_path = Path("config/enhanced_ppt.yaml")
    if config_path.exists():
        print(f"📁 Configuration file found: {config_path}")
        print("   You can customize:")
        print("   - Presenton API settings")
        print("   - LLM model configurations")
        print("   - Template options")
        print("   - Output settings")
        print("   - Performance parameters")
    else:
        print(f"⚠️  Configuration file not found: {config_path}")
        print("   Create this file to customize the enhanced PPT generator.")

    # Show environment variables
    print(f"\n🔑 Environment Variables:")
    print(f"   PRESENTON_API_URL: {os.getenv('PRESENTON_API_URL', 'Not set')}")
    print(f"   OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"   ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not set'}")
    print(f"   GOOGLE_API_KEY: {'Set' if os.getenv('GOOGLE_API_KEY') else 'Not set'}")


async def main():
    """Main demo function."""
    print("🎯 Enhanced PPT Generator with Presenton API Integration")
    print("=" * 60)
    print()

    # Run demos
    await demo_basic_usage()
    await demo_content_analysis()
    await demo_template_selection()
    await demo_multilingual_support()
    await demo_configuration()

    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\nTo use the enhanced PPT generator:")
    print("1. Call the tool via MCP: enhanced_ppt.create")
    print("2. Use the CLI script: python scripts/call_tool.py enhanced_ppt.create params-enhanced-ppt-create.json")
    print("3. Import and use in your code: from mcp_server_openai.tools.enhanced_ppt_generator import create_enhanced_presentation")
    print("\nFor more information, see the configuration file: config/enhanced_ppt.yaml")


if __name__ == "__main__":
    asyncio.run(main())

