/**
 * Chat-related types
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  type: 'message' | 'function_call' | 'web_search' | 'handoff';
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface ChatHistory {
  messages: Message[];
  isLoading: boolean;
  agentName?: string;
}

export interface ChatConfig {
  maxMessages?: number;
  autoScroll?: boolean;
  showTimestamps?: boolean;
}
