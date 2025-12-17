/**
 * Root Component (Docusaurus Theme Override)
 *
 * Wraps the entire Docusaurus app to inject the ChatWidget globally.
 *
 * Constitution: backend/.specify/memory/constitution.md (Section 2 - Frontend isolation)
 * Requirements: T044 (Minimal Docusaurus integration)
 *
 * This file is a theme override that adds the ChatWidget to all pages
 * without modifying any existing Docusaurus functionality.
 */

import React from 'react';
import ChatWidget from '../components/Chatbot/ChatWidget';

// This component wraps your entire application
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
