from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ChatbotBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    appearance_config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class ChatbotCreate(ChatbotBase):
    pass


class ChatbotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    appearance_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class Chatbot(ChatbotBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}