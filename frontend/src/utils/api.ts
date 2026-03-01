import { API_BASE_URL } from '../constants';

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

export const apiCall = async <T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const apiGet = <T>(endpoint: string): Promise<T> => {
  return apiCall<T>(endpoint, { method: 'GET' });
};

export const apiPost = <T>(endpoint: string, data?: any): Promise<T> => {
  return apiCall<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
};

export const apiPut = <T>(endpoint: string, data?: any): Promise<T> => {
  return apiCall<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
};

export const apiPatch = <T>(endpoint: string, data?: any): Promise<T> => {
  return apiCall<T>(endpoint, {
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  });
};

export const apiDelete = <T>(endpoint: string): Promise<T> => {
  return apiCall<T>(endpoint, { method: 'DELETE' });
};

export const apiPostFile = async <T>(
  endpoint: string,
  formData: FormData,
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
  }

  return response.json();
};

export const downloadFile = async (
  endpoint: string,
  filename: string,
): Promise<void> => {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
};

export const publicApiGet = <T>(endpoint: string): Promise<T> => {
  return apiGet<T>(endpoint);
};

export const publicApiPost = <T>(endpoint: string, data?: any): Promise<T> => {
  return apiPost<T>(endpoint, data);
};
