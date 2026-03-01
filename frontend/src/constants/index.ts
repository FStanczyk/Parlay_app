export const APP_CONFIG = {
  APP_NAME: 'Philip Snat',
  APP_VERSION: '1.0.0',
  APP_DESCRIPTION: 'Your ultimate sports betting companion',
  API_BASE_URL: (process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/api/v1',
  MAX_CARDS_PER_ROW: 3,
  DEFAULT_PAGE_SIZE: 10,
  ENABLE_DARK_MODE: true,
  ENABLE_ANALYTICS: false,
  ROUTES: {
    HOME: '/',
    PHILIP_SNAT_MODELS: '/philip-snat-models',
    HUB: '/hub',
    GENERATOR: '/generator',
    EXPERTS_SEARCH: '/experts/search',
    EXPERTS_FOLLOWING: '/experts/following',
    EXPERTS_RECOMMENDATIONS: '/experts/recommendations',
    EXPERTS_STATS: (id: number | string) => `/experts/${id}/stats`,
    SIMULATOR: '/simulator',
    PROFILE_DASHBOARD: '/profile/dashboard',
    PROFILE_PARLAYS: '/profile/parlays',
    PROFILE_STATS: '/profile/stats',
    PROFILE_SETTINGS: '/profile/settings',
    PLANS: '/plans',
    BECOME_EXPERT: '/become-expert',
    EXPERT_PANEL: '/expert-panel',
    EXPERT_EDIT_PROFILE: '/expert-panel/edit-profile',
    EXPERT_RECOMMENDATIONS: '/expert-panel/recommendations',
    EXPERT_MONETIZATION: '/expert-panel/monetization',
    EXPERT_STATISTICS: '/expert-panel/statistics',
    ADMIN_PANEL: '/admin-panel',
    ADMIN_ADD_AI_PREDICTIONS: '/admin-panel/add-ai-predictions',
    ADMIN_USERS: '/admin-panel/users',
    LOGIN: '/login',
    REGISTER: '/register',
    DASHBOARD: '/dashboard',
    PRO_FEATURES: '/pro-features',
    ELITE_FEATURES: '/elite-features',
  },
  STORAGE_KEYS: {
    AUTH_TOKEN: 'auth_token',
    USER_PREFERENCES: 'user_preferences',
    THEME_MODE: 'theme_mode',
  },
  VALIDATION: {
    MIN_PASSWORD_LENGTH: 8,
    MAX_USERNAME_LENGTH: 30,
    MIN_USERNAME_LENGTH: 3,
  },
  ERROR_MESSAGES: {
    NETWORK_ERROR: 'Network error. Please check your connection.',
    UNAUTHORIZED: 'You are not authorized to perform this action.',
    VALIDATION_ERROR: 'Please check your input and try again.',
    GENERIC_ERROR: 'Something went wrong. Please try again.',
  },
  SUCCESS_MESSAGES: {
    LOGIN_SUCCESS: 'Welcome back!',
    REGISTER_SUCCESS: 'Account created successfully!',
    PROFILE_UPDATED: 'Profile updated successfully!',
  },
} as const;
export const APP_NAME = APP_CONFIG.APP_NAME;
export const APP_VERSION = APP_CONFIG.APP_VERSION;
export const API_BASE_URL = APP_CONFIG.API_BASE_URL;
export const ROUTES = APP_CONFIG.ROUTES;
export const STORAGE_KEYS = APP_CONFIG.STORAGE_KEYS;

console.log('🔍 Environment Debug:');
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
console.log('API_BASE_URL:', API_BASE_URL);
console.log('All env vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')));
