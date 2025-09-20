/**
 * Audio-related constants
 */

export const AUDIO_CONFIG = {
  SAMPLE_RATE: 16000,
  CHANNELS: 1,
  BIT_DEPTH: 16,
  BUFFER_SIZE: 4096,
} as const;

export const AUDIO_FORMATS = {
  WAV: 'audio/wav',
  MP3: 'audio/mp3',
  WEBM: 'audio/webm',
} as const;

export const AUDIO_EVENTS = {
  START_RECORDING: 'start_recording',
  STOP_RECORDING: 'stop_recording',
  START_PLAYING: 'start_playing',
  STOP_PLAYING: 'stop_playing',
  ERROR: 'audio_error',
} as const;
