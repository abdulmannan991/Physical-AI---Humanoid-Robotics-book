"""
RAG Service - Retrieval-Augmented Generation

Orchestrates the RAG pipeline: retrieve → generate answer with citations.

Constitution: backend/.specify/memory/constitution.md (Section 4.1)
"""

import logging
import re
import time
from typing import List, Dict, Optional
from uuid import UUID

from app.core.config import settings
from app.models.response import ChatResponse, Citation
from app.services.embeddings import embeddings_service
from app.services.qdrant import qdrant_service
from app.services.llm import llm_service

logger = logging.getLogger(__name__)

# Out-of-scope fallback message (FR-008)
OUT_OF_SCOPE_MESSAGE = (
    "I cannot provide information related to this topic. However, if you have any "
    "queries regarding the 'Physical AI & Humanoid Robotics' book, let me know — "
    "I am here to assist you."
)

# Out-of-scope keywords for early detection
OUT_OF_SCOPE_KEYWORDS = {
    # Weather
    "weather", "temperature", "forecast", "rain", "snow", "climate",
    # Entertainment
    "joke", "funny", "meme", "movie", "song", "music", "game",
    # General knowledge unrelated to AI/robotics
    "capital", "country", "geography", "history", "recipe", "cooking",
    # Sports
    "sports", "football", "basketball", "cricket", "soccer",
    # Current events (non-AI)
    "news", "politics", "election", "president",
    # Personal advice
    "dating", "relationship", "health", "medical",
}


