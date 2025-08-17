#!/usr/bin/env python3
"""
Preflight checks: Black format -> Ruff lint.
Skips missing paths with a warning. Targets src/mcp_server_openai.
"""
import subprocess
import sys
from pathlib import Path

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
    print(f"{GREEN}✔ {desc} OK{RESET}")
  except subprocess.CalledProcessError as e:
    print(f"{RED}✘ {desc} failed. Aborting.{RESET}")
    if e.stdout: print(e.stdout)
    if e.stderr: print(e.stderr)
    sys.exit(e.returncode)

def main() -> None:
  root = (Path(__file__).resolve().parent).parent

  existing_paths = []
  for p in REQUESTED_PATHS:
    path_obj = root / p
    if path_obj.exists():
      existing_paths.append(p)
    else:
      print(f"{YELLOW}⚠ Skipping missing path: {p}{RESET}")

  if not existing_paths:
    print(f"{RED}✘ No valid paths to check. Aborting preflight.{RESET}")
    sys.exit(1)

  black_cmd = ["uv", "run", "black"]
  if (root / "black_two_space.py").exists():
    black_cmd = ["uv", "run", "python", "black_two_space.py"]

  run("Black dry-run (diff)", [*black_cmd, "--diff", "--color", *existing_paths], root)
  run("Black auto-format", [*black_cmd, *existing_paths], root)
  run("Ruff lint", ["uv", "run", "ruff", "check", "--fix", *existing_paths], root)

  print(f"\n{GREEN}✅ All preflight checks passed!{RESET}")

if __name__ == "__main__":
  main()
