"""
WebSocket handler for voice agent server.
Handles WebSocket connections, message routing, and real-time communication.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from ..utils.logger import get_logger
from ..utils.audio_utils import (
    WebsocketHelper, 
    Workflow,
    is_sync_message,
    is_new_text_message,
    is_new_audio_chunk,
    is_audio_complete,
    extract_audio_chunk,
    process_inputs
)
from ..services.agent_config import job_tracking_agent


class WebSocketManager:
    """Manages WebSocket connections and message handling."""
    
    def __init__(self):
        self.logger = get_logger()
        self.active_connections: Dict[str, WebSocket] = {}
        self.voice_pipelines: Dict[str, Any] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection and initialize voice pipeline."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        self.logger.log_websocket_event("connection_established", client_id=client_id)
        
        # Initialize voice pipeline for this connection
        helper = WebsocketHelper(websocket, [], job_tracking_agent)
        self.voice_pipelines[client_id] = helper
        
        return helper
    
    def disconnect(self, client_id: str):
        """Clean up WebSocket connection and voice pipeline."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if client_id in self.voice_pipelines:
            del self.voice_pipelines[client_id]
        
        self.logger.log_websocket_event("connection_closed", client_id=client_id)
    
    async def handle_message(self, websocket: WebSocket, client_id: str, message: str):
        """Route WebSocket messages to appropriate handlers."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            self.logger.log_websocket_event("message_received", 
                client_id=client_id, 
                message_type=message_type,
                data_size=len(message)
            )
            
            if message_type == "history.update":
                await self._handle_history_update(websocket, client_id, data)
            elif message_type == "input_audio_buffer.append":
                await self._handle_audio_append(websocket, client_id, data)
            elif message_type == "input_audio_buffer.commit":
                await self._handle_audio_commit(websocket, client_id, data)
            else:
                self.logger.debug_log(f"Unknown message type: {message_type}", data, level="WARNING")
                
        except json.JSONDecodeError as e:
            self.logger.log_error(e, f"JSON decode error for client {client_id}")
        except Exception as e:
            self.logger.log_error(e, f"Message handling error for client {client_id}")
    
    async def _handle_history_update(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Handle history update messages."""
        inputs = data.get("inputs", [])
        reset_agent = data.get("reset_agent", False)
        
        self.logger.log_websocket_event("history_update", 
            client_id=client_id,
            message_count=len(inputs),
            reset_agent=reset_agent
        )
        
        if client_id in self.voice_pipelines:
            helper = self.voice_pipelines[client_id]
            await helper.update_history(inputs, reset_agent)
    
    async def _handle_audio_append(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Handle audio data append messages."""
        delta = data.get("delta", "")
        
        self.logger.log_audio_processing("append_data", 
            client_id=client_id,
            data_size=len(delta)
        )
        
        if client_id in self.voice_pipelines:
            helper = self.voice_pipelines[client_id]
            await helper.append_audio(delta)
    
    async def _handle_audio_commit(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Handle audio commit messages."""
        self.logger.log_audio_processing("commit_data", client_id=client_id)
        
        if client_id in self.voice_pipelines:
            helper = self.voice_pipelines[client_id]
            await helper.commit_audio()


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint handler based on official OpenAI sample."""
    client_id = f"client_{id(websocket)}"
    logger = get_logger()
    
    try:
        await websocket.accept()
        connection = WebsocketHelper(websocket, [], job_tracking_agent)
        audio_buffer = []
        
        workflow = Workflow(connection)
        logger.log_agent_interaction("connection_ready", client_id=client_id)
        
        while True:
            try:
                message = await websocket.receive_json()
            except WebSocketDisconnect:
                logger.log_websocket_event("disconnect", client_id=client_id)
                return
            
            # Handle text based messages
            if is_sync_message(message):
                connection.history = message["inputs"]
                if message.get("reset_agent", False):
                    connection.latest_agent = job_tracking_agent
            elif is_new_text_message(message):
                user_input = process_inputs(message, connection)
                async for new_output_tokens in workflow.run(user_input):
                    await connection.stream_response(new_output_tokens, is_text=True)

            # Handle a new audio chunk
            elif is_new_audio_chunk(message):
                audio_buffer.append(extract_audio_chunk(message))

            # Send full audio to the agent
            elif is_audio_complete(message):
                # Set the audio buffer in the connection for processing
                connection.audio_buffer = audio_buffer
                await connection.commit_audio()
                audio_buffer = []  # reset the audio buffer
                
    except WebSocketDisconnect:
        logger.log_websocket_event("disconnect", client_id=client_id)
    except Exception as e:
        logger.log_error(e, f"WebSocket connection error for {client_id}")
        import traceback
        traceback.print_exc()
