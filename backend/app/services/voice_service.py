"""
Voice Service - Orchestrates the complete voice chat pipeline
Handles STT → LLM → TTS workflow for voice conversations
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime

from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.message_service import message_service
from app.models.message import ChatRequest
from app.core.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class VoiceService:
    """Main voice service orchestrating STT → LLM → TTS pipeline"""
    
    def __init__(self):
        self.processing_sessions: Dict[str, bool] = {}  # Track active processing
        
        # Default voice settings
        self.default_voice_config = {
            "tts_voice": "aura-asteria-en",
            "tts_speed": 1.0,
            "tts_pitch": 0.0,
            "stt_language": None,  # Auto-detect
            "audio_format": "webm"
        }
    
    async def process_voice_message(
        self,
        session_id: str,
        audio_data: bytes,
        chatbot_id: str,
        user_id: str,
        voice_config: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process complete voice message: STT → LLM → TTS
        
        Args:
            session_id: WebSocket session ID
            audio_data: Raw audio bytes from user
            chatbot_id: Chatbot ID for processing
            user_id: User ID
            voice_config: Voice processing configuration
            conversation_id: Optional conversation ID
            
        Returns:
            Processing result with audio response
        """
        start_time = time.time()
        
        try:
            # Check if session is already processing
            if session_id in self.processing_sessions:
                raise ValueError("Session is already processing a voice message")
            
            self.processing_sessions[session_id] = True
            
            logger.info(f"Starting voice message processing for session {session_id}")
            
            # Merge voice configuration
            config = {**self.default_voice_config, **(voice_config or {})}
            
            # Send processing status
            await websocket_manager.send_message(session_id, {
                "type": "voice_processing_started",
                "stage": "transcription",
                "message": "Converting speech to text..."
            })
            
            # Step 1: Speech-to-Text
            stt_start = time.time()
            transcription_result = await stt_service.transcribe_audio(
                audio_data=audio_data,
                audio_format=config["audio_format"],
                language=config["stt_language"]
            )
            stt_time = time.time() - stt_start
            
            transcribed_text = transcription_result["text"]
            if not transcribed_text.strip():
                raise ValueError("No speech detected in audio")
            
            logger.info(f"STT completed in {stt_time:.2f}s: '{transcribed_text[:100]}...'")
            
            # Send transcription result
            await websocket_manager.send_message(session_id, {
                "type": "transcription_complete",
                "text": transcribed_text,
                "language": transcription_result.get("language"),
                "confidence": transcription_result.get("confidence", 0.8),
                "processing_time": stt_time
            })
            
            # Step 2: LLM Processing
            await websocket_manager.send_message(session_id, {
                "type": "voice_processing_started",
                "stage": "generation",
                "message": "Generating response..."
            })
            
            llm_start = time.time()
            
            # Create chat request
            chat_request = ChatRequest(
                message=transcribed_text,
                chatbot_id=chatbot_id,
                conversation_id=conversation_id,
                use_rag=True,
                stream=False  # Don't stream for voice
            )
            
            # Process with LLM
            chat_response = await message_service.process_chat_message(
                request=chat_request,
                user_id=user_id
            )
            
            llm_time = time.time() - llm_start
            response_text = chat_response.content
            
            logger.info(f"LLM completed in {llm_time:.2f}s: '{response_text[:100]}...'")
            
            # Send LLM response
            await websocket_manager.send_message(session_id, {
                "type": "response_generated",
                "text": response_text,
                "conversation_id": chat_response.conversation_id,
                "model": chat_response.model,
                "processing_time": llm_time,
                "rag_enabled": chat_response.rag_enabled,
                "context_count": chat_response.context_count
            })
            
            # Step 3: Text-to-Speech
            await websocket_manager.send_message(session_id, {
                "type": "voice_processing_started",
                "stage": "synthesis",
                "message": "Converting text to speech..."
            })
            
            tts_start = time.time()
            tts_result = await tts_service.synthesize_speech(
                text=response_text,
                voice=config["tts_voice"],
                speed=config["tts_speed"],
                pitch=config["tts_pitch"],
                encoding="mp3",  # Use MP3 for WebSocket transmission
                sample_rate=24000
            )
            tts_time = time.time() - tts_start
            
            logger.info(f"TTS completed in {tts_time:.2f}s, audio size: {len(tts_result['audio_data'])} bytes")
            
            # Send audio response via WebSocket
            await websocket_manager.send_binary(session_id, tts_result["audio_data"])
            
            # Send completion status
            total_time = time.time() - start_time
            completion_message = {
                "type": "voice_processing_complete",
                "transcription": {
                    "text": transcribed_text,
                    "language": transcription_result.get("language"),
                    "confidence": transcription_result.get("confidence"),
                    "processing_time": stt_time
                },
                "response": {
                    "text": response_text,
                    "conversation_id": chat_response.conversation_id,
                    "model": chat_response.model,
                    "processing_time": llm_time,
                    "rag_enabled": chat_response.rag_enabled
                },
                "audio": {
                    "voice": config["tts_voice"],
                    "duration": tts_result.get("duration", 0),
                    "size": len(tts_result["audio_data"]),
                    "processing_time": tts_time
                },
                "total_processing_time": total_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket_manager.send_message(session_id, completion_message)
            
            # Return result for API responses
            return {
                "success": True,
                "session_id": session_id,
                "transcription": transcription_result,
                "response": chat_response.dict(),
                "audio": tts_result,
                "processing_times": {
                    "stt": stt_time,
                    "llm": llm_time,
                    "tts": tts_time,
                    "total": total_time
                }
            }
            
        except Exception as e:
            logger.error(f"Voice processing failed for session {session_id}: {e}")
            
            # Send error message
            await websocket_manager.send_message(session_id, {
                "type": "voice_processing_error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            
        finally:
            # Clean up processing flag
            self.processing_sessions.pop(session_id, None)
    
    async def process_voice_streaming(
        self,
        session_id: str,
        audio_data: bytes,
        chatbot_id: str,
        user_id: str,
        voice_config: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process voice message with streaming TTS response
        
        Args:
            session_id: WebSocket session ID
            audio_data: Raw audio bytes
            chatbot_id: Chatbot ID
            user_id: User ID
            voice_config: Voice configuration
            conversation_id: Optional conversation ID
            
        Yields:
            Processing status updates and audio chunks
        """
        try:
            if session_id in self.processing_sessions:
                yield {"error": "Session is already processing a voice message"}
                return
            
            self.processing_sessions[session_id] = True
            config = {**self.default_voice_config, **(voice_config or {})}
            
            # STT Phase
            yield {
                "type": "processing_update",
                "stage": "transcription",
                "message": "Converting speech to text..."
            }
            
            transcription_result = await stt_service.transcribe_audio(
                audio_data=audio_data,
                audio_format=config["audio_format"],
                language=config["stt_language"]
            )
            
            transcribed_text = transcription_result["text"]
            if not transcribed_text.strip():
                yield {"error": "No speech detected in audio"}
                return
            
            yield {
                "type": "transcription_complete",
                **transcription_result
            }
            
            # LLM Phase
            yield {
                "type": "processing_update", 
                "stage": "generation",
                "message": "Generating response..."
            }
            
            chat_request = ChatRequest(
                message=transcribed_text,
                chatbot_id=chatbot_id,
                conversation_id=conversation_id,
                use_rag=True,
                stream=False
            )
            
            chat_response = await message_service.process_chat_message(
                request=chat_request,
                user_id=user_id
            )
            
            yield {
                "type": "response_generated",
                "text": chat_response.content,
                "conversation_id": chat_response.conversation_id,
                "model": chat_response.model
            }
            
            # TTS Streaming Phase
            yield {
                "type": "processing_update",
                "stage": "synthesis", 
                "message": "Converting text to speech..."
            }
            
            async for tts_chunk in tts_service.synthesize_streaming(
                text=chat_response.content,
                voice=config["tts_voice"],
                encoding="mp3",
                sample_rate=24000
            ):
                if "error" in tts_chunk:
                    yield {"error": f"TTS error: {tts_chunk['error']}"}
                    continue
                
                # Send audio chunk via WebSocket
                if "audio_data" in tts_chunk:
                    await websocket_manager.send_binary(session_id, tts_chunk["audio_data"])
                
                yield {
                    "type": "audio_chunk",
                    "chunk_index": tts_chunk.get("chunk_index", 0),
                    "total_chunks": tts_chunk.get("total_chunks", 1),
                    "is_final": tts_chunk.get("is_final", False),
                    "audio_size": len(tts_chunk.get("audio_data", b""))
                }
            
            yield {
                "type": "processing_complete",
                "message": "Voice processing completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Streaming voice processing failed: {e}")
            yield {"error": str(e)}
            
        finally:
            self.processing_sessions.pop(session_id, None)
    
    async def handle_text_input(
        self,
        session_id: str,
        text: str,
        chatbot_id: str,
        user_id: str,
        voice_config: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle text input during voice session (skip STT, do LLM → TTS)
        
        Args:
            session_id: WebSocket session ID
            text: Text message from user
            chatbot_id: Chatbot ID
            user_id: User ID
            voice_config: Voice configuration
            conversation_id: Optional conversation ID
            
        Returns:
            Processing result
        """
        try:
            config = {**self.default_voice_config, **(voice_config or {})}
            
            # Send processing status
            await websocket_manager.send_message(session_id, {
                "type": "text_processing_started",
                "message": "Processing text message..."
            })
            
            # Process with LLM
            chat_request = ChatRequest(
                message=text,
                chatbot_id=chatbot_id,
                conversation_id=conversation_id,
                use_rag=True,
                stream=False
            )
            
            chat_response = await message_service.process_chat_message(
                request=chat_request,
                user_id=user_id
            )
            
            # Convert response to speech
            tts_result = await tts_service.synthesize_speech(
                text=chat_response.content,
                voice=config["tts_voice"],
                speed=config["tts_speed"],
                pitch=config["tts_pitch"],
                encoding="mp3"
            )
            
            # Send audio response
            await websocket_manager.send_binary(session_id, tts_result["audio_data"])
            
            # Send completion message
            await websocket_manager.send_message(session_id, {
                "type": "text_processing_complete",
                "input_text": text,
                "response_text": chat_response.content,
                "conversation_id": chat_response.conversation_id,
                "audio_duration": tts_result.get("duration", 0)
            })
            
            return {
                "success": True,
                "response": chat_response.dict(),
                "audio": tts_result
            }
            
        except Exception as e:
            logger.error(f"Text processing failed for session {session_id}: {e}")
            
            await websocket_manager.send_message(session_id, {
                "type": "text_processing_error",
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_voice_config(self, user_id: str, chatbot_id: str) -> Dict[str, Any]:
        """
        Get voice configuration for user/chatbot
        
        Args:
            user_id: User ID
            chatbot_id: Chatbot ID
            
        Returns:
            Voice configuration
        """
        try:
            # TODO: Implement database storage for voice configs
            # For now, return default configuration
            return self.default_voice_config.copy()
            
        except Exception as e:
            logger.error(f"Failed to get voice config: {e}")
            return self.default_voice_config.copy()
    
    async def update_voice_config(
        self,
        user_id: str,
        chatbot_id: str,
        voice_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update voice configuration for user/chatbot
        
        Args:
            user_id: User ID
            chatbot_id: Chatbot ID
            voice_config: New voice configuration
            
        Returns:
            Updated configuration
        """
        try:
            # Validate configuration
            valid_config = {}
            
            if "tts_voice" in voice_config:
                if await tts_service.is_voice_available(voice_config["tts_voice"]):
                    valid_config["tts_voice"] = voice_config["tts_voice"]
            
            if "tts_speed" in voice_config:
                speed = float(voice_config["tts_speed"])
                valid_config["tts_speed"] = max(0.5, min(2.0, speed))
            
            if "tts_pitch" in voice_config:
                pitch = float(voice_config["tts_pitch"])
                valid_config["tts_pitch"] = max(-2.0, min(2.0, pitch))
            
            if "stt_language" in voice_config:
                valid_config["stt_language"] = voice_config["stt_language"]
            
            if "audio_format" in voice_config:
                if stt_service.is_format_supported(voice_config["audio_format"]):
                    valid_config["audio_format"] = voice_config["audio_format"]
            
            # TODO: Store in database
            # For now, return the validated config
            return {**self.default_voice_config, **valid_config}
            
        except Exception as e:
            logger.error(f"Failed to update voice config: {e}")
            raise ValueError(f"Invalid voice configuration: {str(e)}")
    
    def is_session_processing(self, session_id: str) -> bool:
        """Check if session is currently processing"""
        return session_id in self.processing_sessions
    
    async def health_check(self) -> Dict[str, Any]:
        """Check voice service health"""
        try:
            # Simple health check without calling external services
            return {
                "status": "healthy",
                "components": {
                    "stt": {"status": "ready", "note": "Groq Whisper V3"},
                    "tts": {"status": "ready", "note": "Mock TTS (Deepgram needs setup)"}
                },
                "active_sessions": len(self.processing_sessions),
                "default_config": self.default_voice_config,
                "note": "Voice services loaded successfully"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global voice service instance
voice_service = VoiceService()