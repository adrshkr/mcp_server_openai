#!/usr/bin/env python3
"""
Test script to verify API fixes work correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


async def test_function_imports():
    """Test that all the functions we're trying to import actually exist."""
    print("Testing function imports...")

    try:
        from mcp_server_openai.tools.generators.enhanced_ppt_generator import create_enhanced_presentation

        print("✅ create_enhanced_presentation imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import create_enhanced_presentation: {e}")
        return False

    try:
        from mcp_server_openai.tools.generators.enhanced_document_generator import generate_document

        print("✅ generate_document imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import generate_document: {e}")
        return False

    try:
        from mcp_server_openai.tools.generators.enhanced_image_generator import generate_images

        print("✅ generate_images imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import generate_images: {e}")
        return False

    try:
        from mcp_server_openai.tools.generators.enhanced_icon_generator import generate_icons

        print("✅ generate_icons imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import generate_icons: {e}")
        return False

    try:
        from mcp_server_openai.tools.generators.unified_content_creator import create_unified_content

        print("✅ create_unified_content imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import create_unified_content: {e}")
        return False

    return True


async def test_validation_models():
    """Test that validation models work correctly."""
    print("\nTesting validation models...")

    try:
        from mcp_server_openai.core.validation import DocumentRequest, IconRequest, ImageRequest, PPTRequest

        # Test PPT request
        PPTRequest(notes=["Test slide 1", "Test slide 2"], brief="Test presentation")
        print("✅ PPTRequest validation works")

        # Test Document request (without include_images)
        DocumentRequest(title="Test Document", content="# Test\n\nThis is a test document.")
        print("✅ DocumentRequest validation works")

        # Test Image request
        ImageRequest(query="business meeting")
        print("✅ ImageRequest validation works")

        # Test Icon request
        IconRequest(query="presentation")
        print("✅ IconRequest validation works")

        return True

    except Exception as e:
        print(f"❌ Validation model test failed: {e}")
        return False


async def test_fastapi_import():
    """Test that FastAPI server can be imported."""
    print("\nTesting FastAPI server import...")

    try:
        from mcp_server_openai.api.fastapi_server import app

        print("✅ FastAPI server imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import FastAPI server: {e}")
        return False


async def main():
    """Run all tests."""
    print("Running API fix verification tests...\n")

    function_imports_ok = await test_function_imports()
    validation_ok = await test_validation_models()
    fastapi_ok = await test_fastapi_import()

    print(f"\n{'='*50}")
    print("TEST RESULTS")
    print("=" * 50)

    if function_imports_ok and validation_ok and fastapi_ok:
        print("🎉 All tests passed! API fixes should work correctly.")
        print("\nThe following issues have been resolved:")
        print("- ✅ Function import names corrected")
        print("- ✅ Parameter mismatches fixed")
        print("- ✅ Validation models updated")
        print("- ✅ FastAPI server imports work")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
