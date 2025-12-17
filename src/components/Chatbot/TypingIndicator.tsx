/**
 * Typing Indicator Component
 *
 * Animated dots to show the chatbot is processing.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: Visual feedback during loading
 */

import React from 'react';
import styles from './ChatWidget.module.css';

export const TypingIndicator: React.FC = () => {
  return (
    <div className={styles.typingIndicator}>
      <div className={styles.typingDot}></div>
      <div className={styles.typingDot}></div>
      <div className={styles.typingDot}></div>
    </div>
  );
};
