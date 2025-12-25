/**
 * Protected Route Component
 *
 * Wraps components that require authentication (T040).
 * Redirects unauthenticated users to /login per FR-012.
 *
 * Usage:
 * ```tsx
 * <ProtectedRoute>
 *   <ProfilePage />
 * </ProtectedRoute>
 * ```
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import React, { ReactNode, useEffect } from 'react';
import { useHistory } from '@docusaurus/router';
import { useAuth } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const history = useHistory();

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isLoading && !isAuthenticated) {
      history.push('/login');
    }
  }, [isAuthenticated, isLoading, history]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <p>Loading...</p>
      </div>
    );
  }

  // Show nothing if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  // Render children if authenticated
  return <>{children}</>;
};
