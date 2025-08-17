#!/usr/bin/env python
"""
Call an MCP tool by reading params from a JSON file and spawning the Inspector CLI.

Usage:
  uv run python scripts/call_tool.py content.create params.json
  uv run python scripts/call_tool.py web.fetch_url params.json \
      --server-spec src/mcp_server_openai/server.py:app

Tips (Windows):
  - If 'npx' isn't found, set NPX_PATH to the full path, e.g.:
      setx NPX_PATH "C:\\Program Files\\nodejs\\npx.cmd"
    then open a NEW terminal and run again.
"""
import argparse, json, shlex, subprocess, sys, os
from pathlib import Path
from typing import Dict, Any

def build_args_from_json(d: Dict[str, object]) -> list[str]:
  out: list[str] = []
  for k, v in d.items():
    if isinstance(v, (dict, list)):
      val = json.dumps(v, ensure_ascii=False)
    elif isinstance(v, bool):
      val = "true" if v else "false"
    else:
      val = str(v)
    out += ["--tool-arg", f"{k}={val}"]
  return out

def find_npx() -> str:
  # 1) explicit override
  override = os.environ.get("NPX_PATH")
  if override and Path(override).exists():
    return override

  # 2) platform-aware search
  import shutil
  found = shutil.which("npx")
  if found:
    return found

  # 3) common Windows locations
  if os.name == "nt":
    home = Path.home()
    candidates = [
      home / "AppData" / "Roaming" / "npm" / "npx.cmd",
      Path(r"C:\Program Files\nodejs\npx.cmd"),
      Path(r"C:\Program Files (x86)\nodejs\npx.cmd"),
    ]
    for c in candidates:
      if c.exists():
        return str(c)

  raise FileNotFoundError("npx not found. Set NPX_PATH to full path of npx(.cmd).")

def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("tool", help="Tool name, e.g. content.create")
  ap.add_argument("json_path", help="Path to params JSON")
  ap.add_argument("--server-spec", default="src/mcp_server_openai/server.py:app",
                  help="FILE_SPEC or MODULE:OBJECT (default: src/.../server.py:app)")
  args = ap.parse_args()

  params_path = Path(args.json_path)
  if not params_path.exists():
    print(f"Params file not found: {params_path}", file=sys.stderr)
    return 2
  try:
    payload = json.loads(params_path.read_text(encoding="utf-8"))
  except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}", file=sys.stderr)
    return 2

  npx = None
  try:
    npx = find_npx()
  except FileNotFoundError as e:
    print(f"Error: {e}", file=sys.stderr)
    print("Hint: On Windows, try one of:", file=sys.stderr)
    print("  C:\\Program Files\\nodejs\\npx.cmd", file=sys.stderr)
    print("  %USERPROFILE%\\AppData\\Roaming\\npm\\npx.cmd", file=sys.stderr)
    return 127

  # Build command
  # Default path-based server spec (no need to import package)
  if args.server_spec == "src/mcp_server_openai/server.py:app":
    cmd = [
      npx, "@modelcontextprotocol/inspector", "--cli",
      "uv", "run", "python", "-c", "import mcp_server_openai.server as s; s.app.run()",
      "--method", "tools/call",
      "--tool-name", args.tool,
    ] + build_args_from_json(payload)
  else:
    # Use given FILE_SPEC or MODULE:OBJECT directly
    cmd = [
      npx, "@modelcontextprotocol/inspector", "--cli",
      args.server_spec,
      "--method", "tools/call",
      "--tool-name", args.tool,
    ] + build_args_from_json(payload)

  print("$ " + " ".join(shlex.quote(str(c)) for c in cmd))
  try:
    proc = subprocess.run(cmd, check=False)
    return proc.returncode
  except FileNotFoundError:
    print("Error: could not execute npx. Ensure NPX_PATH is set and points to npx(.cmd).", file=sys.stderr)
    return 127

if __name__ == "__main__":
  raise SystemExit(main())