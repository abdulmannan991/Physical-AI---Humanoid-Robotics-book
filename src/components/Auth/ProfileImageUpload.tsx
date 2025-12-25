/**
 * Profile Image Upload Component
 *
 * Allows users to upload and update their profile image.
 *
 * Features:
 * - Client-side image validation (size ≤5MB, format JPG/PNG/WebP)
 * - Base64 encoding for upload
 * - Image preview before upload
 * - Loading state during upload
 * - Error handling
 *
 * Constitution: .specify/memory/constitution.md (Section 7)
 */

import React, { useState, useRef } from 'react';
import { apiPost } from '../../utils/apiClient';
import styles from './ProfileImageUpload.module.css';

interface ProfileImageUploadProps {
  currentImageUrl: string | null;
  onUploadSuccess: (newImageUrl: string) => void;
}

export const ProfileImageUpload: React.FC<ProfileImageUploadProps> = ({
  currentImageUrl,
  onUploadSuccess,
}) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(currentImageUrl);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const MAX_SIZE_MB = 5;
  const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Reset error
    setError(null);

    // Client-side validation
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Invalid format. Please upload JPG, PNG, or WebP image.');
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      setError(`Image size exceeds ${MAX_SIZE_MB}MB limit.`);
      return;
    }

    // Generate preview
    const reader = new FileReader();
    reader.onload = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!previewUrl || previewUrl === currentImageUrl) {
      setError('Please select a new image to upload.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      // Upload image
      const response = await apiPost('/api/v1/profile/image', {
        image_data: previewUrl,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload image');
      }

      const data = await response.json();
      onUploadSuccess(data.profile_image_url);

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.');
      // Revert preview to current image
      setPreviewUrl(currentImageUrl);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCancel = () => {
    setPreviewUrl(currentImageUrl);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const hasChanges = previewUrl !== currentImageUrl;

  return (
    <div className={styles.uploadContainer}>
      <div className={styles.previewSection}>
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Profile preview"
            className={styles.profilePreview}
          />
        ) : (
          <div className={styles.placeholderAvatar}>
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
              <path
                d="M6 21C6 17.134 8.686 14 12 14s6 3.134 6 7"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </div>
        )}
      </div>

      <div className={styles.controlsSection}>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileSelect}
          className={styles.fileInput}
          id="profile-image-input"
          disabled={isUploading}
        />
        <label htmlFor="profile-image-input" className={styles.selectButton}>
          Choose Image
        </label>

        {hasChanges && (
          <div className={styles.actionButtons}>
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className={styles.uploadButton}
            >
              {isUploading ? 'Uploading...' : 'Upload'}
            </button>
            <button
              onClick={handleCancel}
              disabled={isUploading}
              className={styles.cancelButton}
            >
              Cancel
            </button>
          </div>
        )}

        <p className={styles.hint}>JPG, PNG, or WebP (max {MAX_SIZE_MB}MB)</p>

        {error && (
          <div className={styles.errorMessage}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" strokeWidth="2" />
              <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" strokeWidth="2" />
            </svg>
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};
