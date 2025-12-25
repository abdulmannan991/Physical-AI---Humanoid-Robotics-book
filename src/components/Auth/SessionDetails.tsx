/**
 * SessionDetails Component
 *
 * Displays full conversation history for a specific chat session.
 *
 * Features:
 * - Modal display of session conversation
 * - Message history (user queries + bot responses)
 * - Close button
 * - Responsive design
 * - Loading and error states
 *
 * Constitution Reference: FR-028, FR-029 (View session details)
 */

import React, { useState, useEffect } from 'react';
import { apiGet } from '../../utils/apiClient';
import styles from './SessionDetails.module.css';

interface Message {
  id: string;
  query_text: string;
  response_text: string;
  timestamp: string;
  confidence_score: number;
}

interface SessionDetailsProps {
  sessionId: string;
  onClose: () => void;
}

export const SessionDetails: React.FC<SessionDetailsProps> = ({ sessionId, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSessionDetails();
  }, [sessionId]);

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  const fetchSessionDetails = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiGet(`/api/v1/profile/sessions/${sessionId}`);

      if (!response.ok) {
        throw new Error('Failed to load session details');
      }

      const data: Message[] = await response.json();
      setMessages(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load session details');
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Prevent background scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>Session Details</h2>
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close modal"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" strokeWidth="2" />
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" strokeWidth="2" />
            </svg>
          </button>
        </div>

        <div className={styles.modalBody}>
          {isLoading && (
            <div className={styles.loadingState}>
              <div className={styles.spinner}></div>
              <p>Loading conversation...</p>
            </div>
          )}

          {error && (
            <div className={styles.errorState}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" strokeWidth="2" />
                <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" strokeWidth="2" />
              </svg>
              <p>{error}</p>
              <button onClick={fetchSessionDetails} className={styles.retryButton}>
                Try Again
              </button>
            </div>
          )}

          {!isLoading && !error && messages.length === 0 && (
            <div className={styles.emptyState}>
              <p>No messages found in this session.</p>
            </div>
          )}

          {!isLoading && !error && messages.length > 0 && (
            <div className={styles.messagesList}>
              {messages.map((message) => (
                <div key={message.id} className={styles.messageGroup}>
                  <div className={styles.userMessage}>
                    <div className={styles.messageHeader}>
                      <span className={styles.messageLabel}>You</span>
                      <span className={styles.messageTime}>
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                    <div className={styles.messageContent}>{message.query_text}</div>
                  </div>

                  <div className={styles.botMessage}>
                    <div className={styles.messageHeader}>
                      <span className={styles.messageLabel}>Bot</span>
                      {message.confidence_score > 0 && (
                        <span className={styles.confidence}>
                          {Math.round(message.confidence_score * 100)}% confidence
                        </span>
                      )}
                    </div>
                    <div className={styles.messageContent}>{message.response_text}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className={styles.modalFooter}>
          <button onClick={onClose} className={styles.closeFooterButton}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
