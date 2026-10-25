/**
 * Authentication Context for MediLocate AI.
 * Coordinates user sessions, role identification, and state synchronization.
 * Sessions are securely restored via cookie verification upon mount.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext({
  user: null,
  role: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshUser = useCallback(async () => {
    try {
      const data = await authService.getCurrentUser();
      if (data && data.authenticated && data.user) {
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch (err) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (username, password) => {
    setError(null);
    try {
      const data = await authService.login(username, password);
      if (data && data.authenticated && data.user) {
        setUser(data.user);
        return { success: true, user: data.user };
      }
      throw new Error(data.message || 'Login failed.');
    } catch (err) {
      setError(err.message || 'Authentication failed.');
      throw err;
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      const data = await authService.register(userData);
      if (data && data.authenticated && data.user) {
        setUser(data.user);
        return { success: true, user: data.user };
      }
      throw new Error(data.message || 'Registration failed.');
    } catch (err) {
      setError(err.message || 'Registration failed.');
      throw err;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
    }
  };

  const role = user ? (user.role || (user.is_admin ? 'ADMIN' : 'USER')) : null;

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
