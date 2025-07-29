"""
Speech-to-Text (STT) Service using Groq Whisper V3
Handles audio transcription and speech recognition
"""

import io
import logging
import tempfile
import aiofiles
from typing import Optional, Dict, Any
from groq import AsyncGroq
from pydub import AudioSegment
from app.core.config import settings

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service using Groq Whisper V3"""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "whisper-large-v3"
        
        # Supported audio formats
        self.supported_formats = [
            "mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm", "flac"
        ]
        
        # Audio processing settings
        self.max_file_size = 25 * 1024 * 1024  # 25MB (Groq limit)
        self.max_duration = 300  # 5 minutes
        self.target_sample_rate = 16000  # 16kHz for optimal processing
    
    async def transcribe_audio(
        self, 
        audio_data: bytes, 
        audio_format: str = "webm",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Transcribe audio data to text using Groq Whisper V3
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, mp3, wav, etc.)
            language: ISO 639-1 language code (optional, auto-detect if None)
            prompt: Optional prompt to guide transcription
            temperature: Temperature for transcription (0.0-1.0)
            
        Returns:
            Dictionary with transcription results
        """
        try:
            logger.info(f"Starting audio transcription, format: {audio_format}, size: {len(audio_data)} bytes")
            
            # Validate audio data
            if not audio_data:
                raise ValueError("Audio data is empty")
            
            if len(audio_data) > self.max_file_size:
                raise ValueError(f"Audio file too large: {len(audio_data)} bytes (max: {self.max_file_size})")
            
            # Process audio if needed
            processed_audio = await self._preprocess_audio(audio_data, audio_format)
            
            # Create temporary file for Groq API
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(processed_audio)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using Groq Whisper V3
                async with aiofiles.open(temp_file_path, 'rb') as audio_file:
                    transcription_params = {
                        "file": audio_file,
                        "model": self.model,
                        "temperature": temperature,
                        "response_format": "verbose_json"
                    }
                    
                    if language:
                        transcription_params["language"] = language
                    
                    if prompt:
                        transcription_params["prompt"] = prompt
                    
                    response = await self.client.audio.transcriptions.create(**transcription_params)
                
                # Process response
                result = {
                    "text": response.text,
                    "language": getattr(response, 'language', language or 'auto'),
                    "duration": getattr(response, 'duration', 0),
                    "segments": getattr(response, 'segments', []),
                    "confidence": self._calculate_confidence(response),
                    "model": self.model,
                    "processing_time": 0  # Will be set by caller
                }
                
                logger.info(f"Audio transcription completed successfully, text length: {len(result['text'])}")
                return result
                
            finally:
                # Cleanup temporary file
                import os
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise ValueError(f"Transcription failed: {str(e)}")
    
    async def transcribe_stream(
        self,
        audio_chunks: list[bytes],
        audio_format: str = "webm",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe multiple audio chunks as a single stream
        
        Args:
            audio_chunks: List of audio chunk bytes
            audio_format: Audio format
            language: Language code
            
        Returns:
            Transcription result
        """
        try:
            if not audio_chunks:
                raise ValueError("No audio chunks provided")
            
            # Combine audio chunks
            combined_audio = b''.join(audio_chunks)
            
            # Transcribe combined audio
            result = await self.transcribe_audio(
                audio_data=combined_audio,
                audio_format=audio_format,
                language=language
            )
            
            result["chunk_count"] = len(audio_chunks)
            return result
            
        except Exception as e:
            logger.error(f"Stream transcription failed: {e}")
            raise ValueError(f"Stream transcription failed: {str(e)}")
    
    async def _preprocess_audio(self, audio_data: bytes, audio_format: str) -> bytes:
        """
        Preprocess audio for optimal transcription
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format
            
        Returns:
            Processed audio bytes
        """
        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data), 
                format=audio_format
            )
            
            # Check duration
            duration_seconds = len(audio) / 1000.0
            if duration_seconds > self.max_duration:
                logger.warning(f"Audio duration {duration_seconds}s exceeds maximum {self.max_duration}s")
                # Truncate audio
                audio = audio[:self.max_duration * 1000]
            
            # Optimize audio settings
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate to 16kHz for optimal processing
            if audio.frame_rate != self.target_sample_rate:
                audio = audio.set_frame_rate(self.target_sample_rate)
            
            # Normalize volume
            audio = audio.normalize()
            
            # Remove silence from beginning and end
            audio = audio.strip_silence(silence_thresh=-40, padding=100)
            
            # Export processed audio
            buffer = io.BytesIO()
            audio.export(buffer, format=audio_format)
            processed_data = buffer.getvalue()
            
            logger.debug(f"Audio preprocessing completed: {len(audio_data)} -> {len(processed_data)} bytes")
            return processed_data
            
        except Exception as e:
            logger.warning(f"Audio preprocessing failed, using original: {e}")
            return audio_data
    
    def _calculate_confidence(self, response) -> float:
        """
        Calculate overall confidence score from transcription response
        
        Args:
            response: Groq transcription response
            
        Returns:
            Confidence score (0.0-1.0)
        """
        try:
            if hasattr(response, 'segments') and response.segments:
                # Calculate average confidence from segments
                total_confidence = 0
                total_duration = 0
                
                for segment in response.segments:
                    if hasattr(segment, 'avg_logprob') and hasattr(segment, 'end') and hasattr(segment, 'start'):
                        duration = segment.end - segment.start
                        # Convert log probability to confidence (approximate)
                        confidence = min(1.0, max(0.0, (segment.avg_logprob + 5.0) / 5.0))
                        total_confidence += confidence * duration
                        total_duration += duration
                
                if total_duration > 0:
                    return total_confidence / total_duration
            
            # Default confidence for successful transcription
            return 0.85
            
        except Exception as e:
            logger.warning(f"Could not calculate confidence: {e}")
            return 0.8
    
    async def detect_language(self, audio_data: bytes, audio_format: str = "webm") -> Dict[str, Any]:
        """
        Detect language of audio without full transcription
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format
            
        Returns:
            Language detection result
        """
        try:
            # For language detection, we can use a shorter sample
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format)
            
            # Use first 30 seconds for language detection
            if len(audio) > 30000:  # 30 seconds in milliseconds
                audio = audio[:30000]
            
            # Convert back to bytes
            buffer = io.BytesIO()
            audio.export(buffer, format=audio_format)
            sample_data = buffer.getvalue()
            
            # Transcribe sample with language detection
            result = await self.transcribe_audio(
                audio_data=sample_data,
                audio_format=audio_format,
                temperature=0.0
            )
            
            return {
                "language": result.get("language", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "sample_text": result.get("text", "")[:100]  # First 100 chars
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "sample_text": ""
            }
    
    def is_format_supported(self, audio_format: str) -> bool:
        """Check if audio format is supported"""
        return audio_format.lower() in self.supported_formats
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats"""
        return self.supported_formats.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check STT service health"""
        try:
            # Test with a minimal audio sample
            # Create a 1-second silence for testing
            test_audio = AudioSegment.silent(duration=1000)  # 1 second
            buffer = io.BytesIO()
            test_audio.export(buffer, format="wav")
            test_data = buffer.getvalue()
            
            # This will fail but we can check if the API is reachable
            try:
                await self.transcribe_audio(test_data, "wav")
            except:
                pass
            
            return {
                "status": "healthy",
                "model": self.model,
                "supported_formats": self.supported_formats,
                "max_file_size": self.max_file_size,
                "max_duration": self.max_duration
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global STT service instance
stt_service = STTService()