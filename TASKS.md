# Project Refactor Tasks

## Overview
Major refactor based on teacher requirements to switch LLM/Embedding providers and modernize the frontend with ChatKit.

## Requirements

### Backend Requirements
1. **LLM Provider**: Switch from Cohere to **Google Gemini** using the **Google Generative AI Python SDK**
   - Teacher requirement: "Apne agent sdk parha tha to wahi use karna hai"
   - Use official `google-generativeai` package
   - Implement Agent SDK pattern for chat completion

2. **Embeddings Provider**: Switch from Cohere to **OpenAI**
   - Model: `text-embedding-3-small`
   - Use official `openai` Python client

3. **Fix Server Crash**: Resolve `uvicorn main:app --reload` import error
   - Error: "Could not import module 'main'"
   - Ensure all imports (llm, embeddings) are correct
   - Proper initialization and error handling

### Frontend Requirements
1. **Library**: Replace custom chat UI with **React Chat UI Kit** (`@chatscope/chat-ui-kit-react`)
2. **Design Preservation**: Maintain the exact same visual design
   - Purple gradient theme (#667eea to #764ba2)
   - Floating action button
   - Chat window animations
   - Message bubbles styling
   - Citations display
   - Low confidence indicators
   - Text selection feature

### Documentation
1. Updated TASKS.md (this file)
2. Updated requirements.txt
3. .env.example with new API keys

## Deliverables

### Backend Files
- [X] `TASKS.md` - Updated requirements document
- [ ] `requirements.txt` - New dependencies (google-generativeai, openai)
- [ ] `.env.example` - API key templates
- [ ] `backend/app/services/llm.py` - Gemini SDK implementation
- [ ] `backend/app/services/embeddings.py` - OpenAI embeddings implementation
- [ ] `backend/app/main.py` - Fixed import errors

### Frontend Files
- [ ] `package.json` - Add @chatscope/chat-ui-kit-react dependency
- [ ] `src/components/Chatbot/ChatWidget.tsx` - ChatKit integration with custom styling
- [ ] `src/components/Chatbot/ChatWindow.tsx` - Refactored with ChatKit components
- [ ] `src/components/Chatbot/ChatMessage.tsx` - ChatKit message with custom styling
- [ ] `src/components/Chatbot/ChatWidget.module.css` - Custom styles for ChatKit components

## Implementation Status

### Phase 1: Backend Setup ✓
- [X] Document requirements
- [ ] Update dependencies
- [ ] Create environment template

### Phase 2: Backend Refactor
- [ ] Implement Gemini LLM service
- [ ] Implement OpenAI embeddings service
- [ ] Fix main.py imports and initialization

### Phase 3: Frontend Refactor
- [ ] Install ChatKit dependency
- [ ] Refactor ChatWidget with ChatKit components
- [ ] Apply custom styles to match existing design
- [ ] Preserve all existing features (citations, confidence, text selection)

### Phase 4: Testing & Validation
- [ ] Test backend server startup
- [ ] Verify LLM responses work with Gemini
- [ ] Verify embeddings work with OpenAI
- [ ] Test frontend chat functionality
- [ ] Verify design matches original

## Notes

### Old Implementation (Deprecated)
- ~~LLM: Cohere API~~
- ~~Embeddings: Cohere embed-english-v3.0~~
- ~~Frontend: Custom React components~~

### New Implementation (Current)
- **LLM**: Google Gemini (google-generativeai SDK)
- **Embeddings**: OpenAI text-embedding-3-small
- **Frontend**: React Chat UI Kit with custom styling

### Teacher Requirements
The teacher explicitly stated to use the Agent SDK pattern learned in class. This is implemented through:
1. Using Google's official `google-generativeai` Python SDK
2. Proper prompt engineering with system messages
3. Context injection for RAG (Retrieval-Augmented Generation)
4. Error handling and graceful degradation
