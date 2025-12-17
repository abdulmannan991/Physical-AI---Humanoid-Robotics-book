"""
Database Service Layer (Neon PostgreSQL)

Provides abstraction for all database operations.

Constitution: backend/.specify/memory/constitution.md (Section 4.2)
- Service layer required for all DB access
- NO direct SQL in route handlers
- Graceful degradation when Neon unavailable (FR-038)
"""

import logging
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.models.database import Base, ChatSession, QueryLog

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Database service for Neon PostgreSQL operations.

    Handles session creation, query logging, and graceful degradation.
    """

    def __init__(self):
        """Initialize database service with async engine."""
        try:
            # Convert postgresql:// to postgresql+psycopg://
            db_url = settings.DATABASE_URL.replace(
                "postgresql://",
                "postgresql+psycopg://"
            )

            self.engine = create_async_engine(
                db_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_size=settings.DB_POOL_MIN_SIZE,
                max_overflow=settings.DB_POOL_MAX_SIZE - settings.DB_POOL_MIN_SIZE,
                echo=settings.DEBUG,  # Log SQL in debug mode
            )

            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            self._is_available = True
            logger.info("Database service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            self._is_available = False

    async def create_tables(self) -> None:
        """
        Create all database tables if they don't exist.

        Should be called on application startup.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            self._is_available = False

    async def health_check(self) -> bool:
        """
        Check if database is available.

        Returns:
            True if database is healthy, False otherwise
        """
        if not self._is_available:
            return False

        try:
            async with self.async_session_maker() as session:
                await session.execute(select(1))
            return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False

    @asynccontextmanager
    async def get_session(self):
        """
        Get async database session.

        Yields:
            AsyncSession instance

        Example:
            async with db_service.get_session() as session:
                result = await session.execute(query)
        """
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def create_session(self) -> Optional[UUID]:
        """
        Create a new chat session.

        Returns:
            Session ID (UUID) if successful, None if database unavailable

        Constitution Reference: FR-034 (Session creation)
        """
        if not self._is_available:
            logger.warning("Database unavailable - cannot create session")
            return None

        try:
            session_id = uuid4()

            async with self.get_session() as session:
                new_session = ChatSession(
                    session_id=session_id,
                    started_at=datetime.utcnow(),
                    last_activity_at=datetime.utcnow(),
                    message_count=0
                )
                session.add(new_session)

            logger.info(f"Created new chat session: {session_id}")
            return session_id

        except SQLAlchemyError as e:
            logger.error(f"Failed to create session: {e}")
            self._is_available = False  # Mark as unavailable
            return None

    async def get_session_by_id(self, session_id: UUID) -> Optional[ChatSession]:
        """
        Get chat session by ID.

        Args:
            session_id: Session UUID

        Returns:
            ChatSession instance if found, None otherwise

        Constitution Reference: FR-035 (Session retrieval)
        """
        if not self._is_available:
            return None

        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(ChatSession).where(ChatSession.session_id == session_id)
                )
                return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_session_activity(self, session_id: UUID) -> bool:
        """
        Update session last_activity_at timestamp and increment message count.

        Args:
            session_id: Session UUID

        Returns:
            True if successful, False otherwise

        Constitution Reference: Session activity tracking
        """
        if not self._is_available:
            return False

        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(ChatSession).where(ChatSession.session_id == session_id)
                )
                chat_session = result.scalar_one_or_none()

                if chat_session:
                    chat_session.last_activity_at = datetime.utcnow()
                    chat_session.message_count += 1
                    return True

                return False

        except SQLAlchemyError as e:
            logger.error(f"Failed to update session activity: {e}")
            return False

    async def log_query(
        self,
        session_id: UUID,
        query_text: str,
        response_text: Optional[str] = None,
        confidence_score: Optional[float] = None,
        retrieval_latency_ms: Optional[int] = None,
        llm_latency_ms: Optional[int] = None
    ) -> Optional[UUID]:
        """
        Log a query and its response for analytics.

        Args:
            session_id: Session UUID
            query_text: User query
            response_text: LLM response (will be truncated to 500 chars)
            confidence_score: RAG confidence (0.0 to 1.0)
            retrieval_latency_ms: Qdrant retrieval time
            llm_latency_ms: LLM generation time

        Returns:
            Log ID if successful, None if database unavailable

        Constitution Reference: FR-035 (Query logging - NO PII)
        """
        if not self._is_available:
            logger.warning("Database unavailable - skipping query log")
            return None

        try:
            log_id = uuid4()

            # Truncate response to 500 chars for storage
            response_truncated = None
            if response_text:
                response_truncated = response_text[:500]

            async with self.get_session() as session:
                query_log = QueryLog(
                    log_id=log_id,
                    session_id=session_id,
                    query_text=query_text[:2000],  # Enforce max length
                    response_text_truncated=response_truncated,
                    confidence_score=confidence_score,
                    retrieval_latency_ms=retrieval_latency_ms,
                    llm_latency_ms=llm_latency_ms,
                    created_at=datetime.utcnow()
                )
                session.add(query_log)

            logger.info(f"Logged query for session {session_id}")
            return log_id

        except SQLAlchemyError as e:
            logger.error(f"Failed to log query: {e}")
            # Don't mark as unavailable for logging failures
            return None

    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


# Global database service instance
db_service = DatabaseService()
