"""
Voice-related data models and schemas
Handles voice chat requests, responses, and configurations
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class VoiceConfig(BaseModel):
    """Voice processing configuration"""
    tts_voice: str = Field(default="aura-asteria-en", description="TTS voice model")
    tts_speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    tts_pitch: float = Field(default=0.0, ge=-2.0, le=2.0, description="Pitch adjustment")
    stt_language: Optional[str] = Field(default="en", description="STT language code (auto-detect if None)")
    audio_format: str = Field(default="webm", description="Audio format for processing")


class VoiceSessionInfo(BaseModel):
    """Voice session information"""
    session_id: str
    chatbot_id: str
    user_id: str
    conversation_id: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    voice_config: VoiceConfig


class AudioTranscription(BaseModel):
    """Audio transcription result"""
    text: str
    language: str
    duration: float
    confidence: float
    segments: List[Dict[str, Any]] = []
    model: str
    processing_time: float


class VoiceChatRequest(BaseModel):
    """Voice chat processing request"""
    chatbot_id: str
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    voice_config: Optional[VoiceConfig] = None
    use_rag: bool = True
    stream_tts: bool = False


class VoiceChatResponse(BaseModel):
    """Voice chat processing response"""
    success: bool
    session_id: str
    transcription: Optional[AudioTranscription] = None
    response_text: str
    conversation_id: str
    audio_duration: float
    audio_size: int
    processing_times: Dict[str, float]
    error: Optional[str] = None


class TextToSpeechRequest(BaseModel):
    """Text-to-speech conversion request"""
    text: str = Field(..., max_length=10000, description="Text to convert to speech")
    voice: Optional[str] = Field(default="aura-asteria-en", description="Voice model to use")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    pitch: float = Field(default=0.0, ge=-2.0, le=2.0, description="Pitch adjustment")
    encoding: str = Field(default="mp3", description="Audio encoding format")
    sample_rate: int = Field(default=24000, description="Audio sample rate")
    stream: bool = Field(default=False, description="Stream audio chunks")


class TextToSpeechResponse(BaseModel):
    """Text-to-speech conversion response"""
    audio_data: bytes
    voice: str
    encoding: str
    sample_rate: int
    duration: float
    text_length: int
    voice_info: Dict[str, Any]
    settings: Dict[str, Any]


class SpeechToTextRequest(BaseModel):
    """Speech-to-text conversion request"""
    audio_format: str = Field(default="webm", description="Audio format")
    language: Optional[str] = Field(default=None, description="Language code (auto-detect if None)")
    prompt: Optional[str] = Field(default=None, description="Transcription prompt")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0, description="Transcription temperature")


class SpeechToTextResponse(BaseModel):
    """Speech-to-text conversion response"""
    text: str
    language: str
    duration: float
    confidence: float
    segments: List[Dict[str, Any]]
    model: str
    processing_time: float


class VoiceWebSocketMessage(BaseModel):
    """WebSocket message for voice chat"""
    type: Literal[
        "ping", "pong", "audio_start", "audio_stop", "audio_chunk", 
        "text_message", "connection_established", "voice_processing_started",
        "transcription_complete", "response_generated", "voice_processing_complete",
        "voice_processing_error", "text_processing_started", "text_processing_complete",
        "text_processing_error", "audio_ready", "audio_processing", "processing_update",
        "error"
    ]
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class VoiceServiceHealth(BaseModel):
    """Voice service health status"""
    status: Literal["healthy", "degraded", "unhealthy"]
    components: Dict[str, Dict[str, Any]]
    active_sessions: int
    default_config: VoiceConfig
    error: Optional[str] = None


class AvailableVoice(BaseModel):
    """Available TTS voice information"""
    id: str
    language: str
    gender: str
    style: str
    description: Optional[str] = None


class VoicePreviewRequest(BaseModel):
    """Voice preview generation request"""
    voice: str
    sample_text: str = Field(default="Hello, this is a voice preview.", max_length=200)


class StreamingAudioChunk(BaseModel):
    """Streaming audio chunk"""
    chunk_index: int
    total_chunks: int
    is_final: bool
    audio_data: bytes
    chunk_text: Optional[str] = None
    error: Optional[str] = None


class VoiceSessionStats(BaseModel):
    """Voice session statistics"""
    total_sessions: int
    active_sessions: int
    sessions_by_user: Dict[str, int]
    processing_sessions: int
    average_session_duration: float
    total_audio_processed: int


class VoiceConfigUpdate(BaseModel):
    """Voice configuration update request"""
    tts_voice: Optional[str] = None
    tts_speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    tts_pitch: Optional[float] = Field(None, ge=-2.0, le=2.0)
    stt_language: Optional[str] = None
    audio_format: Optional[str] = None


class VoiceError(BaseModel):
    """Voice processing error"""
    error_type: Literal["stt_error", "llm_error", "tts_error", "session_error", "config_error"]
    message: str
    details: Optional[Dict[str, Any]] = None


class VoiceSession(BaseModel):
    """Voice session model for testing"""
    session_id: str
    user_id: str
    chatbot_id: str
    status: str = "active"
    created_at: float  # Unix timestamp
    last_activity: float  # Unix timestamp
    total_messages: int = 0
    total_duration: float = 0.0
    conversation_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VoiceUsage(BaseModel):
    """Voice usage tracking model"""
    id: int
    user_id: str
    chatbot_id: str
    session_id: str
    message_type: str
    duration: float
    audio_format: str
    processing_time: float
    success: bool
    created_at: float  # Unix timestamp
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VoiceUsageRecord(BaseModel):
    """Voice usage tracking record"""
    user_id: str
    chatbot_id: str
    session_id: str
    conversation_id: Optional[str] = None
    audio_duration_input: float  # Duration of input audio
    audio_duration_output: float  # Duration of output audio
    text_length_transcribed: int
    text_length_synthesized: int
    voice_used: str
    processing_times: Dict[str, float]
    timestamp: datetime
    
    model_config = {"from_attributes": True}


class VoiceSessionCreate(BaseModel):
    """Voice session creation request"""
    chatbot_id: str
    voice_config: Optional[VoiceConfig] = None
    conversation_id: Optional[str] = None


class VoiceSessionUpdate(BaseModel):
    """Voice session update request"""
    voice_config: Optional[VoiceConfig] = None
    conversation_id: Optional[str] = None
    is_active: Optional[bool] = None


class BatchVoiceRequest(BaseModel):
    """Batch voice processing request"""
    requests: List[VoiceChatRequest] = Field(..., max_items=10)
    process_parallel: bool = Field(default=False, description="Process requests in parallel")


class BatchVoiceResponse(BaseModel):
    """Batch voice processing response"""
    results: List[VoiceChatResponse]
    total_processing_time: float
    successful_requests: int
    failed_requests: int


class VoiceAnalytics(BaseModel):
    """Voice service analytics"""
    period_start: datetime
    period_end: datetime
    total_sessions: int
    total_audio_minutes_processed: float
    total_words_transcribed: int
    total_words_synthesized: int
    most_used_voices: List[Dict[str, Any]]
    average_processing_times: Dict[str, float]
    error_rate: float
    user_engagement: Dict[str, Any]


class VoiceCapabilities(BaseModel):
    """Voice service capabilities"""
    stt_supported_formats: List[str]
    stt_supported_languages: List[str]
    tts_available_voices: List[AvailableVoice]
    max_audio_duration: int  # seconds
    max_text_length: int  # characters
    streaming_supported: bool
    real_time_processing: bool