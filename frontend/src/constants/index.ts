// Frontend application constants
export const APP_CONFIG = {
  // Application metadata
  APP_NAME: 'Parlay App',
  APP_VERSION: '1.0.0',
  APP_DESCRIPTION: 'Your ultimate sports betting companion',
  
  // API configuration
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // UI configuration
  MAX_CARDS_PER_ROW: 3,
  DEFAULT_PAGE_SIZE: 10,
  
  // Feature flags
  ENABLE_DARK_MODE: true,
  ENABLE_ANALYTICS: false,
  
  // Routes
  ROUTES: {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    DASHBOARD: '/dashboard',
  },
  
  // Local storage keys
  STORAGE_KEYS: {
    AUTH_TOKEN: 'auth_token',
    USER_PREFERENCES: 'user_preferences',
    THEME_MODE: 'theme_mode',
  },
  
  // Validation rules
  VALIDATION: {
    MIN_PASSWORD_LENGTH: 8,
    MAX_USERNAME_LENGTH: 30,
    MIN_USERNAME_LENGTH: 3,
  },
  
  // Error messages
  ERROR_MESSAGES: {
    NETWORK_ERROR: 'Network error. Please check your connection.',
    UNAUTHORIZED: 'You are not authorized to perform this action.',
    VALIDATION_ERROR: 'Please check your input and try again.',
    GENERIC_ERROR: 'Something went wrong. Please try again.',
  },
  
  // Success messages
  SUCCESS_MESSAGES: {
    LOGIN_SUCCESS: 'Welcome back!',
    REGISTER_SUCCESS: 'Account created successfully!',
    PROFILE_UPDATED: 'Profile updated successfully!',
  },
} as const;

// Export individual constants for easier imports
export const APP_NAME = APP_CONFIG.APP_NAME;
export const APP_VERSION = APP_CONFIG.APP_VERSION;
export const API_BASE_URL = APP_CONFIG.API_BASE_URL;
export const ROUTES = APP_CONFIG.ROUTES;
export const STORAGE_KEYS = APP_CONFIG.STORAGE_KEYS;
