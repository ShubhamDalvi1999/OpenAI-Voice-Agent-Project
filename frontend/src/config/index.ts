/**
 * Application configuration
 */

import { API_ENDPOINTS } from '@/constants/api';
import { APP_CONFIG } from '@/constants/app';

export const config = {
  app: APP_CONFIG,
  api: {
    websocketUrl: API_ENDPOINTS.WEBSOCKET,
    healthUrl: API_ENDPOINTS.HEALTH,
    statusUrl: API_ENDPOINTS.STATUS,
  },
  features: {
    audio: {
      enabled: true,
      autoStart: false,
    },
    chat: {
      enabled: true,
      maxHistory: 100,
    },
  },
  development: {
    enableLogging: process.env.NODE_ENV === 'development',
    enableDevTools: process.env.NODE_ENV === 'development',
  },
} as const;

export type AppConfig = typeof config;
