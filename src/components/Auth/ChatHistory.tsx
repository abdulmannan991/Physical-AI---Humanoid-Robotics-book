/**
 * ChatHistory Component
 *
 * Displays user's chat session history with pagination.
 *
 * Features:
 * - List of chat sessions ordered by recent activity
 * - Session metadata (started date, last activity, message count)
 * - Pagination controls (load more)
 * - Click to view session details
 * - Responsive design (mobile, tablet, desktop)
 *
 * Constitution Reference: FR-028, FR-029 (Chat history with pagination)
 */

import React, { useState, useEffect } from 'react';
import { apiGet } from '../../utils/apiClient';
import { SessionDetails } from './SessionDetails';
import styles from './ChatHistory.module.css';

interface ChatSession {
  session_id: string;
  started_at: string;
  last_activity_at: string;
  message_count: number;
}

interface ChatHistoryProps {
  onViewSession?: (sessionId: string) => void;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({ onViewSession }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  const SESSIONS_PER_PAGE = 20;

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async (loadMore = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const offset = loadMore ? sessions.length : 0;
      const response = await apiGet(
        `/api/v1/profile/chat-history?limit=${SESSIONS_PER_PAGE}&offset=${offset}`
      );

      if (!response.ok) {
        throw new Error('Failed to load chat history');
      }

      const newSessions: ChatSession[] = await response.json();

      if (loadMore) {
        setSessions([...sessions, ...newSessions]);
      } else {
        setSessions(newSessions);
      }

      // If we received fewer sessions than requested, there are no more
      setHasMore(newSessions.length === SESSIONS_PER_PAGE);
      setPage(loadMore ? page + 1 : 0);
    } catch (err: any) {
      setError(err.message || 'Failed to load chat history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadMore = () => {
    fetchSessions(true);
  };

  const handleSessionClick = (sessionId: string) => {
    setSelectedSessionId(sessionId);
    if (onViewSession) {
      onViewSession(sessionId);
    }
  };

  const handleCloseModal = () => {
    setSelectedSessionId(null);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) {
      // Today - show time
      return `Today at ${date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })}`;
    } else if (diffInDays === 1) {
      return 'Yesterday';
    } else if (diffInDays < 7) {
      return `${diffInDays} days ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    }
  };

  if (isLoading && sessions.length === 0) {
    return (
      <div className={styles.chatHistory}>
        <h2>Chat History</h2>
        <div className={styles.loadingState}>
          <div className={styles.spinner}></div>
          <p>Loading chat history...</p>
        </div>
      </div>
    );
  }

  if (error && sessions.length === 0) {
    return (
      <div className={styles.chatHistory}>
        <h2>Chat History</h2>
        <div className={styles.errorState}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
            <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" strokeWidth="2" />
            <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" strokeWidth="2" />
          </svg>
          <p>{error}</p>
          <button onClick={() => fetchSessions()} className={styles.retryButton}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className={styles.chatHistory}>
        <h2>Chat History</h2>
        <div className={styles.emptyState}>
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
            <path
              d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p>No chat history yet</p>
          <p className={styles.emptyHint}>
            Start a conversation with the chatbot to see your history here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.chatHistory}>
      <div className={styles.header}>
        <h2>Chat History</h2>
        <p className={styles.count}>
          {sessions.length} session{sessions.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className={styles.sessionsList}>
        {sessions.map((session) => (
          <div
            key={session.session_id}
            className={styles.sessionCard}
            onClick={() => handleSessionClick(session.session_id)}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                handleSessionClick(session.session_id);
              }
            }}
          >
            <div className={styles.sessionHeader}>
              <div className={styles.sessionIcon}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div className={styles.sessionMeta}>
                <div className={styles.sessionDate}>
                  {formatDate(session.last_activity_at)}
                </div>
                <div className={styles.sessionMessages}>
                  {session.message_count} message{session.message_count !== 1 ? 's' : ''}
                </div>
              </div>
            </div>

            <div className={styles.sessionFooter}>
              <div className={styles.sessionTime}>
                Started {formatDate(session.started_at)}
              </div>
              <div className={styles.viewButton}>
                View →
              </div>
            </div>
          </div>
        ))}
      </div>

      {hasMore && (
        <div className={styles.loadMoreContainer}>
          <button
            onClick={handleLoadMore}
            className={styles.loadMoreButton}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className={styles.smallSpinner}></div>
                Loading...
              </>
            ) : (
              'Load More'
            )}
          </button>
        </div>
      )}

      {error && sessions.length > 0 && (
        <div className={styles.errorBanner}>
          Failed to load more sessions. Please try again.
        </div>
      )}

      {selectedSessionId && (
        <SessionDetails
          sessionId={selectedSessionId}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};
