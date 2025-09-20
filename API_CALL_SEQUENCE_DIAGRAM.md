# API Call Sequence Diagram: Voice Processing Flow

This document shows the detailed sequence of API calls and WebSocket messages that occur during a complete voice interaction cycle.

## 🎯 Overview

This sequence diagram illustrates the exact order of operations, API calls, and data flow when a user speaks to the voice assistant and receives a response.

## 📊 Complete API Call Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend (Next.js)
    participant WS as WebSocket
    participant B as Backend (FastAPI)
    participant VP as VoicePipeline
    participant W as Whisper STT
    participant G as GPT-4o-mini
    participant DB as MongoDB
    participant T as TTS
    participant A as Audio Player

    Note over U,A: Voice Input Phase
    U->>F: Clicks microphone button
    F->>F: startRecording()
    F->>F: WavRecorder.record()
    F->>F: Audio chunks collected
    U->>F: Stops recording
    F->>F: stopRecording() → Int16Array
    F->>F: arrayBufferToBase64(audio.buffer)

    Note over F,WS: WebSocket Communication Phase
    F->>WS: WebSocket.send({type: "history.update", inputs: history})
    F->>WS: WebSocket.send({type: "input_audio_buffer.append", delta: base64Audio})
    F->>WS: WebSocket.send({type: "input_audio_buffer.commit"})

    Note over WS,B: Backend Processing Phase
    WS->>B: WebSocket message received
    B->>B: is_new_audio_chunk() → true
    B->>B: extract_audio_chunk() → audio_data
    B->>B: audio_buffer.append(audio_data)
    WS->>B: WebSocket message: input_audio_buffer.commit
    B->>B: is_audio_complete() → true
    B->>B: concat_audio_chunks(audio_buffer) → AudioInput

    Note over B,VP: VoicePipeline Processing
    B->>VP: VoicePipeline.run(audio_input)
    VP->>W: Audio → Text conversion
    W-->>VP: Transcribed text
    VP->>G: Process text with agent
    G->>G: Analyze intent and context
    G->>G: Execute function tools (if needed)
    G->>DB: Database operations (if needed)
    DB-->>G: Database response
    G-->>VP: Generated response text
    VP->>T: Text → Audio conversion
    T-->>VP: Audio response

    Note over VP,A: Response Streaming Phase
    VP->>B: Stream audio events
    B->>B: transform_data_to_events(audio_np)
    B->>WS: WebSocket.send({type: "response.audio.delta", delta: base64Audio})
    WS->>F: WebSocket message received
    F->>F: base64ToArrayBuffer(data.delta)
    F->>F: new Int16Array(audioData)
    F->>A: playAudio(audioData)
    A->>A: WavStreamPlayer.add16BitPCM()
    A->>A: Audio playback starts

    Note over F,U: UI Update Phase
    F->>F: setHistory(updatedHistory)
    F->>F: setAgentName(agentName)
    F->>F: setIsLoading(false)
    F->>U: UI updates with conversation history
    A->>U: Audio response plays

    Note over U,A: End of Interaction
    VP->>B: Audio streaming complete
    B->>WS: WebSocket.send({type: "audio.done"})
    WS->>F: audio.done message
    F->>F: onAudioDone() callback
    A->>A: Audio playback stops
```

## 🔄 Detailed Message Flow

### Phase 1: Voice Input Capture

```mermaid
sequenceDiagram
    participant U as User
    participant AC as AudioChat Component
    participant AH as useAudio Hook
    participant WR as WavRecorder

    U->>AC: Clicks microphone button
    AC->>AH: toggleRecording()
    AH->>WR: new WavRecorder({sampleRate: 24000})
    AH->>WR: record(callback)
    WR->>AH: Audio data chunks
    AH->>AH: audioChunks.push(data.mono)
    AH->>AH: setFrequencies(visualization)
    U->>AC: Stops recording
    AC->>AH: stopRecording()
    AH->>WR: pause()
    AH->>AH: Merge audio chunks
    AH->>AH: Return Int16Array
    AC->>AC: sendAudioMessage(audio)
```

### Phase 2: WebSocket Message Transmission

```mermaid
sequenceDiagram
    participant F as Frontend
    participant WS as WebSocket
    participant B as Backend

    F->>F: arrayBufferToBase64(audio.buffer)
    F->>WS: {type: "history.update", inputs: history}
    WS->>B: Message received
    B->>B: Update connection.history
    
    F->>WS: {type: "input_audio_buffer.append", delta: base64Audio}
    WS->>B: Message received
    B->>B: is_new_audio_chunk() → true
    B->>B: extract_audio_chunk()
    B->>B: audio_buffer.append(audio_data)
    
    F->>WS: {type: "input_audio_buffer.commit"}
    WS->>B: Message received
    B->>B: is_audio_complete() → true
    B->>B: Process complete audio
