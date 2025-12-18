/**
 * useChatbot React Hook
 *
 * Manages chatbot state, API communication, and session storage.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: FR-029, FR-030, FR-031 (Session storage, history persistence)
 */

import { useState, useEffect, useCallback } from 'react';
import type {
  Message,
  ChatRequest,
  ChatResponse,
  UseChatbotReturn,
} from './types';

const API_BASE_URL = 'http://localhost:8001/api/v1';
const SESSION_STORAGE_KEY = 'chatbot_session';

interface StoredSession {
  session_id: string;
  messages: Message[];
}

export const useChatbot = (): UseChatbotReturn => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [initialQuery, setInitialQuery] = useState<string>('');

  // Load session from sessionStorage on mount
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (stored) {
        const session: StoredSession = JSON.parse(stored);
        setSessionId(session.session_id);
        setMessages(
          session.messages.map((msg) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          }))
        );
      } else {
        // No stored session - add welcome greeting
        const greetingMessage: Message = {
          id: 'greeting-initial',
          role: 'assistant',
          content: '🤖 I am Abdul Mannan\'s assistant. I can help you with the Physical AI Humanoid Robotics book.',
          timestamp: new Date(),
        };
        setMessages([greetingMessage]);
      }
    } catch (err) {
      console.error('Failed to load session from storage:', err);
    }
  }, []);

  // Save session to sessionStorage whenever it changes
  useEffect(() => {
    if (sessionId && messages.length > 0) {
      try {
        const session: StoredSession = {
          session_id: sessionId,
          messages,
        };
        sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
      } catch (err) {
        console.error('Failed to save session to storage:', err);
      }
    }
  }, [sessionId, messages]);

  const toggleChat = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const openChat = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearInitialQuery = useCallback(() => {
    setInitialQuery('');
  }, []);

  const sendMessage = useCallback(
    async (query: string) => {
      if (!query.trim()) return;

      // Clear any previous errors
      setError(null);

      // Add user message immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: query,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        // Prepare request
        const request: ChatRequest = {
          query,
          session_id: sessionId || undefined,
          top_k: 5,
        };

        // Call backend API
        const response = await fetch(`${API_BASE_URL}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `HTTP ${response.status}: ${response.statusText}`
          );
        }

        const data: ChatResponse = await response.json();

        // Update session ID if new
        if (data.session_id && data.session_id !== sessionId) {
          setSessionId(data.session_id);
        }

        // Add assistant message
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: data.answer,
          citations: data.citations,
          confidence: data.confidence,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        console.error('Chat API error:', err);
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to send message. Please try again.'
        );

        // Add error message to chat
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content:
            'Sorry, I encountered an error processing your request. Please try again.',
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  const openWithSelectedText = useCallback(
    (text: string) => {
      if (!text.trim()) return;

      // Open chat
      setIsOpen(true);

      // Prepend "Explain: " to the selected text
      const query = `Explain: ${text}`;

      // Set as initial query (will be pre-filled in input)
      setInitialQuery(query);

      // Auto-send after a short delay (optional - remove if you want user to review first)
      // setTimeout(() => {
      //   sendMessage(query);
      // }, 500);
    },
    []
  );

  return {
    // State
    isOpen,
    messages,
    isLoading,
    error,
    sessionId,
    initialQuery,

    // Actions
    toggleChat,
    openChat,
    closeChat,
    sendMessage,
    openWithSelectedText,
    clearInitialQuery,
    clearError,
  };
};
