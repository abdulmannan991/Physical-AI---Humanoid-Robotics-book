/**
 * ProfileView Component
 *
 * Displays user profile information (username, email, profile image).
 *
 * Constitution Reference: FR-016 (View profile)
 */

import React from 'react';
import styles from './Profile.module.css';

export interface ProfileViewProps {
  user: {
    id: string;
    email: string;
    username: string;
    profile_image_url?: string | null;
    created_at: string;
  };
}

export const ProfileView: React.FC<ProfileViewProps> = ({ user }) => {
  // Format creation date
  const formattedDate = new Date(user.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <div className={styles.profileView}>
      <div className={styles.profileHeader}>
        <div className={styles.profileImageContainer}>
          {user.profile_image_url ? (
            <img
              src={user.profile_image_url}
              alt={`${user.username}'s profile`}
              className={styles.profileImage}
            />
          ) : (
            <div className={styles.defaultAvatar}>
              {user.username.charAt(0).toUpperCase()}
            </div>
          )}
        </div>

        <div className={styles.profileInfo}>
          <h1 className={styles.username}>{user.username}</h1>
          <p className={styles.email}>{user.email}</p>
          <p className={styles.memberSince}>Member since {formattedDate}</p>
        </div>
      </div>
    </div>
  );
};
