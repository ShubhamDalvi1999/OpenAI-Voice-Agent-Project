import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ChevronLeftIcon, ChevronRightIcon } from "@/features/ui/components/icons";

interface FunctionInfo {
  name: string;
  description: string;
  icon: string;
  category: string;
  examples: string[];
}

const AVAILABLE_FUNCTIONS: FunctionInfo[] = [
  {
    name: "Add Job Application",
    description: "Add a new job application to your pipeline",
    icon: "📝",
    category: "Applications",
    examples: [
      "Add Google Software Engineer in Mountain View",
      "Track Microsoft Data Scientist position",
      "Add new application for Apple iOS Developer"
    ]
  },
  {
    name: "Update Status",
    description: "Update application status through the hiring pipeline",
    icon: "📊",
    category: "Applications",
    examples: [
      "Update status to applied for Microsoft",
      "Move Google application to tech screen",
      "Mark Apple as rejected"
    ]
  },
  {
    name: "Add Notes",
    description: "Add notes and details to applications",
    icon: "📋",
    category: "Applications",
    examples: [
      "Add note: Had great conversation with hiring manager",
      "Note: Salary discussion went well",
      "Add: Technical interview scheduled for Friday"
    ]
  },
  {
    name: "Schedule Follow-up",
    description: "Set reminders for application follow-ups",
    icon: "⏰",
    category: "Applications",
    examples: [
      "Schedule follow-up for next Friday",
      "Remind me to follow up with Google next week",
      "Set reminder for Microsoft application"
    ]
  },
  {
    name: "Search Applications",
    description: "Find applications with specific criteria",
    icon: "🔍",
    category: "Search",
    examples: [
      "Show me all applications from last week",
      "Find draft applications",
      "Search for Google applications"
    ]
  },
  {
    name: "View All Applications",
    description: "See your complete application pipeline",
    icon: "📋",
    category: "Overview",
    examples: [
      "Show me my applications",
      "What applications do I have?",
      "My to-do list"
    ]
  },
  {
    name: "Pipeline Summary",
    description: "Get insights and statistics about your job search",
    icon: "📈",
    category: "Overview",
    examples: [
      "What's my pipeline status?",
      "Show me job search statistics",
      "How many applications do I have?"
    ]
  }
];

interface FunctionsPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

export function FunctionsPanel({ isOpen, onToggle }: FunctionsPanelProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  
  const categories = ["All", ...Array.from(new Set(AVAILABLE_FUNCTIONS.map(f => f.category)))];
  
  const filteredFunctions = selectedCategory === "All" 
    ? AVAILABLE_FUNCTIONS 
    : AVAILABLE_FUNCTIONS.filter(f => f.category === selectedCategory);

  return (
    <>
      {/* Toggle Button */}
      <motion.button
        onClick={onToggle}
        className="fixed left-4 top-1/2 -translate-y-1/2 z-50 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-r-lg p-2 shadow-lg hover:shadow-xl transition-all duration-200"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {isOpen ? (
          <ChevronLeftIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        ) : (
          <ChevronRightIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        )}
      </motion.button>

      {/* Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: -320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -320, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="fixed left-0 top-0 h-full w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 shadow-xl z-40 overflow-hidden"
          >
            <div className="h-full flex flex-col">
              {/* Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <span className="text-xl">🎯</span>
                  Available Functions
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Voice commands you can use
                </p>
              </div>

              {/* Category Filter */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <button
                      key={category}
                      onClick={() => setSelectedCategory(category)}
                      className={`px-3 py-1 text-xs font-medium rounded-full transition-all duration-200 ${
                        selectedCategory === category
                          ? "bg-blue-500 text-white shadow-md"
                          : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>

              {/* Functions List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {filteredFunctions.map((func, index) => (
                  <motion.div
                    key={func.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all duration-200"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{func.icon}</span>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 dark:text-white text-sm">
                          {func.name}
                        </h3>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {func.description}
                        </p>
                        <div className="mt-2">
                          <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Try saying:
                          </p>
                          <div className="space-y-1">
                            {func.examples.slice(0, 2).map((example, i) => (
                              <div
                                key={i}
                                className="text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-700 px-2 py-1 rounded border-l-2 border-blue-200 dark:border-blue-600"
                              >
                                "{example}"
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Footer */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
                <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  <p>💡 Speak naturally - the AI will understand your intent!</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
