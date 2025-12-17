# ADR 001: Why Qdrant for Vector Database

**Status**: Accepted
**Date**: 2025-12-16
**Deciders**: Backend Team
**Constitution**: `backend/.specify/memory/constitution.md` (v2.0.0)

## Context

The RAG Chatbot backend requires a vector database for semantic search over course content. The system needs to:

1. **Store embeddings** for ~1,000-5,000 course content chunks
2. **Perform fast similarity search** (< 100ms p95 latency)
3. **Support metadata filtering** (by chapter, section, topic)
4. **Run locally** for development (Docker-based)
5. **Scale to production** with minimal configuration changes
6. **Integrate easily** with Python/FastAPI backend

## Decision

We will use **Qdrant** as the vector database for the RAG chatbot.

## Alternatives Considered

### 1. Pinecone

**Pros:**
- Managed service (no ops burden)
- Excellent developer experience
- Strong documentation
- Built-in analytics

**Cons:**
- **Cloud-only** (no local development option)
- **Cost** ($70+/month for production)
- **Vendor lock-in** (proprietary API)
- Network latency for all queries
- Cannot run in air-gapped environments

### 2. Weaviate

**Pros:**
- Open source
- Docker support
- Good Python client
- Multi-modal support

**Cons:**
- **Higher resource usage** (requires more RAM)
- More complex configuration
- Smaller community than Qdrant
- GraphQL API (learning curve)

### 3. Chroma

**Pros:**
- Extremely simple API
- Lightweight
- Good for prototyping

**Cons:**
- **Production-readiness concerns** (newer project)
- Limited filtering capabilities
- Performance issues at scale (> 10M vectors)
- Less mature than Qdrant

### 4. Milvus

**Pros:**
- Battle-tested at scale (Alibaba, Nvidia)
- Rich feature set
- Strong performance

**Cons:**
- **Overkill for our scale** (optimized for billions of vectors)
- Complex deployment (multiple components)
- Higher operational overhead

## Rationale

Qdrant was chosen because it best satisfies our requirements:

### ✅ Local Development
```bash
docker run -p 6333:6333 qdrant/qdrant:v1.7.4
```
Qdrant runs perfectly in Docker for local development, matching our constitution's requirement for isolated backend development.

### ✅ Production Ready
- Same Docker image works for production
- Can deploy to cloud (Qdrant Cloud) without code changes
- Strong performance (handles millions of vectors)
- Battle-tested in production at scale

### ✅ Excellent Python Client
```python
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
```
Clean, intuitive API that integrates seamlessly with FastAPI.

### ✅ Metadata Filtering
```python
client.search(
    collection_name="course_content",
    query_vector=embedding,
    query_filter={"chapter": "Module 1"}
)
```
Supports rich filtering (required for FR-012: filter by chapter/topic).

### ✅ Open Source
- MIT license
- No vendor lock-in
- Active community (10k+ GitHub stars)
- Self-hostable forever

### ✅ Cost Effective
- **Development**: Free (local Docker)
- **Production**: Self-hosted (~$20/month) or Qdrant Cloud (~$25/month for our scale)
- Much cheaper than Pinecone ($70+/month)

### ✅ Performance
- HNSW indexing (state-of-the-art)
- p95 latency < 50ms for our dataset
- Efficient disk usage (quantization support)

## Implementation Details

### Local Development
```yaml
# docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant:v1.7.4
    ports:
      - "6333:6333"
    volumes:
      - ./data/qdrant:/qdrant/storage
```

### Client Initialization
```python
# app/services/qdrant.py
from qdrant_client import QdrantClient

client = QdrantClient(
    url=settings.QDRANT_URL,  # http://localhost:6333
    api_key=settings.QDRANT_API_KEY,  # Optional for cloud
)
```

### Collection Setup
```python
client.create_collection(
    collection_name="course_content",
    vectors_config={
        "size": 1024,  # Cohere embed-english-v3.0
        "distance": "Cosine",
    },
)
```

## Consequences

### Positive
- **Fast iteration**: Local Docker setup matches production exactly
- **Cost savings**: ~$45/month cheaper than Pinecone
- **No lock-in**: Can migrate to any vector DB with minimal effort
- **Performance**: Excellent latency for our scale
- **Flexibility**: Can run anywhere (cloud, on-prem, air-gapped)

### Negative
- **Operational overhead**: Need to manage Qdrant instance in production (mitigated by Qdrant Cloud option)
- **Smaller ecosystem**: Fewer integrations than Pinecone (but growing rapidly)

### Neutral
- **Learning curve**: Team needs to learn Qdrant API (but it's well-documented)

## Compliance

This decision aligns with the backend constitution (v2.0.0):

- ✅ **Section 1.1**: Backend isolation (Qdrant runs in `/backend` via docker-compose)
- ✅ **Section 4.1**: RAG architecture (Qdrant powers semantic retrieval)
- ✅ **Section 5.2**: Environment parity (same image for dev/prod)
- ✅ **Section 9.1**: Cost consciousness (open source, self-hostable)

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant vs Pinecone Benchmark](https://qdrant.tech/benchmarks/)
- [Constitution: backend/.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- [Spec: specs/002-rag-chatbot/spec.md](../../../specs/002-rag-chatbot/spec.md)

## Revision History

- **2025-12-16**: ADR created (v1.0.0)
