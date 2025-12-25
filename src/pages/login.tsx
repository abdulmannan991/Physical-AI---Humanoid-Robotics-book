/**
 * Login Page
 *
 * Displays LoginForm and handles redirect after successful login.
 * FIX: Keeps form mounted during loading to prevent state loss.
 */

import React, { JSX, useEffect } from 'react';
import Layout from '@theme/Layout';
import { useHistory, useLocation } from '@docusaurus/router';
import { LoginForm } from '../components/Auth/LoginForm';
import { useAuth } from '../hooks/useAuth';

export default function LoginPage(): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth();
  const history = useHistory();
  const location = useLocation();

  // Check for query parameters
  const searchParams = new URLSearchParams(location.search);
  const sessionExpired = searchParams.get('session_expired') === 'true';
  const signupSuccess = searchParams.get('signup_success') === 'true';

  // Redirect to home if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      console.log('User is authenticated. Redirecting to home...');
      history.push('/');
    }
  }, [isAuthenticated, isLoading, history]);

  // Handle successful login (Backup trigger in case useEffect is slow)
  const handleLoginSuccess = () => {
    console.log('Login success callback triggered. Redirecting to home...');
    history.push('/');
  };

  return (
    <Layout title="Log In" description="Log in to your account">
      <div style={{ padding: '2rem 0', minHeight: '70vh' }}>
        
        {/* Session Expired Alert */}
        {sessionExpired && (
          <div
            style={{
              maxWidth: '400px',
              margin: '0 auto 1rem',
              padding: '1rem',
              background: 'rgba(255, 165, 0, 0.1)',
              border: '1px solid rgba(255, 165, 0, 0.3)',
              borderRadius: '4px',
              textAlign: 'center',
              color: 'var(--ifm-color-warning)',
            }}
            role="alert"
          >
            ⚠️ Your session has expired. Please log in again.
          </div>
        )}

        {/* Signup Success Alert */}
        {signupSuccess && (
          <div
            style={{
              maxWidth: '400px',
              margin: '0 auto 1rem',
              padding: '1rem',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '4px',
              textAlign: 'center',
              color: 'var(--ifm-color-success)',
            }}
            role="alert"
          >
            ✓ Account created successfully. Please log in.
          </div>
        )}

        {/* LOADING INDICATOR - Displayed ABOVE form, not replacing it */}
        {isLoading && (
          <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
            <p>Verifying credentials...</p>
          </div>
        )}

        {/* Form must ALWAYS remain mounted */}
        <LoginForm onSuccess={handleLoginSuccess} />
      </div>
    </Layout>
  );
}