```

### Phase 3: Backend Processing Pipeline

```mermaid
sequenceDiagram
    participant B as Backend
    participant VP as VoicePipeline
    participant W as Whisper
    participant G as GPT-4o
    participant FT as Function Tools
    participant DB as Database

    B->>B: concat_audio_chunks(audio_buffer)
    B->>VP: VoicePipeline.run(audio_input)
    VP->>W: Audio → Text
    W-->>VP: "Add Google Software Engineer"
    VP->>G: Process with agent
    G->>G: Analyze intent
    G->>FT: Execute add_job_application()
    FT->>DB: create_application_with_dedup()
    DB-->>FT: Application created
    FT-->>G: Success response
    G-->>VP: "I've added Google Software Engineer..."
    VP->>VP: Generate audio response
```

### Phase 4: Response Streaming

```mermaid
sequenceDiagram
    participant VP as VoicePipeline
    participant B as Backend
    participant WS as WebSocket
    participant F as Frontend
    participant A as Audio Player

    VP->>B: Stream audio events
    B->>B: transform_data_to_events(audio_np)
    B->>WS: {type: "response.audio.delta", delta: base64Audio}
    WS->>F: Message received
    F->>F: base64ToArrayBuffer(data.delta)
    F->>F: new Int16Array(audioData)
    F->>A: playAudio(audioData)
    A->>A: WavStreamPlayer.add16BitPCM()
    A->>A: requestAnimationFrame(getFrequencies)
    A->>A: Audio visualization update
```

## 📡 WebSocket Message Types

### Outgoing Messages (Frontend → Backend)

```typescript
// 1. History Update
{
  type: "history.update",
  inputs: Message[],
  reset_agent?: boolean
}

// 2. Audio Chunk
{
  type: "input_audio_buffer.append",
  delta: string  // base64 encoded audio
}

// 3. Audio Complete
{
  type: "input_audio_buffer.commit"
}
```

### Incoming Messages (Backend → Frontend)

```typescript
// 1. History Updated
{
  type: "history.updated",
  reason: "user.input" | "response.text.delta" | "response.done",
  inputs: Message[],
  agent_name: string,
  sync?: boolean
}

// 2. Audio Response Chunk
{
  type: "response.audio.delta",
  delta: string,  // base64 encoded audio
  output_index: number,
  content_index: number,
  item_id: string,
  response_id: string,
  event_id: string
}

// 3. Audio Complete
{
  type: "audio.done"
}
```

## 🔧 Function Tool Execution Sequence

```mermaid
sequenceDiagram
    participant G as GPT-4o
    participant FT as Function Tool
    participant DB as Database
    participant VP as VoicePipeline

    G->>G: Analyze user intent
    G->>FT: add_job_application(company, role_title, ...)
    FT->>FT: Prepare application data
    FT->>DB: create_application_with_dedup(app_data)
    DB->>DB: Check for duplicates
    DB->>DB: Create new application
    DB-->>FT: {application_id, message, updated}
    FT->>FT: Add note if provided
    FT->>DB: add_note_to_application()
    DB-->>FT: Note added
    FT->>FT: Schedule follow-up if provided
    FT->>DB: schedule_followup()
    DB-->>FT: Follow-up scheduled
    FT-->>G: JSON response with success/message
    G-->>VP: Generate natural language response
```

## ⚡ Performance Metrics

### Timing Breakdown
- **Audio Recording**: ~2-5 seconds (user dependent)
- **WebSocket Transmission**: ~50-100ms
- **Whisper STT**: ~1-3 seconds
- **GPT-4o Processing**: ~500ms-2 seconds
- **Function Tool Execution**: ~100-500ms
- **TTS Generation**: ~1-2 seconds
- **Audio Streaming**: Real-time chunks
- **Audio Playback**: Real-time

### Latency Optimization Points
1. **Audio Chunking**: 512 sample buffer size
2. **Parallel Processing**: STT and TTS can overlap
3. **Streaming**: Audio response streams as generated
4. **WebSocket**: Low-latency bidirectional communication

## 🚨 Error Handling Sequences

### WebSocket Connection Failure
```mermaid
sequenceDiagram
    participant F as Frontend
    participant WS as WebSocket
    participant B as Backend

    F->>WS: Attempt connection
    WS-->>F: Connection failed
    F->>F: setIsReady(false)
    F->>F: console.error("Websocket error")
    F->>F: setIsLoading(false)
    F->>F: Show error state in UI
```

### Microphone Permission Denied
```mermaid
sequenceDiagram
    participant F as Frontend
    participant AH as useAudio Hook
    participant U as User

    F->>AH: startRecording()
    AH->>AH: navigator.mediaDevices.getUserMedia()
    AH-->>F: Permission denied
    F->>F: setMicrophoneError("Permission denied")
    F->>U: Show permission request UI
    U->>F: Grants permission
    F->>AH: retryMicrophoneAccess()
    AH->>AH: Reinitialize audio system
```

## 🔍 Debugging Sequence Points

### Key Monitoring Points
1. **WebSocket Connection Status**
2. **Audio Buffer Accumulation**
3. **Function Tool Execution**
4. **Database Operation Success**
5. **Audio Streaming Latency**
6. **TTS Generation Time**

### Common Failure Points
1. **WebSocket Connection**: Backend not running
2. **Microphone Access**: Browser permissions
3. **Audio Quality**: Sample rate mismatch
4. **API Keys**: Invalid OpenAI credentials
5. **Database Connection**: MongoDB unavailable

This sequence diagram provides a complete technical reference for understanding the exact flow of data and API calls in the voice processing system.
