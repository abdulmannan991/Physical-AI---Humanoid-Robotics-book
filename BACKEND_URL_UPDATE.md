# ✅ Backend URL Update - Localhost to Hugging Face

## Date
2025-12-18

## Summary
Updated frontend chatbot to use Hugging Face deployed backend instead of localhost.

---

## Change Details

### File Modified
**`src/components/Chatbot/useChatbot.ts`** - Line 18

### Before
```typescript
const API_BASE_URL = 'http://localhost:8001/api/v1';
```

### After
```typescript
const API_BASE_URL = 'https://itsme00-physical-ai-book.hf.space/api/v1';
```

---

## API Endpoint

### Full Chat Endpoint URL
```
https://itsme00-physical-ai-book.hf.space/api/v1/chat
```

### Backend Base URL
```
https://itsme00-physical-ai-book.hf.space
```

### API Version Path
```
/api/v1
```

---

## Verification

### Search Results
- ✅ **localhost:8001** - Found and replaced in `useChatbot.ts`
- ✅ **localhost:8000** - No occurrences found in src/
- ✅ **localhost (any port)** - No other occurrences in src/

### Files Scanned
- `src/components/Chatbot/useChatbot.ts` ✅ Updated
- `src/components/` - No other localhost references
- `src/` - All subdirectories scanned

---

## Impact

### What Changed
- Frontend chatbot now points to production Hugging Face backend
- All API requests (`/chat` endpoint) now go to HF Space
- Session management works with production backend

### What Stayed the Same
- API request format (ChatRequest/ChatResponse types)
- Session storage logic
- Error handling
- All frontend functionality

---

## Testing Checklist

- [ ] Frontend builds successfully
- [ ] Chat window opens
- [ ] Can send messages to HF backend
- [ ] Receives responses from HF backend
- [ ] Session persistence works
- [ ] Citations display correctly
- [ ] Error handling works for network issues
- [ ] CORS is configured correctly on HF backend

---

## Notes

### CORS Configuration
Ensure your Hugging Face backend has CORS configured to allow requests from your frontend domain:

```python
# backend/app/core/config.py
CORS_ORIGINS: str = Field(
    default="http://localhost:3000,https://your-frontend-domain.com",
    description="Comma-separated list of allowed CORS origins"
)
```

### Environment Variables
The frontend now uses a hardcoded production URL. For better flexibility, consider using environment variables:

```typescript
// Future improvement (optional)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://itsme00-physical-ai-book.hf.space/api/v1';
```

### Backend Health Check
Test the backend is running:
```bash
curl https://itsme00-physical-ai-book.hf.space/api/v1/health
```

---

## Deployment

### Frontend Build
```bash
npm run build
# or
yarn build
```

### Frontend Dev Server
```bash
npm run dev
# or
yarn dev
```

### Production Deployment
After building, deploy your frontend to:
- Vercel
- Netlify
- GitHub Pages
- Or your preferred hosting

---

**Status:** ✅ Complete
**Backend:** Hugging Face Space (https://itsme00-physical-ai-book.hf.space)
**Endpoint:** /api/v1/chat
**Next Steps:** Build and deploy frontend, test end-to-end connectivity
