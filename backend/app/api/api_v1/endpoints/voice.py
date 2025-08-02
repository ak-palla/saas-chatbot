"""
Voice processing REST API endpoints
Handles voice chat requests, TTS, STT, and voice configuration
"""

import io
import logging
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, List

from app.models.voice import (
    VoiceChatRequest, VoiceChatResponse, TextToSpeechRequest, TextToSpeechResponse,
    SpeechToTextRequest, SpeechToTextResponse, VoiceConfig, VoiceConfigUpdate,
    VoicePreviewRequest, AvailableVoice, VoiceCapabilities
)
from app.core.supabase_auth import get_current_user_supabase
from app.services.voice_service import voice_service
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service, DEEPGRAM_AVAILABLE
from app.utils.audio_utils import audio_processor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(
    chatbot_id: str = Form(...),
    audio_file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    voice_config: Optional[str] = Form(None),  # JSON string
    use_rag: bool = Form(True),
    current_user: dict = Depends(get_current_user_supabase)
):
    """
    Process voice message through complete STT→LLM→TTS pipeline
    
    Upload audio file and receive AI response as audio
    """
    try:
        logger.info(f"Voice chat request from user {current_user['id']} for chatbot {chatbot_id}")
        
        # Validate chatbot ownership
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        chatbot_response = supabase.table("chatbots") \
            .select("id,name") \
            .eq("id", chatbot_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Read audio file
        audio_data = await audio_file.read()
        if not audio_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file"
            )
        
        # Validate audio
        audio_format = audio_file.filename.split('.')[-1].lower() if audio_file.filename else "webm"
        validation = audio_processor.validate_audio(audio_data, audio_format)
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid audio: {validation['error']}"
            )
        
        # Parse voice config
        config = None
        if voice_config:
            import json
            try:
                config_dict = json.loads(voice_config)
                config = VoiceConfig(**config_dict)
            except Exception as e:
                logger.warning(f"Invalid voice config: {e}")
        
        # Create temporary session ID for processing
        import uuid
        temp_session_id = str(uuid.uuid4())
        
        # Process voice message
        result = await voice_service.process_voice_message(
            session_id=temp_session_id,
            audio_data=audio_data,
            chatbot_id=chatbot_id,
            user_id=current_user["id"],
            voice_config=config.dict() if config else None,
            conversation_id=conversation_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Voice processing failed")
            )
        
        # Format response
        response = VoiceChatResponse(
            success=True,
            session_id=temp_session_id,
            transcription=result["transcription"],
            response_text=result["response"]["content"],
            conversation_id=result["response"]["conversation_id"],
            audio_duration=result["audio"]["duration"],
            audio_size=len(result["audio"]["audio_data"]),
            processing_times=result["processing_times"]
        )
        
        # Store audio data in response (FastAPI will handle serialization)
        response.audio_data = result["audio"]["audio_data"]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice chat processing failed: {str(e)}"
        )


@router.post("/tts", response_model=bytes)
async def text_to_speech(
    request: TextToSpeechRequest,
    user_email: str
):
    """
    Convert text to speech - Simplified email-based authentication
    
    Returns audio data as bytes
    """
    try:
        logger.info(f"TTS request from user {user_email}, text length: {len(request.text)}")
        logger.info(f"TTS service status: available={tts_service.is_available}, client={tts_service.client is not None}")
        
        # Check if TTS service is available
        if not hasattr(tts_service, 'is_available') or not tts_service.is_available:
            logger.error("TTS service not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="TTS service not available - check Deepgram configuration"
            )
        
        # Verify user exists (similar to other endpoints)
        from app.core.database import get_supabase_admin
        supabase = get_supabase_admin()
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Calling TTS service with voice: {request.voice}, encoding: {request.encoding}")
        
        # Synthesize speech
        result = await tts_service.synthesize_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            pitch=request.pitch,
            encoding=request.encoding,
            sample_rate=request.sample_rate
        )
        
        logger.info(f"TTS synthesis completed, audio size: {len(result['audio_data'])} bytes")
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(result["audio_data"]),
            media_type=f"audio/{request.encoding}",
            headers={
                "Content-Disposition": f"attachment; filename=tts_output.{request.encoding}",
                "X-Audio-Duration": str(result["duration"]),
                "X-Voice-Used": result["voice"],
                "X-Text-Length": str(result["text_length"])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"TTS processing failed for user {user_email} with text: {request.text}")
        logger.error(f"TTS error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-speech failed: {str(e)}"
        )


