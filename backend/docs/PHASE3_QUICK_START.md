# Phase 3 Voice Implementation - Quick Start Guide

## 🚀 Getting Started with Voice Chat

This guide will help you quickly set up and test the Phase 3 voice functionality.

## 📋 Prerequisites

1. **API Keys Required:**
   - Groq API key (for Whisper V3 STT)
   - Deepgram API key (for TTS)
   - Supabase credentials

2. **System Requirements:**
   - Python 3.8+
   - FFmpeg (for audio processing)
   - PostgreSQL database

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Install FFmpeg (macOS)
brew install ffmpeg

# Install FFmpeg (Windows)
# Download from https://ffmpeg.org/download.html
```

### 2. Configure Environment Variables
Create/update your `.env` file:
```bash
# Phase 3 Voice API Keys
GROQ_API_KEY=your_groq_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Existing configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SECRET_KEY=your_secret_key
```

### 3. Setup Database Schema
```bash
# Run the voice schema migration
psql -d your_database_name -f scripts/database/voice_schema.sql

# Or connect and run manually
psql -d your_database_name
\i scripts/database/voice_schema.sql
```

### 4. Validate Installation
```bash
# Run the Phase 3 validator
python scripts/utilities/validate_phase3.py

# Run specific tests
python tests/integration/test_phase3_voice.py
python tests/integration/test_phase3_comprehensive_edge_cases.py
```

## 🏃‍♂️ Quick Test Run

### 1. Start the Server
```bash
# Start FastAPI server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at http://localhost:8000
```

### 2. Test Basic Endpoints

#### Check Voice Service Health
```bash
curl http://localhost:8000/api/v1/voice/health
```

#### Get Available Voices
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/voice/voices
```

#### Test Text-to-Speech
```bash
curl -X POST http://localhost:8000/api/v1/voice/tts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the voice system!",
    "voice": "aura-asteria-en",
    "encoding": "mp3"
  }' \
  --output test_tts.mp3
```

#### Test Speech-to-Text
```bash
curl -X POST http://localhost:8000/api/v1/voice/stt \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "audio_file=@your_audio_file.wav"
```

### 3. Test WebSocket Connection

#### JavaScript WebSocket Test
```javascript
// Test WebSocket connection
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/voice/YOUR_CHATBOT_ID?token=YOUR_TOKEN');

ws.onopen = () => {
    console.log('Voice WebSocket connected');
    ws.send(JSON.stringify({type: 'ping'}));
};

ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        console.log('Received audio response');
    } else {
        const message = JSON.parse(event.data);
        console.log('Status message:', message);
    }
};
```

#### Python WebSocket Test
```python
import asyncio
import websockets
import json

async def test_voice_websocket():
    uri = "ws://localhost:8000/api/v1/ws/voice/YOUR_CHATBOT_ID?token=YOUR_TOKEN"
    
    async with websockets.connect(uri) as websocket:
        # Send ping
        await websocket.send(json.dumps({"type": "ping"}))
        
        # Receive pong
        response = await websocket.recv()
        print("Received:", json.loads(response))

# Run test
asyncio.run(test_voice_websocket())
```

## 🧪 Testing Voice Chat Flow

### Complete Voice Chat Test (Python)
```python
import requests
import json

# 1. Create a test chatbot (if needed)
chatbot_data = {
    "name": "Voice Test Bot",
    "system_prompt": "You are a helpful voice assistant.",
    "voice_enabled": True
}

# 2. Upload audio file for voice chat
with open('test_audio.wav', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8000/api/v1/voice/chat',
        headers={'Authorization': 'Bearer YOUR_TOKEN'},
        files={'audio_file': audio_file},
        data={
            'chatbot_id': 'YOUR_CHATBOT_ID',
            'voice_config': json.dumps({
                'tts_voice': 'aura-asteria-en',
                'tts_speed': 1.0,
                'use_rag': True
            })
        }
    )

if response.status_code == 200:
    result = response.json()
    print("Transcription:", result['transcription']['text'])
    print("AI Response:", result['response_text'])
    print("Processing times:", result['processing_times'])
    
    # Save response audio
    if 'audio_data' in result:
        with open('ai_response.mp3', 'wb') as f:
            f.write(result['audio_data'])
        print("AI audio saved to ai_response.mp3")
else:
    print("Error:", response.text)
```

## 🎯 Feature Testing Checklist

### ✅ Basic Functionality
- [ ] Server starts without errors
- [ ] Voice endpoints are accessible
- [ ] Health check returns healthy status
- [ ] Available voices can be retrieved
- [ ] TTS converts text to audio
- [ ] STT converts audio to text

### ✅ WebSocket Functionality
- [ ] WebSocket connection establishes successfully
- [ ] Ping/pong messages work
- [ ] Audio streaming works
- [ ] Real-time status updates received
- [ ] Session management works
- [ ] Graceful disconnection

