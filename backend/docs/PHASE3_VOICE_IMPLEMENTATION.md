# Phase 3: Voice Chatbot Service - Implementation Guide

## 🎙️ Overview

Phase 3 introduces comprehensive voice chat functionality with real-time WebSocket support, enabling users to have natural voice conversations with AI chatbots. The implementation includes speech-to-text (STT), text-to-speech (TTS), and seamless integration with the existing RAG and agent systems.

## 🏗️ Architecture

### Components

1. **WebSocket Manager** (`app/core/websocket_manager.py`)
   - Real-time connection management
   - Audio streaming and buffering
   - Session lifecycle management

2. **Voice Service** (`app/services/voice_service.py`)
   - Orchestrates STT → LLM → TTS pipeline
   - Handles voice configuration
   - Manages processing sessions

3. **STT Service** (`app/services/stt_service.py`)
   - Groq Whisper V3 integration
   - Audio preprocessing and optimization
   - Multi-language support

4. **TTS Service** (`app/services/tts_service.py`)
   - Deepgram text-to-speech integration
   - Multiple voice models
   - Streaming synthesis support

5. **Audio Utilities** (`app/utils/audio_utils.py`)
   - Format conversion and validation
   - Audio processing and optimization
   - Quality analysis

## 🔧 Features

### Real-Time Voice Chat
- **WebSocket-based communication** for low latency
- **Audio streaming** with chunked processing
- **Bidirectional communication** (voice input → audio output)
- **Session management** with automatic cleanup

### Speech Processing
- **High-quality STT** with Groq Whisper V3
- **Natural TTS** with Deepgram's Aura voices
- **Audio optimization** for speech recognition
- **Format support** for WebM, MP3, WAV, and more

### Integration
- **RAG-enabled responses** using existing knowledge base
- **Agent tool calling** with voice context
- **Conversation continuity** across voice and text
- **Multi-modal interaction** (voice + text in same session)

### Configuration
- **Voice customization** (speed, pitch, voice model)
- **Per-chatbot settings** with user preferences
- **Audio format preferences** and quality settings
- **Language detection** and selection

## 📡 API Endpoints

### WebSocket Endpoints

#### Voice Chat WebSocket
```
WS /api/v1/ws/voice/{chatbot_id}?token={auth_token}
```

**Connection Protocol:**
1. Connect with authentication token
2. Send control messages as JSON text
3. Send audio data as binary messages
4. Receive status updates and audio responses

**Message Types:**
- `ping/pong` - Connection keepalive
- `audio_start` - Begin audio recording
- `audio_stop` - End recording and process
- `text_message` - Send text during voice session

### REST API Endpoints

#### Voice Chat Processing
```http
POST /api/v1/voice/chat
Content-Type: multipart/form-data

chatbot_id: string
audio_file: file
conversation_id?: string
voice_config?: json
use_rag?: boolean
```

#### Text-to-Speech
```http
POST /api/v1/voice/tts
Content-Type: application/json

{
  "text": "Hello world",
  "voice": "aura-asteria-en",
  "speed": 1.0,
  "pitch": 0.0,
  "encoding": "mp3",
  "sample_rate": 24000
}
```

#### Speech-to-Text
```http
POST /api/v1/voice/stt
Content-Type: multipart/form-data

audio_file: file
language?: string
prompt?: string
temperature?: number
```

#### Available Voices
```http
GET /api/v1/voice/voices
```

#### Voice Configuration
```http
GET /api/v1/voice/config/{chatbot_id}
PUT /api/v1/voice/config/{chatbot_id}

{
  "tts_voice": "aura-asteria-en",
  "tts_speed": 1.0,
  "tts_pitch": 0.0,
  "stt_language": "en",
  "audio_format": "webm"
}
```

## 🚀 Usage Examples

### JavaScript WebSocket Client

```javascript
class VoiceChatClient {
    constructor(chatbotId, authToken) {
        this.chatbotId = chatbotId;
        this.authToken = authToken;
        this.ws = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
    }
    
    connect() {
        const wsUrl = `ws://localhost:8000/api/v1/ws/voice/${this.chatbotId}?token=${this.authToken}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('Voice chat connected');
            this.sendMessage({type: 'ping'});
        };
        
        this.ws.onmessage = (event) => {
            if (event.data instanceof Blob) {
                // Received audio response
                this.playAudio(event.data);
            } else {
                // Received status message
                const message = JSON.parse(event.data);
                this.handleStatusMessage(message);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                this.mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                
                this.mediaRecorder.ondataavailable = (event) => {
                    this.audioChunks.push(event.data);
                };
                
                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, {
                        type: 'audio/webm'
                    });
                    this.sendAudio(audioBlob);
                    this.audioChunks = [];
                };
                
                this.sendMessage({type: 'audio_start'});
                this.mediaRecorder.start(100); // 100ms chunks
            })
            .catch(err => console.error('Media access error:', err));
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.sendMessage({type: 'audio_stop'});
        }
    }
    
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
    
    sendAudio(audioBlob) {
        audioBlob.arrayBuffer().then(buffer => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(buffer);
            }
        });
    }
    
    handleStatusMessage(message) {
        switch (message.type) {
            case 'pong':
                console.log('Connection alive');
                break;
            case 'transcription_complete':
                console.log('Transcribed:', message.text);
                this.displayTranscription(message.text);
                break;
            case 'response_generated':
                console.log('AI Response:', message.text);
                this.displayResponse(message.text);
                break;
            case 'voice_processing_complete':
                console.log('Processing complete');
                break;
            case 'voice_processing_error':
                console.error('Processing error:', message.error);
                break;
        }
    }
    
    playAudio(audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play().catch(e => console.error('Audio play error:', e));
    }
    
    sendTextMessage(text) {
        this.sendMessage({
            type: 'text_message',
            content: text
        });
    }
}

