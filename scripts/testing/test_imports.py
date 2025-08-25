#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_core_imports():
    """Test core module imports."""
    print("Testing core imports...")

    try:
        import mcp_server_openai

        print("✅ mcp_server_openai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import mcp_server_openai: {e}")
        return False

    try:
        from mcp_server_openai import __main__

        print("✅ __main__ imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import __main__: {e}")
        return False

    try:
        from mcp_server_openai import server

        print("✅ server imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import server: {e}")
        return False

    try:
        from mcp_server_openai import health

        print("✅ health imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import health: {e}")
        return False

    try:
        from mcp_server_openai import security

        print("✅ security imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import security: {e}")
        return False

    try:
        from mcp_server_openai.api import http_server

        print("✅ api.http_server imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import api.http_server: {e}")
        return False

    try:
        from mcp_server_openai.api import streaming_http

        print("✅ api.streaming_http imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import api.streaming_http: {e}")
        return False

    try:
        from mcp_server_openai import enhanced_server

        print("✅ enhanced_server imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced_server: {e}")
        return False

    return True


def test_tool_imports():
    """Test tool module imports."""
    print("\nTesting tool imports...")

    try:
        from mcp_server_openai.tools.generators import enhanced_ppt_generator

        print("✅ tools.generators.enhanced_ppt_generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced_ppt_generator: {e}")
        return False

    try:
        from mcp_server_openai.tools.generators import enhanced_image_generator

        print("✅ tools.generators.enhanced_image_generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced_image_generator: {e}")
        return False

    try:
        from mcp_server_openai.tools.generators import enhanced_icon_generator

        print("✅ tools.generators.enhanced_icon_generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced_icon_generator: {e}")
        return False

    return True


def main():
    """Run all import tests."""
    print("Running import tests...\n")

    core_success = test_core_imports()
    tool_success = test_tool_imports()

    print(f"\n{'='*50}")
    print("IMPORT TEST RESULTS")
    print("=" * 50)

    if core_success and tool_success:
        print("🎉 All imports successful!")
        return 0
    else:
        print("❌ Some imports failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
