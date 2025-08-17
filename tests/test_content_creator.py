import os
import shutil

from mcp_server_openai.tools import content_creator

def test_ppt_generation_basic(tmp_path):
  client = "Acme"
  project = "Q3"
  src = ["Key result 1", "Key result 2", "Key result 3"]
  brief = "Create a client-facing deck focused on Q3 highlights and next steps."

  # run internal helpers to avoid MCP SDK dependency
  outline = content_creator._heuristic_outline(brief, src, num_slides=3)
  prs = content_creator._create_ppt_from_outline(outline)

  # save under a temp output root
  out_root = tmp_path / "output"
  os.makedirs(out_root, exist_ok=True)
  # monkeypatch the output dir function
  orig = content_creator._ensure_output_dir
  content_creator._ensure_output_dir = lambda c,p: str(out_root / content_creator._safe_name(c) / content_creator._safe_name(p))  # noqa

  try:
    path = content_creator._save_ppt(prs, client, project)
    assert os.path.exists(path)
  finally:
    content_creator._ensure_output_dir = orig

  # cleanup is automatic via tmp_path