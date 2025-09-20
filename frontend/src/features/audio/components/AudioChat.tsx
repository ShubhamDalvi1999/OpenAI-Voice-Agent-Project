import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

import { AudioPlayback } from "./AudioPlayback";
import { cn } from "@/features/ui/components/ui/utils";
import { ArrowUpIcon, MicIcon } from "@/features/ui/components/icons";

interface AudioChatProps {
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Int16Array<ArrayBuffer>>;
  sendAudioMessage: (audio: Int16Array<ArrayBuffer>) => void;
  isReady: boolean;
  frequencies: number[];
  microphoneError?: string | null;
  retryMicrophoneAccess?: () => Promise<void>;
}

const AudioChat = ({
  isReady = true,
  startRecording,
  stopRecording,
  sendAudioMessage,
  frequencies,
  microphoneError,
  retryMicrophoneAccess,
}: AudioChatProps) => {
  const [isRecording, setIsRecording] = useState(false);

  async function toggleRecording() {
    if (isRecording) {
      const audio = await stopRecording();
      sendAudioMessage(audio);
      setIsRecording(false);
    } else {
      await startRecording();
      setIsRecording(true);
    }
  }

  // Show microphone error state
  if (microphoneError) {
    return (
      <div className="flex flex-col items-center gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center gap-2 text-yellow-800">
          <MicIcon />
          <span className="text-sm font-medium">Microphone Access Required</span>
        </div>
        <p className="text-xs text-yellow-700 text-center">{microphoneError}</p>
        {retryMicrophoneAccess && (
          <button
            onClick={retryMicrophoneAccess}
            className="px-3 py-1 text-xs font-medium border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Retry Microphone Access
          </button>
        )}
        <div className="text-xs text-yellow-600 text-center">
          <p>To fix this:</p>
          <ol className="list-decimal list-inside mt-1 space-y-1">
            <li>Click the microphone icon in your browser's address bar</li>
            <li>Select "Allow" for microphone access</li>
            <li>Refresh the page</li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {isRecording ? (
          <motion.div
            key="recording"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.2 }}
            className="flex items-center gap-3 p-3 bg-red-50 border-2 border-red-200 rounded-full shadow-lg"
          >
            {/* Recording indicator with pulsing animation */}
            <motion.div
              className="flex items-center gap-2"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <div className="relative">
                <motion.div
                  className="w-3 h-3 bg-red-500 rounded-full"
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
                <motion.div
                  className="absolute inset-0 w-3 h-3 bg-red-500 rounded-full"
                  animate={{ scale: [1, 2, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              </div>
              <span className="text-sm font-medium text-red-700">Recording</span>
            </motion.div>

            {/* Audio visualization */}
            <div className="flex items-center gap-1">
              <AudioPlayback
                playbackFrequencies={frequencies}
                itemClassName="bg-red-400 w-[3px] rounded-full"
                className="gap-[2px]"
                height={24}
              />
            </div>

            {/* Stop button */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <button
                onClick={toggleRecording}
                className="h-8 w-8 rounded-full bg-red-500 hover:bg-red-600 text-white border-0 shadow-md flex items-center justify-center transition-colors"
              >
                <ArrowUpIcon className="rotate-90 w-4 h-4" />
              </button>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            key="idle"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="relative"
            >
              <button
                disabled={!isReady}
                aria-label="Start Recording"
                className={cn(
                  "relative overflow-hidden border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 w-16 h-16 rounded-full flex flex-col items-center justify-center gap-1",
                  !isReady && "opacity-50 cursor-not-allowed"
                )}
                onClick={toggleRecording}
              >
                <motion.div
                  animate={isReady ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <MicIcon className="text-gray-600 w-5 h-5" />
                </motion.div>
                <span className="text-xs text-gray-500 font-medium">Tap to speak</span>
                
                {/* Subtle background animation when ready */}
                {isReady && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-blue-100 to-purple-100 opacity-0 rounded-full"
                    animate={{ opacity: [0, 0.1, 0] }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />
                )}
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AudioChat;
