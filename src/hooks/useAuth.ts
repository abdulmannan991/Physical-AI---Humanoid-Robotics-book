/**
 * useAuth Hook
 *
 * Custom hook to access authentication context in components.
 * Provides type-safe access to auth state and functions (T033).
 *
 * Usage:
 * ```tsx
 * const { user, isAuthenticated, login, logout } = useAuth();
 * ```
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import { useContext } from 'react';
import { AuthContext, AuthContextType } from '../components/Auth/AuthProvider';

/**
 * Hook to access authentication context
 *
 * @returns AuthContext value with user state and auth functions
 * @throws Error if used outside AuthProvider
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};
