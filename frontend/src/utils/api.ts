// API utility functions for authenticated requests
const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

export const apiCall = async <T>(
  endpoint: string,
  options: RequestInit = {},
  requireAuth: boolean = true
): Promise<T> => {
  const token = localStorage.getItem('access_token');
  
  if (requireAuth && !token) {
    throw new Error('No authentication token found');
  }

  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Convenience methods for common HTTP verbs
export const apiGet = <T>(endpoint: string, requireAuth: boolean = true): Promise<T> => {
  return apiCall<T>(endpoint, { method: 'GET' }, requireAuth);
};

export const apiPost = <T>(endpoint: string, data?: any, requireAuth: boolean = true): Promise<T> => {
  return apiCall<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  }, requireAuth);
};

export const apiPut = <T>(endpoint: string, data?: any, requireAuth: boolean = true): Promise<T> => {
  return apiCall<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  }, requireAuth);
};

export const apiDelete = <T>(endpoint: string, requireAuth: boolean = true): Promise<T> => {
  return apiCall<T>(endpoint, { method: 'DELETE' }, requireAuth);
};

// Public API methods (no authentication required)
export const publicApiGet = <T>(endpoint: string): Promise<T> => {
  return apiGet<T>(endpoint, false);
};

export const publicApiPost = <T>(endpoint: string, data?: any): Promise<T> => {
  return apiPost<T>(endpoint, data, false);
};
