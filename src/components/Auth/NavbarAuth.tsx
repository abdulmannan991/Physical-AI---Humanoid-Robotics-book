/**
 * Navbar Authentication Component
 *
 * Displays Signup button when logged out, Logout button when logged in.
 * FIX: Keeps navbar visible during logout to show "Logging out..." animation.
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useHistory } from '@docusaurus/router';
import './NavbarAuth.css';

export const NavbarAuth: React.FC = () => {
  const { isAuthenticated, user, logout, isLoading } = useAuth();
  const history = useHistory();

  const handleLogout = async () => {
    try {
      await logout();
      history.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleSignup = () => {
    history.push('/signup');
  };

  const handleLogin = () => {
    history.push('/login');
  };

  const handleProfile = () => {
    history.push('/profile');
  };

  // FIX: Only hide the navbar if we are loading INITIAL session data (no user yet).
  // If we have a user and isLoading is true, it means we are logging out, so STAY VISIBLE.
  if (isLoading && !user) {
    return null;
  }

  return (
    <div className="navbar-auth">
      {isAuthenticated ? (
        <div className="navbar-auth-user">
          {user?.profile_image_url ? (
            <img
              src={user.profile_image_url}
              alt={user.username}
              className="navbar-auth-avatar"
              onClick={handleProfile}
            />
          ) : (
            <div className="navbar-auth-avatar-placeholder" onClick={handleProfile}>
              {user?.username?.charAt(0).toUpperCase()}
            </div>
          )}
          <span className="navbar-auth-username" onClick={handleProfile}>
            {user?.username}
          </span>
          
          {/* UPDATED LOGOUT BUTTON */}
          <button
            className="navbar-auth-button navbar-auth-logout"
            onClick={handleLogout}
            disabled={isLoading} // Disable button while processing
            style={{ minWidth: '100px' }} // Keeps width stable
          >
            {isLoading ? (
              // Loading State
              <>Logging out...</>
            ) : (
              // Normal State
              "Logout"
            )}
          </button>
        </div>
      ) : (
        <div className="navbar-auth-buttons">
          <button
            className="navbar-auth-button navbar-auth-login"
            onClick={handleLogin}
          >
            Login
          </button>
          <button
            className="navbar-auth-button navbar-auth-signup"
            onClick={handleSignup}
          >
            Sign Up
          </button>
        </div>
      )}
    </div>
  );
};