"""
Voice interface for MCP Server OpenAI.

Provides speech-to-text input and text-to-speech output capabilities
for hands-free content creation and interaction.
"""

import base64
import os
from typing import Any

import httpx
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from ..core.config import get_config
from ..core.error_handler import APIError
from ..core.logging import get_logger

# Initialize core systems
config = get_config()
logger = get_logger("voice_interface")


class VoiceInterface:
    """Voice interface for speech-to-text and text-to-speech operations."""

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")

    async def speech_to_text(self, audio_file: UploadFile) -> str:
        """Convert speech to text using OpenAI Whisper or Google Speech-to-Text."""
        if not audio_file:
            raise APIError("No audio file provided", code="MISSING_AUDIO", status_code=400)

        # Try OpenAI Whisper first
        if self.openai_key:
            try:
                return await self._whisper_transcribe(audio_file)
            except Exception as e:
                logger.warning(f"OpenAI Whisper failed: {e}")

        # Fallback to Google Speech-to-Text
        if self.google_key:
            try:
                return await self._google_speech_to_text(audio_file)
            except Exception as e:
                logger.warning(f"Google Speech-to-Text failed: {e}")

        raise APIError(
            "No speech-to-text service available. Please set OPENAI_API_KEY or GOOGLE_API_KEY",
            code="NO_STT_SERVICE",
            status_code=503,
        )

    async def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        """Convert text to speech using OpenAI TTS or Google Text-to-Speech."""
        if not text.strip():
            raise APIError("No text provided", code="MISSING_TEXT", status_code=400)

        # Try OpenAI TTS first
        if self.openai_key:
            try:
                return await self._openai_text_to_speech(text, voice)
            except Exception as e:
                logger.warning(f"OpenAI TTS failed: {e}")

        # Fallback to Google Text-to-Speech
        if self.google_key:
            try:
                return await self._google_text_to_speech(text)
            except Exception as e:
                logger.warning(f"Google TTS failed: {e}")

        raise APIError(
            "No text-to-speech service available. Please set OPENAI_API_KEY or GOOGLE_API_KEY",
            code="NO_TTS_SERVICE",
            status_code=503,
        )

    async def _whisper_transcribe(self, audio_file: UploadFile) -> str:
        """Transcribe audio using OpenAI Whisper."""
        # Read audio file content
        audio_content = await audio_file.read()

        # Create form data for multipart upload
        files = {
            "file": (audio_file.filename or "audio.wav", audio_content, audio_file.content_type or "audio/wav"),
            "model": (None, "whisper-1"),
            "language": (None, "en"),  # Auto-detect or specify language
        }

        headers = {"Authorization": f"Bearer {self.openai_key}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)

            if response.status_code == 200:
                data = response.json()
                return data.get("text", "").strip()
            else:
                raise APIError(f"Whisper API error: {response.status_code} - {response.text}")

    async def _google_speech_to_text(self, audio_file: UploadFile) -> str:
        """Transcribe audio using Google Speech-to-Text."""
        audio_content = await audio_file.read()
        audio_base64 = base64.b64encode(audio_content).decode()

        payload = {
            "config": {
                "encoding": "WEBM_OPUS",  # Adjust based on audio format
                "sampleRateHertz": 16000,
                "languageCode": "en-US",
                "enableAutomaticPunctuation": True,
            },
            "audio": {"content": audio_base64},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://speech.googleapis.com/v1/speech:recognize?key={self.google_key}", json=payload
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results and results[0].get("alternatives"):
                    return results[0]["alternatives"][0].get("transcript", "").strip()
                return ""
            else:
                raise APIError(f"Google Speech-to-Text error: {response.status_code} - {response.text}")

    async def _openai_text_to_speech(self, text: str, voice: str) -> bytes:
        """Generate speech using OpenAI TTS."""
        payload = {
            "model": "tts-1",
            "input": text[:4000],  # Limit text length
            "voice": voice,
            "response_format": "mp3",
        }

        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)

            if response.status_code == 200:
                return response.content
            else:
                raise APIError(f"OpenAI TTS error: {response.status_code} - {response.text}")

    async def _google_text_to_speech(self, text: str) -> bytes:
        """Generate speech using Google Text-to-Speech."""
        payload = {
            "input": {"text": text[:5000]},  # Limit text length
            "voice": {"languageCode": "en-US", "name": "en-US-Neural2-F", "ssmlGender": "FEMALE"},
            "audioConfig": {"audioEncoding": "MP3", "speakingRate": 1.0, "pitch": 0.0},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.google_key}", json=payload
            )

            if response.status_code == 200:
                data = response.json()
                audio_base64 = data.get("audioContent", "")
                return base64.b64decode(audio_base64)
            else:
                raise APIError(f"Google TTS error: {response.status_code} - {response.text}")


# Global voice interface instance
voice_interface = VoiceInterface()


async def process_voice_content_request(audio_file: UploadFile, content_type: str = "article") -> dict[str, Any]:
    """Process voice input for content creation."""
    try:
        # Convert speech to text
        logger.info("Converting speech to text")
        prompt = await voice_interface.speech_to_text(audio_file)

        if not prompt:
            raise APIError("Could not transcribe audio", code="TRANSCRIPTION_FAILED", status_code=400)

        logger.info(f"Transcribed prompt: {prompt[:100]}...")

        # Generate content using the free content creator
        from ..tools.generators.free_content_creator import create_content

        result = await create_content(
            prompt=prompt,
            content_type=content_type,
            max_tokens=2000,
            tone="professional",
            audience="general",
            include_research=True,
            language="en",
        )

        # Convert result to speech
        logger.info("Converting result to speech")
        content_text = getattr(result, "content", str(result))
        audio_data = await voice_interface.text_to_speech(content_text)

        return {
            "transcribed_prompt": prompt,
            "generated_content": content_text,
            "audio_response": base64.b64encode(audio_data).decode(),
            "content_type": content_type,
        }

    except Exception as e:
        logger.error(f"Voice content processing failed: {e}")
        raise


async def create_audio_stream(text: str, voice: str = "alloy") -> StreamingResponse:
    """Create streaming audio response."""
    try:
        audio_data = await voice_interface.text_to_speech(text, voice)

        def generate():
            yield audio_data

        return StreamingResponse(
            generate(), media_type="audio/mpeg", headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"Audio streaming failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
