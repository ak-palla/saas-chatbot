"""
WebSocket endpoints for real-time voice chat
Handles WebSocket connections and voice message processing
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Optional

from app.core.websocket_manager import websocket_manager, VoiceSession
from app.core.auth import get_current_user_websocket, get_current_user
from app.services.voice_service import voice_service
from app.models.voice import VoiceConfig

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/voice/{chatbot_id}")
async def voice_chat_websocket(
    websocket: WebSocket,
    chatbot_id: str,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time voice chat
    
    Protocol:
    - Connect with authentication token
    - Send audio chunks as binary data
    - Send control messages as JSON text
    - Receive processed audio and status updates
    """
    session_id = None
    user_id = None
    
    try:
        # Authenticate user
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
            return
        
        try:
            user = await get_current_user_websocket(token)
            user_id = user["id"]
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
            return
        
        # Verify chatbot exists and user has access
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        chatbot_response = supabase.table("chatbots") \
            .select("id,name,system_prompt") \
            .eq("id", chatbot_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not chatbot_response.data:
            await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason="Chatbot not found or access denied")
            return
        
        # Establish WebSocket connection
        session_id = await websocket_manager.connect(websocket, chatbot_id, user_id)
        
        logger.info(f"Voice WebSocket connected: session_id={session_id}, user_id={user_id}, chatbot_id={chatbot_id}")
        
        # Main message loop
        while True:
            try:
                # Check if connection is still active
                session = websocket_manager.get_session(session_id)
                if not session or not session.is_active:
                    break
                
                # Wait for message (can be text or binary)
                message = await websocket.receive()
                
                if "text" in message:
                    # Handle text message (control messages)
                    await handle_text_message(session_id, message["text"], chatbot_id, user_id)
                
                elif "bytes" in message:
                    # Handle binary message (audio data) 
                    await handle_audio_message(session_id, message["bytes"], chatbot_id, user_id)
                
                else:
                    logger.warning(f"Unknown message type from session {session_id}")
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: session_id={session_id}")
                break
                
            except Exception as e:
                logger.error(f"Error handling WebSocket message for session {session_id}: {e}")
                
                # Send error message to client
                await websocket_manager.send_message(session_id, {
                    "type": "error",
                    "message": "Failed to process message",
                    "error": str(e)
                })
                
                # Continue the loop unless it's a critical error
                if "connection" in str(e).lower():
                    break
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        
    finally:
        # Clean up connection
        if session_id:
            await websocket_manager.disconnect(session_id)
        
        logger.info(f"Voice WebSocket cleanup completed for session {session_id}")


async def handle_text_message(session_id: str, text_data: str, chatbot_id: str, user_id: str):
    """Handle incoming text message from WebSocket"""
    try:
        # Parse JSON message
        message = json.loads(text_data)
        
        # Handle different message types
        result = await websocket_manager.handle_websocket_message(session_id, message)
        
        if result:
            if isinstance(result, bytes):
                # Audio data returned from audio_stop
                await process_voice_audio(session_id, result, chatbot_id, user_id)
                
            elif isinstance(result, dict) and result.get("type") == "text_input":
                # Text input during voice session
                await process_text_input(session_id, result["content"], chatbot_id, user_id)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON message from session {session_id}: {e}")
        await websocket_manager.send_message(session_id, {
            "type": "error",
            "message": "Invalid JSON format"
        })
        
    except Exception as e:
        logger.error(f"Error handling text message for session {session_id}: {e}")
        await websocket_manager.send_message(session_id, {
            "type": "error", 
            "message": "Failed to process text message"
        })


async def handle_audio_message(session_id: str, audio_data: bytes, chatbot_id: str, user_id: str):
    """Handle incoming audio data from WebSocket"""
    try:
        # Add audio chunk to session buffer
        await websocket_manager.add_audio_chunk(session_id, audio_data)
        
        # Send acknowledgment
        await websocket_manager.send_message(session_id, {
            "type": "audio_chunk_received",
            "size": len(audio_data)
        })
        
    except Exception as e:
        logger.error(f"Error handling audio message for session {session_id}: {e}")
        await websocket_manager.send_message(session_id, {
            "type": "error",
            "message": "Failed to process audio chunk"
        })


async def process_voice_audio(session_id: str, audio_data: bytes, chatbot_id: str, user_id: str):
    """Process accumulated voice audio through STT→LLM→TTS pipeline"""
    try:
        session = websocket_manager.get_session(session_id)
        if not session:
            return
        
        # Get voice configuration
        voice_config = await voice_service.get_voice_config(user_id, chatbot_id)
        
        # Process voice message
        await voice_service.process_voice_message(
            session_id=session_id,
            audio_data=audio_data,
            chatbot_id=chatbot_id,
            user_id=user_id,
            voice_config=voice_config,
            conversation_id=session.conversation_id
        )
        
    except Exception as e:
        logger.error(f"Voice processing failed for session {session_id}: {e}")
        await websocket_manager.send_message(session_id, {
            "type": "voice_processing_error",
            "error": str(e)
        })


async def process_text_input(session_id: str, text: str, chatbot_id: str, user_id: str):
    """Process text input during voice session"""
    try:
        session = websocket_manager.get_session(session_id)
        if not session:
            return
        
        # Get voice configuration
        voice_config = await voice_service.get_voice_config(user_id, chatbot_id)
        
        # Process text input (skip STT, do LLM→TTS)
        await voice_service.handle_text_input(
            session_id=session_id,
            text=text,
            chatbot_id=chatbot_id,
            user_id=user_id,
            voice_config=voice_config,
            conversation_id=session.conversation_id
        )
        
    except Exception as e:
        logger.error(f"Text processing failed for session {session_id}: {e}")
        await websocket_manager.send_message(session_id, {
            "type": "text_processing_error",
            "error": str(e)
        })


@router.get("/voice/sessions/stats")
async def get_voice_session_stats(current_user: dict = Depends(get_current_user)):
    """Get voice session statistics"""
    try:
        stats = websocket_manager.get_stats()
        
        # Add user-specific stats
        user_sessions = websocket_manager.get_user_sessions(current_user["id"])
        user_stats = {
            "user_active_sessions": len(user_sessions),
            "user_sessions": [
                {
                    "session_id": session.session_id,
                    "chatbot_id": session.chatbot_id,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "conversation_id": session.conversation_id
                }
                for session in user_sessions
            ]
        }
        
        return {**stats, **user_stats}
        
    except Exception as e:
        logger.error(f"Failed to get voice session stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session statistics"
        )


@router.delete("/voice/sessions/{session_id}")
async def disconnect_voice_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Disconnect a specific voice session"""
    try:
        session = websocket_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify session ownership
        if session.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Disconnect session
        await websocket_manager.disconnect(session_id)
        
        return {"message": "Session disconnected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect session"
        )


@router.get("/voice/health")
async def voice_websocket_health():
    """Check voice WebSocket service health"""
    try:
        # Check WebSocket manager
        ws_stats = websocket_manager.get_stats()
        
        # Check voice service
        voice_health = await voice_service.health_check()
        
        return {
            "status": "healthy" if voice_health.get("status") == "healthy" else "degraded",
            "websocket_stats": ws_stats,
            "voice_service": voice_health,
            "endpoints": {
                "voice_chat": "/ws/voice/{chatbot_id}",
                "session_stats": "/voice/sessions/stats",
                "disconnect_session": "/voice/sessions/{session_id}"
            }
        }
        
    except Exception as e:
        logger.error(f"Voice WebSocket health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }