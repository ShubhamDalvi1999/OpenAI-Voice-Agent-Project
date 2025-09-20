/**
 * Local storage service with type safety
 */

import { STORAGE_KEYS } from '@/constants/app';

export class StorageService {
  private static instance: StorageService;

  static getInstance(): StorageService {
    if (!StorageService.instance) {
      StorageService.instance = new StorageService();
    }
    return StorageService.instance;
  }

  setItem<T>(key: string, value: T): void {
    try {
      const serializedValue = JSON.stringify(value);
      localStorage.setItem(key, serializedValue);
    } catch (error) {
      console.error(`Failed to set item ${key}:`, error);
    }
  }

  getItem<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error(`Failed to get item ${key}:`, error);
      return null;
    }
  }

  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove item ${key}:`, error);
    }
  }

  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  }

  // Convenience methods for specific storage keys
  setChatHistory(history: any[]): void {
    this.setItem(STORAGE_KEYS.CHAT_HISTORY, history);
  }

  getChatHistory(): any[] | null {
    return this.getItem(STORAGE_KEYS.CHAT_HISTORY);
  }

  setUserPreferences(preferences: any): void {
    this.setItem(STORAGE_KEYS.USER_PREFERENCES, preferences);
  }

  getUserPreferences(): any | null {
    return this.getItem(STORAGE_KEYS.USER_PREFERENCES);
  }

  setAudioSettings(settings: any): void {
    this.setItem(STORAGE_KEYS.AUDIO_SETTINGS, settings);
  }

  getAudioSettings(): any | null {
    return this.getItem(STORAGE_KEYS.AUDIO_SETTINGS);
  }
}
