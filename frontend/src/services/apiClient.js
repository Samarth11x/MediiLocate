/**
 * Standardized API client for MediLocate AI frontend.
 * Provides configurable base URL, timeout handling, and consistent error normalization.
 * Does not expose any secrets or credentials to client assets.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

let memoryCsrfToken =
  (typeof import.meta !== 'undefined' && import.meta.env?.MODE === 'test') ||
  (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test')
    ? 'test-csrf-token'
    : null;

export function setMemoryCsrfToken(token) {
  memoryCsrfToken = token;
}

export function getCsrfTokenFromCookie() {
  if (typeof document === 'undefined' || !document.cookie) return null;
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function getCsrfToken() {
  return memoryCsrfToken || getCsrfTokenFromCookie();
}

/**
 * Fetches CSRF token from the backend bootstrap endpoint.
 */
export async function fetchCsrfToken() {
  try {
    const res = await apiRequest('/api/v1/auth/csrf/', { method: 'GET' });
    if (res && res.csrfToken) {
      memoryCsrfToken = res.csrfToken;
      return res.csrfToken;
    }
  } catch {
    // Non-fatal; fallback to cookie
  }
  return getCsrfTokenFromCookie();
}

export class ApiError extends Error {
  constructor(message, status = 500, data = null, isNetworkError = false) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.isNetworkError = isNetworkError;
  }
}

/**
 * Execute HTTP fetch request with error handling and timeout.
 * @param {string} endpoint - Relative path (e.g. '/api/v1/search/medicines/')
 * @param {RequestInit} [options] - Fetch options
 * @param {number} [timeoutMs=10000] - Request timeout in milliseconds
 * @returns {Promise<any>}
 */
export async function apiRequest(endpoint, options = {}, timeoutMs = 10000) {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const method = (options.method || 'GET').toUpperCase();
  const isUnsafeMethod = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const headers = {
    'Accept': 'application/json',
    ...(options.headers || {}),
  };

  if (isUnsafeMethod && !headers['X-CSRFToken'] && !headers['x-csrftoken']) {
    const token = getCsrfToken();
    if (token) {
      headers['X-CSRFToken'] = token;
    }
  }

  if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
      credentials: options.credentials || 'include',
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const errorMessage =
        (typeof data === 'object' && (data?.error || data?.message || data?.detail)) ||
        `Request failed with HTTP status ${response.status}`;
      throw new ApiError(errorMessage, response.status, data, false);
    }

    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof ApiError) {
      throw error;
    }

    if (error.name === 'AbortError') {
      throw new ApiError('Request timed out after 10 seconds. Please check your connection.', 408, null, true);
    }

    // Network disconnection or server down
    throw new ApiError(
      'Unable to connect to the MediLocate API server. Please ensure the backend is running at ' + API_BASE_URL,
      0,
      null,
      true
    );
  }
}
