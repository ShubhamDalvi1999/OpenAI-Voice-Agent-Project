import { useCallback, useEffect, useRef, useState } from "react";
import { WavRecorder, WavStreamPlayer } from "wavtools";

import { normalizeArray } from "@/lib/utils";

export function useAudio() {
  const wavRecorder = useRef<WavRecorder | null>(null);
  const wavPlayer = useRef<WavStreamPlayer | null>(null);
  const audioChunks = useRef<Int16Array[]>([]);
  const trackId = useRef<string | null>(null);
  const [frequencies, setFrequencies] = useState<number[]>([]);

  const [audioPlayerIsReady, setAudioPlayerIsReady] = useState(false);
  const [audioRecorderIsReady, setAudioRecorderIsReady] = useState(false);
  const [playbackFrequencies, setPlaybackFrequencies] = useState<number[]>([]);
  const [microphoneError, setMicrophoneError] = useState<string | null>(null);

  const stoppedManually = useRef(false);

  useEffect(() => {
    async function init() {
      try {
        // Check if microphone permissions are available
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          setMicrophoneError("Microphone access is not supported in this browser");
          return;
        }

        // Request microphone permissions first
        try {
          await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (permissionError) {
          console.error("Microphone permission denied:", permissionError);
          setMicrophoneError("Microphone access denied. Please allow microphone permissions and refresh the page.");
          return;
        }

        // Initialize WavRecorder
        wavRecorder.current = new WavRecorder({ sampleRate: 24000 });
        await wavRecorder.current.begin();
        setAudioRecorderIsReady(true);

        // Initialize WavStreamPlayer
        wavPlayer.current = new WavStreamPlayer({ sampleRate: 24000 });
        await wavPlayer.current.connect();
        setAudioPlayerIsReady(true);

        console.log("Audio system initialized successfully");
      } catch (error) {
        console.error("Error initializing audio:", error);
        setMicrophoneError("Failed to initialize audio system. Please check your microphone and refresh the page.");
      }
    }
    init();
  }, []);

  const getFrequencies = useCallback(async () => {
    if (wavPlayer.current) {
      const newFrequencies = wavPlayer.current.getFrequencies("voice").values;
      const normalizedFrequencies = normalizeArray(newFrequencies, 5);
      setPlaybackFrequencies(normalizedFrequencies);

      const status = await wavPlayer.current?.getTrackSampleOffset();
      if (status) {
        window.requestAnimationFrame(getFrequencies);
      } else {
        setPlaybackFrequencies([]);
      }
    }
  }, []);

  const playAudio = useCallback(
    (audio: Int16Array<ArrayBuffer>) => {
      if (wavPlayer.current) {
        wavPlayer.current.add16BitPCM(audio, trackId.current ?? undefined);
        window.requestAnimationFrame(getFrequencies);
      }
    },
    [getFrequencies]
  );

  async function startRecording() {
    if (!wavRecorder.current) {
      console.error("WavRecorder not initialized");
      return;
    }

    try {
      await stopPlaying();
      stoppedManually.current = false;
      trackId.current = crypto.randomUUID();
      await wavRecorder.current?.clear();
      audioChunks.current = [];
      await wavRecorder.current?.record((data) => {
        audioChunks.current.push(data.mono);
        const updatedFrequencies = wavRecorder.current?.getFrequencies(
          "voice"
        ) || {
          values: new Float32Array([0]),
        };
        setFrequencies(normalizeArray(updatedFrequencies.values, 30));
      });
    } catch (error) {
      console.error("Error starting recording:", error);
      setMicrophoneError("Failed to start recording. Please check your microphone permissions.");
    }
  }

  async function stopPlaying() {
    stoppedManually.current = true;
    await wavPlayer.current?.interrupt();
    setPlaybackFrequencies(Array.from({ length: 30 }, () => 0));
  }

  async function stopRecording() {
    if (!wavRecorder.current) {
      console.error("WavRecorder not initialized");
      return new Int16Array(0);
    }

    try {
      await wavRecorder.current?.pause();
      const dataArrays = audioChunks.current.map((chunk) => {
        return new Int16Array(chunk);
      });

      const totalLength = dataArrays.reduce(
        (acc, chunk) => acc + chunk.length,
        0
      );
      const mergedAudio = new Int16Array(totalLength);
      let offset = 0;
      dataArrays.forEach((chunk) => {
        for (let i = 0; i < chunk.length; i++) {
          mergedAudio[offset + i] = chunk[i];
        }
        offset += chunk.length;
      });

      return mergedAudio;
    } catch (error) {
      console.error("Error stopping recording:", error);
      return new Int16Array(0);
    }
  }

  const retryMicrophoneAccess = useCallback(async () => {
    setMicrophoneError(null);
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      // Reinitialize audio system
      if (wavRecorder.current) {
        await wavRecorder.current.begin();
        setAudioRecorderIsReady(true);
      }
      if (wavPlayer.current) {
        await wavPlayer.current.connect();
        setAudioPlayerIsReady(true);
      }
    } catch (error) {
      console.error("Failed to retry microphone access:", error);
      setMicrophoneError("Still cannot access microphone. Please check browser permissions.");
    }
  }, []);

  return {
    isReady: audioPlayerIsReady && audioRecorderIsReady,
    playAudio,
    startRecording,
    stopRecording,
    stopPlaying,
    frequencies,
    playbackFrequencies,
    microphoneError,
    retryMicrophoneAccess,
  };
}
