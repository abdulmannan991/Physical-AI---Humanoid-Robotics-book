"""
Google Gemini Configuration - Code Snippet
Updated: 2025-12-18

This snippet shows how to configure Google Gemini using the OpenAI-compatible endpoint
as documented in: https://github.com/panaversity/learn-agentic-ai

IMPORTANT: Use GOOGLE_API_KEY environment variable (not OpenAI key)
"""

import os
from openai import OpenAI

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get Google API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model ID - using gemini-1.5-flash as requested
MODEL_ID = "gemini-1.5-flash"

# Google's OpenAI-compatible endpoint
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# ============================================================================
# CLIENT INITIALIZATION
# ============================================================================

# Initialize OpenAI client pointing to Google's endpoint
client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url=BASE_URL
)

print(f"✓ Client initialized for Gemini model: {MODEL_ID}")

# ============================================================================
# BASIC USAGE EXAMPLE
# ============================================================================

def generate_response(prompt: str, context: str = "") -> str:
    """
    Generate response using Gemini via OpenAI-compatible API.

    Args:
        prompt: User's question
        context: Optional RAG context

    Returns:
        Generated response text
    """
    try:
        # System message (instructions)
        system_message = "You are a helpful AI assistant."

        # User message
        if context:
            user_message = f"Context: {context}\n\nQuestion: {prompt}"
        else:
            user_message = prompt

        # Call Gemini via OpenAI-compatible endpoint
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=1000,
            top_p=0.95,
        )

        # Extract response
        answer = response.choices[0].message.content
        return answer

    except Exception as e:
        print(f"Error: {e}")
        return None

# ============================================================================
# TEST EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Test the configuration
    test_prompt = "Explain what inverse kinematics is in one sentence."

    print("\nTesting Gemini configuration...")
    print(f"Prompt: {test_prompt}")
    print("\nResponse:")

    response = generate_response(test_prompt)
    if response:
        print(f"{response}\n")
        print("✓ Configuration successful!")
    else:
        print("✗ Configuration failed. Check your GOOGLE_API_KEY.")

# ============================================================================
# CONFIGURATION CHECKLIST
# ============================================================================

"""
SETUP CHECKLIST:

1. ✓ Install OpenAI SDK:
   pip install openai==1.55.3

2. ✓ Set environment variable:
   export GOOGLE_API_KEY=your_key_here  # Linux/Mac
   set GOOGLE_API_KEY=your_key_here     # Windows CMD
   $env:GOOGLE_API_KEY="your_key_here"  # PowerShell

3. ✓ Get API key from:
   https://aistudio.google.com/apikey

4. ✓ Update base URL to:
   https://generativelanguage.googleapis.com/v1beta/openai/

5. ✓ Use model ID:
   gemini-1.5-flash

KEY POINTS:
- Uses OpenAI SDK, not google-generativeai
- Base URL points to Google's OpenAI-compatible endpoint
- API key is GOOGLE_API_KEY, not OPENAI_API_KEY
- Follows official Agent SDK pattern
"""

# ============================================================================
# INTEGRATION WITH YOUR PROJECT
# ============================================================================

"""
In your project, this is already integrated in:

File: backend/app/services/llm.py

The LLMService class uses the same pattern:

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.GOOGLE_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model_name = "gemini-1.5-flash"

    def generate_response(self, prompt, context, ...):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[...],
            ...
        )
        return response.choices[0].message.content
"""
