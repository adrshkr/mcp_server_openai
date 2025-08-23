#!/usr/bin/env python3
"""
Startup script for MCP Server OpenAI with pre-validation and optimization.

Performs quick validation and setup before starting the main server to ensure
fast and reliable startup in production environments like GCP Cloud Run.
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mcp_server_openai.security import validate_configuration, get_log_level


def setup_logging():
    """Configure logging for startup."""
    log_level = get_log_level()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


async def pre_validate():
    """Pre-validate configuration and dependencies."""
    logger = setup_logging()
    start_time = time.time()
    
    logger.info("🚀 Starting MCP Server OpenAI...")
    
    try:
        # Validate configuration
        logger.info("🔍 Validating configuration...")
        validate_configuration()
        
        # Import critical modules to catch import errors early
        logger.info("📦 Validating critical imports...")
        from mcp_server_openai.http_server import app
        from mcp_server_openai.health import health_checker
        
        # Test health checker initialization
        logger.info("🏥 Testing health check system...")
        await health_checker.startup_check()
        
        startup_time = time.time() - start_time
        logger.info(f"✅ Startup validation completed in {startup_time:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Startup validation failed: {e}")
        return False


def main():
    """Main startup function."""
    # Run pre-validation
    if not asyncio.run(pre_validate()):
        sys.exit(1)
    
    # Get server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    workers = int(os.getenv("WORKERS", "1"))
    
    # Start server with optimized settings
    import uvicorn
    
    uvicorn.run(
        "mcp_server_openai.http_server:app",
        host=host,
        port=port,
        workers=workers,
        loop="uvloop",
        access_log=True,
        log_level=get_log_level().lower(),
        # Optimization settings
        timeout_keep_alive=30,
        timeout_graceful_shutdown=10,
        limit_concurrency=100,
        limit_max_requests=1000,
        # Disable reload in production
        reload=False,
    )


if __name__ == "__main__":
    main()