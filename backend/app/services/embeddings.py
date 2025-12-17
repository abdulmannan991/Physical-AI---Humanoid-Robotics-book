"""
Embeddings Service (Cohere)

Handles text embedding generation using Cohere API.

Constitution: backend/.specify/memory/constitution.md (Section 4.1)
- Modular design for future provider replacement (FR-032)
- Cohere embed-english-v3.0 model
"""

import logging
from typing import List, Optional, Dict
import cohere

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """
    Embeddings service using Cohere API.

    Provides text-to-vector conversion with error handling and modular design.
    """

    def __init__(self):
        """Initialize Cohere client."""
        try:
            self.client = cohere.Client(api_key=settings.COHERE_API_KEY)
            self.model_name = settings.EMBEDDING_MODEL_NAME
            self._is_available = True

            logger.info(
                f"Cohere embeddings service initialized: model={self.model_name}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}")
            self._is_available = False
            self.client = None

    def health_check(self) -> bool:
        """
        Check if Cohere API is available.

        Returns:
            True if Cohere is accessible, False otherwise
        """
        if not self._is_available or not self.client:
            return False

        try:
            # Test with a simple embedding
            _ = self.client.embed(
                texts=["test"],
                model=self.model_name,
                input_type="search_query"
            )
            return True
        except Exception as e:
            logger.warning(f"Cohere health check failed: {e}")
            return False

    def generate_embedding(
        self,
        text: str,
        input_type: str = "search_query"
    ) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed
            input_type: Type of input ("search_query" or "search_document")

        Returns:
            Embedding vector (list of floats) or None if failed

        Constitution Reference: FR-032 (Modular embedding architecture)

        Example:
            >>> embeddings_service.generate_embedding("What is inverse kinematics?")
            [0.123, -0.456, ..., 0.789]  # 1024-dimensional vector
        """
        if not self._is_available or not self.client:
            logger.error("Cohere client not available")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
                input_type=input_type,
                truncate="END"  # Truncate if text too long
            )

            embedding = response.embeddings[0]
            logger.debug(f"Generated embedding for text (length={len(text)})")
            return embedding

        except Exception as e:
            logger.error(f"Cohere error generating embedding: {e}")
            if "rate_limit" in str(e).lower():
                logger.error("Rate limit exceeded - consider implementing caching")
            if "api" in str(e).lower() or "connection" in str(e).lower():
                self._is_available = False
            return None

    def generate_embeddings_batch(
        self,
        texts: List[str],
        input_type: str = "search_document"
    ) -> Optional[List[List[float]]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of texts to embed
            input_type: Type of input ("search_query" or "search_document")

        Returns:
            List of embedding vectors or None if failed

        Note: Cohere supports up to 96 texts per batch request.

        Constitution Reference: Section 6 (Content ingestion optimization)
        """
        if not self._is_available or not self.client:
            logger.error("Cohere client not available")
            return None

        if not texts:
            logger.warning("Empty texts list provided")
            return None

        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            logger.warning("All texts are empty after filtering")
            return None

        try:
            # Cohere batch limit is 96 texts
            if len(valid_texts) > 96:
                logger.warning(
                    f"Batch size {len(valid_texts)} exceeds limit of 96. "
                    "Processing in multiple batches..."
                )
                return self._generate_embeddings_chunked(valid_texts, input_type)

            response = self.client.embed(
                texts=valid_texts,
                model=self.model_name,
                input_type=input_type,
                truncate="END"
            )

            embeddings = response.embeddings
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings

        except Exception as e:
            logger.error(f"Cohere error in batch embedding: {e}")
            if "api" in str(e).lower() or "connection" in str(e).lower():
                self._is_available = False
            return None

    def _generate_embeddings_chunked(
        self,
        texts: List[str],
        input_type: str
    ) -> Optional[List[List[float]]]:
        """
        Generate embeddings in chunks of 96 texts.

        Args:
            texts: List of texts to embed
            input_type: Type of input

        Returns:
            List of all embeddings or None if any batch fails
        """
        all_embeddings = []
        batch_size = 96

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}: {len(batch)} texts")

            try:
                response = self.client.embed(
                    texts=batch,
                    model=self.model_name,
                    input_type=input_type,
                    truncate="END"
                )
                all_embeddings.extend(response.embeddings)

            except Exception as e:
                logger.error(f"Failed to process batch {i // batch_size + 1}: {e}")
                return None

        logger.info(f"Generated {len(all_embeddings)} embeddings across all batches")
        return all_embeddings

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: int = 5
    ) -> Optional[List[Dict]]:
        """
        Rerank documents using Cohere reranking API (optional feature).

        Args:
            query: Search query
            documents: List of document texts to rerank
            top_n: Number of top results to return

        Returns:
            List of reranked results with indices and scores, or None if failed

        Constitution Reference: FR-033 (Optional Cohere reranking)

        Note: Only use if ENABLE_COHERE_RERANKING is True in settings.
        """
        if not settings.ENABLE_COHERE_RERANKING:
            logger.debug("Reranking is disabled in settings")
            return None

        if not self._is_available or not self.client:
            logger.error("Cohere client not available for reranking")
            return None

        try:
            response = self.client.rerank(
                query=query,
                documents=documents,
                top_n=min(top_n, len(documents)),
                model="rerank-english-v2.0"
            )

            results = []
            for result in response.results:
                results.append({
                    "index": result.index,
                    "relevance_score": result.relevance_score,
                    "document": documents[result.index]
                })

            logger.info(f"Reranked {len(documents)} documents, returned top {top_n}")
            return results

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return None


# Global embeddings service instance
embeddings_service = EmbeddingsService()
