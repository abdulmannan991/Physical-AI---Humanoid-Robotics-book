# RAG Chatbot - Quick Start Guide

**Version**: 2.0.0
**Last Updated**: 2025-12-16

---

## 🚀 Quick Start (5 minutes)

Get the RAG Chatbot running in just 5 minutes!

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- API Keys:
  - **Cohere** (for embeddings): https://dashboard.cohere.com/
  - **OpenAI** or **Anthropic** (for LLM)
  - **Neon PostgreSQL** (connection string): https://neon.tech/

---

## Step 1: Backend Setup (3 minutes)

### 1.1 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or with Poetry:

```bash
poetry install
poetry shell
```

### 1.2 Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required
COHERE_API_KEY=your-cohere-api-key-here
DATABASE_URL=postgresql://user:password@ep-example.aws.neon.tech/neondb?sslmode=require
ADMIN_API_KEY=your-secret-admin-key

# Choose one LLM provider
OPENAI_API_KEY=sk-your-openai-key
# OR
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
LLM_PROVIDER=openai  # or "anthropic"
```

### 1.3 Start Qdrant (Vector Database)

```bash
docker-compose up -d qdrant
```

Verify it's running:

```bash
curl http://localhost:6333/health
```

### 1.4 Ingest Course Content

```bash
python scripts/run_ingestion.py
```

Expected output:
```
Ingestion Results
==================
Status: SUCCESS
Chunks ingested: 1247
Duration: 45.2s
```

### 1.5 Start Backend API

```bash
uvicorn app.main:app --reload --port 8000
```

Test it:

```bash
curl http://localhost:8000/api/v1/health
```

---

## Step 2: Frontend Setup (2 minutes)

### 2.1 Install Dependencies

```bash
cd ..  # Back to project root
yarn install
```

Or with npm:

```bash
npm install
```

### 2.2 Start Docusaurus

```bash
yarn start
```

Or:

```bash
npm start
```

---

## Step 3: Test the Chatbot! 🎉

1. Open http://localhost:3000
2. Look for the purple FAB (Floating Action Button) in the bottom-right corner
3. Click it to open the chatbot
4. Ask: **"What is the Perception-Action Loop?"**
5. You should get a response with citations!

---

## 🧪 Testing

### Backend Tests

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is inverse kinematics?",
    "top_k": 5
  }'
```

### Swagger UI

Interactive API documentation:
http://localhost:8000/docs

---

## 📝 What's Included

### Backend (FastAPI)
- ✅ `/api/v1/health` - System health check
- ✅ `/api/v1/chat` - RAG-powered Q&A endpoint
- ✅ Cohere embeddings (embed-english-v3.0)
- ✅ Qdrant vector database (HNSW indexing)
- ✅ Neon PostgreSQL (session metadata)
- ✅ OpenAI/Anthropic LLM integration
- ✅ Rate limiting (10 req/min)
- ✅ Input sanitization & security
- ✅ Confidence-based guardrails (< 0.6 → fallback)

### Frontend (React)
- ✅ Floating Action Button (FAB)
- ✅ Chat window with animations
- ✅ Message bubbles (user vs bot)
- ✅ Clickable citations
- ✅ Typing indicator
- ✅ Session storage (conversation history)
- ✅ Mobile responsive (< 768px)
- ✅ Scoped CSS (no global pollution)

---

## 🔧 Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Qdrant connection failed

**Error**: `Failed to connect to Qdrant`

**Solution**:
```bash
docker-compose up -d qdrant
docker ps  # Verify it's running
```

### Ingestion failed

**Error**: `No chunks parsed from docs folder`

**Solution**:
```bash
# Make sure you're in the backend directory
cd backend
# Check docs path in .env
DOCS_PATH=../docs
```

### Frontend can't reach backend

**Error**: `Failed to fetch` in browser console

**Solution**:
1. Make sure backend is running on port 8000
2. Check CORS settings in `backend/.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000
   ```
3. Update `src/components/Chatbot/useChatbot.ts` if using different port:
   ```typescript
   const API_BASE_URL = 'http://localhost:8000/api/v1';
   ```

### Rate limit errors

**Error**: `429 Too Many Requests`

**Solution**: Wait 1 minute or increase limit in `backend/.env`:
```env
RATE_LIMIT_PER_MINUTE=20
```

---

## 📚 Next Steps

### For Development

1. **Add Content**: Place Markdown files in `/docs`
2. **Re-ingest**: Run `python scripts/run_ingestion.py` after adding content
3. **Customize Styles**: Edit `src/components/Chatbot/ChatWidget.module.css`
4. **Change LLM**: Switch between OpenAI/Anthropic in `.env`

### For Production

1. **Use Qdrant Cloud**: Sign up at https://qdrant.tech/cloud/
2. **Deploy Backend**: Railway, Render, or AWS
3. **Deploy Frontend**: Vercel, Netlify, or Cloudflare Pages
4. **Environment Variables**: Set all API keys in production environment
5. **Update API URL**: Change `API_BASE_URL` in `useChatbot.ts` to production URL

---

## 📖 Documentation

- **Backend API**: http://localhost:8000/docs
- **Backend README**: `backend/README.md`
- **Implementation Status**: `IMPLEMENTATION_STATUS.md`
- **Constitution**: `backend/.specify/memory/constitution.md`
- **Specification**: `specs/002-rag-chatbot/spec.md`
- **Tasks**: `specs/002-rag-chatbot/tasks.md`

---

## 🆘 Need Help?

1. Check logs:
   - Backend: Terminal where `uvicorn` is running
   - Frontend: Browser DevTools console
   - Qdrant: `docker logs rag-chatbot-qdrant`

2. Verify services:
   ```bash
   # Qdrant
   curl http://localhost:6333/health

   # Backend
   curl http://localhost:8000/api/v1/health

   # Frontend
   # Open http://localhost:3000
   ```

3. Reset everything:
   ```bash
   # Stop all services
   docker-compose down

   # Clear Qdrant data
   rm -rf backend/data/qdrant

   # Re-run setup
   docker-compose up -d qdrant
   python backend/scripts/run_ingestion.py
   uvicorn app.main:app --reload --port 8000
   ```

---

**Status**: ✅ MVP Complete - Ready for Testing

**Completed**: 44/75 tasks (59%)
- Backend: 34/34 (100%) ✅
- Frontend: 10/10 (100%) ✅
- Docker: 1/4 (25%) ⚠️
- Admin Endpoint: 0/2 (0%) ❌
- Polish: 0/8 (0%) ❌

**Ready for Production?** Backend + Frontend MVP is complete and functional. Docker containerization, admin endpoint, and polish tasks are optional for basic functionality.
