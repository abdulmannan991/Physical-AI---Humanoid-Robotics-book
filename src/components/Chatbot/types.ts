/**
 * TypeScript Types for RAG Chatbot
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 */

export interface Citation {
  chapter: string;
  section: string;
  url: string;
  relevance_score: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  confidence?: number;
  timestamp: Date;
}

export interface ChatSession {
  session_id: string;
  messages: Message[];
  started_at: Date;
  last_activity_at: Date;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  selected_text?: string;
  top_k?: number;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  session_id: string;
}

export interface ChatbotState {
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
}

export interface UseChatbotReturn {
  // State
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  initialQuery: string;

  // Actions
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;
  sendMessage: (query: string) => Promise<void>;
  openWithSelectedText: (text: string) => void;
  clearInitialQuery: () => void;
  clearError: () => void;
}
