/**
 * Signup Page
 *
 * Displays SignupForm and handles redirect after successful signup.
 * FIX: Keeps form mounted during loading to prevent state loss.
 */

import React, { JSX, useEffect } from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import { SignupForm } from '../components/Auth/SignupForm';
import { useAuth } from '../hooks/useAuth';

export default function SignupPage(): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth();
  const history = useHistory();

  // Redirect to home if already authenticated
  useEffect(() => {
    // Only redirect if we are sure we are authenticated and NOT currently loading
    // (This prevents premature redirects during initial check)
    if (!isLoading && isAuthenticated) {
      history.push('/');
    }
  }, [isAuthenticated, isLoading, history]);

  // Handle successful signup
  const handleSignupSuccess = () => {
    console.log('Signup success callback triggered. Redirecting to login...');
    history.push('/login?signup_success=true');
  };

  return (
    <Layout title="Sign Up" description="Create a new account">
      <div style={{ padding: '2rem 0', minHeight: '70vh', position: 'relative' }}>
        
        {/* OPTIONAL: Show a global loading overlay if you want, 
            but DO NOT unmount the form below */}
        {isLoading && (
          <div style={{ 
            textAlign: 'center', 
            marginBottom: '1rem',
            color: 'var(--ifm-color-primary)'
          }}>
            <p>Processing account creation...</p>
          </div>
        )}

        {/* Form must ALWAYS remain mounted so it can receive the 'success' callback */}
        <SignupForm onSuccess={handleSignupSuccess} />
      </div>
    </Layout>
  );
}