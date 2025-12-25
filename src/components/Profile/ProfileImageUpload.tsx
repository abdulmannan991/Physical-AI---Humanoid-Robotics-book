/**
 * ProfileImageUpload Component
 *
 * Handles profile image upload with validation and preview.
 *
 * Features:
 * - Client-side validation (size ≤5MB, format: JPG/PNG/WebP)
 * - Image preview before upload
 * - Loading state during upload
 * - Error handling
 *
 * Constitution Reference: FR-019, FR-020, FR-021
 */

import React, { useState, useRef } from 'react';
import styles from './Profile.module.css';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export interface ProfileImageUploadProps {
  currentImageUrl?: string | null;
  onUploadSuccess: (imageUrl: string) => void;
  onUploadError: (error: string) => void;
}

export const ProfileImageUpload: React.FC<ProfileImageUploadProps> = ({
  currentImageUrl,
  onUploadSuccess,
  onUploadError
}) => {
  const [preview, setPreview] = useState<string | null>(currentImageUrl || null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Only JPG, PNG, and WebP images are allowed';
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
      return `Image is too large (${sizeMB}MB). Maximum size is 5MB`;
    }

    return null;
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Reset errors
    setError(null);

    // Validate file
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      onUploadError(validationError);
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload image
    await uploadImage(file);
  };

  const uploadImage = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      // Convert to base64
      const base64 = await fileToBase64(file);

      // Send to backend
      const response = await fetch('/api/v1/profile/image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include', // Send cookies
        body: JSON.stringify({ image_data: base64 })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to upload image');
      }

      const data = await response.json();
      onUploadSuccess(data.profile_image_url);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      onUploadError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        resolve(reader.result as string);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={styles.imageUpload}>
      <h3>Profile Picture</h3>

      <div className={styles.uploadContainer}>
        {preview && (
          <div className={styles.previewContainer}>
            <img
              src={preview}
              alt="Profile preview"
              className={styles.previewImage}
            />
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          className={styles.fileInput}
          disabled={isUploading}
        />

        <button
          type="button"
          onClick={handleButtonClick}
          className={styles.uploadButton}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : preview ? 'Change Picture' : 'Upload Picture'}
        </button>

        <p className={styles.uploadHint}>
          Max 5MB • JPG, PNG, or WebP
        </p>

        {isUploading && (
          <div className={styles.loadingSpinner}>
            <div className={styles.spinner}></div>
            <p>Uploading image...</p>
          </div>
        )}

        {error && (
          <div className={styles.errorMessage}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
};
