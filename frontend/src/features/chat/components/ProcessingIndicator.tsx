import React from "react";
import { motion } from "motion/react";

interface ProcessingIndicatorProps {
  isProcessing: boolean;
  message?: string;
}

export function ProcessingIndicator({ isProcessing, message = "Processing audio..." }: ProcessingIndicatorProps) {
  if (!isProcessing) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="flex items-center gap-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl mx-4 mb-3 shadow-sm"
    >
      {/* Enhanced loading animation */}
      <div className="flex items-center gap-1">
        <motion.div
          className="w-2.5 h-2.5 bg-blue-500 rounded-full"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{ 
            duration: 1.2, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }}
        />
        <motion.div
          className="w-2.5 h-2.5 bg-blue-500 rounded-full"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{ 
            duration: 1.2, 
            repeat: Infinity, 
            ease: "easeInOut", 
            delay: 0.2 
          }}
        />
        <motion.div
          className="w-2.5 h-2.5 bg-blue-500 rounded-full"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{ 
            duration: 1.2, 
            repeat: Infinity, 
            ease: "easeInOut", 
            delay: 0.4 
          }}
        />
      </div>
      
      {/* Message with icon */}
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <span className="text-blue-600">🎤</span>
        </motion.div>
        <span className="text-sm text-blue-700 font-medium">{message}</span>
      </div>
    </motion.div>
  );
}
