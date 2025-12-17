# RAG Chatbot Testing Guide

**Version**: 2.0.0
**Date**: 2025-12-16

---

## ⚠️ Important Note

Before testing, you need to:
1. **Get API Keys** (Cohere, OpenAI/Anthropic, Neon PostgreSQL)
2. **Configure `.env` file** with your keys
3. **Install dependencies** (Python + Node.js)

---

## 🔑 Step 1: Get API Keys

### Required Services

1. **Cohere** (for embeddings)
   - Sign up: https://dashboard.cohere.com/
   - Create API key
   - Free tier available

2. **OpenAI** or **Anthropic** (for LLM)
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - Choose one (OpenAI recommended for testing)

3. **Neon PostgreSQL** (for session metadata)
   - Sign up: https://neon.tech/
   - Create database
   - Copy connection string

---

## 🚀 Step 2: Backend Setup

### 2.1 Navigate to Backend

```bash
cd backend
```

### 2.2 Install Dependencies

**Option A: Using pip**
```bash
python -m pip install -r requirements.txt
```

**Option B: Using Poetry (recommended)**
```bash
poetry install
poetry shell
```

### 2.3 Configure Environment

```bash
# Copy example to .env
cp .env.example .env
```

**Edit `backend/.env` with your API keys:**

```env
# Cohere (REQUIRED)
COHERE_API_KEY=your-cohere-api-key-here
EMBEDDING_MODEL_NAME=embed-english-v3.0

# LLM Provider (REQUIRED - choose one)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-your-openai-key-here

# OR use Anthropic
# LLM_PROVIDER=anthropic
# LLM_MODEL=claude-3-5-sonnet-20241022
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Neon PostgreSQL (REQUIRED)
DATABASE_URL=postgresql://user:password@ep-example.us-east-2.aws.neon.tech/neondb?sslmode=require

# Qdrant (local)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=course_content
QDRANT_VECTOR_SIZE=1024

# Admin (REQUIRED)
ADMIN_API_KEY=your-secret-admin-key-change-this

# CORS (REQUIRED for frontend)
CORS_ORIGINS=http://localhost:3000

# RAG Settings
RETRIEVAL_TOP_K=5
CONFIDENCE_THRESHOLD=0.6
MAX_CHUNK_SIZE=512
CHUNK_OVERLAP=50

# API Settings
RATE_LIMIT_PER_MINUTE=10
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### 2.4 Start Qdrant (Vector Database)

```bash
docker-compose up -d qdrant
```

**Verify Qdrant is running:**
```bash
curl http://localhost:6333/health
```

Expected output:
```json
{"title":"qdrant - vector search engine","version":"1.7.4"}
```

### 2.5 Ingest Course Content

```bash
python scripts/run_ingestion.py
```

**Expected output:**
```
==========================================
RAG Chatbot Content Ingestion
==========================================
Docs path: ../docs
Force reindex: False
Chunk size: 512 tokens
Chunk overlap: 50 tokens
Embedding model: embed-english-v3.0
==========================================

Step 1/3: Parsing Markdown files...
Found 25 Markdown files in ../docs
Parsed 25 files, 487 total chunks

Step 2/3: Generating embeddings...
Generated 487 embeddings in batch

Step 3/3: Storing in Qdrant...
Successfully stored 487 chunks

==========================================
Ingestion Results
==========================================
Status: SUCCESS
Chunks ingested: 487
Duration: 45.2s
==========================================

✓ Ingestion completed successfully!
```

### 2.6 Start Backend API

```bash
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['D:\\...\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🧪 Step 3: Test Backend API

**Open a new terminal** (keep backend running in the first terminal)

### 3.1 Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "qdrant_status": "available",
  "llm_status": "available",
  "database_status": "available",
  "embeddings_status": "available"
}
```

### 3.2 Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is inverse kinematics?",
    "top_k": 5
  }'
```

**Expected response:**
```json
{
  "answer": "Inverse kinematics is a mathematical process used in robotics to calculate the joint angles needed to position a robot's end-effector at a desired location...",
  "citations": [
    {
      "chapter": "Module 2: Robot Kinematics",
      "section": "Inverse Kinematics Fundamentals",
      "url": "/docs/02-kinematics/inverse-kinematics",
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.87,
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3.3 Test Out-of-Scope Question

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?",
    "top_k": 5
  }'
```

