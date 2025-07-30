"""
Text-to-Speech (TTS) Service using Deepgram
Handles text-to-speech conversion and audio generation
"""

import io
import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
try:
    from deepgram import DeepgramClient, SpeakOptions
    DEEPGRAM_ASYNC_AVAILABLE = False
except ImportError:
    try:
        from deepgram import AsyncDeepgramClient as DeepgramClient, SpeakOptions
        DEEPGRAM_ASYNC_AVAILABLE = True
    except ImportError:
        from deepgram import Deepgram
        DeepgramClient = Deepgram
        SpeakOptions = None
        DEEPGRAM_ASYNC_AVAILABLE = False
from app.core.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using Deepgram"""
    
    def __init__(self):
        self.client = DeepgramClient(settings.DEEPGRAM_API_KEY)
        
        # Available voice models
        self.voice_models = {
            "aura-asteria-en": {"language": "en", "gender": "female", "style": "conversational"},
            "aura-luna-en": {"language": "en", "gender": "female", "style": "young"},
            "aura-stella-en": {"language": "en", "gender": "female", "style": "professional"},
            "aura-athena-en": {"language": "en", "gender": "female", "style": "authoritative"},
            "aura-hera-en": {"language": "en", "gender": "female", "style": "warm"},
            "aura-orion-en": {"language": "en", "gender": "male", "style": "conversational"},
            "aura-arcas-en": {"language": "en", "gender": "male", "style": "young"},
            "aura-perseus-en": {"language": "en", "gender": "male", "style": "professional"},  
            "aura-angus-en": {"language": "en", "gender": "male", "style": "authoritative"},
            "aura-orpheus-en": {"language": "en", "gender": "male", "style": "warm"}
        }
        
        # Default settings
        self.default_voice = "aura-asteria-en"
        self.default_encoding = "linear16"  # High quality
        self.default_sample_rate = 24000  # 24kHz
        
        # Limits
        self.max_text_length = 10000  # 10k characters
        self.max_chunk_size = 2000  # 2k characters per chunk for streaming
    
    async def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        encoding: str = "linear16",
        sample_rate: int = 24000,
        bit_rate: Optional[int] = None,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> Dict[str, Any]:
        """
        Convert text to speech using Deepgram TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice model to use
            encoding: Audio encoding format
            sample_rate: Audio sample rate
            bit_rate: Audio bit rate (optional)
            speed: Speech speed multiplier (0.5-2.0)
            pitch: Pitch adjustment (-2.0 to 2.0)
            
        Returns:
            Dictionary with audio data and metadata
        """
        try:
            logger.info(f"Starting TTS synthesis, text length: {len(text)}, voice: {voice or self.default_voice}")
            
            # Validate input
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            if len(text) > self.max_text_length:
                raise ValueError(f"Text too long: {len(text)} characters (max: {self.max_text_length})")
            
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Set voice
            voice_model = voice or self.default_voice
            if voice_model not in self.voice_models:
                logger.warning(f"Unknown voice {voice_model}, using default {self.default_voice}")
                voice_model = self.default_voice
            
            # Configure speech options
            try:
                options = SpeakOptions(
                    model=voice_model,
                    encoding=encoding,
                    sample_rate=sample_rate
                )
            except Exception:
                # Fallback for older SDK versions
                options = {
                    "model": voice_model,
                    "encoding": encoding,
                    "sample_rate": sample_rate
                }
            
            if bit_rate:
                try:
                    options.bit_rate = bit_rate
                except:
                    if isinstance(options, dict):
                        options["bit_rate"] = bit_rate
            
            # Generate speech - Mock implementation for now
            # TODO: Fix Deepgram SDK integration
            logger.warning("Using mock TTS - Deepgram integration needs to be fixed")
            
            # Create fake audio data for testing
            import hashlib
            text_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
            audio_data = f"MOCK_AUDIO_DATA_{text_hash}_{voice_model}".encode()
            
            # In real implementation, this would be:
            # response = await self.client.speak.v("1").save(cleaned_text, options)
            # audio_data = response.content
            
            result = {
                "audio_data": audio_data,
                "voice": voice_model,
                "encoding": encoding,
                "sample_rate": sample_rate,
                "duration": self._estimate_duration(cleaned_text, speed),
                "text_length": len(cleaned_text),
                "voice_info": self.voice_models.get(voice_model, {}),
                "settings": {
                    "speed": speed,
                    "pitch": pitch,
                    "bit_rate": bit_rate
                }
            }
            
            logger.info(f"TTS synthesis completed, audio size: {len(audio_data)} bytes")
            return result
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise ValueError(f"Speech synthesis failed: {str(e)}")
    
    async def synthesize_streaming(
        self,
        text: str,
        voice: Optional[str] = None,
        encoding: str = "linear16",
        sample_rate: int = 24000,
        chunk_size: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream TTS synthesis for long text
        
        Args:
            text: Text to convert to speech
            voice: Voice model to use
            encoding: Audio encoding format  
            sample_rate: Audio sample rate
            chunk_size: Text chunk size for streaming
            
        Yields:
            Dictionary with audio chunk and metadata
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            cleaned_text = self._clean_text(text)
            chunk_size = chunk_size or self.max_chunk_size
            
            # Split text into chunks
            text_chunks = self._split_text_for_streaming(cleaned_text, chunk_size)
            
            total_chunks = len(text_chunks)
            voice_model = voice or self.default_voice
            
            logger.info(f"Starting streaming TTS synthesis, {total_chunks} chunks, voice: {voice_model}")
            
            for i, chunk in enumerate(text_chunks):
                try:
                    # Synthesize chunk
                    result = await self.synthesize_speech(
                        text=chunk,
                        voice=voice_model,
                        encoding=encoding,
                        sample_rate=sample_rate
                    )
                    
                    # Add streaming metadata
                    chunk_result = {
                        **result,
                        "chunk_index": i,
                        "total_chunks": total_chunks,
                        "is_final": i == total_chunks - 1,
                        "chunk_text": chunk
                    }
                    
                    yield chunk_result
                    
                except Exception as e:
                    logger.error(f"Failed to synthesize chunk {i}: {e}")
                    yield {
                        "error": str(e),
                        "chunk_index": i,
                        "total_chunks": total_chunks,
                        "is_final": i == total_chunks - 1
                    }
            
            logger.info("Streaming TTS synthesis completed")
            
        except Exception as e:
            logger.error(f"Streaming TTS synthesis failed: {e}")
            yield {
                "error": str(e),
                "chunk_index": 0,
                "total_chunks": 1,
                "is_final": True
            }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for TTS
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        cleaned = " ".join(text.split())
        
        # Replace common problematic characters
        replacements = {
            """: '"',
            """: '"',
            "'": "'",
            "'": "'",
            "…": "...",
            "—": " - ",
            "–": " - ",
            "\n": " ",
            "\t": " "
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove markdown formatting
        import re
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Bold
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)      # Italic
        cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)        # Code
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)  # Links
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _split_text_for_streaming(self, text: str, chunk_size: int) -> list[str]:
        """
        Split text into chunks for streaming synthesis
        
        Args:
            text: Text to split
            chunk_size: Maximum chunk size
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences first
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # If single sentence is too long, split by clauses/commas
            if len(sentence) > chunk_size:
                clauses = sentence.split(', ')
                for clause in clauses:
                    if len(current_chunk + clause) <= chunk_size:
                        current_chunk += clause + ", "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip().rstrip(','))
                            current_chunk = clause + ", "
                        else:
                            # Even single clause is too long, force split
                            chunks.append(clause[:chunk_size])
                            current_chunk = clause[chunk_size:] + ", "
            else:
                if len(current_chunk + sentence) <= chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """
        Estimate audio duration based on text length and speed
        
        Args:
            text: Text content
            speed: Speech speed multiplier
            
        Returns:
            Estimated duration in seconds
        """
        # Average speaking rate: ~150 words per minute
        words = len(text.split())
        base_duration = (words / 150.0) * 60.0  # seconds
        return base_duration / speed
    
    async def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available voices with metadata"""
        return self.voice_models.copy()
    
    def is_voice_available(self, voice: str) -> bool:
        """Check if voice is available"""
        return voice in self.voice_models
    
    async def health_check(self) -> Dict[str, Any]:
        """Check TTS service health"""
        try:
            # For now, just return healthy status without actual API call
            # TODO: Fix Deepgram SDK integration
            return {
                "status": "healthy",
                "default_voice": self.default_voice,
                "available_voices": len(self.voice_models),
                "max_text_length": self.max_text_length,
                "supported_encodings": ["linear16", "mp3", "wav"],
                "note": "Mock TTS service - Deepgram integration needs API key setup"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def voice_preview(self, voice: str, sample_text: str = "Hello, this is a voice preview.") -> Dict[str, Any]:
        """
        Generate a voice preview sample
        
        Args:
            voice: Voice model to preview
            sample_text: Sample text to speak
            
        Returns:
            Audio preview result
        """
        try:
            if not self.is_voice_available(voice):
                raise ValueError(f"Voice '{voice}' is not available")
            
            result = await self.synthesize_speech(
                text=sample_text,
                voice=voice,
                encoding="mp3",  # Use MP3 for smaller preview files
                sample_rate=24000
            )
            
            result["is_preview"] = True
            result["sample_text"] = sample_text
            
            return result
            
        except Exception as e:
            logger.error(f"Voice preview failed: {e}")
            raise ValueError(f"Voice preview failed: {str(e)}")


# Global TTS service instance
tts_service = TTSService()