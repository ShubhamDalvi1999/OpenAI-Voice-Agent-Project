"""
HTTP routes for the voice agent server.
Provides REST API endpoints for health checks and basic server information.
"""

import time
from fastapi import APIRouter
from ..utils.logger import get_logger

# Create router for HTTP endpoints
router = APIRouter()
logger = get_logger()


@router.get("/")
async def root():
    """Root endpoint providing basic server information."""
    logger.log_request("GET", "/")
    return {
        "message": "Voice Agent Server is running (DEBUG MODE)", 
        "websocket": "/ws",
        "health": "/health"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    logger.log_request("GET", "/health")
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "service": "voice-agent-server"
    }


@router.get("/status")
async def server_status():
    """Detailed server status endpoint."""
    logger.log_request("GET", "/status")
    return {
        "status": "running",
        "timestamp": time.time(),
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "root": "/"
        },
        "features": [
            "voice-to-voice",
            "real-time-audio",
            "job-tracking-agent"
        ]
    }
