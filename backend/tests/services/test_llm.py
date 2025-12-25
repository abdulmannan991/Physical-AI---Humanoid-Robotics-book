"""
Unit Tests for LLM Service and Guardrails

Tests query classification, greeting detection, ambiguous question handling,
and off-topic detection (T041-T043).

Constitution: .specify/memory/constitution.md (Section 7 - 80% coverage)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.guardrails import (
    classify_query,
    generate_clarification,
    get_greeting_response,
    get_off_topic_response
)


class TestGreetingDetection:
    """Tests for greeting detection (T041)"""

    @pytest.mark.asyncio
    async def test_classify_simple_greeting(self):
        """Test simple greetings are classified correctly"""
        # Mock LLM response
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>GREETING</classification>
            <score>1.0</score>
            <reasoning>Simple greeting</reasoning>
            """

            result = await classify_query("Hello!")

            assert result['classification'] == 'GREETING'
            assert result['score'] == 1.0

    @pytest.mark.asyncio
    async def test_classify_informal_greeting(self):
        """Test informal greetings (Hi, Hey)"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>GREETING</classification>
            <score>1.0</score>
            """

            result = await classify_query("Hey there!")

            assert result['classification'] == 'GREETING'
            assert result['score'] == 1.0

    def test_get_greeting_response(self):
        """Test greeting response message"""
        response = get_greeting_response()

        assert "Hello" in response
        assert "Abdul Mannan" in response
        assert "Physical AI" in response
        assert "Humanoid Robotics" in response

    @pytest.mark.asyncio
    async def test_greeting_vs_question_distinction(self):
        """Test greetings are distinguished from questions starting with 'Hi'"""
        # "Hi, how do I..." should be classified as ON_TOPIC, not GREETING
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>ON_TOPIC</classification>
            <score>1.0</score>
            <reasoning>Question about course content</reasoning>
            """

            result = await classify_query("Hi, how do I understand humanoid robotics?")

            assert result['classification'] == 'ON_TOPIC'


class TestAmbiguousQuestionClassification:
    """Tests for ambiguous question classification (T042)"""

    @pytest.mark.asyncio
    async def test_classify_ambiguous_query(self):
        """Test ambiguous questions are classified with score 0.5"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>AMBIGUOUS</classification>
            <score>0.5</score>
            <reasoning>Could refer to course or general concept</reasoning>
            """

            result = await classify_query("What is Physical AI?")

            assert result['classification'] == 'AMBIGUOUS'
            assert result['score'] == 0.5

    @pytest.mark.asyncio
    async def test_generate_clarification_has_numbered_options(self):
        """Test clarification includes numbered options"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <clarification>
            Are you asking about:
            1. The Physical AI & Humanoid Robotics course content
            2. A different book on Physical AI
            3. The general concept of Physical AI
            </clarification>
            """

            clarification = await generate_clarification("What is Physical AI?")

            assert "1." in clarification
            assert "2." in clarification
            assert "course" in clarification.lower()

    @pytest.mark.asyncio
    async def test_generate_clarification_fallback(self):
        """Test clarification fallback on LLM error"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM error")

            clarification = await generate_clarification("What is Physical AI?")

            # Should return fallback message
            assert "clarify" in clarification.lower()
            assert "course" in clarification.lower()

    @pytest.mark.asyncio
    async def test_ambiguous_vs_clear_questions(self):
        """Test ambiguous questions are distinguished from clear questions"""
        # "Which chapters are in the book?" is clear ON_TOPIC
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>ON_TOPIC</classification>
            <score>1.0</score>
            <reasoning>Clearly asking about course content</reasoning>
            """

            result = await classify_query("Which chapters are included in this book?")

            assert result['classification'] == 'ON_TOPIC'
            assert result['score'] == 1.0


class TestOffTopicDetection:
    """Tests for off-topic detection (T043)"""

    @pytest.mark.asyncio
    async def test_classify_completely_off_topic(self):
        """Test clearly off-topic queries are detected"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>OFF_TOPIC</classification>
            <score>0.0</score>
            <reasoning>Cooking is unrelated to course</reasoning>
            """

            result = await classify_query("How do I bake a cake?")

            assert result['classification'] == 'OFF_TOPIC'
            assert result['score'] == 0.0

    @pytest.mark.asyncio
    async def test_classify_unrelated_tech_topic(self):
        """Test unrelated tech topics are off-topic"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>OFF_TOPIC</classification>
            <score>0.0</score>
            <reasoning>React is not related to Physical AI course</reasoning>
            """

            result = await classify_query("Tell me about React documentation")

            assert result['classification'] == 'OFF_TOPIC'
            assert result['score'] == 0.0

    def test_get_off_topic_response(self):
        """Test off-topic response message"""
        response = get_off_topic_response()

        assert "Physical AI" in response
        assert "Humanoid Robotics" in response
        assert "course" in response
        # Should be polite (not harsh rejection)
        assert "only help with" in response.lower() or "related to" in response.lower()

    @pytest.mark.asyncio
    async def test_fallback_on_classification_error(self):
        """Test fallback to ON_TOPIC when classification fails"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM error")

            result = await classify_query("Some query")

            # Should fallback to ON_TOPIC (safe default)
            assert result['classification'] == 'ON_TOPIC'
            assert result['score'] == 1.0
            assert 'fallback' in result['reasoning'].lower()


class TestOnTopicClassification:
    """Tests for on-topic query classification"""

    @pytest.mark.asyncio
    async def test_classify_clear_course_question(self):
        """Test clear course questions are ON_TOPIC with score 1.0"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>ON_TOPIC</classification>
            <score>1.0</score>
            <reasoning>Direct question about course content</reasoning>
            """

            result = await classify_query("What are the main topics in humanoid robotics?")

            assert result['classification'] == 'ON_TOPIC'
            assert result['score'] == 1.0

    @pytest.mark.asyncio
    async def test_classify_specific_chapter_question(self):
        """Test specific chapter questions are ON_TOPIC"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>ON_TOPIC</classification>
            <score>1.0</score>
            <reasoning>Asking about specific course chapter</reasoning>
            """

            result = await classify_query("Tell me about Chapter 3")

            assert result['classification'] == 'ON_TOPIC'
            assert result['score'] == 1.0


class TestXMLParsing:
    """Tests for XML parsing robustness"""

    @pytest.mark.asyncio
    async def test_parse_classification_with_extra_whitespace(self):
        """Test XML parsing handles whitespace correctly"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>  GREETING  </classification>
            <score> 1.0 </score>
            <reasoning>  Simple greeting  </reasoning>
            """

            result = await classify_query("Hello")

            assert result['classification'] == 'GREETING'
            assert result['score'] == 1.0

    @pytest.mark.asyncio
    async def test_parse_missing_reasoning_tag(self):
        """Test parsing handles missing optional tags"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            <classification>GREETING</classification>
            <score>1.0</score>
            """

            result = await classify_query("Hello")

            assert result['classification'] == 'GREETING'
            assert result['score'] == 1.0
            assert result['reasoning'] == ''

    @pytest.mark.asyncio
    async def test_parse_malformed_xml_fallback(self):
        """Test fallback when XML is completely malformed"""
        with patch('app.services.guardrails.llm_service.generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "This is not XML at all"

            result = await classify_query("Hello")

            # Should fallback to ON_TOPIC
            assert result['classification'] == 'ON_TOPIC'
            assert result['score'] == 1.0
