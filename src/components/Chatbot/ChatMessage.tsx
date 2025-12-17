/**
 * Chat Message Component
 *
 * Displays individual messages with citations as clickable links.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: FR-004, FR-009 (Message bubbles, citations as links)
 */

import React from 'react';
import type { Message } from './types';
import styles from './ChatWidget.module.css';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isLowConfidence = message.confidence !== undefined && message.confidence < 0.6;

  return (
    <div className={`${styles.message} ${isUser ? styles.userMessage : styles.botMessage}`}>
      <div className={styles.messageContent}>
        <p>{message.content}</p>

        {/* Citations (only for assistant messages with citations) */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className={styles.citations}>
            <p className={styles.citationsHeader}>Sources:</p>
            <ul className={styles.citationsList}>
              {message.citations.map((citation, index) => (
                <li key={index} className={styles.citationItem}>
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.citationLink}
                  >
                    {citation.chapter} - {citation.section}
                  </a>
                  <span className={styles.citationScore}>
                    ({Math.round(citation.relevance_score * 100)}% relevant)
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Low confidence indicator (User Story 3) */}
        {!isUser && isLowConfidence && (
          <div className={styles.lowConfidenceBadge}>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>This question may be outside the course content</span>
          </div>
        )}
      </div>

      <div className={styles.messageTimestamp}>
        {message.timestamp.toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </div>
  );
};
