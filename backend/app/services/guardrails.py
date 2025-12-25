"""
Guardrails Service for Query Classification

Implements multi-stage LLM classification for chatbot guardrails (US4).

Features:
- Stage 1: Query classification (GREETING/ON_TOPIC/AMBIGUOUS/OFF_TOPIC)
- Stage 2: Clarification generation for ambiguous queries
- XML-based structured prompts for reliable parsing

Research: specs/001-auth-profile-guardrails/research.md (Section 6)
Constitution: .specify/memory/constitution.md (Section 7)
"""

import re
import logging
from typing import Dict, Optional
from app.services.llm import llm_service

logger = logging.getLogger(__name__)

# Classification system prompt with few-shot examples (UPDATED: Less strict, course-first assumption)
CLASSIFICATION_SYSTEM_PROMPT = """You are a classification assistant for a RAG chatbot about the "Physical AI & Humanoid Robotics" course.

IMPORTANT GUIDELINES:
- **ASSUME questions are about THIS course** unless explicitly stated otherwise
- Greetings should ALWAYS be classified as GREETING
- Book-related questions (modules, chapters, topics) are ON_TOPIC by default
- Only mark as AMBIGUOUS if the question could genuinely refer to another resource
- Only mark as OFF_TOPIC if clearly unrelated (other books, cooking, sports, etc.)

Categories:
1. GREETING (score: 1.0): Any greeting like "Hello", "Hi", "Hey", "Good morning"
2. ON_TOPIC (score: 1.0): Questions about Physical AI, Humanoid Robotics, course content, chapters, modules
3. AMBIGUOUS (score: 0.5): Questions that might refer to another book or resource (use sparingly)
4. OFF_TOPIC (score: 0.0): Clearly unrelated topics (other books explicitly named, cooking, sports, etc.)

Examples:

<example>
<query>Hello!</query>
<classification>GREETING</classification>
<score>1.0</score>
<reasoning>Simple greeting</reasoning>
</example>

<example>
<query>Hi, how are you?</query>
<classification>GREETING</classification>
<score>1.0</score>
<reasoning>Greeting with pleasantries</reasoning>
</example>

<example>
<query>How many modules are in the book?</query>
<classification>ON_TOPIC</classification>
<score>1.0</score>
<reasoning>Asking about THIS course structure</reasoning>
</example>

<example>
<query>What is Physical AI?</query>
<classification>ON_TOPIC</classification>
<score>1.0</score>
<reasoning>Assume user means THIS course unless stated otherwise</reasoning>
</example>

<example>
<query>Which chapters are included?</query>
<classification>ON_TOPIC</classification>
<score>1.0</score>
<reasoning>Clearly asking about THIS course content</reasoning>
</example>

<example>
<query>Explain humanoid robotics</query>
<classification>ON_TOPIC</classification>
<score>1.0</score>
<reasoning>Core topic of THIS course</reasoning>
</example>

<example>
<query>Tell me about the MIT robotics course</query>
<classification>AMBIGUOUS</classification>
<score>0.5</score>
<reasoning>Explicitly mentions another course - needs clarification</reasoning>
</example>

<example>
<query>Summarize NCERT Physics Chapter 5</query>
<classification>OFF_TOPIC</classification>
<score>0.0</score>
<reasoning>Different book explicitly mentioned</reasoning>
</example>

<example>
<query>Explain Harry Potter plot</query>
<classification>OFF_TOPIC</classification>
<score>0.0</score>
<reasoning>Completely unrelated book/topic</reasoning>
</example>

<example>
<query>How do I bake a cake?</query>
<classification>OFF_TOPIC</classification>
<score>0.0</score>
<reasoning>Cooking is unrelated to course content</reasoning>
</example>

Output format (XML):
<classification>CATEGORY_NAME</classification>
<score>X.X</score>
<reasoning>Brief explanation</reasoning>
"""

# Clarification generation prompt (UPDATED: More specific options)
CLARIFICATION_SYSTEM_PROMPT = """You are a helpful assistant for the "Physical AI & Humanoid Robotics" course.

When a user's question is ambiguous (could refer to multiple topics), generate a clarification question with 2-3 options.

IMPORTANT: Make the first option always be about THIS course to guide the user.

Examples:

<example>
<query>Tell me about the MIT robotics course</query>
<clarification>
Are you asking about:
1. Physical AI & Humanoid Robotics (this course)
2. A different MIT robotics course
3. Comparing courses
</clarification>
</example>

<example>
<query>Recommend a good AI book</query>
<clarification>
Are you asking about:
1. This Physical AI & Humanoid Robotics course
2. Other AI books or resources
</clarification>
</example>

Output format (XML):
<clarification>
[Clarification question with 2-3 numbered options, first option about THIS course]
</clarification>
"""


async def classify_query(query: str) -> Dict[str, any]:
    """
    Classify user query using LLM (T041-T043 tests).

    Args:
        query: User's question

    Returns:
        dict: {
            'classification': 'GREETING' | 'ON_TOPIC' | 'AMBIGUOUS' | 'OFF_TOPIC',
            'score': float (0.0, 0.5, or 1.0),
            'reasoning': str
        }

    Raises:
        Exception: If LLM call fails (caught by caller for fallback)
    """
    try:
        user_message = f"<query>{query}</query>"

        # Call LLM with classification prompt
        response = await llm_service.generate(
            prompt=user_message,
            preamble=CLASSIFICATION_SYSTEM_PROMPT,
            max_tokens=200,
            temperature=0.0  # Deterministic classification
        )

        # Parse XML response
        classification_match = re.search(r'<classification>(.*?)</classification>', response)
        score_match = re.search(r'<score>(.*?)</score>', response)
        reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response)

        return {
            'classification': classification_match.group(1).strip() if classification_match else 'ON_TOPIC',
            'score': float(score_match.group(1)) if score_match else 1.0,
            'reasoning': reasoning_match.group(1).strip() if reasoning_match else ''
        }

    except Exception as e:
        logger.error(f"Query classification failed: {e}")
        # Fallback: treat as on-topic (safe default)
        return {
            'classification': 'ON_TOPIC',
            'score': 1.0,
            'reasoning': 'Fallback due to classification error'
        }


async def generate_clarification(query: str) -> str:
    """
    Generate clarification question for ambiguous query (T042 test).

    Args:
        query: User's ambiguous question

    Returns:
        str: Clarification question with 2-3 numbered options
    """
    try:
        user_message = f"<query>{query}</query>"

        # Call LLM with clarification prompt
        response = await llm_service.generate(
            prompt=user_message,
            preamble=CLARIFICATION_SYSTEM_PROMPT,
            max_tokens=300,
            temperature=0.3  # Slight creativity for phrasing
        )

        # Parse XML
        match = re.search(r'<clarification>(.*?)</clarification>', response, re.DOTALL)
        return match.group(1).strip() if match else (
            "Could you clarify your question? "
            "Are you asking about this course specifically?"
        )

    except Exception as e:
        logger.error(f"Clarification generation failed: {e}")
        # Fallback to generic clarification
        return (
            "Could you clarify your question? "
            "Are you asking about this course specifically?"
        )


def get_greeting_response() -> str:
    """
    Get friendly greeting response.

    Returns:
        str: Greeting message
    """
    return (
        "Hello 👋 How can I help you with the Physical AI & Humanoid Robotics course?"
    )


def get_off_topic_response() -> str:
    """
    Get polite off-topic decline message.

    Returns:
        str: Off-topic decline message
    """
    return (
        "I can only help with the Physical AI & Humanoid Robotics "
        "course content. Please ask a question related to this course."
    )
