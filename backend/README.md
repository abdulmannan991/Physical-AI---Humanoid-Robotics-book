# RAG Chatbot Backend (v2.0.0)

> **Intelligent Q&A System for Physical AI & Humanoid Robotics Course**

This backend subsystem implements a Retrieval-Augmented Generation (RAG) chatbot that enables natural language queries over the course content using FastAPI, Qdrant vector database, and modern LLM integration.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Governance](#governance)

## Architecture

```
┌─────────────────┐
│  Docusaurus UI  │
│  (v1.x Book)    │
└────────┬────────┘
         │
         │ HTTP
         ↓
┌──────────────────────────────────────────────────────────┐
│          FastAPI Backend (v2.0.0) - Dockerized          │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌────────────┐  ┌─────────┐  ┌─────┐│
│  │  API Routes  │→ │  Services  │→ │  Qdrant │  │Neon ││
│  │              │  │            │  │ Vector  │  │ DB  ││
│  │  - /chat     │  │  - RAG     │  │   DB    │  │     ││
│  │  - /ingest   │  │  - Embed   │  └─────────┘  │Meta ││
│  │  - /health   │  │  - LLM     │               │data ││
│  │              │  │  - DB      │               │Logs ││
│  └──────────────┘  └────────────┘               └─────┘│
└──────────────────────────────────────────────────────────┘
         ↓           ↓            ↓
   ┌─────────┐  ┌────────┐  ┌──────────────┐
   │   LLM   │  │Cohere  │  │  Content     │
   │ (GPT-4/ │  │Embed   │  │  Ingestion   │
   │ Claude) │  │ API    │  │  Pipeline    │
   └─────────┘  └────────┘  └──────────────┘
```

## Prerequisites

- **Python**: 3.11 or higher
- **Docker**: For running Qdrant locally and containerizing the backend
- **Docker Compose**: For local development orchestration
- **Poetry**: Dependency management (or pip + venv)
- **API Keys**:
  - OpenAI or Anthropic (for LLM)
  - Cohere (for embeddings)
  - Neon PostgreSQL (connection string)
  - Optional: Qdrant Cloud

## Quick Start

### 1. Clone & Navigate

```bash
cd backend
```

### 2. Install Dependencies

Using Poetry (recommended):

```bash
poetry install
poetry shell
```

Or using pip:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Qdrant (Local Development)

```bash
docker-compose up -d
```

This starts Qdrant on `http://localhost:6333`.

### 4. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Cohere (for embeddings)
COHERE_API_KEY=your-cohere-api-key-here

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty for local Docker instance

# Neon PostgreSQL
DATABASE_URL=postgresql://user:password@ep-example.us-east-2.aws.neon.tech/neondb?sslmode=require

# Embedding Model (Cohere)
EMBEDDING_MODEL_NAME=embed-english-v3.0

# CORS
CORS_ORIGINS=http://localhost:3000

# Admin
ADMIN_API_KEY=your-secret-admin-key
```

### 5. Ingest Course Content

Run the ingestion script to populate the vector database:

```bash
python -m app.scripts.ingest
```

This will:
1. Parse all Markdown files from `/docs/`
2. Chunk content intelligently
3. Generate embeddings
4. Upload to Qdrant

### 6. Start the API

```bash
uvicorn app.main:app --reload --port 8000
```

API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py           # Chat endpoint
│   │   ├── health.py         # Health check
│   │   └── ingest.py         # Admin ingestion endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Environment variables & settings
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── middleware.py     # CORS, rate limiting, etc.
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py       # Pydantic request models
│   │   └── responses.py      # Pydantic response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embeddings.py     # Embedding generation
│   │   ├── llm.py            # LLM client (OpenAI/Anthropic)
│   │   ├── qdrant.py         # Qdrant client & operations
│   │   └── rag.py            # RAG orchestration
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── ingest.py         # Content ingestion script
│   └── main.py               # FastAPI app entry point
├── data/
│   ├── qdrant/               # Qdrant data (gitignored)
│   └── raw/                  # Optional: cached parsed content
├── tests/
│   ├── __init__.py
│   ├── test_api.py           # API endpoint tests
│   ├── test_rag.py           # RAG pipeline tests
│   └── test_services.py      # Service unit tests
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   │   └── 001-why-qdrant.md
│   └── api.md                # Extended API documentation
├── .env.example              # Environment variables template
├── .gitignore
├── docker-compose.yml        # Qdrant + optional services
├── pyproject.toml            # Poetry dependencies
├── requirements.txt          # Pip dependencies (generated from pyproject.toml)
├── README.md                 # This file
└── .specify/
    └── memory/
        └── constitution.md   # Backend governance (v2.0.0)
```

## API Documentation

### Core Endpoints

#### `POST /api/v1/chat`

Send a question and receive a RAG-powered response.

**Request:**
```json
{
  "query": "What is the Perception-Action Loop?",
  "top_k": 5,
  "stream": false
}
```

**Response:**
```json
{
  "answer": "The Perception-Action Loop is a fundamental concept...",
  "sources": [
    {
      "chapter": "Module 1: Physical AI Foundations",
      "section": "Understanding the Perception-Action Loop",
      "url": "/docs/01-intro/perception-action-loop",
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.87
}
```

#### `GET /api/v1/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "qdrant_status": "connected",
  "llm_status": "available"
}
```

#### `POST /api/v1/ingest` (Admin Only)

Trigger content re-ingestion.

**Headers:**
```
X-API-Key: your-admin-api-key
```

**Response:**
```json
{
  "status": "success",
  "chunks_ingested": 1247,
  "duration_seconds": 45.2
}
```

### Interactive Docs

Visit `/docs` (Swagger UI) or `/redoc` for interactive API documentation.

## Configuration

All configuration is managed via environment variables (`.env` file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key (if using GPT models) |
| `ANTHROPIC_API_KEY` | Yes* | - | Anthropic API key (if using Claude) |
| `QDRANT_URL` | Yes | `http://localhost:6333` | Qdrant instance URL |
| `QDRANT_API_KEY` | No | - | Qdrant API key (for cloud) |
| `EMBEDDING_MODEL_NAME` | Yes | `all-MiniLM-L6-v2` | Hugging Face model name |
| `CORS_ORIGINS` | Yes | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `ADMIN_API_KEY` | Yes | - | Secret key for admin endpoints |
| `MAX_CHUNK_SIZE` | No | `512` | Max tokens per content chunk |
| `RETRIEVAL_TOP_K` | No | `5` | Default number of chunks to retrieve |
| `CONFIDENCE_THRESHOLD` | No | `0.6` | Minimum confidence for answering |

