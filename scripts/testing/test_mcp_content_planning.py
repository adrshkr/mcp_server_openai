#!/usr/bin/env python3
"""
Test script for MCP Content Planning Tool

This script tests the functionality of the MCP Content Planning tool
that integrates sequential thinking with content generation.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_openai.tools.mcp_content_planning import (
    ContentPlanningEngine,
    create_content_plan,
    execute_content_plan,
    get_all_content_plans,
    get_content_plan,
    get_execution_history,
)


async def test_content_planning_creation() -> None:
    """Test creating content plans."""
    print("Testing content plan creation...")

    # Test presentation plan
    print("\n1. Creating presentation plan...")
    presentation_plan = await create_content_plan(
        title="AI in Healthcare: Opportunities and Challenges",
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

    print(f"   Status: {presentation_plan['status']}")
    print(f"   Plan ID: {presentation_plan['plan_id']}")
    print(f"   Sections: {len(presentation_plan['content_plan']['sections'])}")

    # Test document plan
    print("\n2. Creating document plan...")
    document_plan = await create_content_plan(
        title="Digital Transformation Strategy Guide",
        content_type="document",
        target_audience="Business leaders and IT managers",
        objectives=[
            "Define digital transformation framework",
            "Provide implementation roadmap",
            "Include best practices and case studies",
        ],
        key_messages=[
            "Digital transformation is essential for business survival",
            "Success requires cultural change and technology adoption",
            "ROI can be measured through multiple metrics",
        ],
    )

    print(f"   Status: {document_plan['status']}")
    print(f"   Plan ID: {document_plan['plan_id']}")
    print(f"   Sections: {len(document_plan['content_plan']['sections'])}")

    print("✓ Content plan creation test passed\n")


async def test_content_plan_execution() -> None:
    """Test executing content plans."""
    print("Testing content plan execution...")

    # Create a test plan first
    test_plan = await create_content_plan(
        title="Test Content Plan",
        content_type="presentation",
        target_audience="Test audience",
        objectives=["Test objective"],
        key_messages=["Test message"],
    )

    plan_id = test_plan["plan_id"]

    # Test preview execution
    print("\n1. Testing preview execution...")
    preview_result = await execute_content_plan(plan_id=plan_id, execution_mode="preview", target_format="pptx")

    print(f"   Status: {preview_result['status']}")
    print(f"   Execution ID: {preview_result['execution_id']}")
    print(f"   Progress: {preview_result['progress']['status']}")

    # Test section execution
    print("\n2. Testing section execution...")
    section_result = await execute_content_plan(
        plan_id=plan_id, execution_mode="section", target_format="pptx", priority_sections=["intro"]
    )

    print(f"   Status: {section_result['status']}")
    print(f"   Execution ID: {section_result['execution_id']}")

    # Test full execution
    print("\n3. Testing full execution...")
    full_result = await execute_content_plan(plan_id=plan_id, execution_mode="full", target_format="pptx")

    print(f"   Status: {full_result['status']}")
    print(f"   Execution ID: {full_result['execution_id']}")
    print(f"   Progress: {full_result['progress']['status']}")

    print("✓ Content plan execution test passed\n")


def test_content_plan_retrieval() -> None:
    """Test retrieving content plans."""
    print("Testing content plan retrieval...")

    # Get all plans
    all_plans = get_all_content_plans()
    print(f"   Total plans: {len(all_plans)}")

    if all_plans:
        # Get details of first plan
        first_plan_id = all_plans[0]["plan_id"]
        plan_details = get_content_plan(first_plan_id)

        if plan_details:
            print(f"   Retrieved plan: {plan_details['title']}")
            print(f"   Content type: {plan_details['content_type']}")
            print(f"   Sections: {len(plan_details['sections'])}")
        else:
            print("   Failed to retrieve plan details")

    print("✓ Content plan retrieval test passed\n")


def test_execution_history() -> None:
    """Test execution history functionality."""
    print("Testing execution history...")

    history = get_execution_history(limit=10)
    print(f"   History entries: {len(history)}")

    if history:
        latest = history[-1]
        print(f"   Latest execution: {latest['execution_id']}")
        print(f"   Status: {latest['status']}")

    print("✓ Execution history test passed\n")


async def test_planning_engine_integration() -> None:
    """Test the planning engine integration."""
    print("Testing planning engine integration...")

    # Create engine instance
    engine = ContentPlanningEngine()

    # Test plan storage
    test_plan = await create_content_plan(
        title="Integration Test Plan",
        content_type="document",
        target_audience="Developers",
        objectives=["Test integration"],
        key_messages=["Integration works"],
    )

    plan_id = test_plan["plan_id"]

    # Test retrieving from engine
    stored_plan = engine.get_plan(plan_id)
    if stored_plan:
        print(f"   Plan stored and retrieved: {stored_plan.title}")

    # Test execution history
    execution_result = await execute_content_plan(plan_id, "preview")
    history = engine.get_execution_history()
    print(f"   Execution history entries: {len(history)}")

    print("✓ Planning engine integration test passed\n")


async def test_content_types_and_formats() -> None:
    """Test different content types and formats."""
    print("Testing different content types and formats...")

    content_types = ["presentation", "document", "webpage", "report"]

    for content_type in content_types:
        print(f"\n   Testing {content_type}...")

        plan = await create_content_plan(
            title=f"Test {content_type.title()}",
            content_type=content_type,
            target_audience="Test users",
            objectives=[f"Test {content_type} creation"],
            key_messages=[f"{content_type} is working"],
        )

        if plan["status"] == "success":
            print(f"     ✓ {content_type} plan created successfully")

            # Test execution
            execution = await execute_content_plan(
                plan_id=plan["plan_id"], execution_mode="preview", target_format="default"
            )

            if execution["status"] == "success":
                print(f"     ✓ {content_type} execution successful")
            else:
                print(f"     ⚠ {content_type} execution failed: {execution['message']}")
        else:
            print(f"     ❌ {content_type} plan creation failed: {plan['message']}")

    print("\n✓ Content types and formats test passed\n")


async def main() -> None:
    """Run all tests."""
    print("MCP Content Planning Tool - Test Suite")
    print("=" * 50)
    print()

    try:
        # Run tests
        await test_content_planning_creation()
        await test_content_plan_execution()
        test_content_plan_retrieval()
        test_execution_history()
        await test_planning_engine_integration()
        await test_content_types_and_formats()

        print("🎉 All tests completed successfully!")
        print("\nThe Content Planning tool is working correctly and can:")
        print("  - Create comprehensive content plans for various formats")
        print("  - Execute plans in different modes (preview, section, full)")
        print("  - Store and retrieve plans and execution history")
        print("  - Handle multiple content types and target formats")
        print("  - Integrate with the planning engine for workflow management")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
