/**
 * Profile View Component
 *
 * Displays user profile information with image upload capability.
 *
 * Features:
 * - Profile image upload
 * - Display username and email
 * - Account creation date
 * - Loading state
 * - Error handling
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { ProfileImageUpload } from './ProfileImageUpload';
import { ChatHistory } from './ChatHistory';
import { apiGet } from '../../utils/apiClient';
import styles from './ProfileView.module.css';

interface UserProfile {
  id: string;
  email: string;
  username: string;
  profile_image_url: string | null;
  created_at: string;
}

export const ProfileView: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiGet('/api/v1/profile');

      if (!response.ok) {
        throw new Error('Failed to load profile');
      }

      const data = await response.json();
      setProfile(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = async (newImageUrl: string) => {
    // Update local profile state
    if (profile) {
      setProfile({ ...profile, profile_image_url: newImageUrl });
    }

    // Refresh auth context to update navbar
    await refreshUser();
  };

  if (isLoading) {
    return (
      <div className={styles.profileContainer}>
        <div className={styles.loadingState}>
          <div className={styles.spinner}></div>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.profileContainer}>
        <div className={styles.errorState}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
            <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" strokeWidth="2" />
            <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" strokeWidth="2" />
          </svg>
          <p>{error}</p>
          <button onClick={fetchProfile} className={styles.retryButton}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  const createdDate = new Date(profile.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className={styles.profileContainer}>
      <div className={styles.profileHeader}>
        <h1>My Profile</h1>
        <p className={styles.subtitle}>Manage your account settings</p>
      </div>

      <div className={styles.profileContent}>
        <section className={styles.imageSection}>
          <h2>Profile Picture</h2>
          <ProfileImageUpload
            currentImageUrl={profile.profile_image_url}
            onUploadSuccess={handleUploadSuccess}
          />
        </section>

        <section className={styles.infoSection}>
          <h2>Account Information</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoField}>
              <label>Username</label>
              <div className={styles.fieldValue}>{profile.username}</div>
            </div>

            <div className={styles.infoField}>
              <label>Email Address</label>
              <div className={styles.fieldValue}>{profile.email}</div>
            </div>

            <div className={styles.infoField}>
              <label>Member Since</label>
              <div className={styles.fieldValue}>{createdDate}</div>
            </div>

            <div className={styles.infoField}>
              <label>Account ID</label>
              <div className={styles.fieldValue}>
                <code>{profile.id.substring(0, 8)}...</code>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.historySection}>
          <ChatHistory />
        </section>
      </div>
    </div>
  );
};