**Expected response (fallback message):**
```json
{
  "answer": "I cannot provide information related to this topic. However, if you have any queries regarding the 'Physical AI & Humanoid Robotics' book, let me know — I am here to assist you.",
  "citations": [],
  "confidence": 0.0,
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3.4 Test Swagger UI

Open in browser: http://localhost:8000/docs

You should see the interactive API documentation with:
- `GET /api/v1/health`
- `POST /api/v1/chat`

---

## 🎨 Step 4: Frontend Setup

**Open a new terminal** (keep backend running)

### 4.1 Navigate to Project Root

```bash
cd ..  # Go back to project root
```

### 4.2 Install Frontend Dependencies

```bash
yarn install
```

Or with npm:
```bash
npm install
```

### 4.3 Start Docusaurus

```bash
yarn start
```

Or:
```bash
npm start
```

**Expected output:**
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at http://localhost:3000/
```

---

## 🎯 Step 5: Test Chatbot UI

### 5.1 Open Browser

Navigate to: http://localhost:3000

### 5.2 Verify FAB Appears

- Look for a **purple circular button** in the bottom-right corner
- Size: 56x56px
- Icon: Chat bubble

### 5.3 Open Chat

1. **Click the FAB**
2. Chat window should **slide up** from the bottom (300ms animation)
3. Header should show: "Course Assistant"

### 5.4 Send a Message

1. Type in the input field: **"What is the Perception-Action Loop?"**
2. Press **Enter** or click **Send button**
3. Verify:
   - Your message appears (purple bubble, right-aligned)
   - Typing indicator shows (3 animated dots)
   - Bot response appears (white bubble, left-aligned)
   - Citations shown as blue clickable links
   - Response time < 5 seconds

### 5.5 Test Citation Links

1. Click on a citation link
2. Should navigate to the corresponding course page

### 5.6 Test Session History

1. Send 2-3 messages
2. **Close the chat** (click X button or FAB)
3. **Reopen the chat**
4. Verify: All previous messages are still visible

### 5.7 Test Mobile View

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Set viewport to **375px width** (iPhone SE)
4. Verify:
   - FAB is responsive
   - Chat fills 90% of viewport height
   - Input remains visible when typing
   - Tap outside closes chat

---

## ✅ Acceptance Test Checklist

### Backend Tests

- [ ] Qdrant is running (`curl http://localhost:6333/health`)
- [ ] Backend starts without errors
- [ ] Health check returns "healthy" status
- [ ] Chat endpoint returns valid response
- [ ] Out-of-scope questions return fallback message
- [ ] Session IDs are generated and returned
- [ ] Rate limiting works (try 11 requests in 1 minute)
- [ ] Swagger UI is accessible

### Frontend Tests

- [ ] FAB appears in bottom-right corner
- [ ] FAB has purple gradient background
- [ ] Click FAB opens chat window
- [ ] Chat window slides up smoothly (300ms)
- [ ] Header shows "Course Assistant"
- [ ] Close button works
- [ ] Input field accepts text
- [ ] Send button disabled when input is empty
- [ ] Enter key sends message
- [ ] User message appears (purple bubble)
- [ ] Typing indicator shows while loading
- [ ] Bot response appears (white bubble)
- [ ] Citations are clickable links
- [ ] Citation relevance scores displayed
- [ ] Messages have timestamps
- [ ] Auto-scrolls to bottom on new message
- [ ] Session history persists (close/reopen)
- [ ] Error messages display if backend is down
- [ ] Mobile responsive (< 768px)

### Integration Tests

- [ ] Frontend can reach backend (no CORS errors)
- [ ] Session ID persists across messages
- [ ] Low confidence responses show fallback message
- [ ] Citations link to correct course pages
- [ ] Multiple users can chat simultaneously (open in 2 tabs)

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

---

**Error**: `pydantic_core._pydantic_core.ValidationError: ... COHERE_API_KEY`