*One of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is required.

## Development

### Code Quality Tools

Format code:
```bash
black app/ tests/
isort app/ tests/
```

Lint code:
```bash
ruff app/ tests/
```

Type check:
```bash
mypy app/
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

Run specific test file:
```bash
pytest tests/test_rag.py -v
```

## Deployment

### Docker Deployment (Local & Production)

#### Local Development with Docker

Run the full stack (FastAPI + Qdrant) using Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

This starts:
- **Qdrant**: http://localhost:6333 (vector database)
- **FastAPI Backend**: http://localhost:8000 (API server)

#### Docker Production Build

Build the backend image:
```bash
docker build -t rag-backend:2.0.0 .
```

Run in production mode:
```bash
docker run -d \
  --name rag-backend \
  -p 8000:8000 \
  --env-file .env \
  rag-backend:2.0.0
```

Or use docker-compose for production:
```bash
docker-compose -f docker-compose.yml up -d
```

### Cloud Deployment (Recommended)

#### Option 1: Railway

1. Connect GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Use Qdrant Cloud for vector database
4. Deploy automatically on push to `main`

#### Option 2: Render

1. Create new Web Service on Render
2. Link GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Environment-Specific Configs

- **Development**: Local Qdrant (Docker), debug logging enabled
- **Staging**: Qdrant Cloud, moderate rate limits, logging to file
- **Production**: Qdrant Cloud, strict rate limits, structured logging (JSON), APM monitoring

## Governance

This backend subsystem follows its own constitution at `backend/.specify/memory/constitution.md` (v2.0.0).

**Key Rules:**
1. **Isolation**: ALL backend code lives in `/backend`. ZERO modifications to Docusaurus book (v1.x).
2. **Spec-Kit Workflow**: Specification → Planning → Tasks → Implementation (no "vibe coding").
3. **Testing**: Minimum 80% code coverage required.
4. **Type Safety**: 100% type hints + `mypy` strict mode.
5. **Security**: No hardcoded secrets, API key authentication for admin endpoints, CORS whitelisting.

### Contributing

Before submitting a PR:
1. Read `backend/.specify/memory/constitution.md`
2. Ensure changes align with RAG principles
3. Run all tests and code quality checks
4. Update API documentation if endpoints changed
5. Reference this constitution in PR description

## Troubleshooting

### Qdrant Connection Error

**Error:** `Failed to connect to Qdrant at http://localhost:6333`

**Solution:**
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not, start it
docker-compose up -d qdrant
```

### Embedding Model Download Issue

**Error:** `OSError: Can't load tokenizer for 'sentence-transformers/all-MiniLM-L6-v2'`

**Solution:**
```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Rate Limit Exceeded

**Error:** `429 Too Many Requests`

**Solution:** Implement caching or increase rate limit in `app/core/middleware.py`.

## License

This backend subsystem inherits the MIT License from the parent project.

---

**Version**: 2.0.0
**Last Updated**: 2025-12-13
**Constitution**: `backend/.specify/memory/constitution.md`
**Main Project**: [Physical AI & Humanoid Robotics Course](../README.md)