class RAGService:
    """
    RAG service for intelligent Q&A.

    Combines vector search with LLM generation to provide accurate,
    source-cited answers to user questions.
    """

    def __init__(self):
        """Initialize RAG service."""
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        logger.info(
            f"RAG service initialized (confidence_threshold={self.confidence_threshold})"
        )

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, str]] = None
    ) -> tuple[List[Dict], int]:
        """
        Retrieve relevant chunks from Qdrant.

        Args:
            query: User query
            top_k: Number of chunks to retrieve
            metadata_filter: Optional metadata filters

        Returns:
            Tuple of (retrieved_chunks, retrieval_latency_ms)

        Constitution Reference: Section 4.1 (Top-k retrieval)
        """
        start_time = time.time()

        try:
            # Generate query embedding
            query_embedding = embeddings_service.generate_embedding(
                text=query,
                input_type="search_query"
            )

            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return [], 0

            # Search Qdrant
            chunks = qdrant_service.search_similar(
                query_vector=query_embedding,
                top_k=top_k,
                metadata_filter=metadata_filter
            )

            retrieval_latency = int((time.time() - start_time) * 1000)
            logger.info(
                f"Retrieved {len(chunks)} chunks in {retrieval_latency}ms "
                f"(top_k={top_k})"
            )

            return chunks, retrieval_latency

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return [], 0

    def is_out_of_scope(self, query: str) -> bool:
        """
        Check if query contains out-of-scope keywords.

        Args:
            query: User query text

        Returns:
            True if query is likely out of scope

        Constitution Reference: FR-008 (Out-of-scope handling)
        """
        query_lower = query.lower()

        # Check for out-of-scope keywords
        for keyword in OUT_OF_SCOPE_KEYWORDS:
            if keyword in query_lower:
                logger.info(f"Out-of-scope keyword detected: '{keyword}' in query")
                return True

        return False

    def check_confidence(self, chunks: List[Dict]) -> float:
        """
        Calculate confidence score from retrieved chunks.

        Args:
            chunks: Retrieved chunks with relevance scores

        Returns:
            Confidence score (0.0 to 1.0)

        Constitution Reference: FR-008 (Confidence threshold 0.6)
        """
        if not chunks:
            return 0.0

        # Average relevance score of top chunks
        scores = [chunk.get("score", 0.0) for chunk in chunks]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Weight top result more heavily
        if len(chunks) > 0:
            top_score = chunks[0].get("score", 0.0)
            confidence = (top_score * 0.6) + (avg_score * 0.4)
        else:
            confidence = 0.0

        logger.debug(f"Confidence score: {confidence:.3f}")
        return confidence

    async def generate_answer(
        self,
        query: str,
        chunks: List[Dict],
        session_id: UUID
    ) -> tuple[ChatResponse, int]:
        """
        Generate answer from retrieved chunks using LLM.

        Args:
            query: User query
            chunks: Retrieved content chunks
            session_id: Session UUID

        Returns:
            Tuple of (ChatResponse, llm_latency_ms)

        Constitution Reference: FR-005, FR-008, FR-009 (Generation + citations)
        """
        start_time = time.time()

        # Early out-of-scope detection via keywords
        if self.is_out_of_scope(query):
            logger.info("Query rejected: out-of-scope keyword detected")
            return ChatResponse(
                answer=OUT_OF_SCOPE_MESSAGE,
                citations=[],
                confidence=0.0,
                session_id=session_id
            ), 0

        # Check confidence
        confidence = self.check_confidence(chunks)

        # If confidence too low, return fallback message
        if confidence < self.confidence_threshold:
            logger.info(
                f"Low confidence ({confidence:.3f} < {self.confidence_threshold}), "
                "returning fallback message"
            )
            return ChatResponse(
                answer=OUT_OF_SCOPE_MESSAGE,
                citations=[],
                confidence=0.0,
                session_id=session_id
            ), 0

        # Confidence passed threshold - log success
        logger.info(
            f"Confidence score {confidence:.3f} passed threshold {self.confidence_threshold}"
        )

        try:
            # Build context from chunks
            context = self._build_context(chunks)

            # Generate answer using LLM
            answer = llm_service.generate_response(
                prompt=query,
                context=context,
                max_tokens=1000,
                temperature=0.3
            )

            llm_latency = int((time.time() - start_time) * 1000)

            if not answer:
                logger.error("LLM generation failed, returning fallback")
                return ChatResponse(
                    answer=OUT_OF_SCOPE_MESSAGE,
                    citations=[],
                    confidence=0.0,
                    session_id=session_id
                ), llm_latency

            # Extract citations from chunks
            citations = self._build_citations(chunks)

            response = ChatResponse(
                answer=answer,
                citations=citations,
                confidence=confidence,
                session_id=session_id
            )

            logger.info(
                f"Generated answer in {llm_latency}ms "
                f"(confidence={confidence:.3f}, citations={len(citations)})"
            )

            return response, llm_latency

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            llm_latency = int((time.time() - start_time) * 1000)

            # Return fallback on error
            return ChatResponse(
                answer=OUT_OF_SCOPE_MESSAGE,
                citations=[],
                confidence=0.0,
                session_id=session_id
            ), llm_latency

    def _build_context(self, chunks: List[Dict]) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            chunks: Retrieved chunks

        Returns:
            Formatted context string for LLM
        """
        context_parts = []

        for i, chunk in enumerate(chunks[:5], 1):  # Top 5 chunks
            chapter = chunk.get("chapter", "Unknown")
            section = chunk.get("section", "Unknown")
            text = chunk.get("raw_text", "")

            context_parts.append(
                f"[Source {i}: {chapter} - {section}]\n{text}\n"
            )

        return "\n\n".join(context_parts)

    def _build_citations(self, chunks: List[Dict]) -> List[Citation]:
        """
        Build citation list from retrieved chunks.

        Args:
            chunks: Retrieved chunks

        Returns:
            List of Citation objects

        Constitution Reference: FR-009 (Citations required)
        """
        citations = []
        seen_urls = set()  # Deduplicate citations by URL

        for chunk in chunks[:5]:  # Top 5 chunks
            url = chunk.get("url", "")

            # Clean the URL to fix 404 issues
            url = self._clean_citation_url(url)

            # Skip if we've already added this URL
            if url in seen_urls:
                continue

            citation = Citation(
                chapter=chunk.get("chapter", "Unknown"),
                section=chunk.get("section", "Unknown"),
                url=url,
                relevance_score=chunk.get("score", 0.0)
            )

            citations.append(citation)
            seen_urls.add(url)

        return citations

    def _clean_citation_url(self, url: str) -> str:
        """
        Clean citation URL to match Docusaurus routing.

        Args:
            url: Raw URL from chunk metadata (e.g., 'docs/02-ros2/2.1-intro.md')

        Returns:
            Cleaned URL that works with Docusaurus (e.g., '/ros2/intro')

        Transformations:
        1. Remove 'docs/' prefix
        2. Remove '.md' extension
        3. Remove '/index' suffix
        4. Remove numeric prefixes from path segments (e.g., '01-', '2.1-')
        5. Ensure starts with '/'

        Examples:
        - 'docs/02-ros2/2.1-intro.md' -> '/ros2/intro'
        - 'docs/01-intro/index.md' -> '/intro'
        - '03-perception/3.2-cameras.md' -> '/perception/cameras'
        """
        if not url:
            return ""

        # Step 1: Remove 'docs/' prefix (case-insensitive)
        if url.startswith("docs/"):
            url = url[5:]  # Remove "docs/"
        elif url.startswith("/docs/"):
            url = url[6:]  # Remove "/docs/"

        # Step 2: Remove .md extension
        if url.endswith(".md"):
            url = url[:-3]

        # Step 3: Remove /index suffix (critical fix for 404 errors)
        if url.endswith("/index"):
            url = url[:-6]

        # Step 4: Remove numeric prefixes from path segments
        # Pattern: digit(s) followed by dot or hyphen (e.g., '01-', '2.1-', '10-')
        # Split by /, clean each segment, rejoin
        path_segments = url.split("/")
        cleaned_segments = []

        for segment in path_segments:
            if segment:  # Skip empty segments
                # Remove numeric prefix: '01-intro' -> 'intro', '2.1-cameras' -> 'cameras'
                cleaned = re.sub(r"^(\d+[.-])+", "", segment)
                if cleaned:  # Only add if segment is not empty after cleaning
                    cleaned_segments.append(cleaned)

        url = "/".join(cleaned_segments)

        # Step 5: Ensure starts with /
        if not url.startswith("/"):
            url = "/" + url

        return url
# Global RAG service instance
rag_service = RAGService()
