import React from "react";
import { motion } from "motion/react";

export default function ChatLoadingDots() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4 p-4 absolute bottom-0 pb-8"
      role="status"
      aria-live="polite"
    >
      {/* Enhanced loading animation */}
      <div className="flex items-center gap-1.5">
        <motion.span
          className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{ 
            duration: 1.2, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }}
        />
        <motion.span
          className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.2,
          }}
        />
        <motion.span
          className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.4,
          }}
        />
      </div>
      
      {/* Enhanced message with icon */}
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        >
          <span className="text-lg">🤖</span>
        </motion.div>
        <span className="text-sm text-gray-600 dark:text-gray-400 font-medium">
          AI is thinking...
        </span>
      </div>
      
      <span className="sr-only">Loading...</span>
    </motion.div>
  );
}
