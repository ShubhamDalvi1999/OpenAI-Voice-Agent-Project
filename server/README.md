# Voice Agent Server

A FastAPI-based server for real-time voice interaction with AI agents using OpenAI's Voice Agents SDK.

## Features

- Real-time voice-to-voice interaction
- WebSocket-based communication
- Modular, industry-standard architecture
- Comprehensive logging and debugging
- REST API endpoints for health checks
- CORS support for frontend integration

## Architecture

The server follows industry-standard Python project structure:

```
src/voice_agent_server/
├── api/                    # API layer
│   ├── routes.py          # HTTP routes
│   └── websocket_handler.py # WebSocket handlers
├── core/                   # Core configuration
│   └── config.py          # Server configuration
├── models/                 # Data models (future)
├── services/               # Business logic
│   ├── agent_config.py    # AI agent configuration
│   ├── database.py        # Database operations
│   └── mock_api.py        # Mock API services
├── utils/                  # Utilities
│   ├── logger.py          # Logging utilities
│   └── audio_utils.py     # Audio processing utilities
└── main.py                # Application entry point
```

## Quick Start

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_connection_string
   HOST=0.0.0.0
   PORT=8000
   LOG_LEVEL=INFO
   ```

3. Run the server:
   ```bash
   uv run server.py
   # or
   python -m src.voice_agent_server.main
   ```

## API Endpoints

- `GET /` - Server information
- `GET /health` - Health check
- `GET /status` - Detailed server status
- `WebSocket /ws` - Real-time voice interaction

## Development

The server includes comprehensive logging and debugging capabilities:

- Request tracking with unique IDs
- Structured logging to both console and file
- Suppressed noisy third-party logs
- Clean, readable log format

## Configuration

All configuration is managed through environment variables and the `ServerConfig` class in `core/config.py`.

## Testing

Run tests with:
```bash
pytest tests/
```

## Contributing

1. Follow the modular architecture
2. Add proper logging using the logger utility
3. Update documentation for new features
4. Write tests for new functionality
