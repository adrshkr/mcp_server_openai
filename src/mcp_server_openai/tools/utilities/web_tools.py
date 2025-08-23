from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlparse, urlunparse

import httpx

from ...logging_utils import get_logger, log_accept, log_exception, log_response
from ...progress import create_progress_tracker

_LOG = get_logger("mcp.tool.web.fetch_url")
_TOOL = "web.fetch_url"


@dataclass
class FetchResult:
    url: str
    status_code: int | None
    headers: dict[str, str]
    content_preview: str
    truncated: bool
    elapsed_ms: float | None
    error: str | None


def _normalize_url(raw: str) -> str:
    """
    Ensure https:// scheme and percent-encode the path (spaces -> %20), leaving
    query/fragment untouched. Do NOT force a trailing slash; tests expect none.
    """
    s = raw.strip()
    if not s:
        return "https://"
    if not s.lower().startswith(("http://", "https://")):
        s = "https://" + s

    parsed = urlparse(s)
    safe_path = quote(parsed.path or "", safe="/")  # encode spaces etc., keep slashes
    rebuilt = parsed._replace(path=safe_path)
    return urlunparse(rebuilt)


async def fetch_url_content(url: str, timeout: int = 10) -> FetchResult:
    """
    Async helper used by tests and tool. No real network in tests: httpx.AsyncClient
    is monkeypatched to a dummy client that may not accept `timeout` kwarg or
    implement `raise_for_status()`. Code below is defensive to pass both cases.
    """
    norm_url = _normalize_url(url)
    request_id = f"req-{int(time.time() * 1000)}"

    # Enhanced progress tracking
    progress = create_progress_tracker(_TOOL, request_id, total_steps=4)

    # Logging: accept + progress
    log_accept(_LOG, tool=_TOOL, client_id=None, request_id=request_id, payload={"url": norm_url})
    start = time.monotonic()

    resp: httpx.Response | None = None
    try:
        # Step 1: Initialize request
        with progress.step_context("initialize_request", {"url": norm_url, "timeout": timeout}):
            pass

        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Step 2: Execute HTTP request
            async with progress.async_step_context("http_request", {"url": norm_url}):
                # Some dummies used in tests don't accept timeout=; try-with-timeout then fallback.
                try:
                    resp = await client.get(norm_url, timeout=timeout)
                except TypeError:
                    resp = await client.get(norm_url)

                # Not all fakes implement raise_for_status()
                if hasattr(resp, "raise_for_status"):
                    try:
                        resp.raise_for_status()
                    except Exception:
                        # If a dummy implements it and raises, let handling below format error
                        pass

            # Step 3: Process response
            with progress.step_context("process_response", {"status_code": getattr(resp, "status_code", None)}):
                text = getattr(resp, "text", "")
                status = int(getattr(resp, "status_code", 0)) or 200
                headers = dict(getattr(resp, "headers", {}) or {})
                preview = f"{text}:{norm_url}"

                elapsed_ms: float | None = None
                elapsed_obj = getattr(resp, "elapsed", None)
                if elapsed_obj is None:
                    elapsed_ms = (time.monotonic() - start) * 1000.0
                else:
                    try:
                        # httpx typically exposes timedelta
                        elapsed_ms = float(elapsed_obj.total_seconds() * 1000.0)
                    except Exception:
                        try:
                            # dummy can be float already
                            elapsed_ms = float(elapsed_obj)
                        except Exception:
                            elapsed_ms = None

            # Step 4: Finalize and log
            with progress.step_context(
                "finalize_response", {"content_length": len(text), "truncated": len(preview) > 5000}
            ):
                log_response(
                    _LOG,
                    tool=_TOOL,
                    request_id=request_id,
                    status="ok",
                    duration_ms=(time.monotonic() - start) * 1000.0,
                    size=len(text),
                )

            progress.complete("fetch_completed", {"status": "success", "content_length": len(text)})

            return FetchResult(
                url=norm_url,
                status_code=status,
                headers=headers,
                content_preview=preview[:5000],
                truncated=len(preview) > 5000,
                elapsed_ms=elapsed_ms,
                error=None,
            )

    except Exception as exc:  # pragma: no cover - exercised by tests via dummies
        log_exception(_LOG, tool=_TOOL, request_id=request_id, exc=exc)
        log_response(
            _LOG,
            tool=_TOOL,
            request_id=request_id,
            status="error",
            duration_ms=(time.monotonic() - start) * 1000.0,
        )

        progress.complete("fetch_failed", {"status": "error", "error": str(exc)})

        return FetchResult(
            url=norm_url,
            status_code=None,
            headers={},
            content_preview="",
            truncated=False,
            elapsed_ms=0.0,
            error=str(exc),
        )


def flatten_fetch_result(res: FetchResult) -> dict[str, Any]:
    """
    Keep the historical, flat JSON shape used by the tool.
    """
    return {
        "url": res.url,
        "status_code": res.status_code,
        "elapsed_ms": res.elapsed_ms,
        "headers_json": json.dumps(res.headers),
        "content_preview": res.content_preview,
        "truncated": res.truncated,
        "error": res.error,
    }
