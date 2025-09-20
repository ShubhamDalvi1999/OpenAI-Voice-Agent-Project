/**
 * API-related constants
 */

export const API_ENDPOINTS = {
  WEBSOCKET: process.env.NEXT_PUBLIC_WEBSOCKET_ENDPOINT || 'ws://localhost:8000/ws',
  HEALTH: '/health',
  STATUS: '/status',
} as const;

export const WEBSOCKET_EVENTS = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  MESSAGE: 'message',
  ERROR: 'error',
  HISTORY_UPDATE: 'history.update',
  AUDIO_APPEND: 'input_audio_buffer.append',
  AUDIO_COMMIT: 'input_audio_buffer.commit',
} as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;
