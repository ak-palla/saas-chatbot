"""
Audio utilities for format conversion, validation, and processing
Handles various audio operations needed for voice chat functionality
"""

import io
import logging
import tempfile
import base64
import os
from typing import Optional, Tuple, Dict, Any, Union, List
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

logger = logging.getLogger(__name__)

# Configure pydub to use the correct FFmpeg path
def configure_ffmpeg_path():
    """Configure pydub to use the correct FFmpeg executable"""
    ffmpeg_path = r"C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin\ffmpeg.exe"
    ffprobe_path = r"C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin\ffprobe.exe"
    
    # Only configure if files exist
    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffmpeg = ffmpeg_path
        AudioSegment.ffprobe = ffprobe_path
        logger.info(f"Configured pydub to use FFmpeg at: {ffmpeg_path}")
    else:
        logger.warning("FFmpeg not found at expected location, using system PATH")

# Configure FFmpeg on module import
configure_ffmpeg_path()


class AudioProcessor:
    """Audio processing utilities"""
    
    def __init__(self):
        # Supported formats
        self.supported_input_formats = [
            "mp3", "wav", "flac", "aac", "ogg", "webm", "m4a", "mp4", "wma"
        ]
        self.supported_output_formats = [
            "mp3", "wav", "flac", "ogg", "webm"
        ]
        
        # Audio quality settings
        self.quality_presets = {
            "low": {"bitrate": "64k", "sample_rate": 16000},
            "medium": {"bitrate": "128k", "sample_rate": 22050},
            "high": {"bitrate": "192k", "sample_rate": 44100},
            "ultra": {"bitrate": "320k", "sample_rate": 48000}
        }
        
        # Processing limits
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_duration = 3600  # 1 hour in seconds
        self.min_duration = 0.1  # 0.1 seconds
    
    def validate_audio(self, audio_data: bytes, format_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate audio data and extract metadata
        
        Args:
            audio_data: Audio bytes
            format_hint: Expected format
            
        Returns:
            Validation result with metadata
        """
        try:
            if not audio_data:
                return {"valid": False, "error": "Audio data is empty"}
            
            if len(audio_data) > self.max_file_size:
                return {
                    "valid": False, 
                    "error": f"File too large: {len(audio_data)} bytes (max: {self.max_file_size})"
                }
            
            # Try to load audio
            try:
                if format_hint:
                    audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format_hint)
                else:
                    # Try common formats
                    audio = None
                    for fmt in ["webm", "mp3", "wav", "ogg", "m4a"]:
                        try:
                            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=fmt)
                            format_hint = fmt
                            break
                        except:
                            continue
                    
                    if audio is None:
                        return {"valid": False, "error": "Could not decode audio format"}
                        
            except CouldntDecodeError as e:
                return {"valid": False, "error": f"Could not decode audio: {str(e)}"}
            
            # Extract metadata
            duration_seconds = len(audio) / 1000.0
            
            if duration_seconds < self.min_duration:
                return {
                    "valid": False,
                    "error": f"Audio too short: {duration_seconds:.2f}s (min: {self.min_duration}s)"
                }
            
            if duration_seconds > self.max_duration:
                return {
                    "valid": False,
                    "error": f"Audio too long: {duration_seconds:.2f}s (max: {self.max_duration}s)"
                }
            
            metadata = {
                "valid": True,
                "format": format_hint,
                "duration": duration_seconds,
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "frame_count": audio.frame_count(),
                "sample_width": audio.sample_width,
                "file_size": len(audio_data),
                "bit_rate": self._estimate_bitrate(len(audio_data), duration_seconds)
            }
            
            logger.debug(f"Audio validation successful: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def convert_format(
        self,
        audio_data: bytes,
        input_format: str,
        output_format: str,
        quality: str = "medium"
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Convert audio between formats
        
        Args:
            audio_data: Input audio bytes
            input_format: Input format
            output_format: Output format
            quality: Quality preset
            
        Returns:
            Tuple of (converted_audio_bytes, conversion_info)
        """
        try:
            if output_format not in self.supported_output_formats:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            if quality not in self.quality_presets:
                quality = "medium"
            
            preset = self.quality_presets[quality]
            
            # Load audio
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)
            
            # Apply quality settings
            if audio.frame_rate != preset["sample_rate"]:
                audio = audio.set_frame_rate(preset["sample_rate"])
            
            # Convert to mono if needed for better compression
            if output_format in ["mp3", "ogg"] and audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Export with quality settings
            buffer = io.BytesIO()
            export_params = {"format": output_format}
            
            if output_format == "mp3":
                export_params["bitrate"] = preset["bitrate"]
                export_params["parameters"] = ["-q:a", "2"]  # High quality MP3
            elif output_format == "ogg":
                export_params["bitrate"] = preset["bitrate"]
            elif output_format == "wav":
                # WAV doesn't use bitrate
                pass
            
            audio.export(buffer, **export_params)
            converted_data = buffer.getvalue()
            
            conversion_info = {
                "input_format": input_format,
                "output_format": output_format,
                "input_size": len(audio_data),
                "output_size": len(converted_data),
                "compression_ratio": len(audio_data) / len(converted_data) if converted_data else 0,
                "quality": quality,
                "duration": len(audio) / 1000.0,
                "sample_rate": preset["sample_rate"],
                "channels": audio.channels
            }
            
            logger.debug(f"Audio conversion completed: {conversion_info}")
            return converted_data, conversion_info
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise ValueError(f"Audio conversion failed: {str(e)}")
    
    def optimize_for_speech(
        self,
        audio_data: bytes,
        input_format: str,
        target_format: str = "wav"
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Optimize audio for speech recognition
        
        Args:
            audio_data: Input audio bytes
            input_format: Input format
            target_format: Target format
            
        Returns:
            Tuple of (optimized_audio_bytes, optimization_info)
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)
            
            original_duration = len(audio) / 1000.0
            
            # Speech optimization steps:
            
            # 1. Convert to mono (speech recognition works better with mono)
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # 2. Normalize audio level
            audio = audio.normalize()
            
            # 3. Set optimal sample rate for speech (16kHz is standard)
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
            
            # 4. Remove silence from beginning and end
            audio = audio.strip_silence(silence_thresh=-40, chunk_len=100, padding=50)
            
            # 5. Apply gentle noise reduction (high-pass filter for low-frequency noise)
            # This is a simple approach - more sophisticated noise reduction could be added
            audio = audio.high_pass_filter(80)  # Remove very low frequencies
            
            # 6. Compress dynamic range slightly to normalize volume levels
            audio = audio.compress_dynamic_range(threshold=-20.0, ratio=2.0, attack=5.0, release=50.0)
            
            # Export optimized audio
            buffer = io.BytesIO()
            audio.export(buffer, format=target_format)
            optimized_data = buffer.getvalue()
            
            optimization_info = {
                "input_format": input_format,
                "output_format": target_format,
                "input_size": len(audio_data),
                "output_size": len(optimized_data),
                "original_duration": original_duration,
                "optimized_duration": len(audio) / 1000.0,
                "sample_rate": 16000,
                "channels": 1,
                "optimizations_applied": [
                    "mono_conversion",
                    "normalization", 
                    "sample_rate_optimization",
                    "silence_removal",
                    "noise_reduction",
                    "dynamic_range_compression"
                ]
            }
            
            logger.debug(f"Speech optimization completed: {optimization_info}")
            return optimized_data, optimization_info
            
        except Exception as e:
            logger.error(f"Speech optimization failed: {e}")
            raise ValueError(f"Speech optimization failed: {str(e)}")
    
    def split_audio(
        self,
        audio_data: bytes,
        input_format: str,
        chunk_duration: float,
        overlap: float = 0.0
    ) -> List[Tuple[bytes, Dict[str, Any]]]:
        """
        Split audio into chunks
        
        Args:
            audio_data: Input audio bytes
            input_format: Input format
            chunk_duration: Duration of each chunk in seconds
            overlap: Overlap between chunks in seconds
            
        Returns:
            List of (chunk_bytes, chunk_info) tuples
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)
            
            chunk_length_ms = int(chunk_duration * 1000)
            overlap_ms = int(overlap * 1000)
            step_ms = chunk_length_ms - overlap_ms
            
            chunks = []
            start = 0
            chunk_index = 0
            
            while start < len(audio):
                end = min(start + chunk_length_ms, len(audio))
                chunk = audio[start:end]
                
                # Export chunk
                buffer = io.BytesIO()
                chunk.export(buffer, format=input_format)
                chunk_data = buffer.getvalue()
                
                chunk_info = {
                    "index": chunk_index,
                    "start_time": start / 1000.0,
                    "end_time": end / 1000.0,
                    "duration": (end - start) / 1000.0,
                    "size": len(chunk_data),
                    "format": input_format
                }
                
                chunks.append((chunk_data, chunk_info))
                
                start += step_ms
                chunk_index += 1
                
                # Prevent infinite loop
                if chunk_index > 1000:
                    logger.warning("Too many chunks, stopping at 1000")
                    break
            
            logger.debug(f"Audio split into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Audio splitting failed: {e}")
            raise ValueError(f"Audio splitting failed: {str(e)}")
    
    def combine_audio_chunks(
        self,
        chunks: List[bytes],
        format: str,
        crossfade_ms: int = 0
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Combine audio chunks into single audio
        
        Args:
            chunks: List of audio chunk bytes
            format: Audio format
            crossfade_ms: Crossfade duration in milliseconds
            
        Returns:
            Tuple of (combined_audio, combine_info)
        """
        try:
            if not chunks:
                raise ValueError("No chunks provided")
            
            # Load first chunk
            combined = AudioSegment.from_file(io.BytesIO(chunks[0]), format=format)
            
            # Combine remaining chunks
            for i, chunk_data in enumerate(chunks[1:], 1):
                chunk = AudioSegment.from_file(io.BytesIO(chunk_data), format=format)
                
                if crossfade_ms > 0 and len(combined) > crossfade_ms and len(chunk) > crossfade_ms:
                    # Apply crossfade
                    combined = combined.append(chunk, crossfade=crossfade_ms)
                else:
                    # Simple append
                    combined = combined + chunk
            
            # Export combined audio
            buffer = io.BytesIO()
            combined.export(buffer, format=format)
            combined_data = buffer.getvalue()
            
            combine_info = {
                "chunk_count": len(chunks),
                "total_duration": len(combined) / 1000.0,
                "combined_size": len(combined_data),
                "crossfade_ms": crossfade_ms,
                "format": format
            }
            
            logger.debug(f"Audio combination completed: {combine_info}")
            return combined_data, combine_info
            
        except Exception as e:
            logger.error(f"Audio combination failed: {e}")
            raise ValueError(f"Audio combination failed: {str(e)}")
    
    def get_audio_info(self, audio_data: bytes, format_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed audio information
        
        Args:
            audio_data: Audio bytes
            format_hint: Format hint
            
        Returns:
            Audio information dictionary
        """
        try:
            validation = self.validate_audio(audio_data, format_hint)
            if not validation["valid"]:
                return validation
            
            # Load audio for detailed analysis
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data), 
                format=validation.get("format", format_hint)
            )
            
            # Calculate additional metrics
            rms = audio.rms
            max_amplitude = audio.max
            
            # Estimate speech content (very basic)
            # Real speech detection would need more sophisticated analysis
            silence_ratio = self._calculate_silence_ratio(audio)
            
            info = {
                **validation,
                "rms_level": rms,
                "max_amplitude": max_amplitude,
                "silence_ratio": silence_ratio,
                "estimated_speech_content": 1.0 - silence_ratio,
                "dynamic_range": max_amplitude - rms if max_amplitude > rms else 0,
                "is_likely_speech": silence_ratio < 0.7 and rms > 100  # Basic heuristic
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return {"valid": False, "error": str(e)}
    
    def _estimate_bitrate(self, file_size: int, duration: float) -> int:
        """Estimate bitrate from file size and duration"""
        if duration <= 0:
            return 0
        # bitrate = (file_size * 8) / duration / 1000  # kbps
        return int((file_size * 8) / duration / 1000)
    
    def _calculate_silence_ratio(self, audio: AudioSegment, silence_thresh: int = -40) -> float:
        """Calculate ratio of silence in audio"""
        try:
            # Split audio into 100ms chunks and check for silence
            chunk_length = 100  # ms
            total_chunks = 0
            silent_chunks = 0
            
            for i in range(0, len(audio), chunk_length):
                chunk = audio[i:i + chunk_length]
                if len(chunk) > 0:
                    total_chunks += 1
                    if chunk.dBFS < silence_thresh:
                        silent_chunks += 1
            
            return silent_chunks / total_chunks if total_chunks > 0 else 0
            
        except Exception:
            return 0.5  # Default assumption
    
    def encode_to_base64(self, audio_data: bytes) -> str:
        """Encode audio data to base64 string"""
        return base64.b64encode(audio_data).decode('utf-8')
    
    def decode_from_base64(self, base64_string: str) -> bytes:
        """Decode audio data from base64 string"""
        return base64.b64decode(base64_string)
    
    def is_format_supported(self, format: str, for_output: bool = False) -> bool:
        """Check if audio format is supported"""
        formats = self.supported_output_formats if for_output else self.supported_input_formats
        return format.lower() in formats
    
    def get_supported_formats(self, for_output: bool = False) -> List[str]:
        """Get list of supported formats"""
        return (self.supported_output_formats if for_output else self.supported_input_formats).copy()
    
    def analyze_audio_quality(self, audio_data: bytes, format_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze audio quality metrics
        
        Args:
            audio_data: Audio bytes
            format_hint: Format hint
            
        Returns:
            Quality analysis dictionary
        """
        try:
            validation = self.validate_audio(audio_data, format_hint)
            if not validation["valid"]:
                return validation
            
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data), 
                format=validation.get("format", format_hint)
            )
            
            # Calculate quality metrics
            rms = audio.rms
            max_amplitude = audio.max
            silence_ratio = self._calculate_silence_ratio(audio)
            
            # Estimate SNR (Signal-to-Noise Ratio) - simplified
            signal_power = rms ** 2 if rms > 0 else 1
            noise_floor = max_amplitude * 0.01  # Assume 1% of max is noise
            snr_estimate = 10 * (signal_power / (noise_floor ** 2) if noise_floor > 0 else 100)
            
            quality_score = min(100, max(0, (snr_estimate / 10) * (1 - silence_ratio) * 100))
            
            # Calculate clarity score based on dynamic range and SNR
            clarity_score = min(100, max(0, (max_amplitude - rms) / 1000 * 100 if max_amplitude > rms else 0))
            
            # Generate recommendations based on analysis
            recommendations = []
            if quality_score < 50:
                recommendations.append("Consider using a better microphone")
            if silence_ratio > 0.8:
                recommendations.append("Audio appears to be mostly silent")
            if rms < 100:
                recommendations.append("Audio level is very low, consider increasing volume")
            if clarity_score < 30:
                recommendations.append("Audio clarity could be improved")
            if not recommendations:
                recommendations.append("Audio quality is acceptable for speech processing")
            
            return {
                "valid": True,
                "rms_level": rms,
                "max_amplitude": max_amplitude,
                "dynamic_range": max_amplitude - rms if max_amplitude > rms else 0,
                "silence_ratio": silence_ratio,
                "estimated_snr": snr_estimate,
                "noise_level": noise_floor,
                "clarity": clarity_score,
                "quality_score": quality_score,
                "recommendations": recommendations,
                "is_high_quality": quality_score > 70,
                "is_speech_like": silence_ratio < 0.7 and rms > 100,
                "recommended_for_stt": quality_score > 50 and silence_ratio < 0.8
            }
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}")
            return {"valid": False, "error": str(e)}
    
    def extract_metadata(self, audio_data: bytes, format_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract comprehensive audio metadata
        
        Args:
            audio_data: Audio bytes
            format_hint: Format hint
            
        Returns:
            Metadata dictionary
        """
        try:
            validation = self.validate_audio(audio_data, format_hint)
            if not validation["valid"]:
                return validation
            
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data), 
                format=validation.get("format", format_hint)
            )
            
            # Extract comprehensive metadata
            metadata = {
                "valid": True,
                "format": validation.get("format", format_hint),
                "file_size": len(audio_data),
                "duration": len(audio) / 1000.0,
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "bit_rate": self._estimate_bitrate(len(audio_data), len(audio) / 1000.0),
                "encoding": "PCM" if format_hint == "wav" else "Compressed",
                "channel_layout": "mono" if audio.channels == 1 else "stereo" if audio.channels == 2 else f"{audio.channels}ch",
                "bit_depth": audio.sample_width * 8,
                "is_lossless": format_hint in ["wav", "flac"],
                "estimated_compression_ratio": 1.0 if format_hint == "wav" else 0.1,  # Rough estimate
                "created_at": None,  # Would need file system metadata
                "artist": None,      # Would need ID3 tags
                "title": None,       # Would need ID3 tags
                "album": None,       # Would need ID3 tags
                "codec": format_hint.upper() if format_hint else "UNKNOWN"
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {"valid": False, "error": str(e)}


# Global audio processor instance
audio_processor = AudioProcessor()