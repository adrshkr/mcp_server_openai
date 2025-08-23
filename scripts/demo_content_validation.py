#!/usr/bin/env python3
"""
Demo script for the MCP Content Validation Tool.

This script demonstrates how to use the content validation tool
through the MCP server interface.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mcp_server_openai.tools.mcp_content_validation import (
    validate_content_quality,
    get_validation_history,
    get_validation_result
)


async def demo_basic_validation():
    """Demonstrate basic content validation."""
    
    print("🔍 Basic Content Validation Demo")
    print("=" * 50)
    
    # Sample content for validation
    content = """
    # Marketing Strategy 2024
    
    ## Executive Summary
    Our marketing strategy focuses on digital transformation and customer engagement.
    
    ## Key Objectives
    - Increase brand awareness by 25%
    - Generate 1000 qualified leads
    - Improve customer retention by 15%
    
    ## Target Audience
    - B2B companies in technology sector
    - Decision makers aged 30-50
    - Companies with 100+ employees
    
    ## Marketing Channels
    - Social media (LinkedIn, Twitter)
    - Content marketing (blog, whitepapers)
    - Email campaigns
    - Industry events and conferences
    
    ## Success Metrics
    - Website traffic growth
    - Lead generation rates
    - Social media engagement
    - Customer acquisition cost
    """
    
    print("📝 Sample Content:")
    print(content)
    print("\n" + "="*50)
    
    try:
        print("🚀 Running validation...")
        
        result = await validate_content_quality(
            content=content,
            content_type="document",
            target_audience="Marketing professionals and executives",
            objectives=[
                "Define marketing strategy for 2024",
                "Set clear objectives and metrics",
                "Identify target audience and channels"
            ],
            key_messages=[
                "Digital transformation is key to success",
                "Data-driven approach to marketing",
                "Focus on customer engagement and retention"
            ]
        )
        
        print("✅ Validation completed!")
        print(f"📊 Overall Score: {result['overall_score']:.2f}")
        print(f"✅ Passed Rules: {result['passed_rules']}")
        print(f"❌ Failed Rules: {result['failed_rules']}")
        print(f"⚠️  Warning Rules: {result['warning_rules']}")
        
        # Show key metrics
        metrics = result['content_metrics']
        print(f"\n📈 Content Metrics:")
        print(f"   Words: {metrics['word_count']}")
        print(f"   Sentences: {metrics['sentence_count']}")
        print(f"   Paragraphs: {metrics['paragraph_count']}")
        print(f"   Readability: {metrics['readability_score']:.2f}")
        print(f"   Structure: {metrics['content_structure_score']:.2f}")
        print(f"   Visual Elements: {metrics['visual_element_score']:.2f}")
        print(f"   Accessibility: {metrics['accessibility_score']:.2f}")
        print(f"   SEO: {metrics['seo_score']:.2f}")
        
        # Show top recommendations
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(result['recommendations'][:5], 1):
            print(f"   {i}. {rec}")
        
        return result['validation_id']
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return None


async def demo_custom_validation():
    """Demonstrate custom validation rules."""
    
    print("\n🔧 Custom Validation Rules Demo")
    print("=" * 50)
    
    content = """
    # Quick Product Overview
    
    Our product offers:
    - Fast performance
    - Easy integration
    - Comprehensive support
    
    Get started today!
    """
    
    print("📝 Content for Custom Validation:")
    print(content)
    print("\n" + "="*50)
    
    try:
        print("🚀 Running custom validation...")
        
        result = await validate_content_quality(
            content=content,
            content_type="webpage",
            target_audience="General users",
            objectives=["Provide product overview"],
            key_messages=["Product benefits"],
            validation_rules=["readability", "completeness"],
            custom_thresholds={"readability": 0.5, "completeness": 0.6},
            include_suggestions=True
        )
        
        print("✅ Custom validation completed!")
        print(f"📊 Overall Score: {result['overall_score']:.2f}")
        print(f"✅ Passed Rules: {result['passed_rules']}")
        print(f"❌ Failed Rules: {result['failed_rules']}")
        
        return result['validation_id']
        
    except Exception as e:
        print(f"❌ Error during custom validation: {e}")
        return None


async def demo_validation_history():
    """Demonstrate validation history functionality."""
    
    print("\n📚 Validation History Demo")
    print("=" * 50)
    
    try:
        print("🔍 Retrieving validation history...")
        
        history = get_validation_history(limit=10)
        
        if history:
            print(f"✅ Found {len(history)} validation entries:")
            for i, entry in enumerate(history[:5], 1):
                print(f"   {i}. ID: {entry['validation_id']}")
                print(f"      Score: {entry['overall_score']:.2f}")
                print(f"      Passed: {entry['passed_rules']}, Failed: {entry['failed_rules']}")
                print(f"      Time: {entry['timestamp']}")
                print()
        else:
            print("ℹ️  No validation history found.")
            
    except Exception as e:
        print(f"❌ Error retrieving history: {e}")


async def demo_retrieve_result(validation_id: str):
    """Demonstrate retrieving a specific validation result."""
    
    if not validation_id:
        print("⚠️  No validation ID available for retrieval demo.")
        return
    
    print("\n🔍 Retrieve Validation Result Demo")
    print("=" * 50)
    
    try:
        print(f"🔍 Retrieving result for: {validation_id}")
        
        result = get_validation_result(validation_id)
        
        if result:
            print("✅ Result retrieved successfully!")
            print(f"📊 Overall Score: {result['overall_score']:.2f}")
            print(f"✅ Passed Rules: {result['passed_rules']}")
            print(f"❌ Failed Rules: {result['failed_rules']}")
            print(f"⚠️  Warning Rules: {result['warning_rules']}")
            
            # Show some validation results
            print(f"\n📋 Validation Results:")
            for rule_result in result['validation_results'][:3]:
                print(f"   • {rule_result['rule_name']}: {rule_result['status']}")
                print(f"     Score: {rule_result['score']:.2f}")
                print(f"     Message: {rule_result['message']}")
                print()
        else:
            print("❌ Result not found.")
            
    except Exception as e:
        print(f"❌ Error retrieving result: {e}")


async def main():
    """Main demo function."""
    
    print("🎯 MCP Content Validation Tool - Interactive Demo")
    print("=" * 60)
    print("This demo showcases the content validation capabilities")
    print("including basic validation, custom rules, and result retrieval.")
    print()
    
    # Run demos
    validation_id1 = await demo_basic_validation()
    validation_id2 = await demo_custom_validation()
    
    # Show history and retrieve results
    await demo_validation_history()
    
    # Try to retrieve the first validation result
    await demo_retrieve_result(validation_id1)
    
    print("\n" + "="*60)
    print("🎉 Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("✅ Basic content validation with comprehensive metrics")
    print("✅ Custom validation rules and thresholds")
    print("✅ Validation history tracking")
    print("✅ Result retrieval and analysis")
    print("✅ Detailed recommendations and suggestions")
    
    print("\nThe tool is now ready for use in your MCP server!")
    print("You can integrate it with other tools for automated content quality assessment.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)


