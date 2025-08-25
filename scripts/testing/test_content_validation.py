#!/usr/bin/env python3
"""
Test script for the MCP Content Validation Tool.

This script tests the content validation functionality by running a sample validation
and displaying the results.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mcp_server_openai.tools.mcp_content_validation import validate_content_quality


async def test_content_validation():
    """Test the content validation tool with sample content."""

    print("Testing MCP Content Validation Tool")
    print("=" * 50)

    # Sample content for testing
    sample_content = """
    # AI in Healthcare: Opportunities and Challenges

    Artificial Intelligence (AI) is transforming healthcare delivery across the globe.
    This presentation explores the current state of AI applications in healthcare,
    identifies key challenges and opportunities, and provides actionable recommendations
    for successful implementation.

    ## Current Applications

    AI is currently being used in:
    - Medical imaging and diagnostics
    - Drug discovery and development
    - Patient care and monitoring
    - Administrative tasks and scheduling

    ## Key Challenges

    Despite its potential, AI implementation faces several challenges:
    - Data privacy and security concerns
    - Regulatory compliance requirements
    - Integration with existing systems
    - Staff training and adoption

    ## Recommendations

    To successfully implement AI in healthcare:
    1. Start with pilot projects
    2. Ensure robust data governance
    3. Invest in staff training
    4. Monitor and evaluate outcomes
    """

    print("Sample Content:")
    print(sample_content)
    print("\n" + "=" * 50)

    try:
        print("Running content validation...")

        validation_result = await validate_content_quality(
            content=sample_content,
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

        print("Validation completed successfully!")
        print(f"Status: {validation_result['status']}")
        print(f"Validation ID: {validation_result['validation_id']}")
        print(f"Overall Score: {validation_result['overall_score']:.2f}")
        print(f"Passed Rules: {validation_result['passed_rules']}")
        print(f"Failed Rules: {validation_result['failed_rules']}")
        print(f"Warning Rules: {validation_result['warning_rules']}")

        # Display content metrics
        metrics = validation_result["content_metrics"]
        print("\nContent Metrics:")
        print(f"  Word Count: {metrics['word_count']}")
        print(f"  Sentence Count: {metrics['sentence_count']}")
        print(f"  Paragraph Count: {metrics['paragraph_count']}")
        print(f"  Readability Score: {metrics['readability_score']:.2f}")
        print(f"  Content Structure Score: {metrics['content_structure_score']:.2f}")
        print(f"  Visual Element Score: {metrics['visual_element_score']:.2f}")
        print(f"  Accessibility Score: {metrics['accessibility_score']:.2f}")
        print(f"  SEO Score: {metrics['seo_score']:.2f}")
        print(f"  Overall Quality Score: {metrics['overall_quality_score']:.2f}")

        # Display validation results
        print(f"\nValidation Results ({len(validation_result['validation_results'])}):")
        for result in validation_result["validation_results"]:
            print(f"  {result['rule_name']}: {result['status']} (Score: {result['score']:.2f})")
            print(f"    {result['message']}")
            if result["suggestions"]:
                for suggestion in result["suggestions"]:
                    print(f"    - {suggestion}")
            print()

        # Display recommendations
        print(f"Recommendations ({len(validation_result['recommendations'])}):")
        for rec in validation_result["recommendations"]:
            print(f"  - {rec}")

        print(f"\nTimestamp: {validation_result['timestamp']}")

        return True

    except Exception as e:
        print(f"Error during validation: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_validation_with_custom_rules():
    """Test validation with custom rules and thresholds."""

    print("\n" + "=" * 50)
    print("Testing Custom Validation Rules")
    print("=" * 50)

    sample_content = """
    # Quick Overview

    This is a brief document with minimal content.
    It has some basic structure but limited depth.
    """

    try:
        print("Running validation with custom rules...")

        validation_result = await validate_content_quality(
            content=sample_content,
            content_type="document",
            target_audience="General audience",
            objectives=["Provide overview"],
            key_messages=["Basic information"],
            validation_rules=["readability", "completeness"],
            custom_thresholds={"readability": 0.6, "completeness": 0.5},
            include_suggestions=True,
        )

        print("Custom validation completed!")
        print(f"Status: {validation_result['status']}")
        print(f"Overall Score: {validation_result['overall_score']:.2f}")

        return True

    except Exception as e:
        print(f"Error during custom validation: {e}")
        return False


async def main():
    """Main test function."""
    print("MCP Content Validation Tool Test Suite")
    print("=" * 60)

    # Test basic validation
    success1 = await test_content_validation()

    # Test custom rules
    success2 = await test_validation_with_custom_rules()

    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print(f"Basic Validation: {'PASSED' if success1 else 'FAILED'}")
    print(f"Custom Rules: {'PASSED' if success2 else 'FAILED'}")

    if success1 and success2:
        print("\n🎉 All tests passed! The content validation tool is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
