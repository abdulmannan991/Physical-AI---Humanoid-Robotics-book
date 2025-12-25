"""
LLM Client Service

Provides interface for Cohere LLM chat completion.

Constitution: backend/.specify/memory/constitution.md (Section 4.1)
"""

import logging
from typing import Optional
import cohere

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using Cohere for chat completion.

    Provides text generation with RAG context injection.
    """

    def __init__(self):
        """Initialize Cohere LLM client."""
        self.model = settings.COHERE_CHAT_MODEL
        self._is_available = True

        try:
            self.client = cohere.Client(api_key=settings.COHERE_API_KEY)
            logger.info(f"Cohere LLM initialized: model={self.model}")

        except Exception as e:
            logger.error(f"Failed to initialize Cohere LLM client: {e}")
            self._is_available = False
            self.client = None

    def health_check(self) -> bool:
        """
        Check if LLM is available.

        Returns:
            True if LLM is accessible, False otherwise
        """
        if not self._is_available or not self.client:
            return False

        # Simple availability check without making an API call
        # (to avoid costs on health checks)
        return True

    def generate(
        self,
        prompt: str,
        preamble: str,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        Generate response using Cohere LLM with custom preamble.

        This is a lower-level method for guardrails classification and clarification.

        Args:
            prompt: User message/query
            preamble: System prompt/instructions
            max_tokens: Maximum response length
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text response or None if failed
        """
        if not self._is_available or not self.client:
            logger.error("Cohere LLM client not available")
            return None

        try:
            response = self.client.chat(
                model=self.model,
                message=prompt,
                preamble=preamble,
                max_tokens=max_tokens,
                temperature=temperature
            )

            answer = response.text
            return answer

        except cohere.CohereAPIError as e:
            logger.error(f"Cohere API error: {e}")
            self._is_available = False
            return None
        except Exception as e:
            logger.error(f"Cohere generation failed: {e}")
            self._is_available = False
            return None

    def generate_response(
        self,
        prompt: str,
        context: str,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        Generate response using Cohere LLM with RAG context (T045 - Updated preamble).

        Args:
            prompt: User query/question
            context: Retrieved context from Qdrant
            max_tokens: Maximum response length
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text response or None if failed

        Constitution Reference: Section 4.1 (RAG generation)
        Research Reference: research.md Section 6 (Guardrails - NEW preamble)
        """
        if not self._is_available or not self.client:
            logger.error("Cohere LLM client not available")
            return None

        try:
            # NEW preamble (relaxed guardrails, conversational)
            preamble = """You are a friendly assistant for the "Physical AI & Humanoid Robotics" course by Abdul Mannan.

Guidelines:
- Respond warmly to greetings and introduce yourself
- Answer questions using the provided course context
- If context doesn't fully answer the question, say what you know and what's unclear
- Stay focused on course content, but be conversational
- If asked about other resources, politely redirect to this course"""

            user_message = f"""Context from course materials:
{context}

User question: {prompt}

Provide a helpful, accurate answer based on the course context above."""

            response = self.client.chat(
                model=self.model,
                message=user_message,
                preamble=preamble,
                max_tokens=max_tokens,
                temperature=temperature
            )

            answer = response.text
            logger.info("Generated response using Cohere")
            return answer

        except cohere.CohereAPIError as e:
            logger.error(f"Cohere API error: {e}")
            self._is_available = False
            return None
        except Exception as e:
            logger.error(f"Cohere generation failed: {e}")
            self._is_available = False
            return None


# Global LLM service instance
llm_service = LLMService()
