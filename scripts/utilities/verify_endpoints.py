#!/usr/bin/env python3
"""
Quick endpoint verification script.

This script quickly checks if all individual endpoints are accessible and responding.
"""

import asyncio
from typing import Any

import httpx

# Define all endpoints to test
ENDPOINTS: list[tuple[str, str, str, dict]] = [
    # Enhanced PPT Generator
    ("GET", "/api/v1/ppt/templates", "PPT Templates", {}),
    ("POST", "/api/v1/ppt/analyze", "PPT Analyze", {"content": "test"}),
    ("POST", "/api/v1/ppt/generate", "PPT Generate", {"notes": ["test"], "brief": "test"}),
    ("GET", "/api/v1/ppt/status/test", "PPT Status", {}),
    # Enhanced Document Generator
    ("GET", "/api/v1/document/templates", "Document Templates", {}),
    ("GET", "/api/v1/document/formats", "Document Formats", {}),
    ("POST", "/api/v1/document/generate", "Document Generate", {"content": "test", "output_format": "html"}),
    ("GET", "/api/v1/document/status/test", "Document Status", {}),
    # Enhanced Image Generator
    ("GET", "/api/v1/image/providers", "Image Providers", {}),
    ("POST", "/api/v1/image/generate", "Image Generate", {"prompt": "test"}),
    ("GET", "/api/v1/image/status/test", "Image Status", {}),
    # Enhanced Icon Generator
    ("GET", "/api/v1/icon/providers", "Icon Providers", {}),
    ("GET", "/api/v1/icon/search?q=test", "Icon Search", {}),
    ("POST", "/api/v1/icon/generate", "Icon Generate", {"query": "test"}),
    ("GET", "/api/v1/icon/status/test", "Icon Status", {}),
    # Enhanced Content Creator
    ("GET", "/api/v1/content/templates", "Content Templates", {}),
    ("POST", "/api/v1/content/create", "Content Create", {"title": "test", "content_type": "presentation"}),
    ("GET", "/api/v1/content/status/test", "Content Status", {}),
    # Unified Content Creator
    ("GET", "/api/v1/unified/formats", "Unified Formats", {}),
    ("POST", "/api/v1/unified/create", "Unified Create", {"brief": "test", "notes": ["test"]}),
    ("GET", "/api/v1/unified/status/test", "Unified Status", {}),
    # System Endpoints
    ("GET", "/health", "Health", {}),
    ("GET", "/info", "Info", {}),
    ("GET", "/metrics", "Metrics", {}),
    ("GET", "/usage", "Usage", {}),
    ("GET", "/mcp/sse", "SSE", {}),
    ("GET", "/stream", "Stream", {}),
]


async def verify_endpoint(
    client: httpx.AsyncClient, method: str, endpoint: str, description: str, data: dict
) -> dict[str, Any]:
    """Verify a single endpoint."""
    url = f"http://127.0.0.1:8000{endpoint}"

    try:
        if method.upper() == "GET":
            response = await client.get(url, timeout=10.0)
        elif method.upper() == "POST":
            response = await client.post(url, json=data, timeout=10.0)
        else:
            return {
                "description": description,
                "endpoint": endpoint,
                "method": method,
                "status": "error",
                "error": f"Unsupported method: {method}",
            }

        return {
            "description": description,
            "endpoint": endpoint,
            "method": method,
            "status": "success" if response.status_code < 400 else "error",
            "status_code": response.status_code,
            "response_size": len(response.content),
            "error": None if response.status_code < 400 else f"HTTP {response.status_code}",
        }

    except Exception as e:
        return {
            "description": description,
            "endpoint": endpoint,
            "method": method,
            "status": "error",
            "error": str(e),
            "status_code": None,
            "response_size": 0,
        }


async def verify_all_endpoints() -> None:
    """Verify all endpoints."""
    print("🔍 Verifying all endpoints...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        results = []

        for method, endpoint, description, data in ENDPOINTS:
            result = await verify_endpoint(client, method, endpoint, description, data)
            results.append(result)

            # Print result immediately
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"{status_icon} {description}: {result['status']}")

            if result["status"] == "error":
                print(f"   Error: {result['error']}")

        # Print summary
        print("\n" + "=" * 60)
        successful = sum(1 for r in results if r["status"] == "success")
        total = len(results)

        print(f"📊 SUMMARY: {successful}/{total} endpoints successful ({successful/total*100:.1f}%)")

        if successful < total:
            print("\n❌ Failed endpoints:")
            for result in results:
                if result["status"] == "error":
                    print(f"   {result['method']} {result['endpoint']}: {result['error']}")
        else:
            print("🎉 All endpoints are working correctly!")


async def main() -> None:
    """Main function."""
    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://127.0.0.1:8000/health")
            if response.status_code == 200:
                print("✅ Server is running and responding")
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure the server is running with:")
        print("   uv run uvicorn mcp_server_openai.streaming_http:app --host 0.0.0.0 --port 8000")
        return

    # Verify all endpoints
    await verify_all_endpoints()


if __name__ == "__main__":
    asyncio.run(main())
