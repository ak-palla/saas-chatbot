from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ConversationBase(BaseModel):
    session_id: Optional[str] = None
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    chatbot_id: str


class Conversation(ConversationBase):
    id: str
    chatbot_id: str
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}