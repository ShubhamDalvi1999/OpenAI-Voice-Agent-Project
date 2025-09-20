"""
Logger utility for the voice agent server.
Provides clean, structured logging with request tracking and debug capabilities.
"""

import logging
import json
import time
from typing import Any, Optional
from pathlib import Path


class VoiceAgentLogger:
    """Custom logger for voice agent server with request tracking and clean output."""
    
    def __init__(self, log_file: str = "backend_debug.log", log_level: str = "INFO"):
        self.request_counter = 0
        self.log_file = log_file
        self.log_level = log_level
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging with clean output and suppressed noise."""
        # Configure main logger
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_file)
            ]
        )
        
        # Suppress noisy loggers
        noisy_loggers = [
            'watchfiles',
            'asyncio', 
            'openai.agents',
            'uvicorn',
            'uvicorn.access'
        ]
        
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
        
        self.logger = logging.getLogger(__name__)
    
    def debug_log(self, message: str, data: Any = None, level: str = "INFO") -> None:
        """
        Enhanced logging function with request tracking.
        
        Args:
            message: The log message
            data: Optional data to include in the log
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        self.request_counter += 1
        
        log_message = f"[REQ-{self.request_counter}] {message}"
        
        if data is not None:
            if isinstance(data, (dict, list)):
                log_message += f" | Data: {json.dumps(data, default=str, indent=2)}"
            else:
                log_message += f" | Data: {str(data)}"
        
        # Log to file and console
        if level == "DEBUG":
            self.logger.debug(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
        
        # Also print to console for immediate visibility (Windows compatible)
        print(f"[DEBUG] {log_message}")
    
    def log_request(self, method: str, endpoint: str, **kwargs) -> None:
        """Log HTTP request details."""
        self.debug_log(f"HTTP {method} {endpoint}", kwargs)
    
    def log_websocket_event(self, event_type: str, **kwargs) -> None:
        """Log WebSocket event details."""
        self.debug_log(f"WebSocket {event_type}", kwargs)
    
    def log_audio_processing(self, action: str, **kwargs) -> None:
        """Log audio processing events."""
        self.debug_log(f"Audio {action}", kwargs)
    
    def log_agent_interaction(self, action: str, **kwargs) -> None:
        """Log AI agent interactions."""
        self.debug_log(f"Agent {action}", kwargs)
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log errors with context."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.debug_log(f"ERROR in {context}", error_data, level="ERROR")


# Global logger instance
logger = VoiceAgentLogger()


def get_logger() -> VoiceAgentLogger:
    """Get the global logger instance."""
    return logger


def setup_logger(log_file: str = "backend_debug.log", log_level: str = "INFO") -> VoiceAgentLogger:
    """Setup and return a new logger instance."""
    return VoiceAgentLogger(log_file, log_level)
