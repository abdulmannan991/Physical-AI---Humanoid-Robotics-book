/**
 * Main ChatWidget Component
 *
 * Composes all chatbot components and wires up the useChatbot hook.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: User Story 1 - Complete Q&A interaction, User Story 2 - Text Selection
 */

import React from 'react';
import { FloatingActionButton } from './FloatingActionButton';
import { ChatWindow } from './ChatWindow';
import { TextSelectionHandler } from './TextSelectionHandler';
import { useChatbot } from './useChatbot';

export const ChatWidget: React.FC = () => {
  const {
    isOpen,
    messages,
    isLoading,
    error,
    initialQuery,
    toggleChat,
    closeChat,
    sendMessage,
    openWithSelectedText,
    clearError,
  } = useChatbot();

  return (
    <>
      <TextSelectionHandler onTextSelected={openWithSelectedText} />
      <FloatingActionButton isOpen={isOpen} onClick={toggleChat} />
      <ChatWindow
        isOpen={isOpen}
        messages={messages}
        isLoading={isLoading}
        error={error}
        initialQuery={initialQuery}
        onClose={closeChat}
        onSendMessage={sendMessage}
        onClearError={clearError}
      />
    </>
  );
};

export default ChatWidget;