**Solution**: Missing API key in `.env` file
```bash
# Edit backend/.env and add:
COHERE_API_KEY=your-key-here
```

---

**Error**: `Failed to connect to Qdrant`

**Solution**: Start Qdrant
```bash
cd backend
docker-compose up -d qdrant
```

---

### Ingestion Failed

**Error**: `No chunks parsed from docs folder`

**Solution**: Check docs path
```bash
# In backend/.env, ensure:
DOCS_PATH=../docs
```

---

### Frontend Can't Reach Backend

**Error**: `Failed to fetch` in browser console

**Solution**: Check CORS and backend URL

1. Verify backend is running on port 8000
2. Check `backend/.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000
   ```
3. Check `src/components/Chatbot/useChatbot.ts`:
   ```typescript
   const API_BASE_URL = 'http://localhost:8000/api/v1';
   ```

---

### Rate Limit Errors

**Error**: `429 Too Many Requests`

**Solution**: Wait 1 minute or increase limit in `.env`:
```env
RATE_LIMIT_PER_MINUTE=20
```

---

## 📊 Expected Performance

### Backend
- Health check: < 100ms
- Chat endpoint (cold start): 3-5 seconds
- Chat endpoint (warm): 1-3 seconds
- Ingestion: 30-60 seconds (depends on content size)

### Frontend
- FAB click → Chat open: 300ms (animation)
- Message send → Response: 1-5 seconds (backend processing)
- Session load: < 100ms (sessionStorage)

---

## 🎥 Demo Script

Follow this script to demonstrate all features:

1. **Open chatbot**
   - Click FAB
   - Show slide-up animation

2. **Ask course question**
   - Type: "What is the Perception-Action Loop?"
   - Press Enter
   - Show typing indicator
   - Show response with citations
   - Click a citation to navigate

3. **Ask out-of-scope question**
   - Type: "What's the weather today?"
   - Show fallback message

4. **Test session history**
   - Close chat (click X)
   - Reopen chat (click FAB)
   - Show messages persist

5. **Test mobile view**
   - Open DevTools
   - Switch to mobile viewport (375px)
   - Show responsive design
   - Show tap-outside-to-close

6. **Test error handling**
   - Stop backend (Ctrl+C)
   - Try to send message
   - Show error message
   - Restart backend
   - Show recovery

---

## 🚀 Next Steps

### After Successful Testing

1. **Deploy Backend**
   - Railway: https://railway.app/
   - Render: https://render.com/
   - AWS/GCP/Azure

2. **Deploy Frontend**
   - Vercel: https://vercel.com/
   - Netlify: https://netlify.com/
   - Cloudflare Pages

3. **Update Configuration**
   - Change `API_BASE_URL` in `useChatbot.ts` to production URL
   - Update CORS_ORIGINS in backend `.env`
   - Use Qdrant Cloud instead of local Docker

4. **Monitor Performance**
   - Set up logging (Sentry, LogRocket)
   - Monitor API usage (OpenAI/Anthropic dashboard)
   - Track Qdrant performance

---

## 📝 Test Results Template

Use this template to document your test results:

```
RAG Chatbot Test Results
========================

Date: YYYY-MM-DD
Tester: [Your Name]

Backend Tests:
- [ ] Health check: PASS/FAIL
- [ ] Chat endpoint: PASS/FAIL
- [ ] Fallback message: PASS/FAIL
- [ ] Session management: PASS/FAIL

Frontend Tests:
- [ ] FAB display: PASS/FAIL
- [ ] Chat window animation: PASS/FAIL
- [ ] Message sending: PASS/FAIL
- [ ] Citation links: PASS/FAIL
- [ ] Session persistence: PASS/FAIL
- [ ] Mobile responsive: PASS/FAIL

Performance:
- Health check latency: ___ ms
- Chat response time: ___ seconds
- Ingestion time: ___ seconds

Issues Found:
1. [Describe issue]
2. [Describe issue]

Notes:
- [Any additional observations]
```

---

**Status**: Ready for testing! Follow the steps above to run and test the chatbot.

**Need Help?** Check the troubleshooting section or refer to `QUICKSTART.md`.
