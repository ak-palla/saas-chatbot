# Chatbot SaaS API Documentation

Complete API reference for the Chatbot SaaS backend with text and voice capabilities.

## 🔗 Base URL
```
http://localhost:8000
```

## 📖 Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

Most endpoints require authentication via Supabase JWT tokens.

### Headers
```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

## 📊 Core Endpoints

### Health Check
```http
GET /health
```
Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🤖 Chatbot Management

### Create Chatbot
```http
POST /api/v1/chatbots
```

**Request Body:**
```json
{
  "name": "Customer Support Bot",
  "description": "Handles customer inquiries",
  "prompt": "You are a helpful customer support assistant...",
  "model": "llama3-70b-8192",
  "temperature": 0.7,
  "max_tokens": 2000,
  "use_rag": true
}
```

### Get Chatbots
```http
GET /api/v1/chatbots
```

### Update Chatbot
```http
PUT /api/v1/chatbots/{chatbot_id}
```

### Delete Chatbot
```http
DELETE /api/v1/chatbots/{chatbot_id}
```

## 💬 Text Chat

### Send Message
```http
POST /api/v1/chat
```

**Request Body:**
```json
{
  "message": "Hello, how can you help me?",
  "chatbot_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": "optional-conversation-id",
  "user_id": "user-123",
  "use_rag": true,
  "stream": false
}
```

**Response:**
```json
{
  "response": "Hello! I'm here to help you with any questions you have...",
  "conversation_id": "conv-456",
  "sources": ["doc1.pdf", "doc2.pdf"],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 75,
    "total_tokens": 225
  }
}
```

### Streaming Chat
```http
POST /api/v1/chat
```
With `"stream": true` in request body for Server-Sent Events.

## 🎙️ Voice Chat

### Complete Voice Chat
```http
POST /api/v1/voice/chat
```

**Request:**
- **Content-Type**: `multipart/form-data`
- **audio_file**: Audio file (WAV, MP3, WebM, OGG)
- **chatbot_id**: UUID string
- **user_id**: User identifier
- **conversation_id**: Optional conversation ID
- **voice_config**: Optional JSON configuration

**Voice Config Example:**
```json
{
  "tts_voice": "aura-asteria-en",
  "tts_speed": 1.0,
  "tts_pitch": 0.0,
  "stt_language": "en",
  "audio_format": "mp3"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "voice-session-123",
  "transcription": {
    "text": "Hello, how are you today?",
    "language": "en",
    "duration": 2.5,
    "confidence": 0.95
  },
  "response_text": "I'm doing well, thank you for asking!",
  "conversation_id": "conv-789",
  "audio_duration": 3.2,
  "audio_size": 48000,
  "processing_times": {
    "stt": 0.8,
    "llm": 1.2,
    "tts": 1.5
  }
}
```

### Speech-to-Text Only
```http
POST /api/v1/voice/transcribe
```

**Request:**
- **Content-Type**: `multipart/form-data`
- **audio_file**: Audio file
- **language**: Optional language code

**Response:**
```json
{
  "text": "Hello, how are you today?",
  "language": "en",
  "duration": 2.5,
  "confidence": 0.95,
  "segments": [],
  "model": "whisper-v3",
  "processing_time": 0.8
}
```

### Text-to-Speech Only
```http
POST /api/v1/voice/synthesize
```

**Request Body:**
```json
{
  "text": "Hello, this is a test message",
  "voice": "aura-asteria-en",
  "speed": 1.0,
  "pitch": 0.0,
  "encoding": "mp3",
  "sample_rate": 24000
}
```

**Response:**
- **Content-Type**: `audio/mpeg` (or appropriate format)
- **Binary audio data**

### Voice Service Health
```http
GET /api/v1/voice/health
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "stt_service": {"status": "healthy", "latency": 0.8},
    "tts_service": {"status": "healthy", "latency": 1.2},
    "audio_processor": {"status": "healthy"}
  },
  "active_sessions": 5,
  "default_config": {
    "tts_voice": "aura-asteria-en",
    "tts_speed": 1.0,
    "tts_pitch": 0.0
  }
}
```

## 🔄 WebSocket Communication

### Voice WebSocket
```
WS /api/v1/voice/ws/{session_id}
```

**Connection Parameters:**
- `session_id`: Unique session identifier
- `chatbot_id`: Chatbot UUID (query parameter)
- `user_id`: User identifier (query parameter)

**Message Types:**

#### Client → Server
```json
{
  "type": "audio_chunk",
  "data": {
    "audio_data": "base64_encoded_audio",
    "is_final": false
  }
}
```

#### Server → Client
```json
{
  "type": "transcription_complete",
  "data": {
    "text": "Hello world",
    "confidence": 0.95
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**WebSocket Message Types:**
- `ping` / `pong` - Connection keep-alive
- `audio_start` / `audio_stop` - Audio session control
- `audio_chunk` - Audio data transmission
- `transcription_complete` - STT results
- `response_generated` - LLM response
- `audio_ready` - TTS audio available
- `processing_update` - Status updates
- `error` - Error notifications

## 📄 Document Management

### Upload Document
```http
POST /api/v1/documents/upload
```

**Request:**
- **Content-Type**: `multipart/form-data`
- **file**: Document file (PDF, TXT, DOCX)
- **chatbot_id**: Target chatbot UUID

### List Documents
```http
GET /api/v1/documents?chatbot_id={chatbot_id}
```

### Delete Document
```http
DELETE /api/v1/documents/{document_id}
```

## 📈 Usage Analytics

### Get Usage Stats
```http
GET /api/v1/usage/stats?chatbot_id={chatbot_id}&period=7d
```

**Response:**
```json
{
  "period": "7d",
  "total_messages": 1250,
  "total_voice_sessions": 85,
  "total_audio_minutes": 42.5,
  "daily_breakdown": [
    {
      "date": "2024-01-01",
      "messages": 180,
      "voice_sessions": 12,
      "audio_minutes": 6.2
    }
  ],
  "top_users": [
    {"user_id": "user-123", "message_count": 45}
  ]
}
```

## 🎛️ Configuration

### Available Voices
```http
GET /api/v1/voice/voices
```

**Response:**
```json
{
  "voices": [
    {
      "id": "aura-asteria-en",
      "language": "en",
      "gender": "female",
      "style": "conversational",
      "description": "Warm, friendly female voice"
    }
  ]
}
```

### Supported Audio Formats
- **Input**: WAV, MP3, WebM, OGG, M4A, MP4, WMA, FLAC, AAC
- **Output**: MP3, WAV, OGG, WebM, FLAC

## ❌ Error Responses

### Standard Error Format
```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid audio format",
    "details": {
      "field": "audio_file",
      "supported_formats": ["wav", "mp3", "webm"]
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `413` - Payload Too Large (file size limit)
- `422` - Unprocessable Entity (business logic error)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## 🔒 Rate Limits

### Default Limits
- **Text Chat**: 100 requests/minute per user
- **Voice Chat**: 20 requests/minute per user
- **File Upload**: 10 uploads/minute per user
- **WebSocket**: 5 concurrent connections per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

## 📝 Request/Response Examples

### Complete Voice Chat Example

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/voice/chat" \
  -H "Authorization: Bearer <token>" \
  -F "audio_file=@recording.wav" \
  -F "chatbot_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "user_id=user-123" \
  -F 'voice_config={"tts_voice":"aura-asteria-en","tts_speed":1.1}'
```

**Response:**
```json
{
  "success": true,
  "session_id": "vs_abc123",
  "transcription": {
    "text": "What's the weather like today?",
    "language": "en",
    "duration": 2.1,
    "confidence": 0.98
  },
  "response_text": "I'd be happy to help with weather information, but I don't have access to real-time weather data. You might want to check a weather app or website for current conditions.",
  "conversation_id": "conv_xyz789",
  "audio_duration": 4.2,
  "audio_size": 67200,
  "processing_times": {
    "stt": 0.7,
    "llm": 1.1,
    "tts": 1.8
  }
}
```

## 🚀 SDKs and Integration

### JavaScript/TypeScript
```javascript
// Voice chat example
const formData = new FormData();
formData.append('audio_file', audioBlob);
formData.append('chatbot_id', 'your-chatbot-id');
formData.append('user_id', 'user-123');

const response = await fetch('/api/v1/voice/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
```

### Python
```python
import requests

# Text chat example
response = requests.post(
    'http://localhost:8000/api/v1/chat',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'message': 'Hello!',
        'chatbot_id': 'your-chatbot-id',
        'user_id': 'user-123'
    }
)

result = response.json()
```

This API provides complete text and voice chat capabilities for building sophisticated chatbot applications. For more details and testing, visit the interactive documentation at http://localhost:8000/docs when your server is running.