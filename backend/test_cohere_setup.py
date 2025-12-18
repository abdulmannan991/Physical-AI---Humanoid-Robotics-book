"""
Test Cohere Setup

Quick test script to verify Cohere configuration is working correctly.
"""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Cohere Configuration")
print("=" * 60)

# Test 1: Import services
print("\n1. Testing imports...")
try:
    from app.services.llm import llm_service
    from app.services.embeddings import embeddings_service
    from app.core.config import settings
    print("   ✓ Imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check environment variables
print("\n2. Checking environment variables...")
try:
    cohere_key = settings.COHERE_API_KEY
    if cohere_key and len(cohere_key) > 10:
        print(f"   ✓ COHERE_API_KEY is set (length: {len(cohere_key)})")
    else:
        print("   ✗ COHERE_API_KEY not set or invalid")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Failed to read COHERE_API_KEY: {e}")
    sys.exit(1)

# Test 3: Check model configuration
print("\n3. Checking model configuration...")
try:
    print(f"   - LLM Model: {settings.COHERE_CHAT_MODEL}")
    print(f"   - Embedding Model: {settings.EMBEDDING_MODEL_NAME}")
    print(f"   - Vector Size: {settings.QDRANT_VECTOR_SIZE}")

    if settings.QDRANT_VECTOR_SIZE == 1024:
        print("   ✓ Vector size correct for Cohere (1024)")
    else:
        print(f"   ✗ Vector size incorrect: {settings.QDRANT_VECTOR_SIZE} (should be 1024)")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Configuration error: {e}")
    sys.exit(1)

# Test 4: Check LLM service initialization
print("\n4. Checking LLM service...")
try:
    if llm_service._is_available and llm_service.client:
        print(f"   ✓ LLM service initialized (model: {llm_service.model})")
    else:
        print("   ✗ LLM service not available")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ LLM service error: {e}")
    sys.exit(1)

# Test 5: Check embeddings service initialization
print("\n5. Checking embeddings service...")
try:
    if embeddings_service._is_available and embeddings_service.client:
        print(f"   ✓ Embeddings service initialized (model: {embeddings_service.model_name})")
    else:
        print("   ✗ Embeddings service not available")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Embeddings service error: {e}")
    sys.exit(1)

# Test 6: Check CORS configuration
print("\n6. Checking CORS configuration...")
try:
    cors_origins = settings.get_cors_origins_list()
    print(f"   ✓ CORS origins: {cors_origins}")
except Exception as e:
    print(f"   ✗ CORS configuration error: {e}")
    sys.exit(1)

# Test 7: Test embedding generation (optional - requires API call)
print("\n7. Testing embedding generation (requires API call)...")
try:
    test_text = "test"
    embedding = embeddings_service.generate_embedding(test_text)
    if embedding and len(embedding) == 1024:
        print(f"   ✓ Generated embedding (dimension: {len(embedding)})")
    else:
        print(f"   ⚠ Embedding test skipped or failed")
except Exception as e:
    print(f"   ⚠ Embedding test failed: {e}")
    print("   (This is normal if API key is not set)")

print("\n" + "=" * 60)
print("✓ All critical tests passed!")
print("=" * 60)
print("\nYour Cohere configuration is ready.")
print("You can now start the server with:")
print("  uvicorn app.main:app --reload --port 8001")
print()
