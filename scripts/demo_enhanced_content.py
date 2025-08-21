#!/usr/bin/env python3
"""
Demo script for the Enhanced Content Creator with MCP server integration.

This script demonstrates how to use the enhanced content creator to generate
PowerPoint presentations with intelligent content planning, research enhancement,
and advanced content generation.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_openai.tools.enhanced_content_creator import (
    create_enhanced_presentation,
    MCPClient,
    ContentRequest
)


async def demo_basic_usage():
    """Demonstrate basic usage of the enhanced content creator."""
    print("🚀 Enhanced Content Creator Demo")
    print("=" * 50)
    
    # Create a sample content request
    request = ContentRequest(
        number_of_slides=5,
        brief="Digital Transformation Strategy",
        notes="Current state assessment\nTechnology roadmap\nChange management plan\nSuccess metrics\nImplementation timeline",
        style="professional",
        tone="persuasive",
        audience="executives",
        client_id="demo_client"
    )
    
    print(f"📋 Content Request:")
    print(f"   Brief: {request.brief}")
    print(f"   Slides: {request.number_of_slides}")
    print(f"   Style: {request.style}")
    print(f"   Tone: {request.tone}")
    print(f"   Audience: {request.audience}")
    print()
    
    try:
        # Generate the presentation
        print("🔄 Generating enhanced presentation...")
        result = await create_enhanced_presentation(
            number_of_slides=request.number_of_slides,
            brief=request.brief,
            notes=request.notes,
            style=request.style,
            tone=request.tone,
            audience=request.audience,
            client_id=request.client_id
        )
        
        if result["status"] == "success":
            print("✅ Presentation generated successfully!")
            print(f"   📁 Output path: {result['path']}")
            print(f"   📊 Slides created: {result['slides']}")
            print(f"   🎯 Style applied: {result['style']}")
            print(f"   🗣️  Tone used: {result['tone']}")
            print(f"   👥 Target audience: {result['audience']}")
            print(f"   🔧 Enhancement methods: {', '.join(result['enhancement_methods'])}")
            print(f"   ⏰ Generated at: {result['generated_at']}")
        else:
            print("❌ Presentation generation failed!")
            print(f"   Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error during presentation generation: {e}")


async def demo_mcp_client():
    """Demonstrate MCP client functionality."""
    print("\n🔌 MCP Client Demo")
    print("=" * 30)
    
    client = MCPClient()
    
    # Test sequential thinking
    print("🧠 Testing Sequential Thinking Server...")
    plan_result = await client.call_server("sequential_thinking", "plan_presentation", {
        "brief": "AI Strategy Overview",
        "notes": "Market analysis\nTechnology trends\nImplementation plan",
        "number_of_slides": 4
    })
    
    if "error" not in plan_result:
        print("✅ Sequential thinking successful!")
        print(f"   Title: {plan_result.get('title', 'N/A')}")
        print(f"   Slides planned: {len(plan_result.get('slides', []))}")
        print(f"   Key messages: {len(plan_result.get('key_messages', []))}")
    else:
        print(f"❌ Sequential thinking failed: {plan_result['error']}")
    
    # Test brave search
    print("\n🔍 Testing Brave Search Server...")
    search_result = await client.call_server("brave_search", "search_content", {
        "query": "AI strategy implementation best practices"
    })
    
    if "error" not in search_result:
        print("✅ Brave search successful!")
        print(f"   Search results: {len(search_result.get('search_results', []))}")
        print(f"   Sources: {len(search_result.get('sources', []))}")
    else:
        print(f"❌ Brave search failed: {search_result['error']}")
    
    # Test memory server
    print("\n💾 Testing Memory Server...")
    memory_result = await client.call_server("memory", "generate_content", {
        "slide_info": {"title": "AI Strategy Overview"}
    })
    
    if "error" not in memory_result:
        print("✅ Memory server successful!")
        print(f"   Title: {memory_result.get('title', 'N/A')}")
        print(f"   Bullet points: {len(memory_result.get('bullet_points', []))}")
        print(f"   Visual suggestions: {len(memory_result.get('visual_suggestions', []))}")
    else:
        print(f"❌ Memory server failed: {memory_result['error']}")


async def demo_configuration():
    """Demonstrate configuration options."""
    print("\n⚙️  Configuration Demo")
    print("=" * 30)
    
    # Show available MCP servers
    from mcp_server_openai.tools.enhanced_content_creator import MCP_SERVERS
    
    print("Available MCP Servers:")
    for server_name, package in MCP_SERVERS.items():
        print(f"   🔧 {server_name}: {package}")
    
    # Show configuration file location
    config_path = Path("config/enhanced_content.yaml")
    if config_path.exists():
        print(f"\n📁 Configuration file found: {config_path}")
        print("   You can customize server settings, content generation options,")
        print("   and client-specific overrides in this file.")
    else:
        print(f"\n⚠️  Configuration file not found: {config_path}")
        print("   Create this file to customize the enhanced content creator.")


async def main():
    """Main demo function."""
    print("🎯 Enhanced Content Creator with MCP Server Integration")
    print("=" * 60)
    print()
    
    # Run demos
    await demo_basic_usage()
    await demo_mcp_client()
    await demo_configuration()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\nTo use the enhanced content creator:")
    print("1. Call the tool via MCP: enhanced_content.create")
    print("2. Use the CLI script: python scripts/call_tool.py enhanced_content.create params-enhanced-content-create.json")
    print("3. Import and use in your code: from mcp_server_openai.tools.enhanced_content_creator import create_enhanced_presentation")
    print("\nFor more information, see ENHANCED_CONTENT_CREATOR_README.md")


if __name__ == "__main__":
    asyncio.run(main())
