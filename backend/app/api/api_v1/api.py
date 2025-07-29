from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, health, chatbots, conversations

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(chatbots.router, prefix="/chatbots", tags=["chatbots"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])