#!/usr/bin/env python3
"""
Start the FastAPI server with voice endpoints.

This script starts the FastAPI server (with voice endpoints) instead of the streaming server.
"""

import uvicorn

from src.mcp_server_openai.api.fastapi_server import app

if __name__ == "__main__":
    print("🎤 Starting FastAPI Server with Voice Endpoints...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🎯 Voice Endpoints:")
    print("   - POST /api/v1/voice/transcribe")
    print("   - POST /api/v1/voice/speak")
    print("   - POST /api/v1/voice/content")
    print("\n🚀 Starting server...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Different port to avoid conflict
        log_level="info",
        reload=False,
    )
