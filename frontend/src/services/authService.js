/**
 * Authentication service for MediLocate AI.
 * Communicates with backend session authentication endpoints.
 * Transmits zero secrets in URLs or local storage.
 */

import { apiRequest } from './apiClient';

export const authService = {
  /**
   * Fetches the current authenticated user session if one exists.
   * @returns {Promise<{ authenticated: boolean, user: object | null }>}
   */
  async getCurrentUser() {
    try {
      return await apiRequest('/api/v1/auth/me/');
    } catch {
      return { authenticated: false, user: null };
    }
  },

  /**
   * Logs in with username and password.
   * @param {string} username
   * @param {string} password
   * @returns {Promise<{ authenticated: boolean, user: object }>}
   */
  async login(username, password) {
    return await apiRequest('/api/v1/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  },

  /**
   * Registers a new User or Pharmacist account.
   * @param {object} userData
   * @returns {Promise<{ authenticated: boolean, user: object }>}
   */
  async register(userData) {
    return await apiRequest('/api/v1/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Terminates the current authenticated session.
   * @returns {Promise<{ authenticated: boolean }>}
   */
  async logout() {
    try {
      return await apiRequest('/api/v1/auth/logout/', {
        method: 'POST',
      });
    } catch {
      return { authenticated: false };
    }
  },
};
