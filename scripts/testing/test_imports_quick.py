#!/usr/bin/env python3
"""
Quick test to check if all imports work correctly after fixes.
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
        from mcp_server_openai.core.error_handler import APIError, UnifiedErrorHandler

        print("✅ error_handler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import error_handler: {e}")
        return False

    try:
        from mcp_server_openai.core.logging import get_logger

        print("✅ logging imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import logging: {e}")
        return False

    try:
        from mcp_server_openai.core.config import get_config

        print("✅ config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False

    try:
        from mcp_server_openai.core.validation import PPTRequest

        print("✅ validation imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import validation: {e}")
        return False

    return True


def test_api_imports():
    """Test API module imports."""
    print("\nTesting API imports...")

    try:
        from mcp_server_openai.api.fastapi_server import app

        print("✅ fastapi_server imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import fastapi_server: {e}")
        return False

    try:
        from mcp_server_openai.api.request_handlers import RequestParser

        print("✅ request_handlers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import request_handlers: {e}")
        return False

    return True


def main():
    """Run all import tests."""
    print("Running import tests after make check fixes...\n")

    core_success = test_core_imports()
    api_success = test_api_imports()

    print(f"\n{'='*50}")
    print("IMPORT TEST RESULTS")
    print("=" * 50)

    if core_success and api_success:
        print("🎉 All imports successful!")
        return 0
    else:
        print("❌ Some imports failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
