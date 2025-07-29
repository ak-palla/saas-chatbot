"""
Message models for chat functionality
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class MessageRole(str):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"]
    metadata: Optional[Dict[str, Any]] = None


class ChatMessage(MessageBase):
    """Individual chat message"""
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request for chat completion"""
    message: str
    conversation_id: Optional[str] = None
    chatbot_id: str
    session_id: Optional[str] = None
    use_rag: bool = True
    stream: bool = False
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    """Response from chat completion"""
    content: str
    conversation_id: str
    message_id: Optional[str] = None
    model: str
    usage: Dict[str, int]
    rag_enabled: bool = False
    context_count: int = 0
    tools_used: List[Dict[str, Any]] = []
    response_time: float


class StreamingChatChunk(BaseModel):
    """Streaming chat response chunk"""
    content: str
    full_content: str
    finished: bool
    conversation_id: Optional[str] = None
    error: Optional[str] = None


class ConversationHistory(BaseModel):
    """Full conversation history"""
    conversation_id: str
    chatbot_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


class MessageCreateRequest(BaseModel):
    """Request to add message to conversation"""
    conversation_id: str
    content: str
    role: Literal["user", "assistant"]
    metadata: Optional[Dict[str, Any]] = None


class UsageRecord(BaseModel):
    """Usage tracking record"""
    user_id: str
    chatbot_id: str
    conversation_id: str
    message_count: int
    tokens_used: int
    model: str
    timestamp: datetime
    
    model_config = {"from_attributes": True}