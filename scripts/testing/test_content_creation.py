#!/usr/bin/env python3
"""
Test the content creation endpoint on the streaming server.
"""

import asyncio
import json

import httpx


async def test_content_creation():
    """Test the content creation endpoint."""

    print("🧪 Testing Content Creation on Streaming Server (Port 8000)")
    print("=" * 60)

    # Test data
    test_requests = [
        {
            "name": "Simple Article",
            "data": {
                "prompt": "Explain artificial intelligence in simple terms",
                "content_type": "article",
                "tone": "professional",
                "audience": "general",
            },
        },
        {
            "name": "Blog Post",
            "data": {
                "brief": "Benefits of remote work for productivity",
                "content_type": "blog",
                "tone": "casual",
                "audience": "professionals",
            },
        },
        {
            "name": "Presentation Outline",
            "data": {
                "prompt": "Machine learning fundamentals for beginners",
                "content_type": "presentation",
                "tone": "educational",
                "audience": "students",
            },
        },
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_requests:
            print(f"\n📝 Testing: {test['name']}")
            print(f"Request: {json.dumps(test['data'], indent=2)}")

            try:
                response = await client.post("http://localhost:8000/api/v1/content/create", json=test["data"])

                print(f"Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Success!")

                    # Show key parts of the response
                    if isinstance(result, dict):
                        if "content" in result:
                            content = (
                                result["content"][:200] + "..."
                                if len(result.get("content", "")) > 200
                                else result.get("content", "")
                            )
                            print(f"Content Preview: {content}")

                        if "processing_time" in result:
                            print(f"Processing Time: {result['processing_time']}s")

                        if "research_sources" in result:
                            print(f"Research Sources: {len(result.get('research_sources', []))}")

                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:300]}")

            except Exception as e:
                print(f"❌ Exception: {e}")

            print("-" * 40)


if __name__ == "__main__":
    asyncio.run(test_content_creation())
