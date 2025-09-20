#!/usr/bin/env python3
"""
Main entry point for the Voice Agent Server.

This module creates and configures the FastAPI application with all necessary
middleware, routes, and WebSocket handlers.
"""

import json
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

from .core.config import config
from .utils.logger import get_logger
from .api.routes import router
from .api.websocket_handler import websocket_endpoint

# Initialize logger
logger = get_logger()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app
    app = FastAPI(
        title="Voice Agent Server",
        description="Real-time voice interaction with AI agent",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include HTTP routes
    app.include_router(router)

    # Add WebSocket endpoint
    @app.websocket(config.websocket_endpoint)
    async def websocket_route(websocket: WebSocket):
        """WebSocket endpoint for real-time voice interaction."""
        await websocket_endpoint(websocket)

    return app


# Create the app instance for uvicorn
app = create_app()


def main():
    """Main entry point for the server."""
    logger.debug_log("Starting voice agent server", config.to_dict())
    
    uvicorn.run(
        "src.voice_agent_server.main:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower()
    )


if __name__ == "__main__":
    main()
