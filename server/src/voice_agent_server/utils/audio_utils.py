import base64
import json
import time
from collections.abc import AsyncIterator

import numpy as np
from agents import (
    Agent,
    Runner,
    RunItemStreamEvent,
    RawResponsesStreamEvent,
    AgentUpdatedStreamEvent,
    trace,
)
from agents.voice import (
    AudioInput, 
    VoiceStreamEvent, 
    VoiceStreamEventAudio,
    TTSModelSettings,
    VoicePipeline,
    VoicePipelineConfig,
    VoiceWorkflowBase,
)
from fastapi import WebSocket
from openai.types.responses import ResponseTextDeltaEvent


def transform_data_to_events(audio_np: np.ndarray) -> dict:
    return {
        "type": "response.audio.delta",
        "delta": base64.b64encode(audio_np.tobytes()).decode("utf-8"),
        "output_index": 0,
        "content_index": 0,
        "item_id": "",
        "response_id": "",
        "event_id": "",
    }


def is_new_output_item(event):
    return isinstance(event, RunItemStreamEvent)


def is_text_output(event):
    return event.type == "raw_response_event" and isinstance(
        event.data, ResponseTextDeltaEvent
    )


def is_sync_message(data):
    return data["type"] == "history.update" and (
        not data["inputs"] or data["inputs"][-1].get("role") != "user"
    )


def is_new_text_message(data):
    return data["type"] == "history.update" and (
        data["inputs"] and data["inputs"][-1].get("role") == "user"
    )


def process_inputs(data, connection) -> str:
    connection.history = data["inputs"][:-1]
    return data["inputs"][-1]["content"]


def is_new_audio_chunk(data):
    return data["type"] == "input_audio_buffer.append"


def is_audio_complete(data):
    return data["type"] == "input_audio_buffer.commit"


def extract_audio_chunk(data):
    decoded_bytes = base64.b64decode(data["delta"])
    audio_int16 = np.frombuffer(decoded_bytes, dtype=np.int16)
    audio_data = audio_int16.astype(np.float32) / 32768.0
    return audio_data


def concat_audio_chunks(chunks) -> AudioInput:
    return AudioInput(np.concatenate(chunks))


class Workflow(VoiceWorkflowBase):
    """Voice workflow implementation based on official OpenAI sample."""
    
    def __init__(self, connection: 'WebsocketHelper'):
        self.connection = connection

    async def run(self, input_text: str) -> AsyncIterator[str]:
        """Run the workflow with text input."""
        conversation_history, latest_agent = await self.connection.show_user_input(
            input_text
        )

        output = Runner.run_streamed(
            latest_agent,
            conversation_history,
        )

        async for event in output.stream_events():
            await self.connection.handle_new_item(event)

            if is_text_output(event):
                yield event.data.delta  # type: ignore

        await self.connection.text_output_complete(output, is_done=True)


