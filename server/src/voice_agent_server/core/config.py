"""
Configuration module for the voice agent server.
Handles environment variables, server settings, and application configuration.
"""

import os
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv


class ServerConfig:
    """Server configuration class."""
    
    def __init__(self):
        # Load environment variables from project root (server directory)
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / ".env"
        load_dotenv(dotenv_path=env_path, override=True)
        
        # Also try loading from current directory as fallback
        if not os.getenv("OPENAI_API_KEY"):
            load_dotenv(dotenv_path="../.env", override=True)
        
        # Server settings
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.reload: bool = os.getenv("RELOAD", "true").lower() == "true"
        
        # API keys
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.mongodb_uri: Optional[str] = os.getenv("MONGODB_URI")
        
        # Logging settings
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv("LOG_FILE", "backend_debug.log")
        
        # CORS settings
        self.cors_origins: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        
        # WebSocket settings
        self.websocket_endpoint: str = os.getenv("WEBSOCKET_ENDPOINT", "/ws")
        
        # Language settings
        self.default_language: str = os.getenv("DEFAULT_LANGUAGE", "en")
        self.supported_languages: list = os.getenv("SUPPORTED_LANGUAGES", "en,es,fr,de").split(",")
        self.auto_detect_language: bool = os.getenv("AUTO_DETECT_LANGUAGE", "true").lower() == "true"
        
        # Voice settings
        self.default_voice: str = os.getenv("DEFAULT_VOICE", "alloy")
        self.voice_language_mapping: dict = {
            "en": os.getenv("VOICE_EN", "alloy"),
            "es": os.getenv("VOICE_ES", "nova"),
            "fr": os.getenv("VOICE_FR", "echo"),
            "de": os.getenv("VOICE_DE", "onyx")
        }
        
        # Validate required settings
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration."""
        if not self.openai_api_key:
            print("WARNING: OPENAI_API_KEY environment variable is not set")
            # Don't raise error in development, just warn
        
        if not self.mongodb_uri:
            print("WARNING: MONGODB_URI environment variable is not set")
            # Don't raise error in development, just warn
    
    def get_server_url(self) -> str:
        """Get the full server URL."""
        return f"http://{self.host}:{self.port}"
    
    def get_websocket_url(self) -> str:
        """Get the WebSocket URL."""
        return f"ws://{self.host}:{self.port}{self.websocket_endpoint}"
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "cors_origins": self.cors_origins,
            "websocket_endpoint": self.websocket_endpoint,
            "has_openai_key": bool(self.openai_api_key),
            "has_mongodb_uri": bool(self.mongodb_uri)
        }


# Global configuration instance
config = ServerConfig()
