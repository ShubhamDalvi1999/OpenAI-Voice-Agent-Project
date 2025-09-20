/**
 * Audio-related types
 */

export interface AudioConfig {
  sampleRate: number;
  channels: number;
  bitDepth: number;
}

export interface AudioState {
  isRecording: boolean;
  isPlaying: boolean;
  isReady: boolean;
  error?: string;
}

export interface FrequencyData {
  frequencies: number[];
  timestamp: number;
}

export interface AudioError {
  type: 'microphone' | 'playback' | 'permission';
  message: string;
  code?: string;
}
