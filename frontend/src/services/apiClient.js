/**
 * Standardized API client for MediLocate AI frontend.
 * Provides configurable base URL, timeout handling, and consistent error normalization.
 * Does not expose any secrets or credentials to client assets.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

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

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const headers = {
    'Accept': 'application/json',
    ...(options.headers || {}),
  };

  if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
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
