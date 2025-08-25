#!/usr/bin/env python3
"""
Test the voice endpoints on both servers.
"""

import asyncio
import io
import math
import struct
import wave

import httpx


def create_test_audio():
    """Create a simple test audio file (sine wave)."""
    # Audio parameters
    sample_rate = 16000
    duration = 2  # seconds
    frequency = 440  # Hz (A note)

    # Generate sine wave
    samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        sample = int(32767 * math.sin(2 * math.pi * frequency * t))
        samples.append(sample)

    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)

        # Write samples
        for sample in samples:
            wav_file.writeframes(struct.pack("<h", sample))

    buffer.seek(0)
    return buffer.getvalue()


async def test_voice_endpoints():
    """Test voice endpoints on both servers."""

    print("🎤 Testing Voice Endpoints")
    print("=" * 50)

    # Test servers
    servers = [
        {"name": "Streaming Server", "url": "http://localhost:8000"},
        {"name": "FastAPI Server", "url": "http://localhost:8001"},
    ]

    # Create test audio
    print("🎵 Creating test audio file...")
    test_audio = create_test_audio()
    print(f"✅ Created {len(test_audio)} bytes of test audio")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for server in servers:
            print(f"\n🔍 Testing {server['name']} ({server['url']})")
            print("-" * 40)

            # Test 1: Check if server is running
            try:
                response = await client.get(f"{server['url']}/health")
                if response.status_code == 200:
                    print("✅ Server is running")
                else:
                    print(f"❌ Server health check failed: {response.status_code}")
                    continue
            except Exception as e:
                print(f"❌ Server not accessible: {e}")
                continue

            # Test 2: Check server info for voice endpoints
            try:
                response = await client.get(f"{server['url']}/info")
                if response.status_code == 200:
                    info = response.json()
                    endpoints = info.get("endpoints", {})
                    voice_endpoints = [k for k in endpoints.keys() if "voice" in k]
                    if voice_endpoints:
                        print(f"✅ Voice endpoints found: {voice_endpoints}")
                    else:
                        print("❌ No voice endpoints found")
                        continue
                else:
                    print(f"❌ Info endpoint failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Info check failed: {e}")

            # Test 3: Text-to-Speech
            print("\n🗣️ Testing Text-to-Speech...")
            try:
                files = {"text": (None, "Hello, this is a test of the voice system")}
                response = await client.post(f"{server['url']}/api/v1/voice/speak", files=files)

                if response.status_code == 200:
                    print(f"✅ TTS Success! Received {len(response.content)} bytes of audio")
                    # Save audio file for verification
                    with open(f"test_tts_{server['name'].lower().replace(' ', '_')}.mp3", "wb") as f:
                        f.write(response.content)
                    print(f"💾 Saved audio to test_tts_{server['name'].lower().replace(' ', '_')}.mp3")
                else:
                    print(f"❌ TTS failed: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                print(f"❌ TTS exception: {e}")

            # Test 4: Speech-to-Text (with generated audio)
            print("\n👂 Testing Speech-to-Text...")
            try:
                files = {"audio": ("test.wav", test_audio, "audio/wav")}
                response = await client.post(f"{server['url']}/api/v1/voice/transcribe", files=files)

                if response.status_code == 200:
                    result = response.json()
                    transcribed_text = result.get("transcribed_text", "No text found")
                    print(f"✅ STT Success! Transcribed: '{transcribed_text}'")
                else:
                    print(f"❌ STT failed: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                print(f"❌ STT exception: {e}")

            # Test 5: Voice Content Creation
            print("\n📝 Testing Voice Content Creation...")
            try:
                files = {
                    "audio": ("test.wav", test_audio, "audio/wav"),
                    "content_type": (None, "article"),
                    "return_audio": (None, "false"),
                }
                response = await client.post(f"{server['url']}/api/v1/voice/content", files=files)

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Voice Content Creation Success!")
                    if "data" in result:
                        data = result["data"]
                        if "transcribed_prompt" in data:
                            print(f"   Transcribed: {data['transcribed_prompt'][:100]}...")
                        if "generated_content" in data:
                            print(f"   Content: {data['generated_content'][:100]}...")
                else:
                    print(f"❌ Voice Content failed: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                print(f"❌ Voice Content exception: {e}")

            print("-" * 40)


if __name__ == "__main__":
    asyncio.run(test_voice_endpoints())
