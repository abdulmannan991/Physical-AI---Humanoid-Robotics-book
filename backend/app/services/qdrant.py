"""
Qdrant Vector Database Service

Handles all vector database operations including collection management,
upserting embeddings, and similarity search.

Constitution: backend/.specify/memory/constitution.md (Section 4.1)
"""

import logging
from typing import List, Dict, Optional
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Qdrant vector database service.

    Manages collections, embeddings storage, and similarity search.
    """

    def __init__(self):
        """Initialize Qdrant client."""
        try:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=30.0
            )

            self.collection_name = settings.QDRANT_COLLECTION_NAME
            self.vector_size = settings.QDRANT_VECTOR_SIZE
            self._is_available = True

            logger.info(
                f"Qdrant client initialized: {settings.QDRANT_URL}, "
                f"collection: {self.collection_name}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            self._is_available = False
            self.client = None

    async def health_check(self) -> bool:
        """
        Check if Qdrant is available.

        Returns:
            True if Qdrant is healthy, False otherwise
        """
        if not self._is_available or not self.client:
            return False

        try:
            # Try to get collection info
            self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            logger.warning(f"Qdrant health check failed: {e}")
            return False

    def create_collection(self) -> bool:
        """
        Create Qdrant collection with HNSW indexing if it doesn't exist.

        Returns:
            True if collection created or already exists, False on error

        Constitution Reference: Section 4.1 (HNSW indexing for < 500ms search)
        """
        if not self._is_available or not self.client:
            logger.error("Qdrant client not available")
            return False

        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True

            # Create collection with HNSW index configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,  # Cosine similarity
                ),
                # HNSW index parameters (optimized for < 500ms search)
                hnsw_config={
                    "m": 16,  # Number of edges per node
                    "ef_construct": 100,  # Construction time/accuracy tradeoff
                },
            )

            logger.info(
                f"Created collection '{self.collection_name}' "
                f"with HNSW indexing (vector_size={self.vector_size})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            self._is_available = False
            return False

    def upsert_chunks(self, chunks: List[Dict]) -> bool:
        """
        Upsert content chunks with embeddings to Qdrant.

        Args:
            chunks: List of chunk dictionaries with keys:
                - chunk_id: str (UUID)
                - embedding: List[float] (vector)
                - source_file: str
                - chapter: str
                - section: str
                - url: str
                - raw_text: str
                - token_count: int

        Returns:
            True if successful, False otherwise

        Constitution Reference: Section 6 (Content ingestion - idempotent)
        """
        if not self._is_available or not self.client:
            logger.error("Qdrant client not available")
            return False

        if not chunks:
            logger.warning("No chunks to upsert")
            return True

        try:
            points = []
            for chunk in chunks:
                point = PointStruct(
                    id=chunk["chunk_id"],
                    vector=chunk["embedding"],
                    payload={
                        "source_file": chunk["source_file"],
                        "chapter": chunk["chapter"],
                        "section": chunk["section"],
                        "url": chunk["url"],
                        "raw_text": chunk["raw_text"],
                        "token_count": chunk["token_count"],
                    }
                )
                points.append(point)

            # Upsert in batches of 100 for performance
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )

            logger.info(f"Upserted {len(chunks)} chunks to Qdrant")
            return True

        except UnexpectedResponse as e:
            logger.error(f"Failed to upsert chunks: {e}")
            self._is_available = False
            return False

    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, str]] = None
    ) -> List[Dict]:
        """
        Search for similar content chunks using vector similarity.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return (default: 5, max: 10)
            metadata_filter: Optional metadata filters (e.g., {"chapter": "Module 1"})

        Returns:
            List of search results with metadata and relevance scores

        Constitution Reference: Section 4.1 (Top-k retrieval)
        """
        if not self._is_available or not self.client:
            logger.error("Qdrant client not available for search")
            return []

        try:
            # Debug: Print current collection count
            try:
                count_result = self.client.count(collection_name=self.collection_name)
                print(f"DEBUG: Current DB Count: {count_result.count}")
            except Exception as e:
                print(f"DEBUG: Could not get count: {e}")

            # Build filter if provided
            query_filter = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                query_filter = Filter(must=conditions)

            # Perform search using query_points (qdrant-client 1.7.x API)
            # NOTE: No score_threshold parameter - return top results regardless of score
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=min(top_k, 10),  # Enforce max of 10
                query_filter=query_filter,
                with_payload=True,
                with_vectors=False  # Don't return vectors (saves bandwidth)
            )

            # Format results (query_points returns QueryResponse with .points attribute)
            results = []
            for hit in search_result.points:
                results.append({
                    "chunk_id": str(hit.id),
                    "score": hit.score,
                    "chapter": hit.payload.get("chapter", "Unknown"),
                    "section": hit.payload.get("section", "Unknown"),
                    "url": hit.payload.get("url", ""),
                    "raw_text": hit.payload.get("raw_text", ""),
                    "source_file": hit.payload.get("source_file", ""),
                    "token_count": hit.payload.get("token_count", 0),
                })

            logger.info(f"Found {len(results)} similar chunks (top_k={top_k})")
            return results

        except UnexpectedResponse as e:
            logger.error(f"Failed to search Qdrant: {e}")
            self._is_available = False
            return []

    def get_collection_stats(self) -> Optional[Dict]:
        """
        Get collection statistics.

        Returns:
            Dict with collection stats or None if unavailable
        """
        if not self._is_available or not self.client:
            return None

        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "status": "available",
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return None

    def delete_collection(self) -> bool:
        """
        Delete the collection (use with caution - for testing/re-ingestion).

        Returns:
            True if successful, False otherwise
        """
        if not self._is_available or not self.client:
            return False

        try:
            self.client.delete_collection(self.collection_name)
            logger.warning(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False


# Global Qdrant service instance
qdrant_service = QdrantService()
