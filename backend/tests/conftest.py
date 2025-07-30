"""
Test configuration and fixtures for all phases including Phase 3 voice tests
Handles environment setup and missing dependencies gracefully
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import warnings

# Add the parent directory to the Python path so tests can import app modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Change working directory to backend for relative imports
os.chdir(backend_dir)

# Suppress pydub warnings about missing ffmpeg during tests
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment and handle missing dependencies"""
    print("\n🔧 Setting up test environment...")
    
    # Check for FFmpeg availability
    ffmpeg_available = check_ffmpeg_availability()
    if not ffmpeg_available:
        print("⚠️  FFmpeg not available - audio conversion tests will be mocked")
    
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"  # Reduce log noise during tests
    
    yield
    
    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)


def check_ffmpeg_availability():
    """Check if FFmpeg is available on the system"""
    try:
        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture
def mock_audio_processor():
    """Mock audio processor for tests when FFmpeg is unavailable"""
    with patch('app.utils.audio_utils.audio_processor') as mock:
        # Mock audio processing methods
        mock.validate_audio.return_value = True
        mock.get_audio_info.return_value = {
            "duration": 5.0,
            "format": "webm",
            "sample_rate": 16000,
            "channels": 1,
            "size": 80000
        }
        mock.convert_format.return_value = (b"mock_audio_data", {
            "input_format": "webm",
            "output_format": "wav", 
            "input_size": 80000,
            "output_size": 80000,
            "compression_ratio": 1.0,
            "duration": 5.0,
            "sample_rate": 16000,
            "channels": 1
        })
        mock.optimize_for_speech.return_value = (b"optimized_audio", {
            "optimizations_applied": ["noise_reduction", "normalization"],
            "quality_score": 0.85
        })
        yield mock


@pytest.fixture
def sample_audio_data():
    """Generate sample audio data for testing"""
    # Create a simple WAV header + data
    # This is a minimal valid WAV file (1 second of silence)
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x08, 0x00, 0x00,  # File size
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Subchunk1Size
        0x01, 0x00,              # AudioFormat (PCM)
        0x01, 0x00,              # NumChannels (mono)
        0x44, 0xAC, 0x00, 0x00,  # SampleRate (44100)
        0x88, 0x58, 0x01, 0x00,  # ByteRate
        0x02, 0x00,              # BlockAlign
        0x10, 0x00,              # BitsPerSample
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x08, 0x00, 0x00,  # Subchunk2Size
    ])
    # Add 1 second of silence (44100 samples * 2 bytes)
    silence_data = bytes([0x00] * 2048)  # Shorter for testing
    return wav_header + silence_data


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "requires_ffmpeg: mark test as requiring FFmpeg to be installed"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle missing dependencies"""
    ffmpeg_available = check_ffmpeg_availability()
    
    for item in items:
        # Skip FFmpeg-dependent tests if FFmpeg is not available
        if "requires_ffmpeg" in item.keywords and not ffmpeg_available:
            item.add_marker(pytest.mark.skip(reason="FFmpeg not available"))