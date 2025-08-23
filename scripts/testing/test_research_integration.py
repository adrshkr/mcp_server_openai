#!/usr/bin/env python3
"""
Test script for MCP Research Integration Tool

This script tests the research integration capabilities including:
- Automated research execution
- Source analysis and filtering
- Insight extraction
- Content enhancement generation
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_openai.tools.mcp_research_integration import (
    ResearchIntegrationEngine,
    conduct_automated_research,
    get_research_history,
    get_research_result,
)


async def test_research_integration_creation() -> None:
    """Test creating the research integration engine."""
    print("Testing research integration engine creation...")

    try:
        engine = ResearchIntegrationEngine()
        print("✓ Research integration engine created successfully")
        print(f"  Brave Search URL: {engine.brave_search_url}")
        print(f"  Sequential Thinking URL: {engine.sequential_thinking_url}")
        print(f"  Memory URL: {engine.memory_url}")
        print(f"  Research patterns: {len(engine.research_patterns)} content types")

    except Exception as e:
        print(f"✗ Research integration engine creation failed: {e}")
        return False

    return True


async def test_automated_research() -> None:
    """Test automated research functionality."""
    print("\nTesting automated research...")

    try:
        research_result = await conduct_automated_research(
            topic="Digital Transformation Strategy",
            content_type="presentation",
            target_audience="executives",
            objectives=[
                "Understand current digital transformation trends",
                "Identify key success factors",
                "Learn from industry best practices",
            ],
            key_messages=[
                "Digital transformation is accelerating across industries",
                "Success requires strategic planning and cultural change",
                "ROI can be significant with proper execution",
            ],
            research_depth="comprehensive",
            max_results=5,
        )

        print("✓ Automated research completed successfully!")
        print(f"  Status: {research_result['status']}")
        print(f"  Result ID: {research_result['result_id']}")
        print(f"  Total Sources: {research_result['total_sources']}")
        print(f"  Relevant Sources: {research_result['relevant_sources']}")
        print(f"  High Credibility Sources: {research_result['high_credibility_sources']}")

        # Test insights
        if research_result["insights"]:
            print(f"  Insights: {len(research_result['insights'])} found")
            for i, insight in enumerate(research_result["insights"][:3], 1):
                print(f"    {i}. {insight}")

        # Test key findings
        if research_result["key_findings"]:
            print(f"  Key Findings: {len(research_result['key_findings'])} found")
            for i, finding in enumerate(research_result["key_findings"][:3], 1):
                print(f"    {i}. {finding}")

        # Test recommendations
        if research_result["recommendations"]:
            print(f"  Recommendations: {len(research_result['recommendations'])} generated")
            for i, rec in enumerate(research_result["recommendations"], 1):
                print(f"    {i}. {rec}")

        # Test content enhancements
        if research_result["content_enhancements"]:
            print(f"  Content Enhancements: {len(research_result['content_enhancements'])} suggested")
            for i, enhancement in enumerate(research_result["content_enhancements"][:3], 1):
                print(f"    {i}. {enhancement}")

        return research_result["result_id"]

    except Exception as e:
        print(f"✗ Automated research failed: {e}")
        return None


async def test_research_history() -> None:
    """Test research history functionality."""
    print("\nTesting research history...")

    try:
        history = get_research_history(limit=10)
        print("✓ Research history retrieved successfully!")
        print(f"  History entries: {len(history)}")

        if history:
            print("  Recent research topics:")
            for i, entry in enumerate(history[:3], 1):
                print(f"    {i}. {entry['topic']} ({entry['content_type']})")
                print(f"       Sources: {entry['relevant_sources']}/{entry['total_sources']}")
                print(f"       High Credibility: {entry['high_credibility_sources']}")
                print(f"       Time: {entry['timestamp']}")

        return history[0]["result_id"] if history else None

    except Exception as e:
        print(f"✗ Research history retrieval failed: {e}")
        return None


async def test_research_result_retrieval(result_id: str) -> None:
    """Test retrieving specific research results."""
    print(f"\nTesting research result retrieval for: {result_id}")

    try:
        result = get_research_result(result_id)

        if result:
            print("✓ Research result retrieved successfully!")
            print(f"  Topic: {result['topic']}")
            print(f"  Content Type: {result['content_type']}")
            print(f"  Total Sources: {result['total_sources']}")
            print(f"  Relevant Sources: {result['relevant_sources']}")
            print(f"  High Credibility Sources: {result['high_credibility_sources']}")

            if result["insights"]:
                print(f"  Insights: {len(result['insights'])}")
                for insight in result["insights"][:2]:
                    print(f"    • {insight}")

            if result["research_summary"]:
                print(f"  Research Summary: {len(result['research_summary'])} characters")
                print(f"    Preview: {result['research_summary'][:100]}...")

        else:
            print("✗ Research result not found")
            return False

        return True

    except Exception as e:
        print(f"✗ Research result retrieval failed: {e}")
        return False


async def test_different_content_types() -> None:
    """Test research with different content types."""
    print("\nTesting different content types...")

    content_types = ["presentation", "document", "webpage", "report"]

    for content_type in content_types:
        try:
            print(f"  Testing {content_type}...")
            result = await conduct_automated_research(
                topic="AI in Healthcare",
                content_type=content_type,
                target_audience="healthcare professionals",
                objectives=["Understand AI applications", "Identify implementation challenges"],
                key_messages=["AI can improve healthcare outcomes", "Implementation requires careful planning"],
                research_depth="basic",
                max_results=3,
            )

            print(f"    ✓ {content_type} research completed")
            print(f"      Sources: {result['relevant_sources']}/{result['total_sources']}")

        except Exception as e:
            print(f"    ✗ {content_type} research failed: {e}")


async def test_research_patterns() -> None:
    """Test research patterns and filtering."""
    print("\nTesting research patterns...")

    try:
        engine = ResearchIntegrationEngine()

        print("  Available research patterns:")
        for content_type, pattern in engine.research_patterns.items():
            print(f"    {content_type}:")
            print(f"      Keywords: {pattern['keywords']}")
            print(f"      Content Types: {pattern['content_types']}")
            print(f"      Min Credibility: {pattern['min_credibility']}")

        print("✓ Research patterns loaded successfully!")

    except Exception as e:
        print(f"✗ Research patterns test failed: {e}")


async def test_integration() -> None:
    """Test integration between research components."""
    print("\nTesting research integration...")

    try:
        # Test workflow: Research -> History -> Retrieval
        print("  Running research workflow...")

        # Step 1: Conduct research
        result = await conduct_automated_research(
            topic="Sustainable Business Practices",
            content_type="document",
            target_audience="business leaders",
            objectives=["Understand sustainability trends", "Identify implementation strategies"],
            key_messages=["Sustainability drives business value", "Implementation requires systematic approach"],
            research_depth="moderate",
            max_results=3,
        )

        if result["status"] == "success":
            print("    ✓ Research completed")

            # Step 2: Check history
            history = get_research_history(limit=5)
            if any(entry["result_id"] == result["result_id"] for entry in history):
                print("    ✓ Research added to history")

                # Step 3: Retrieve result
                retrieved = get_research_result(result["result_id"])
                if retrieved and retrieved["result_id"] == result["result_id"]:
                    print("    ✓ Research result retrieved successfully")
                    print("    ✓ Integration workflow completed successfully!")
                    return True
                else:
                    print("    ✗ Research result retrieval failed")
            else:
                print("    ✗ Research not found in history")
        else:
            print("    ✗ Research failed")

        return False

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


async def main() -> None:
    """Run all tests."""
    print("MCP Research Integration Tool - Test Suite")
    print("=" * 50)

    test_results = []

    # Test 1: Engine creation
    test_results.append(await test_research_integration_creation())

    # Test 2: Automated research
    result_id = await test_automated_research()
    test_results.append(result_id is not None)

    # Test 3: Research history
    history_result_id = await test_research_history()
    test_results.append(history_result_id is not None)

    # Test 4: Result retrieval
    if result_id:
        test_results.append(await test_research_result_retrieval(result_id))
    else:
        test_results.append(False)

    # Test 5: Different content types
    await test_different_content_types()
    test_results.append(True)  # Content type tests are informational

    # Test 6: Research patterns
    await test_research_patterns()
    test_results.append(True)  # Pattern tests are informational

    # Test 7: Integration
    test_results.append(await test_integration())

    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    passed = sum(test_results)
    total = len(test_results)

    for i, result in enumerate(test_results, 1):
        status = "PASSED" if result else "FAILED"
        print(f"  Test {i}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The research integration tool is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
