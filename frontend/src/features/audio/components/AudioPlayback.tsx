import { motion } from "motion/react";

import { cn } from "@/features/ui";

export function AudioPlayback({
  playbackFrequencies,
  itemClassName,
  className,
  height = 36,
}: {
  playbackFrequencies: number[];
  itemClassName?: string;
  className?: string;
  height?: number;
}) {
  return (
    <div
      className={cn(`flex items-end justify-center gap-[2px]`, className)}
    >
      {playbackFrequencies.map((frequency: number, index: number) => (
        <motion.div
          key={index}
          className={cn("w-[3px] rounded-full", itemClassName)}
          initial={{ height: 2 }}
          animate={{ 
            height: `${Math.max(2, frequency * height)}px`,
            opacity: frequency > 0.1 ? 1 : 0.3
          }}
          transition={{ 
            duration: 0.15, 
            ease: "easeOut",
            delay: index * 0.01
          }}
          style={{
            background: `linear-gradient(to top, ${itemClassName?.includes('red') ? '#ef4444' : '#3b82f6'}, ${itemClassName?.includes('red') ? '#fca5a5' : '#93c5fd'})`
          }}
        />
      ))}
    </div>
  );
}
