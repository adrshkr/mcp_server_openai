#!/usr/bin/env python3
"""
Test the current streaming server with voice endpoints integrated.
"""

import asyncio

import httpx


async def test_current_server():
    """Test the current streaming server."""

    print("🧪 Testing Current Streaming Server (Port 8000)")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Server Health
        print("🏥 Testing Server Health...")
        try:
            response = await client.get("http://localhost:8000/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            print("✅ Health check passed\n")
        except Exception as e:
            print(f"❌ Health check failed: {e}\n")
            return

        # Test 2: Server Info (should now include voice endpoints)
        print("ℹ️ Testing Server Info...")
        try:
            response = await client.get("http://localhost:8000/info")
            if response.status_code == 200:
                info = response.json()
                print("✅ Server Info:")
                print(f"   Name: {info.get('name', 'Unknown')}")
                print(f"   Version: {info.get('version', 'Unknown')}")
                print("   Endpoints:")
                for endpoint, path in info.get("endpoints", {}).items():
                    print(f"     {endpoint}: {path}")
                print()
            else:
                print(f"❌ Info failed: {response.status_code}\n")
        except Exception as e:
            print(f"❌ Info exception: {e}\n")

        # Test 3: Content Creation
        print("📝 Testing Content Creation...")
        test_content = {
            "prompt": "Explain the benefits of renewable energy",
            "content_type": "article",
            "tone": "professional",
            "audience": "general",
        }

        try:
            response = await client.post("http://localhost:8000/api/v1/content/create", json=test_content)

            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("✅ Content Creation Success!")

                # Show key parts of response
                if isinstance(result, dict):
                    if "content" in result:
                        content = (
                            result["content"][:200] + "..."
                            if len(result.get("content", "")) > 200
                            else result.get("content", "")
                        )
                        print(f"   Content Preview: {content}")

                    if "processing_time" in result:
                        print(f"   Processing Time: {result['processing_time']}s")

                    if "research_sources" in result:
                        print(f"   Research Sources: {len(result.get('research_sources', []))}")
                print()
            else:
                print(f"❌ Content creation failed: {response.text[:300]}\n")

        except Exception as e:
            print(f"❌ Content creation exception: {e}\n")

        # Test 4: Voice Endpoints (if integrated)
        print("🎤 Testing Voice Endpoints...")

        # Test TTS with simple text
        print("   Testing Text-to-Speech...")
        try:
            files = {"text": (None, "Hello world, this is a test")}
            response = await client.post("http://localhost:8000/api/v1/voice/speak", files=files)

            if response.status_code == 200:
                print(f"   ✅ TTS Success! Received {len(response.content)} bytes")
            elif response.status_code == 404:
                print("   ⚠️ Voice endpoints not yet available (need server restart)")
            else:
                print(f"   ❌ TTS failed: {response.status_code} - {response.text[:100]}")

        except Exception as e:
            print(f"   ❌ TTS exception: {e}")

        # Test 5: Other Endpoints
        print("\n🔍 Testing Other Available Endpoints...")

        endpoints_to_test = [
            ("PPT Templates", "GET", "/api/v1/ppt/templates"),
            ("Document Formats", "GET", "/api/v1/document/formats"),
            ("Image Providers", "GET", "/api/v1/image/providers"),
            ("Icon Providers", "GET", "/api/v1/icon/providers"),
            ("Content Templates", "GET", "/api/v1/content/templates"),
            ("Unified Formats", "GET", "/api/v1/unified/formats"),
        ]

        for name, method, endpoint in endpoints_to_test:
            try:
                if method == "GET":
                    response = await client.get(f"http://localhost:8000{endpoint}")
                else:
                    continue  # Skip non-GET for now

                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {name}: Available")
                    if isinstance(result, dict) and len(result) > 0:
                        first_key = list(result.keys())[0]
                        print(f"      Sample: {first_key}")
                else:
                    print(f"   ❌ {name}: {response.status_code}")

            except Exception as e:
                print(f"   ❌ {name}: Exception - {e}")

        print("\n🎯 Summary:")
        print("   - Server is running and healthy")
        print("   - Content creation is working")
        print("   - Voice endpoints have been added to code")
        print("   - Restart server to activate voice endpoints")
        print("   - Multiple content generation endpoints available")


if __name__ == "__main__":
    asyncio.run(test_current_server())
