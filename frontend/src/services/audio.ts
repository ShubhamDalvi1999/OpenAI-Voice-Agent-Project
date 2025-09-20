/**
 * Audio service for recording and playback
 */

import { AUDIO_CONFIG } from '@/constants/audio';
import type { AudioConfig, AudioState } from '@/types/audio';

export class AudioService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private stream: MediaStream | null = null;
  private config: AudioConfig;

  constructor(config: AudioConfig = {
    sampleRate: AUDIO_CONFIG.SAMPLE_RATE,
    channels: AUDIO_CONFIG.CHANNELS,
    bitDepth: AUDIO_CONFIG.BIT_DEPTH,
  }) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channels,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      this.audioContext = new AudioContext({
        sampleRate: this.config.sampleRate,
      });
    } catch (error) {
      throw new Error(`Failed to initialize audio: ${error}`);
    }
  }

  async startRecording(): Promise<void> {
    if (!this.stream) {
      throw new Error('Audio stream not initialized');
    }

    this.mediaRecorder = new MediaRecorder(this.stream);
    this.mediaRecorder.start();
  }

  stopRecording(): Promise<Blob> {
    return new Promise((resolve) => {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.onstop = () => {
          const chunks: Blob[] = [];
          this.mediaRecorder!.ondataavailable = (event) => {
            chunks.push(event.data);
          };
          resolve(new Blob(chunks, { type: 'audio/wav' }));
        };
        this.mediaRecorder.stop();
      }
    });
  }

  async playAudio(audioBlob: Blob): Promise<void> {
    if (!this.audioContext) {
      throw new Error('Audio context not initialized');
    }

    const arrayBuffer = await audioBlob.arrayBuffer();
    const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
    const source = this.audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.audioContext.destination);
    source.start();
  }

  cleanup(): void {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}
