/**
 * API-related types
 */

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: number;
}

export interface WebSocketConfig {
  url: string;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}
