#!/usr/bin/env python3
"""
Run make check components manually to diagnose issues.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and capture output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent, timeout=300)

        if result.stdout:
            print("STDOUT:")
            print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Return code: {result.returncode}")

        if result.returncode != 0:
            print(f"❌ {description} FAILED")
            return False
        else:
            print(f"✅ {description} PASSED")
            return True

    except subprocess.TimeoutExpired:
        print(f"❌ {description} TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ {description} ERROR: {e}")
        return False


def main():
    """Run all make check components."""
    print("Running make check components manually...")

    # Change to project root
    os.chdir(Path(__file__).parent)

    results = []

    # 1. Black formatting check
    results.append(
        run_command(
            ["python", "-m", "black", "--diff", "--color", "src/mcp_server_openai", "tests"], "Black formatting check"
        )
    )

    # 2. Black auto-format
    results.append(run_command(["python", "-m", "black", "src/mcp_server_openai", "tests"], "Black auto-format"))

    # 3. Ruff linting
    results.append(
        run_command(["python", "-m", "ruff", "check", "--fix", "src/mcp_server_openai", "tests"], "Ruff linting")
    )

    # 4. MyPy type checking (core files)
    core_files = [
        "src/mcp_server_openai/__init__.py",
        "src/mcp_server_openai/__main__.py",
        "src/mcp_server_openai/server.py",
        "src/mcp_server_openai/health.py",
        "src/mcp_server_openai/security.py",
        "src/mcp_server_openai/api/http_server.py",
    ]

    results.append(
        run_command(["python", "-m", "mypy", "--config-file", "config/mypy.ini"] + core_files, "MyPy type checking")
    )

    # 5. Fast tests
    results.append(
        run_command(
            [
                "python",
                "-m",
                "pytest",
                "-q",
                "--maxfail=1",
                "--durations=10",
                "-m",
                "not slow and not integration and not e2e and not network",
                "tests",
            ],
            "Fast tests",
        )
    )

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All checks passed!")
        return 0
    else:
        print("❌ Some checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