class WebsocketHelper:
    def __init__(self, websocket: WebSocket, history: list, initial_agent: Agent):
        self.websocket = websocket
        self.history = history or []
        self.latest_agent = initial_agent
        self.partial_response = ""

    async def show_user_input(self, user_input: str):
        self.history.append(
            {
                "type": "message",
                "role": "user",
                "content": user_input,
            }
        )
        await self.websocket.send_text(
            json.dumps(
                {
                    "type": "history.updated",
                    "reason": "user.input",
                    "inputs": self.history,
                    "agent_name": self.latest_agent.name,
                }
            )
        )
        return (self.history, self.latest_agent)

    async def stream_response(self, new_tokens: str, is_text: bool = False):
        if is_text:
            return

        self.partial_response += new_tokens
        await self.websocket.send_text(
            json.dumps(
                {
                    "type": "history.updated",
                    "reason": "response.text.delta",
                    "inputs": self.history
                    + [
                        {
                            "type": "message",
                            "role": "assistant",
                            "content": self.partial_response,
                        }
                    ],
                    "agent_name": self.latest_agent.name,
                }
            )
        )

    async def handle_new_item(
        self,
        event: RawResponsesStreamEvent | RunItemStreamEvent | AgentUpdatedStreamEvent,
    ):
        if is_new_output_item(event):
            self.history.append(event.item.to_input_item())  # type: ignore

            await self.websocket.send_text(
                json.dumps(
                    {
                        "type": "history.updated",
                        "reason": "response.input_item",
                        "inputs": self.history,
                        "agent_name": self.latest_agent.name,
                    }
                )
            )
        elif is_text_output(event):
            await self.stream_response(event.data.delta)  # type: ignore

    async def text_output_complete(self, output, is_done=False):
        if not is_done:
            await self.websocket.send_text(
                json.dumps(
                    {
                        "type": "history.updated",
                        "inputs": self.history,
                        "sync": True,
                        "agent_name": self.latest_agent.name,
                    }
                )
            )
        else:
            self.partial_response = ""
            self.latest_agent = output.last_agent
            self.history = output.to_input_list()
            await self.websocket.send_text(
                json.dumps(
                    {
                        "type": "history.updated",
                        "inputs": self.history,
                        "reason": "response.done",
                        "agent_name": self.latest_agent.name,
                    }
                )
            )

    async def send_audio_chunk(self, event: VoiceStreamEvent):
        if isinstance(event, VoiceStreamEventAudio):
            await self.websocket.send_text(
                json.dumps(transform_data_to_events(event.data))  # type: ignore
            )

    async def send_audio_done(self):
        await self.websocket.send_text(json.dumps({"type": "audio.done"}))

    async def send_fallback_response(self, user_input: str):
        """Send a simple text response when voice agent fails."""
        try:
            # Create a simple response based on the user input
            response_text = f"I heard you say: '{user_input}'. I'm a job application tracking assistant. How can I help you with your job search?"
            
            # Add assistant response to history
            assistant_message = {
                "type": "message",
                "role": "assistant",
                "content": response_text
            }
            self.history.append(assistant_message)
            
            # Send updated history to frontend
            await self.websocket.send_text(json.dumps({
                "type": "history.updated",
                "reason": "assistant.text_response",
                "inputs": self.history,
                "agent_name": self.latest_agent.name if hasattr(self.latest_agent, 'name') else "Voice Agent"
            }))
            
            print(f"Sent fallback response: {response_text}")
            
            # Generate audio response
            await self.generate_audio_response(response_text)
            
        except Exception as e:
            print(f"Error sending fallback response: {e}")

    async def generate_audio_response(self, text: str):
        """Generate audio response using OpenAI TTS."""
        try:
            import openai
            
            print(f"Generating audio for: {text}")
            
            # Generate speech using OpenAI TTS
            response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            # Convert audio to base64 and send to frontend
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Send audio data to frontend
            await self.websocket.send_text(json.dumps({
                "type": "response.audio.delta",
                "delta": audio_base64,
                "output_index": 0,
                "content_index": 0,
                "item_id": "",
                "response_id": "",
                "event_id": "",
            }))
            
            # Send audio done signal
            await self.send_audio_done()
            
            print("Audio response sent successfully")
            
        except Exception as e:
            print(f"Error generating audio response: {e}")
            # Send audio done signal even if generation failed
            await self.send_audio_done()

    async def append_audio(self, delta: str):
        """Append audio data to the input buffer."""
        # Decode base64 audio data
        try:
            audio_bytes = base64.b64decode(delta)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Store audio data for processing
            if not hasattr(self, 'audio_buffer'):
                self.audio_buffer = []
            self.audio_buffer.append(audio_np)
            
        except Exception as e:
            print(f"Error appending audio: {e}")

    async def commit_audio(self):
        """Commit the audio buffer and process it using VoicePipeline."""
        if not hasattr(self, 'audio_buffer') or not self.audio_buffer:
            print("No audio buffer to process")
            return
            
        try:
            print(f"Processing audio with {len(self.audio_buffer)} chunks")
            
            # Concatenate all audio chunks
            full_audio = np.concatenate(self.audio_buffer)
            print(f"Concatenated audio shape: {full_audio.shape}")
            
            # Create AudioInput object
            audio_input = AudioInput(full_audio)
            print("Created AudioInput object")
            
            # Create workflow
            workflow = Workflow(self)
            
            # Process with VoicePipeline (this handles STT, agent processing, and TTS)
            start_time = time.perf_counter()
            
            def transform_data(data):
                nonlocal start_time
                if start_time:
                    print(f"Time taken to first byte: {time.perf_counter() - start_time}s")
                    start_time = None
                return data
            
            print("Starting VoicePipeline processing...")
            
            output = await VoicePipeline(
                workflow=workflow,
                config=VoicePipelineConfig(
                    tts_settings=TTSModelSettings(
                        buffer_size=512, 
                        transform_data=transform_data
                    )
                ),
            ).run(audio_input)
            
            # Stream the audio response
            async for event in output.stream():
                await self.send_audio_chunk(event)
            
            print("VoicePipeline processing completed")
            
            # Clear the buffer
            self.audio_buffer = []
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            import traceback
            traceback.print_exc()
            # Clear buffer on error
            if hasattr(self, 'audio_buffer'):
                self.audio_buffer = []


    async def update_history(self, inputs: list, reset_agent: bool = False):
        """Update the conversation history."""
        try:
            self.history = inputs
            
            if reset_agent:
                # Reset the agent if requested
                from ..services.agent_config import job_tracking_agent
                self.latest_agent = job_tracking_agent
            
            # Send history update to frontend
            await self.websocket.send_text(json.dumps({
                "type": "history.updated",
                "reason": "history.update",
                "inputs": self.history,
                "agent_name": self.latest_agent.name if hasattr(self.latest_agent, 'name') else "Voice Agent"
            }))
            
        except Exception as e:
            print(f"Error updating history: {e}")