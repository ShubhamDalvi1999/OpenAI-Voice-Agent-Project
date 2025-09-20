#!/usr/bin/env python3
"""
Legacy server entry point.

This file is kept for backward compatibility but now imports from the new
modular structure. The main application is now in src/voice_agent_server/main.py
"""

from src.voice_agent_server.main import create_app, main

# Create the app for uvicorn
app = create_app()

if __name__ == "__main__":
    main()