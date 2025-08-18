from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class FetchResult:
    url: str
    status_code: int
    headers: dict[str, str]
    elapsed_ms: float | None
    content_preview: str
    truncated: bool
    error: str | None


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not re.match(r"^https?://", url, flags=re.I):
        url = "https://" + url
    # encode spaces minimally for sanity
    return url.replace(" ", "%20")


async def fetch_url_content(url: str, max_preview_bytes: int = 8_192) -> FetchResult:
    """
    Fetch a URL over HTTP(S) and return a flattened result suitable for display/logging.
    """
    norm = _normalize_url(url)

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(norm)

        # elapsed can be a timedelta or absent; normalize defensively
        elapsed_attr: Any = getattr(resp, "elapsed", None)
        elapsed_ms: float | None = None
        if elapsed_attr is not None:
            try:
                # timedelta.total_seconds()
                elapsed_ms = float(elapsed_attr.total_seconds() * 1000.0)
            except Exception:
                try:
                    # sometimes libraries stash a raw float seconds
                    elapsed_ms = float(elapsed_attr) * 1000.0
                except Exception:
                    elapsed_ms = None

        raw = resp.text or ""
        preview = raw[:max_preview_bytes]
        truncated = len(raw) > len(preview)

        headers = {k.lower(): v for k, v in resp.headers.items()}
        return FetchResult(
            url=norm,
            status_code=int(resp.status_code),
            headers=headers,
            elapsed_ms=elapsed_ms,
            content_preview=preview,
            truncated=truncated,
            error=None,
        )
    except Exception as exc:
        return FetchResult(
            url=norm,
            status_code=0,
            headers={},
            elapsed_ms=None,
            content_preview="",
            truncated=False,
            error=str(exc),
        )


def flatten_fetch_result(res: FetchResult) -> dict[str, Any]:
    """
    Flatten FetchResult into a plain dict for tool output.
    """
    return {
        "url": res.url,
        "status_code": res.status_code,
        "headers_json": json.dumps(res.headers),
        "elapsed_ms": res.elapsed_ms,
        "content_preview": res.content_preview,
        "truncated": res.truncated,
        "error": res.error,
    }


# Tool adapter (kept simple for existing tests)
async def tool_fetch_url(url: str) -> dict[str, Any]:
    res = await fetch_url_content(url)
    return flatten_fetch_result(res)
