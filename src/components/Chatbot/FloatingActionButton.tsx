/**
 * Floating Action Button (FAB) Component
 *
 * A fixed button in the bottom-right corner that toggles the chatbot.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: FR-001 (56x56px FAB, bottom-right fixed)
 */

import React from 'react';
import styles from './ChatWidget.module.css';

interface FloatingActionButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  isOpen,
  onClick,
}) => {
  return (
    <button
      className={styles.fab}
      onClick={onClick}
      aria-label={isOpen ? 'Close chatbot' : 'Open chatbot'}
      title={isOpen ? 'Close chatbot' : 'Ask a question about the course'}
    >
      {isOpen ? (
        // Close icon (X)
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      ) : (
        // Chat icon
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      )}
    </button>
  );
};
