/**
 * Authentication Provider Component
 *
 * Provides global authentication state and functions to the application.
 * Uses React Context API for state management (T032).
 *
 * Features:
 * - User state management
 * - Login/logout/signup functions
 * - Session initialization on mount
 * - Automatic session expiry detection (T039)
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import React, { createContext, useState, useEffect, useMemo, useCallback, ReactNode } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { apiGet, apiPost } from '../../utils/apiClient';

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  profile_image_url: string | null;
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  refreshUser: () => Promise<void>;
  error: string | null;
}

// Create context
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Get API URL from Docusaurus config (fixes "process is not defined" error)
  const { siteConfig } = useDocusaurusContext();
const API_BASE_URL = 'http://localhost:8001';

  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Refresh current user from /api/v1/auth/me
   * Called on mount and after login/signup
   */
  const refreshUser = useCallback(async (): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        method: 'GET',
        credentials: 'include', // Send cookies
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setError(null);
      } else if (response.status === 401) {
        // Not authenticated (expected case)
        setUser(null);
      } else {
        throw new Error('Failed to fetch user');
      }
    } catch (err) {
      console.error('Error refreshing user:', err);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL]);

  /**
   * Initialize user session on component mount
   */
  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  /**
   * Login with email and password
   *
   * @param email User email
   * @param password User password
   * @param rememberMe Extend session to 7 days
   */
  const login = useCallback(async (email: string, password: string, rememberMe: boolean = false): Promise<void> => {
    try {
      setError(null);
      setIsLoading(true);

      console.log('[AUTH] Login attempt:', { email, API_BASE_URL });

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        credentials: 'include', // Send/receive cookies
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, remember_me: rememberMe }),
      });

      console.log('[AUTH] Login response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('[AUTH] Login failed:', errorData);
        throw new Error(errorData.detail || 'Login failed');
      }

      const userData = await response.json();
      console.log('[AUTH] Login success:', { userId: userData.id, email: userData.email });
      setUser(userData);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      console.error('[AUTH] Login error:', errorMessage);
      setError(errorMessage);
      throw err; // Re-throw for component error handling
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL]);

  /**
   * Sign up new user with email and password
   *
   * Note: User is NOT auto-logged in after signup (security best practice)
   * User must manually log in after account creation
   *
   * @param email User email
   * @param password User password (validated by backend)
   */
  const signup = useCallback(async (email: string, password: string): Promise<void> => {
    try {
      setError(null);
      setIsLoading(true);

      console.log('[AUTH] Signup attempt:', { email, API_BASE_URL });

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      console.log('[AUTH] Signup response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('[AUTH] Signup failed:', errorData);
        throw new Error(errorData.detail || 'Signup failed');
      }

      // Success - user created but NOT logged in
      // DO NOT set user state here
      console.log('[AUTH] Signup success - account created (not logged in)');
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Signup failed';
      console.error('[AUTH] Signup error:', errorMessage);
      setError(errorMessage);
      throw err; // Re-throw for component error handling
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL]);

  /**
   * Logout current user
   * Clears cookies on backend and resets local state
   */
  const logout = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true);

      await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include', // Clear cookies
      });

      setUser(null);
      setError(null);
    } catch (err) {
      console.error('Logout error:', err);
      // Still clear user locally even if API fails
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL]);

  /**
   * Memoize context value to prevent unnecessary re-renders
   *
   * NOTE: We intentionally do NOT include login, logout, signup, refreshUser in deps
   * because they are defined with useCallback below to maintain stable references.
   * Including them would cause infinite re-render loops.
   */
  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      logout,
      signup,
      refreshUser,
      error,
    }),
    [user, isLoading, error, login, logout, signup, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
