/**
 * Chat Input Component
 *
 * Input field with send button. Supports Enter to send, disables on empty/whitespace.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: FR-003 (Input field, Enter to send, clear after send)
 */

import React, { useState, useEffect, useRef, KeyboardEvent, ChangeEvent } from 'react';
import styles from './ChatWidget.module.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  initialValue?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  placeholder = 'Ask a question about the course...',
  initialValue = '',
}) => {
  const [input, setInput] = useState(initialValue);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Update input when initialValue changes (for text selection feature)
  useEffect(() => {
    if (initialValue) {
      setInput(initialValue);
      // Focus the input and move cursor to end
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.setSelectionRange(initialValue.length, initialValue.length);
      }
    }
  }, [initialValue]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setInput(''); // Clear after send
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  const isDisabled = disabled || !input.trim();

  return (
    <div className={styles.inputContainer}>
      <textarea
        ref={textareaRef}
        className={styles.input}
        value={input}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        aria-label="Chat input"
      />
      <button
        className={styles.sendButton}
        onClick={handleSend}
        disabled={isDisabled}
        aria-label="Send message"
        title={isDisabled ? 'Enter a message to send' : 'Send message'}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  );
};