// Usage
const voiceChat = new VoiceChatClient('chatbot-123', 'your-auth-token');
voiceChat.connect();

// Start recording when user presses button
document.getElementById('recordBtn').addEventListener('mousedown', () => {
    voiceChat.startRecording();
});

document.getElementById('recordBtn').addEventListener('mouseup', () => {
    voiceChat.stopRecording();
});
```

### Python REST API Client

```python
import requests
import json
from pathlib import Path

class VoiceChatAPI:
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {auth_token}'}
    
    def voice_chat(self, chatbot_id: str, audio_file_path: str, 
                   conversation_id: str = None, voice_config: dict = None):
        """Process voice message through full pipeline"""
        url = f"{self.base_url}/api/v1/voice/chat"
        
        files = {'audio_file': open(audio_file_path, 'rb')}
        data = {'chatbot_id': chatbot_id}
        
        if conversation_id:
            data['conversation_id'] = conversation_id
        if voice_config:
            data['voice_config'] = json.dumps(voice_config)
        
        response = requests.post(url, files=files, data=data, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            # Save audio response
            if hasattr(result, 'audio_data'):
                with open('response_audio.mp3', 'wb') as f:
                    f.write(result.audio_data)
            return result
        else:
            raise Exception(f"Voice chat failed: {response.text}")
    
    def text_to_speech(self, text: str, voice: str = "aura-asteria-en", 
                       output_file: str = "tts_output.mp3"):
        """Convert text to speech"""
        url = f"{self.base_url}/api/v1/voice/tts"
        
        payload = {
            "text": text,
            "voice": voice,
            "encoding": "mp3",
            "sample_rate": 24000
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return output_file
        else:
            raise Exception(f"TTS failed: {response.text}")
    
    def speech_to_text(self, audio_file_path: str, language: str = None):
        """Convert speech to text"""
        url = f"{self.base_url}/api/v1/voice/stt"
        
        files = {'audio_file': open(audio_file_path, 'rb')}
        data = {}
        
        if language:
            data['language'] = language
        
        response = requests.post(url, files=files, data=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"STT failed: {response.text}")
    
    def get_available_voices(self):
        """Get list of available TTS voices"""
        url = f"{self.base_url}/api/v1/voice/voices"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get voices: {response.text}")
    
    def get_voice_config(self, chatbot_id: str):
        """Get voice configuration for chatbot"""
        url = f"{self.base_url}/api/v1/voice/config/{chatbot_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get config: {response.text}")
    
    def update_voice_config(self, chatbot_id: str, config: dict):
        """Update voice configuration"""
        url = f"{self.base_url}/api/v1/voice/config/{chatbot_id}"
        response = requests.put(url, json=config, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update config: {response.text}")

# Usage example
api = VoiceChatAPI("http://localhost:8000", "your-auth-token")

# Text to speech
audio_file = api.text_to_speech("Hello, how are you today?", voice="aura-asteria-en")
print(f"Audio saved to: {audio_file}")

# Speech to text
result = api.speech_to_text("user_audio.wav")
print(f"Transcription: {result['text']}")
print(f"Confidence: {result['confidence']}")

# Full voice chat
response = api.voice_chat(
    chatbot_id="chatbot-123",
    audio_file_path="question.wav",
    voice_config={
        "tts_voice": "aura-luna-en",
        "tts_speed": 1.2,
        "use_rag": True
    }
)
print(f"AI Response: {response['response_text']}")
```

## 🔧 Configuration

### Environment Variables
```bash
# Add to .env file
GROQ_API_KEY=your_groq_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### Voice Configuration Options

```json
{
  "tts_voice": "aura-asteria-en",    // Voice model ID
  "tts_speed": 1.0,                  // Speed: 0.5-2.0
  "tts_pitch": 0.0,                  // Pitch: -2.0 to 2.0
  "stt_language": "en",              // Language code or null (auto)
  "audio_format": "webm"             // Preferred audio format
}
```

### Available TTS Voices

| Voice ID | Language | Gender | Style |
|----------|----------|---------|-------|
| aura-asteria-en | English | Female | Conversational |
| aura-luna-en | English | Female | Young |
| aura-stella-en | English | Female | Professional |
| aura-athena-en | English | Female | Authoritative |
| aura-hera-en | English | Female | Warm |
| aura-orion-en | English | Male | Conversational |
| aura-arcas-en | English | Male | Young |
| aura-perseus-en | English | Male | Professional |
| aura-angus-en | English | Male | Authoritative |
| aura-orpheus-en | English | Male | Warm |

## 🗄️ Database Schema

### New Tables

1. **voice_sessions** - Active WebSocket sessions
2. **voice_configs** - User/chatbot voice preferences
3. **voice_usage** - Usage tracking and analytics
4. **voice_errors** - Error logging and monitoring

### Schema Updates
```sql
-- Run the voice schema update
psql -d your_database -f scripts/database/voice_schema.sql
```

## 🧪 Testing

### Run Voice Functionality Tests
```bash
# Run Phase 3 voice tests
python tests/integration/test_phase3_voice.py

# Run specific test categories
pytest tests/integration/test_phase3_voice.py::TestPhase3VoiceImplementation::test_voice_service_full_pipeline
```

### Test Audio Files
Create test audio files for development:
```python
from pydub import AudioSegment
from pydub.generators import Sine

# Generate test audio
tone = Sine(440).to_audio_segment(duration=2000)  # 2 second A note
tone.export("test_audio.wav", format="wav")
```

## 📊 Monitoring & Analytics

### Health Checks
```http
GET /api/v1/voice/health
GET /api/v1/ws/voice/health
```

### Session Statistics
```http
GET /api/v1/ws/voice/sessions/stats
```

### Performance Metrics
- **Processing Times**: STT, LLM, TTS pipeline stages
- **Audio Quality**: Transcription confidence, duration
- **Session Analytics**: Active sessions, usage patterns
- **Error Tracking**: Component failures, recovery

## 🚨 Error Handling

### Common Issues

1. **Audio Format Not Supported**
   - Ensure audio format is in supported list
   - Use audio conversion utilities

2. **WebSocket Connection Failed**
   - Verify authentication token
   - Check network connectivity

3. **STT/TTS Service Errors**
   - Verify API keys are configured
   - Check service health endpoints

4. **Audio Quality Issues**
   - Use audio optimization for speech
   - Ensure adequate recording quality

### Error Responses
```json
{
  "type": "voice_processing_error",
  "error": "STT service error: Invalid audio format",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔐 Security Considerations

1. **Authentication**: All endpoints require valid JWT tokens
2. **Rate Limiting**: Prevent audio processing abuse
3. **File Validation**: Strict audio file validation
4. **Session Management**: Automatic cleanup of expired sessions
5. **Error Logging**: Detailed error tracking without exposing sensitive data

## 🚀 Deployment

### Dependencies
```bash
# Install audio processing dependencies
sudo apt-get install ffmpeg
pip install -r requirements.txt
```

### Docker Considerations
```dockerfile
# Add to Dockerfile
RUN apt-get update && apt-get install -y ffmpeg
```

### Production Settings
- Configure proper WebSocket limits
- Set up audio file cleanup jobs
- Monitor processing queue sizes
- Scale WebSocket connections

## 🔄 Integration with Existing Features

### RAG Integration
Voice messages automatically use existing RAG pipeline:
- Document search with voice context
- Knowledge base integration
- Context-aware responses

### Agent Integration
Voice commands trigger existing agents:
- Tool calling from voice input
- Multi-modal agent responses
- Conversation continuity

### Analytics Integration
Voice usage feeds into existing analytics:
- User engagement metrics
- Chatbot performance tracking
- Usage-based billing

## 📈 Future Enhancements

1. **Real-time Streaming STT** - Process audio as it's spoken
2. **Voice Cloning** - Custom voice training
3. **Emotional Recognition** - Detect sentiment in voice
4. **Multi-language Support** - Automatic language switching
5. **Background Noise Reduction** - Advanced audio filtering
6. **Voice Commands** - Direct bot control via voice

## 🎯 Performance Optimization

### Audio Processing
- Use optimized audio formats (16kHz mono for STT)
- Implement audio chunking for large files
- Cache frequently used TTS responses

### WebSocket Management
- Connection pooling and load balancing
- Automatic session cleanup
- Memory-efficient audio buffering

### API Optimization
- Async processing pipelines
- Parallel STT/TTS processing where possible
- Efficient audio format conversions

---

## 🎉 Phase 3 Complete!

The voice chatbot service is now fully implemented with:

✅ **Real-time WebSocket voice chat**  
✅ **High-quality STT with Groq Whisper V3**  
✅ **Natural TTS with Deepgram Aura voices**  
✅ **Complete REST API for voice processing**  
✅ **Comprehensive audio utilities**  
✅ **Voice configuration management**  
✅ **Integration with existing RAG and agents**  
✅ **Full test coverage**  
✅ **Production-ready implementation**  

The system now supports both text and voice interactions, providing a complete conversational AI platform with cutting-edge voice capabilities.