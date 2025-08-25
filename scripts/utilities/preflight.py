#!/usr/bin/env python3
"""
Preflight checks: Black format -> Ruff lint.
Skips missing paths with a warning. Targets src/mcp_server_openai.
"""

import os
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 encoding for Windows
if os.name == "nt":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

REQUESTED_PATHS = ["src/mcp_server_openai", "tests"]


def run(desc: str, cmd: list[str], cwd: Path) -> None:
    print(f"{BLUE}[PRE-FLIGHT]{RESET} {desc}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=cwd)
        print(f"{GREEN}[OK] {desc}{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[FAIL] {desc} failed. Aborting.{RESET}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        sys.exit(e.returncode)


def main() -> None:
    root = (Path(__file__).resolve().parent).parent.parent

    existing_paths = []
    for p in REQUESTED_PATHS:
        path_obj = root / p
        if path_obj.exists():
            existing_paths.append(p)
        else:
            print(f"{YELLOW}[SKIP] Missing path: {p}{RESET}")

    if not existing_paths:
        print(f"{RED}[FAIL] No valid paths to check. Aborting preflight.{RESET}")
        sys.exit(1)

    uv_prefix = ["env", "UV_CACHE_DIR=.uv-cache", "UV_PIP_INDEX_URL=", "UV_LINK_MODE=copy", "uv", "run"]
    black_cmd = [*uv_prefix, "black"]
    if (root / "black_two_space.py").exists():
        black_cmd = [*uv_prefix, "python", "black_two_space.py"]

    # Run Black in single-process mode to avoid sandboxed socket usage
    # As a fallback in restricted sandboxes, disable multiprocessing via env
    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    env["BLACK_NUM_WORKERS"] = "1"

    def run_env(desc, args):
        print(f"{BLUE}[PRE-FLIGHT]{RESET} {desc}...")
        try:
            subprocess.run(args, check=True, capture_output=True, text=True, cwd=root, env=env)
            print(f"{GREEN}[OK] {desc}{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{RED}[FAIL] {desc} failed. Aborting.{RESET}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            sys.exit(e.returncode)

    run_env("Black dry-run (diff)", [*black_cmd, "--workers", "1", "--diff", "--color", *existing_paths])
    run_env("Black auto-format", [*black_cmd, "--workers", "1", *existing_paths])
    run_env("Ruff lint", [*uv_prefix, "ruff", "check", "--fix", *existing_paths])

    print(f"\n{GREEN}[SUCCESS] All preflight checks passed!{RESET}")


if __name__ == "__main__":
    main()
