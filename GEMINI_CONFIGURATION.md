# Google Gemini Configuration - Agent SDK Pattern

## Overview
This document shows the updated configuration for switching from OpenAI to Google Gemini using the **OpenAI-compatible endpoint** as documented in the official Agent SDK guide.

**Reference Documentation**: https://github.com/panaversity/learn-agentic-ai/blob/main/01_ai_agents_first/05_model_configuration/readme.md

## Why Use the OpenAI-Compatible Endpoint?

Instead of using Google's native SDK (`google-generativeai`), we use the **OpenAI SDK** pointed at Google's OpenAI-compatible endpoint. This approach:

✅ Follows the official Agent SDK pattern
✅ Uses standardized OpenAI interface (easier to switch models)
✅ Compatible with Agent SDK framework
✅ Recommended by the official documentation

## Configuration Steps

### 1. Environment Variables

Create or update your `.env` file:

```bash
# Google Gemini API Key (required)
GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration
GEMINI_MODEL=gemini-1.5-flash

# OpenAI API Key (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Updated LLM Service Code

**File**: `backend/app/services/llm.py`

```python
"""
LLM Client Service

Provides interface for Google Gemini LLM chat completion using OpenAI-compatible endpoint.

Official Documentation: https://github.com/panaversity/learn-agentic-ai/blob/main/01_ai_agents_first/05_model_configuration/readme.md
"""

import logging
from typing import Optional
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using Google Gemini via OpenAI-compatible endpoint.

    Uses OpenAI SDK with Google's OpenAI-compatible base URL.
    """

    def __init__(self):
        """Initialize Google Gemini LLM client using OpenAI-compatible endpoint."""
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
        self._is_available = True
        self.client = None

        try:
            # Get Google API key from environment
            api_key = getattr(settings, 'GOOGLE_API_KEY', None)
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in settings")

            # Initialize OpenAI client pointing to Google's OpenAI-compatible endpoint
            # This is the official Agent SDK pattern
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

            logger.info(f"Google Gemini initialized: model={self.model_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._is_available = False
            self.client = None

    def generate_response(
        self,
        prompt: str,
        context: str,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        Generate response using Google Gemini via OpenAI-compatible API.
        """
        if not self._is_available or not self.client:
            logger.error("Gemini client not available")
            return None

        try:
            # System instruction
            system_message = (
                "You are a helpful assistant for the Physical AI & Humanoid Robotics course. "
                "Answer questions based ONLY on the provided context. "
                "If the context doesn't contain enough information, say so honestly. "
                "Cite specific sections when possible."
            )

            # User message with RAG context
            user_message = f"""Context from course content:
{context}

Question: {prompt}

Answer the question based on the context above. Be concise and accurate."""

            # Call Gemini via OpenAI-compatible chat completions endpoint
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
            )

            # Extract response
            if response and response.choices and len(response.choices) > 0:
                answer = response.choices[0].message.content
                logger.info(f"Generated response using Gemini ({self.model_name})")
                return answer
            else:
                logger.warning("Empty response from Gemini")
                return None

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None


# Global service instance
llm_service = LLMService()
```

### 3. Key Configuration Elements

| Element | Value | Description |
|---------|-------|-------------|
| **Base URL** | `https://generativelanguage.googleapis.com/v1beta/openai/` | Google's OpenAI-compatible endpoint |
| **Model ID** | `gemini-1.5-flash` | Latest stable Gemini model (as requested) |
| **API Key** | `GOOGLE_API_KEY` | Environment variable for authentication |
| **SDK** | `openai` (Python package) | OpenAI SDK for standardized interface |

### 4. Dependencies

**File**: `backend/requirements.txt`

```txt
# OpenAI SDK (used for both Gemini LLM and OpenAI Embeddings)
openai==1.55.3

# Other dependencies remain the same...
```

**Note**: We removed `google-generativeai` because we're using the OpenAI SDK instead.

## Usage Examples

### Basic Usage (Already Integrated)

The service is already integrated into your FastAPI application:

```python
from app.services.llm import llm_service

# Generate response with RAG context
response = llm_service.generate_response(
    prompt="What is inverse kinematics?",
    context="[Retrieved context from Qdrant...]",
    temperature=0.3,
    max_tokens=1000
)
```

