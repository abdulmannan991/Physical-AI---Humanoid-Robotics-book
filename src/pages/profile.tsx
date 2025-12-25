/**
 * Profile Page
 *
 * Protected route for authenticated users to view and manage their profile.
 *
 * Features:
 * - Protected with ProtectedRoute component
 * - Profile image upload
 * - Account information display
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import React, { JSX } from 'react';
import Layout from '@theme/Layout';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { ProfileView } from '../components/Auth/ProfileView';

export default function ProfilePage(): JSX.Element {
  return (
    <ProtectedRoute>
      <Layout
        title="My Profile"
        description="Manage your account settings and profile information"
      >
        <ProfileView />
      </Layout>
    </ProtectedRoute>
  );
}
