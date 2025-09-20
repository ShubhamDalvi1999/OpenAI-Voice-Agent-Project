/**
 * Application-wide constants
 */

export const APP_CONFIG = {
  NAME: 'Voice Agent Sample App',
  DESCRIPTION: 'Starter app for building voice agents using the OpenAI Agents SDK',
  VERSION: '1.0.0',
  AUTHOR: 'Voice Agent Team',
} as const;

export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
  SETTINGS: '/settings',
  ABOUT: '/about',
} as const;

export const STORAGE_KEYS = {
  CHAT_HISTORY: 'chat_history',
  USER_PREFERENCES: 'user_preferences',
  AUDIO_SETTINGS: 'audio_settings',
} as const;