### Agent SDK Pattern (Advanced)

If you want to use the full Agent SDK framework in the future:

```python
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner

# Create client
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Create agent
agent = Agent(
    name="CourseAssistant",
    instructions="You are a helpful assistant for Physical AI & Humanoid Robotics.",
    model=OpenAIChatCompletionsModel(
        model="gemini-1.5-flash",
        openai_client=gemini_client
    )
)

# Run agent
result = await Runner.run(agent, "What is inverse kinematics?")
```

## Configuration Levels

According to the documentation, there are three ways to configure the model:

### 1. Agent Level (Recommended)
Each agent uses its own client:
```python
agent = Agent(
    model=OpenAIChatCompletionsModel(
        model="gemini-1.5-flash",
        openai_client=gemini_client
    )
)
```

### 2. Run Level
Pass configuration at runtime:
```python
config = RunConfig(
    model=OpenAIChatCompletionsModel(
        model="gemini-1.5-flash",
        openai_client=gemini_client
    )
)
result = Runner.run_sync(agent, prompt, run_config=config)
```

### 3. Global Level
Set defaults for all agents:
```python
from agents import set_default_openai_client
set_default_openai_client(gemini_client)
```

## Testing

### Test the Configuration

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GOOGLE_API_KEY=your_api_key_here  # Linux/Mac
set GOOGLE_API_KEY=your_api_key_here     # Windows CMD
$env:GOOGLE_API_KEY="your_api_key_here"  # Windows PowerShell

# Test import
python -c "from app.services.llm import llm_service; print('✓ Import successful')"

# Start server
uvicorn app.main:app --reload --port 8001
```

### Verify the Endpoint

```bash
# Health check
curl http://localhost:8001/api/v1/health

# Test chat (requires full setup)
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is inverse kinematics?"}'
```

## Comparison: Old vs New

| Aspect | Old (Native SDK) | New (OpenAI-Compatible) |
|--------|------------------|-------------------------|
| **SDK** | `google-generativeai` | `openai` |
| **Import** | `import google.generativeai as genai` | `from openai import OpenAI` |
| **Client** | `genai.GenerativeModel()` | `OpenAI(base_url=...)` |
| **Method** | `generate_content()` | `chat.completions.create()` |
| **Pattern** | Google-specific | OpenAI-compatible (Agent SDK) |
| **Switching** | Hard (Google-specific code) | Easy (standard interface) |

## Advantages of This Approach

1. **Standards-Based**: Uses OpenAI's widely-adopted API format
2. **Future-Proof**: Easy to switch between models (Gemini, GPT-4, etc.)
3. **Agent SDK Ready**: Compatible with Agent SDK framework
4. **Documentation**: Follows official Agent SDK documentation
5. **Tooling**: Works with OpenAI-compatible tools and libraries

## Important Notes

⚠️ **API Key**: Make sure you're using a Google AI API key, not a Google Cloud API key
⚠️ **Base URL**: The base URL must include the `/v1beta/openai/` path
⚠️ **Model ID**: Use `gemini-1.5-flash` (not `models/gemini-1.5-flash`)
⚠️ **Endpoint**: This is a beta endpoint, subject to Google's terms

## Troubleshooting

### Issue: "Invalid API key"
- Verify your `GOOGLE_API_KEY` is correct
- Get a key from https://aistudio.google.com/apikey

### Issue: "Model not found"
- Ensure you're using `gemini-1.5-flash` (not `gemini-2.0-flash` which may require different access)
- Check Google's documentation for available models

### Issue: "Connection error"
- Verify the base URL is exactly: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Check your internet connection

## Next Steps

1. ✅ Configuration complete
2. Set your `GOOGLE_API_KEY` in `.env`
3. Install dependencies: `pip install -r requirements.txt`
4. Test the server: `uvicorn app.main:app --reload`
5. Verify responses are coming from Gemini

---

**Configuration Date**: 2025-12-18
**Model**: gemini-1.5-flash
**Pattern**: Agent SDK (OpenAI-compatible endpoint)
**Status**: ✅ Complete
