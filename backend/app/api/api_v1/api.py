from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, health, chatbots, conversations, documents, chat, voice, voice_websocket, billing

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(chatbots.router, prefix="/chatbots", tags=["chatbots"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(voice_websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])