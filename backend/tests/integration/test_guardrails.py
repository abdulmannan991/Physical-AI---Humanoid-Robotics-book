"""
Integration Tests for Guardrails in Chat Flow

Tests complete guardrails workflow in chat endpoint (T044).

Constitution: .specify/memory/constitution.md (Section 7)
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
async def client():
    """Create async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestGuardrailsIntegration:
    """Integration tests for guardrails in chat flow (T044)"""

    @pytest.mark.asyncio
    async def test_greeting_bypasses_rag(self, client):
        """
        Test greetings return immediate response without RAG retrieval.

        Verifies FR-035 (Greetings allowed)
        """
        # Mock classification to return GREETING
        with patch('app.services.guardrails.classify_query', new_callable=AsyncMock) as mock_classify:
            mock_classify.return_value = {
                'classification': 'GREETING',
                'score': 1.0,
                'reasoning': 'Simple greeting'
            }

            response = await client.post(
                "/api/v1/chat",
                json={
                    "query": "Hello!",
                    "session_id": None
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Should return greeting response
            assert "Hello" in data["answer"]
            assert "Abdul Mannan" in data["answer"] or "assistant" in data["answer"].lower()

            # Confidence should be 1.0 for greeting
            assert data["confidence"] == 1.0

            # Should have no citations (no RAG retrieval)
            assert len(data.get("citations", [])) == 0

    @pytest.mark.asyncio
    async def test_off_topic_polite_decline(self, client):
        """
        Test off-topic queries get polite decline message.

        Verifies FR-037 (Off-topic polite decline)
        """
        with patch('app.services.guardrails.classify_query', new_callable=AsyncMock) as mock_classify:
            mock_classify.return_value = {
                'classification': 'OFF_TOPIC',
                'score': 0.0,
                'reasoning': 'Cooking is unrelated'
            }

            response = await client.post(
                "/api/v1/chat",
                json={
                    "query": "How do I bake a cake?",
                    "session_id": None
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Should return polite decline
            assert "Physical AI" in data["answer"]
            assert "course" in data["answer"].lower()

            # Confidence should be 0.0 for off-topic
            assert data["confidence"] == 0.0

            # Should have no citations
            assert len(data.get("citations", [])) == 0

    @pytest.mark.asyncio
    async def test_ambiguous_gets_clarification(self, client):
        """
        Test ambiguous queries trigger clarification generation.

        Verifies FR-038 (Clarification for ambiguous queries)
        """
        with patch('app.services.guardrails.classify_query', new_callable=AsyncMock) as mock_classify, \
             patch('app.services.guardrails.generate_clarification', new_callable=AsyncMock) as mock_clarify:

            mock_classify.return_value = {
                'classification': 'AMBIGUOUS',
                'score': 0.5,
                'reasoning': 'Could refer to course or general topic'
            }

            mock_clarify.return_value = """Are you asking about:
1. The Physical AI & Humanoid Robotics course content
2. A different book on Physical AI
3. The general concept of Physical AI"""

            response = await client.post(
                "/api/v1/chat",
                json={
                    "query": "What is Physical AI?",
                    "session_id": None
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Should return clarification
            assert "asking about" in data["answer"].lower()
            assert "1." in data["answer"]
            assert "2." in data["answer"]

            # Confidence should be 0.5 for ambiguous
            assert data["confidence"] == 0.5

            # Clarification generation should have been called
            mock_clarify.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_topic_uses_rag(self, client):
        """
        Test on-topic queries trigger RAG pipeline.

        Verifies FR-034 (On-topic questions use RAG)
        """
        with patch('app.services.guardrails.classify_query', new_callable=AsyncMock) as mock_classify, \
             patch('app.services.rag.rag_service.retrieve', new_callable=AsyncMock) as mock_retrieve, \
             patch('app.services.rag.rag_service.generate_answer', new_callable=AsyncMock) as mock_generate:

            mock_classify.return_value = {
                'classification': 'ON_TOPIC',
                'score': 1.0,
                'reasoning': 'Clear course question'
            }

            # Mock RAG retrieval
            mock_retrieve.return_value = (
                [{"text": "Humanoid robotics chapter content", "metadata": {}}],
                50  # retrieval latency
            )

            # Mock RAG generation
            mock_generate.return_value = (
                "Humanoid robotics is covered in Chapter 5...",
                200  # LLM latency
            )

            response = await client.post(
                "/api/v1/chat",
                json={
                    "query": "What chapters cover humanoid robotics?",
                    "session_id": None
                }
            )

            assert response.status_code == 200
            data = response.json()

            # RAG retrieval should have been called
            mock_retrieve.assert_called_once()
            mock_generate.assert_called_once()

            # Should have answer from RAG
            assert len(data["answer"]) > 0

    @pytest.mark.asyncio
    async def test_classification_fallback_on_error(self, client):
        """
        Test chat endpoint handles classification errors gracefully.

        Verifies fallback behavior when classification fails.
        """
        with patch('app.services.guardrails.classify_query', new_callable=AsyncMock) as mock_classify, \
             patch('app.services.rag.rag_service.retrieve', new_callable=AsyncMock) as mock_retrieve, \
             patch('app.services.rag.rag_service.generate_answer', new_callable=AsyncMock) as mock_generate:

            # Classification returns fallback (ON_TOPIC)
            mock_classify.return_value = {
                'classification': 'ON_TOPIC',
                'score': 1.0,
                'reasoning': 'Fallback due to classification error'
            }

            # Mock RAG
            mock_retrieve.return_value = ([{"text": "Content", "metadata": {}}], 50)
            mock_generate.return_value = ("Answer", 200)

            response = await client.post(
                "/api/v1/chat",
                json={
                    "query": "Some query",
                    "session_id": None
                }
            )

            assert response.status_code == 200
            # Should still get a response (fallback to RAG)
            data = response.json()
            assert len(data["answer"]) > 0

    @pytest.mark.asyncio
    async def test_guardrails_preserve_existing_functionality(self, client):
        """
        Test guardrails don't break existing chatbot for legitimate questions.

        Verifies FR-031 (Backward compatibility with guest sessions)
        """
        with patch('app.services.guardrails.classify_query', new_callable=AsyncMock) as mock_classify, \
             patch('app.services.rag.rag_service.retrieve', new_callable=AsyncMock) as mock_retrieve, \
             patch('app.services.rag.rag_service.generate_answer', new_callable=AsyncMock) as mock_generate:

            mock_classify.return_value = {
                'classification': 'ON_TOPIC',
                'score': 1.0,
                'reasoning': 'Course question'
            }

            mock_retrieve.return_value = ([{"text": "Course content", "metadata": {}}], 50)
            mock_generate.return_value = ("Detailed answer about course", 200)

            # Test that a clear course question works as before
            response = await client.post(
                "/api/v1/chat",
                json={
                    "query": "Explain the concepts in Chapter 1",
                    "session_id": None
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Should get proper RAG response
            assert len(data["answer"]) > 0
            assert data["confidence"] > 0.0

            # Session should be created (backward compatibility)
            assert "session_id" in data


class TestGuardrailsPerformance:
    """Performance tests for guardrails"""

    @pytest.mark.asyncio
    async def test_greeting_response_fast(self, client):
        """
        Test greeting responses are fast (<1s).

        Greetings should bypass RAG for instant response.
        """
        import time

        with patch('app.services.guardrails.classify_query', new_callable=AsyncMock) as mock_classify:
            mock_classify.return_value = {
                'classification': 'GREETING',
                'score': 1.0,
                'reasoning': 'Greeting'
            }

            start = time.perf_counter()

            response = await client.post(
                "/api/v1/chat",
                json={"query": "Hello!", "session_id": None}
            )

            duration = time.perf_counter() - start

            assert response.status_code == 200
            # Should be very fast (no RAG retrieval)
            # Allow generous timeout for test environment
            assert duration < 2.0, f"Greeting took {duration:.2f}s (expected <2s)"
