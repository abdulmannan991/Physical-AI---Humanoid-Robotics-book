"""
API v1 Router Aggregator

Combines all v1 endpoints into a single router.

Constitution: backend/.specify/memory/constitution.md (Section 5.1)
"""

from fastapi import APIRouter

from app.api.v1 import health, chat, ingest, auth, profile

# Create v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(ingest.router)
api_router.include_router(auth.router)
api_router.include_router(profile.router)
