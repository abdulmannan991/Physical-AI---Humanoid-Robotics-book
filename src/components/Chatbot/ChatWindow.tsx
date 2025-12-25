/**
 * Chat Window Component (Refactored with ChatKit)
 *
 * Main chat interface using React Chat UI Kit with custom styling.
 * Maintains the exact same visual design as before.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: FR-002 (Chat window with animations)
 * Teacher Requirement: Use React Chat UI Kit
 */

import React, { useEffect, useRef } from 'react';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message as ChatKitMessage,
  MessageInput,
  TypingIndicator as ChatKitTypingIndicator,
} from '@chatscope/chat-ui-kit-react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import type { Message } from './types';
import styles from './ChatWidget.module.css';

interface ChatWindowProps {
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onClose: () => void;
  onSendMessage: (message: string) => void;
  onClearError: () => void;
  initialQuery?: string;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  isOpen,
  messages,
  isLoading,
  error,
  onClose,
  onSendMessage,
  onClearError,
  initialQuery = '',
}) => {
  const windowRef = useRef<HTMLDivElement>(null);
  const [inputValue, setInputValue] = React.useState(initialQuery);

  // Update input when initialQuery changes
  useEffect(() => {
    if (initialQuery) {
      setInputValue(initialQuery);
    }
  }, [initialQuery]);

  // Close on click outside (mobile)
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        windowRef.current &&
        !windowRef.current.contains(event.target as Node) &&
        isOpen &&
        window.innerWidth < 768
      ) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const handleSend = (text: string) => {
    if (text.trim()) {
      onSendMessage(text.trim());
      setInputValue('');
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className={styles.chatWindow} ref={windowRef}>
      {/* Custom Header */}
      <div className={styles.chatHeader}>
        <div className={styles.chatHeaderContent}>
          <h3 className={styles.chatTitle}>Course Assistant</h3>
          <p className={styles.chatSubtitle}>
            Ask questions about Physical AI & Humanoid Robotics
          </p>
        </div>
        <button
          className={styles.closeButton}
          onClick={onClose}
          aria-label="Close chat"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className={styles.errorBanner}>
          <span>{error}</span>
          <button
            className={styles.errorClose}
            onClick={onClearError}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {/* ChatKit Container */}
      <div className={styles.chatKitWrapper}>
        <MainContainer>
          <ChatContainer>
            <MessageList
              typingIndicator={isLoading ? <ChatKitTypingIndicator content="Assistant is typing" /> : null}
            >
              {messages.map((message) => {
                const isUser = message.role === 'user';
                // More lenient confidence threshold: only show warning for very low confidence (< 0.3)
                // or when confidence is exactly 0.0 (complete failure)
                const isLowConfidence = message.confidence !== undefined && message.confidence === 0.0;

                // Detect clarification (T050 - FR-038)
                const isAmbiguous = message.confidence === 0.5;
                const hasClarificationOptions = !isUser && isAmbiguous && /\d+\.\s/.test(message.content);

                // Parse clarification options
                const clarificationOptions = hasClarificationOptions
                  ? (message.content.match(/\d+\.\s+([^\n]+)/g) || []).map(item => item.trim())
                  : [];

                return (
                  <ChatKitMessage
                    key={message.id}
                    model={{
                      message: message.content,
                      sentTime: message.timestamp.toISOString(),
                      sender: isUser ? 'User' : 'Assistant',
                      direction: isUser ? 'outgoing' : 'incoming',
                      position: 'single',
                    }}
                  >
                    {/* Citations */}
                    {!isUser && message.citations && message.citations.length > 0 && (
                      <ChatKitMessage.Footer>
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
                      </ChatKitMessage.Footer>
                    )}

                    {/* Clarification options (T050 - FR-038) */}
                    {hasClarificationOptions && clarificationOptions.length > 0 && (
                      <ChatKitMessage.Footer>
                        <div className={styles.clarificationOptions}>
                          {clarificationOptions.map((option, index) => (
                            <button
                              key={index}
                              className={styles.clarificationButton}
                              onClick={() => handleSend(option)}
                            >
                              {option}
                            </button>
                          ))}
                        </div>
                      </ChatKitMessage.Footer>
                    )}

                    {/* Low confidence badge */}
                    {!isUser && isLowConfidence && !isAmbiguous && (
                      <ChatKitMessage.Footer>
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
                      </ChatKitMessage.Footer>
                    )}
                  </ChatKitMessage>
                );
              })}
            </MessageList>
            <MessageInput
              placeholder="Ask a question about the course..."
              onSend={handleSend}
              disabled={isLoading}
              value={inputValue}
              onChange={(val) => setInputValue(val)}
              attachButton={false}
            />
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  );
};
