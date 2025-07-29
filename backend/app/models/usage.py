from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UsageType(str, Enum):
    TEXT_CHAT = "text_chat"
    VOICE_CHAT = "voice_chat"
    DOCUMENT_UPLOAD = "document_upload"
    EMBEDDING_GENERATION = "embedding_generation"
    STT_PROCESSING = "stt_processing"
    TTS_PROCESSING = "tts_processing"


class UsageRecord(BaseModel):
    id: str
    user_id: str
    chatbot_id: Optional[str] = None
    usage_type: UsageType
    tokens_used: Optional[int] = None
    audio_seconds: Optional[float] = None
    api_endpoint: str
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UsageStats(BaseModel):
    user_id: str
    total_tokens: int
    total_audio_seconds: float
    total_cost: float
    period_start: datetime
    period_end: datetime
    breakdown_by_type: Dict[UsageType, Dict[str, Any]]