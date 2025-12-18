# Google Gemini - Quick Reference Card

## ⚡ Quick Setup (3 Steps)

### 1. Get API Key
Visit: https://aistudio.google.com/apikey

### 2. Set Environment Variable
```bash
export GOOGLE_API_KEY=your_key_here  # Linux/Mac
set GOOGLE_API_KEY=your_key_here     # Windows CMD
$env:GOOGLE_API_KEY="your_key_here"  # PowerShell
```

### 3. Run
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 🔧 Configuration

```python
from openai import OpenAI

client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

## 📋 Key Values

| Setting | Value |
|---------|-------|
| **Base URL** | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| **Model ID** | `gemini-1.5-flash` |
| **Environment Variable** | `GOOGLE_API_KEY` |
| **SDK Package** | `openai` (not google-generativeai) |

## 🧪 Test Command

```bash
python -c "from openai import OpenAI; client = OpenAI(api_key='YOUR_KEY', base_url='https://generativelanguage.googleapis.com/v1beta/openai/'); print(client.chat.completions.create(model='gemini-1.5-flash', messages=[{'role':'user','content':'Hi'}]).choices[0].message.content)"
```

## 📁 Files Modified

1. `backend/app/services/llm.py` - Updated to OpenAI-compatible endpoint
2. `backend/requirements.txt` - Removed google-generativeai

## 🔍 Verify Configuration

```python
# Test import
from app.services.llm import llm_service
print("✓ Import successful")

# Test initialization
if llm_service.client:
    print("✓ Client initialized")
    print(f"✓ Model: {llm_service.model_name}")
```

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Get new key from https://aistudio.google.com/apikey |
| "Model not found" | Use `gemini-1.5-flash` (not gemini-2.0) |
| "Connection error" | Check base URL has `/v1beta/openai/` at end |
| "Import error" | Run `pip install openai==1.55.3` |

## 📚 Documentation

- **Setup Guide**: `GEMINI_CONFIGURATION.md`
- **Code Example**: `gemini_code_snippet.py`
- **Comparison**: `CONFIGURATION_COMPARISON.md`
- **Full Summary**: `IMPLEMENTATION_SUMMARY.md`

## ✅ Checklist

- [ ] API key obtained
- [ ] Environment variable set
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test import successful
- [ ] Server starts without errors
- [ ] Chat endpoint responds

## 🎯 Quick Commands

```bash
# Install
pip install openai==1.55.3

# Test
python gemini_code_snippet.py

# Run server
cd backend && uvicorn app.main:app --reload

# Health check
curl http://localhost:8001/api/v1/health
```

## 🔗 URLs

- **API Key**: https://aistudio.google.com/apikey
- **Docs**: https://github.com/panaversity/learn-agentic-ai
- **Base URL**: https://generativelanguage.googleapis.com/v1beta/openai/

---

**Status**: ✅ Configured and Ready
**Model**: gemini-1.5-flash
**Pattern**: Agent SDK (OpenAI-compatible)
