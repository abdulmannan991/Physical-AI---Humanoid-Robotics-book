/**
 * Login Form Component
 *
 * Provides login UI with email, password, and "Remember Me" checkbox (T035).
 *
 * Features:
 * - Email and password input validation
 * - "Remember Me" checkbox (extends session to 7 days per FR-006)
 * - Error message display
 * - Loading state during API call
 * - Link to signup page
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import React, { useState, FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Toast } from '../Common/Toast';
import './AuthForms.css';

interface LoginFormProps {
  onSuccess?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const { login, isLoading, error: authError } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    // Client-side validation
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    try {
      await login(email, password, rememberMe);
      // Success - show toast and redirect immediately
      setShowSuccessToast(true);

      // Redirect immediately without waiting
      // The toast will be visible during the navigation
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      // Error is thrown from AuthProvider, extract message
      const errorMessage = err instanceof Error ? err.message : 'Login failed. Please try again.';
      setError(errorMessage);
      console.error('Login error:', errorMessage);
    }
  };

  return (
    <>
      {showSuccessToast && (
        <Toast
          message="You are logged in successfully"
          type="success"
          duration={1500}
          onClose={() => setShowSuccessToast(false)}
        />
      )}
      <div className="auth-form-container">
        <h2 className="auth-form-title">Log In</h2>

        <form onSubmit={handleSubmit} className="auth-form">
        {/* Email Input */}
        <div className="form-group">
          <label htmlFor="email" className="form-label">
            Email
          </label>
          <input
            type="email"
            id="email"
            className="form-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your.email@example.com"
            required
            autoComplete="email"
            disabled={isLoading}
          />
        </div>

        {/* Password Input */}
        <div className="form-group">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <div className="password-input-wrapper">
            <input
              type={showPassword ? "text" : "password"}
              id="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
              disabled={isLoading}
            />
            <button
              type="button"
              className="password-toggle-button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
              tabIndex={-1}
            >
              {showPassword ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <line x1="1" y1="1" x2="23" y2="23" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="12" cy="12" r="3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Remember Me Checkbox */}
        <div className="form-group form-checkbox-group">
          <input
            type="checkbox"
            id="rememberMe"
            className="form-checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            disabled={isLoading}
          />
          <label htmlFor="rememberMe" className="form-checkbox-label">
            Remember me for 7 days
          </label>
        </div>

        {/* Error Message */}
        {error && (
          <div className="auth-error" role="alert">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button type="submit" className="auth-submit-button" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Log In'}
        </button>

        {/* Link to Signup */}
        <div className="auth-alternate-link">
          Don't have an account?{' '}
          <a href="/signup" className="auth-link">
            Sign up
          </a>
        </div>
      </form>
    </div>
    </>
  );
};
