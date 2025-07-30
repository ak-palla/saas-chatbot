#!/usr/bin/env python3
"""
Configure pydub to use the correct FFmpeg path
This fixes the "Couldn't find ffmpeg or avconv" warning
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def configure_pydub_ffmpeg():
    """Configure pydub to use the correct FFmpeg executable"""
    print("🔧 Configuring pydub to use FFmpeg...")
    
    # Set the FFmpeg path for pydub
    ffmpeg_path = r"C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin\ffmpeg.exe"
    ffprobe_path = r"C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin\ffprobe.exe"
    
    # Check if files exist
    if not os.path.exists(ffmpeg_path):
        print(f"❌ FFmpeg not found at: {ffmpeg_path}")
        return False
        
    if not os.path.exists(ffprobe_path):
        print(f"❌ FFprobe not found at: {ffprobe_path}")
        return False
    
    print(f"✅ Found FFmpeg at: {ffmpeg_path}")
    print(f"✅ Found FFprobe at: {ffprobe_path}")
    
    # Import pydub and configure it
    try:
        from pydub import AudioSegment
        from pydub.utils import which
        
        # Set the converter and ffprobe paths
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffmpeg = ffmpeg_path  
        AudioSegment.ffprobe = ffprobe_path
        
        print("🔧 Configured pydub paths:")
        print(f"   converter: {AudioSegment.converter}")
        print(f"   ffmpeg: {AudioSegment.ffmpeg}")
        print(f"   ffprobe: {AudioSegment.ffprobe}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import pydub: {e}")
        return False

def test_pydub_with_configured_paths():
    """Test pydub with the configured FFmpeg paths"""
    print("\n🧪 Testing pydub with configured FFmpeg...")
    
    try:
        from pydub import AudioSegment
        import tempfile
        import os
        
        # Create a simple audio segment
        print("  📀 Creating test audio...")
        audio = AudioSegment.silent(duration=500)  # 0.5 seconds of silence
        
        # Test export to MP3 with configured path
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            print("  🎵 Exporting to MP3...")
            audio.export(temp_path, format="mp3")
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                file_size = os.path.getsize(temp_path)
                print(f"  ✅ MP3 export successful: {file_size} bytes")
                os.unlink(temp_path)  # Clean up
                return True
            else:
                print("  ❌ MP3 file was not created or is empty")
                return False
                
        except Exception as e:
            print(f"  ❌ MP3 export failed: {e}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)  # Clean up
            return False
            
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def main():
    """Main function"""
    print("🎙️ Pydub FFmpeg Configuration Tool")
    print("=" * 50)
    
    # Configure pydub
    if not configure_pydub_ffmpeg():
        print("❌ Failed to configure pydub with FFmpeg")
        return 1
    
    # Test the configuration
    if test_pydub_with_configured_paths():
        print("\n🎉 SUCCESS! Pydub is now working with FFmpeg!")
        print("\n📝 To make this permanent, add this to your app startup:")
        print("   from pydub import AudioSegment")
        print("   AudioSegment.converter = r'C:\\Users\\NJ-25\\scoop\\apps\\ffmpeg\\7.1.1\\bin\\ffmpeg.exe'")
        print("   AudioSegment.ffprobe = r'C:\\Users\\NJ-25\\scoop\\apps\\ffmpeg\\7.1.1\\bin\\ffprobe.exe'")
        return 0
    else:
        print("\n❌ Configuration test failed")
        return 1

if __name__ == "__main__":
    exit(main())