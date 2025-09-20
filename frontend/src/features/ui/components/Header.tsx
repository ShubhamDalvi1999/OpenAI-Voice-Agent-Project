"use client";

import clsx from "clsx";
import { AnimatePresence, motion } from "motion/react";
import Image from "next/image";

import { AudioPlayback } from "@/features/audio";
import { PauseIcon, WriteIcon } from "./icons";
import { Button } from "./ui";

export function Header({
  agentName,
  playbackFrequencies,
  stopPlaying,
  resetConversation,
}: {
  agentName: string;
  playbackFrequencies: number[];
  stopPlaying: () => Promise<void>;
  resetConversation: () => void;
}) {
  const showAudioPlayback = playbackFrequencies.length === 5;

  return (
    <div className="flex flex-row gap-2 w-full relative justify-between items-center py-4 px-4 bg-white text-black border-b border-gray-100 dark:bg-gray-900 dark:text-white dark:border-gray-800">
      <div className="flex flex-row gap-2 items-center px-5">
        <Image src="/openai_logo.svg" alt="OpenAI Logo" width={24} height={24} className="dark:invert" />
        <div className="flex flex-col">
          <span className="text-sm font-semibold">Job Application Tracker</span>
          <span className="text-xs text-gray-500">Powered by OpenAI Voice • Click left edge for functions</span>
        </div>
      </div>
      {agentName && (
        <div
          className={clsx(
            "flex text-sm font-semibold border-2 border-gray-100 rounded-full py-3 items-center overflow-hidden dark:border-gray-700 bg-white dark:bg-gray-800 dark:text-white"
          )}
        >
          <div className="ml-6 mr-4">
            <AnimatePresence initial={false}>
              {showAudioPlayback && (
                <motion.div
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  transition={{
                    type: "spring",
                    stiffness: 200,
                    damping: 8,
                    mass: 0.5,
                  }}
                  style={{ originX: 0 }}
                  className="flex items-center overflow-hidden"
                >
                  <AudioPlayback
                    playbackFrequencies={playbackFrequencies}
                    itemClassName="bg-black"
                    height={24}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          <motion.div
            layout="size"
            initial={{ width: 0 }}
            animate={{ width: "auto" }}
            transition={{
              type: "spring",
              stiffness: 200,
              damping: 8,
              mass: 0.5,
            }}
            style={{ originX: 0.5 }}
            className="overflow-hidden whitespace-nowrap text-center"
          >
            <AnimatePresence mode="wait">
              <motion.span
                key={agentName}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                {agentName}
              </motion.span>
            </AnimatePresence>
          </motion.div>
          <div className="mr-6 ml-4">
            <AnimatePresence initial={false}>
              {showAudioPlayback && (
                <motion.div
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  transition={{
                    type: "spring",
                    stiffness: 200,
                    damping: 8,
                    mass: 0.5,
                  }}
                  style={{ originX: 1 }}
                  className="flex items-center overflow-hidden -pr-2"
                >
                  <Button
                    variant="primary"
                    size="iconTiny"
                    onClick={stopPlaying}
                  >
                    <PauseIcon />
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}
      <div className="flex flex-row gap-2 px-5 items-center">
        <Button
          onClick={resetConversation}
          aria-label="Start new conversation"
          size="icon"
        >
          <WriteIcon width={24} height={24} />
        </Button>
      </div>
    </div>
  );
}