### ✅ Advanced Features
- [ ] Complete voice chat pipeline (STT→LLM→TTS)
- [ ] RAG integration with voice queries
- [ ] Voice configuration management
- [ ] Multi-format audio support
- [ ] Error handling and recovery
- [ ] Performance under load

### ✅ Integration
- [ ] Database operations work
- [ ] Existing chatbot integration
- [ ] Conversation continuity
- [ ] User authentication
- [ ] Analytics and usage tracking

## 🐛 Troubleshooting

### Common Issues

#### 1. Dependencies Not Found
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Install FFmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
```

#### 2. API Key Issues
```bash
# Verify API keys are set
echo $GROQ_API_KEY
echo $DEEPGRAM_API_KEY

# Test API keys
curl -H "Authorization: Bearer $GROQ_API_KEY" \
     https://api.groq.com/openai/v1/models
```

#### 3. Database Connection Issues
```bash
# Test database connection
psql -d your_database_name -c "SELECT 1;"

# Check if voice tables exist
psql -d your_database_name -c "\dt voice*"
```

#### 4. Audio Processing Issues
```bash
# Test FFmpeg installation
ffmpeg -version

# Test audio file conversion
ffmpeg -i input.wav -ar 16000 -ac 1 output.wav
```

#### 5. WebSocket Connection Issues
- Check firewall settings
- Verify authentication token
- Ensure server is running on correct port
- Check CORS configuration

### Debug Mode
```bash
# Start server in debug mode
DEBUG=True uvicorn app.main:app --reload --log-level debug

# Enable verbose logging
export LOG_LEVEL=DEBUG
python scripts/utilities/validate_phase3.py
```

## 📊 Performance Testing

### Load Testing WebSocket Connections
```python
import asyncio
import websockets
import json
import time

async def load_test_websocket(connection_id):
    uri = f"ws://localhost:8000/api/v1/ws/voice/test-chatbot?token=test-token"
    
    try:
        async with websockets.connect(uri) as websocket:
            start_time = time.time()
            
            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Wait for pong
            response = await websocket.recv()
            
            end_time = time.time()
            print(f"Connection {connection_id}: {end_time - start_time:.3f}s")
            
    except Exception as e:
        print(f"Connection {connection_id} failed: {e}")

# Test multiple connections
async def run_load_test():
    tasks = [load_test_websocket(i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(run_load_test())
```

### Audio Processing Performance
```python
import time
from app.utils.audio_utils import audio_processor

# Test audio validation performance
start_time = time.time()
with open('test_audio.wav', 'rb') as f:
    audio_data = f.read()
    result = audio_processor.validate_audio(audio_data, 'wav')
end_time = time.time()

print(f"Audio validation: {end_time - start_time:.3f}s")
print(f"Audio valid: {result['valid']}")
```

## 📈 Monitoring and Analytics

### Voice Usage Analytics
```sql
-- Check voice usage statistics
SELECT 
    DATE(created_at) as date,
    COUNT(*) as voice_messages,
    AVG(audio_duration_input) as avg_input_duration,
    AVG(total_processing_time) as avg_processing_time
FROM voice_usage 
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Check most used voices
SELECT 
    voice_used,
    COUNT(*) as usage_count,
    AVG(transcription_confidence) as avg_confidence
FROM voice_usage 
GROUP BY voice_used
ORDER BY usage_count DESC;
```

### Active Sessions Monitoring
```sql
-- Check active voice sessions
SELECT 
    COUNT(*) as active_sessions,
    COUNT(DISTINCT user_id) as active_users
FROM voice_sessions 
WHERE is_active = true 
AND last_activity_at > NOW() - INTERVAL '5 minutes';
```

## 🎉 Success Criteria

Your Phase 3 implementation is successful when:

1. **✅ All validation tests pass**
2. **✅ Voice chat pipeline works end-to-end**
3. **✅ WebSocket connections are stable**
4. **✅ Audio quality is acceptable**
5. **✅ Performance meets requirements**
6. **✅ Error handling is robust**
7. **✅ Integration with existing features works**

## 🔗 Next Steps

After successful Phase 3 validation:

1. **Phase 4**: Frontend Dashboard Development
2. **Phase 5**: Embeddable Widget Creation
3. **Phase 6**: Payment & Billing Integration
4. **Phase 7**: Production Deployment

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the comprehensive documentation in `PHASE3_VOICE_IMPLEMENTATION.md`
3. Run the validation script: `python scripts/utilities/validate_phase3.py`
4. Check the test results for specific failure points

---

**🎊 Congratulations on implementing Phase 3 voice functionality!** Your chatbot platform now supports both text and voice interactions with real-time WebSocket communication.