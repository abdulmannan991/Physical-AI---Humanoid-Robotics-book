/**
 * Root Component (Docusaurus Theme Override)
 *
 * Wraps the entire Docusaurus app to inject:
 * - AuthProvider for global authentication state (T034)
 * - ChatWidget for global chatbot access
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: T034 (Wrap app with AuthProvider), T044 (Minimal Docusaurus integration)
 *
 * This file is a theme override that adds global providers and the ChatWidget
 * to all pages without modifying any existing Docusaurus functionality.
 */

import React from 'react';
import { AuthProvider } from '../components/Auth/AuthProvider';
import ChatWidget from '../components/Chatbot/ChatWidget';

// This component wraps your entire application
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      {children}
      <ChatWidget />
    </AuthProvider>
  );
}