@router.post("/stt", response_model=SpeechToTextResponse)
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    temperature: float = Form(0.0),
    current_user: dict = Depends(get_current_user_supabase)
):
    """
    Convert speech to text
    
    Upload audio file and receive transcription
    """
    try:
        logger.info(f"STT request from user {current_user['id']}")
        
        # Read audio file
        audio_data = await audio_file.read()
        if not audio_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file"
            )
        
        # Determine audio format
        audio_format = audio_file.filename.split('.')[-1].lower() if audio_file.filename else "webm"
        
        if not stt_service.is_format_supported(audio_format):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported audio format: {audio_format}"
            )
        
        # Transcribe audio
        result = await stt_service.transcribe_audio(
            audio_data=audio_data,
            audio_format=audio_format,
            language=language,
            prompt=prompt,
            temperature=temperature
        )
        
        # Format response
        response = SpeechToTextResponse(
            text=result["text"],
            language=result["language"],
            duration=result["duration"],
            confidence=result["confidence"],
            segments=result["segments"],
            model=result["model"],
            processing_time=result["processing_time"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech-to-text failed: {str(e)}"
        )


@router.get("/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices_dict = await tts_service.get_available_voices()
        
        # Return simple list of voice IDs as expected by tests
        voice_ids = list(voices_dict.keys())
        return {"voices": voice_ids}
        
    except Exception as e:
        logger.error(f"Failed to get available voices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available voices"
        )


@router.post("/voices/{voice_id}/preview")
async def preview_voice(
    voice_id: str,
    request: VoicePreviewRequest,
    current_user: dict = Depends(get_current_user_supabase)
):
    """
    Generate voice preview sample
    
    Returns audio preview as streaming response
    """
    try:
        if not tts_service.is_voice_available(voice_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice not found"
            )
        
        # Generate preview
        result = await tts_service.voice_preview(voice_id, request.sample_text)
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(result["audio_data"]),
            media_type="audio/mp3",
            headers={
                "Content-Disposition": f"attachment; filename=voice_preview_{voice_id}.mp3",
                "X-Voice-ID": voice_id,
                "X-Sample-Text": request.sample_text,
                "X-Duration": str(result["duration"])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice preview failed: {str(e)}"
        )


@router.get("/config/{chatbot_id}", response_model=VoiceConfig)
async def get_voice_config(
    chatbot_id: str,
    current_user: dict = Depends(get_current_user_supabase)
):
    """Get voice configuration for chatbot"""
    try:
        # Verify chatbot ownership
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        chatbot_response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", chatbot_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Get voice configuration
        config = await voice_service.get_voice_config(current_user["id"], chatbot_id)
        
        return VoiceConfig(**config)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get voice config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get voice configuration"
        )


@router.put("/config/{chatbot_id}", response_model=VoiceConfig)
async def update_voice_config(
    chatbot_id: str,
    config_update: VoiceConfigUpdate,
    current_user: dict = Depends(get_current_user_supabase)
):
    """Update voice configuration for chatbot"""
    try:
        # Verify chatbot ownership
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        chatbot_response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", chatbot_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Update voice configuration
        config_dict = {k: v for k, v in config_update.dict().items() if v is not None}
        
        updated_config = await voice_service.update_voice_config(
            current_user["id"],
            chatbot_id,
            config_dict
        )
        
        return VoiceConfig(**updated_config)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update voice config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update voice configuration: {str(e)}"
        )


@router.get("/capabilities")
async def get_voice_capabilities():
    """Get voice service capabilities and supported features"""
    try:
        # Get available voices
        voices_dict = await tts_service.get_available_voices()
        available_voices = []
        
        for voice_id, voice_info in voices_dict.items():
            available_voices.append(AvailableVoice(
                id=voice_id,
                language=voice_info.get("language", "en"),
                gender=voice_info.get("gender", "unknown"),
                style=voice_info.get("style", "neutral")
            ))
        
        # Get STT capabilities
        stt_formats = stt_service.get_supported_formats()
        
        capabilities = VoiceCapabilities(
            stt_supported_formats=stt_formats,
            stt_supported_languages=["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh", "auto"],  # Common languages
            tts_available_voices=available_voices,
            max_audio_duration=300,  # 5 minutes
            max_text_length=10000,   # 10k characters
            streaming_supported=True,
            real_time_processing=True
        )
        
        # Return with stt field for test compatibility
        return {
            "stt": {
                "supported_formats": capabilities.stt_supported_formats,
                "supported_languages": capabilities.stt_supported_languages
            },
            "supported_formats": capabilities.stt_supported_formats,
            "tts": {
                "available_voices": capabilities.tts_available_voices
            },
            "websocket": {
                "real_time_streaming": True,
                "audio_buffer_support": True,
                "session_management": True
            },
            "max_audio_duration": capabilities.max_audio_duration,
            "max_text_length": capabilities.max_text_length,
            "streaming_supported": capabilities.streaming_supported,
            "real_time_processing": capabilities.real_time_processing
        }
        
    except Exception as e:
        logger.error(f"Failed to get voice capabilities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get voice capabilities"
        )


@router.get("/health")
async def voice_service_health():
    """Check voice service health"""
    try:
        health = await voice_service.health_check()
        
        # Also check TTS service specifically
        tts_status = {
            "available": getattr(tts_service, 'is_available', False),
            "client_initialized": getattr(tts_service, 'client', None) is not None,
        }
        
        return {
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "active_sessions": health.get("active_sessions", 0),
            "tts_service": tts_status,
            "endpoints": {
                "voice_chat": "/voice/chat",
                "text_to_speech": "/voice/tts", 
                "speech_to_text": "/voice/stt",
                "available_voices": "/voice/voices",
                "voice_config": "/voice/config/{chatbot_id}",
                "capabilities": "/voice/capabilities"
            }
        }
        
    except Exception as e:
        logger.error(f"Voice service health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/tts/health")
async def tts_service_health():
    """Check TTS service health specifically"""
    try:
        return {
            "tts_available": getattr(tts_service, 'is_available', False),
            "client_initialized": getattr(tts_service, 'client', None) is not None,
            "deepgram_available": DEEPGRAM_AVAILABLE,
            "service_status": "healthy" if getattr(tts_service, 'is_available', False) else "unavailable"
        }
    except Exception as e:
        logger.error(f"TTS health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }