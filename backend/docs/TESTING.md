# Comprehensive Testing Guide

## Overview
This guide covers the complete testing suite for the Chatbot SaaS platform, including all implemented phases (1-3) with text and voice capabilities.

**📁 All test files are organized in the `tests/` directory.**

## 🧪 Test Structure

### Development Tools
- **`scripts/dev-tools.py`** - Comprehensive development utility
- **`dev.bat`** - Windows wrapper for dev tools

### Unit Tests (`tests/unit/`)
- **`test_phase1.py`** - Core infrastructure tests
- Basic service validation
- **Run time**: ~10 seconds

### Integration Tests (`tests/integration/`)
- **`test_phase1_complete.py`** - Phase 1 complete validation
- **`test_phase2_complete.py`** - Phase 2 text chat validation  
- **`test_phase3_voice.py`** - Phase 3 voice functionality tests
- **`test_phase3_comprehensive_edge_cases.py`** - Advanced voice scenarios
- **`test_phase3_complete_validation.py`** - Master validation runner
- **Run time**: ~60-120 seconds

### Utility Tests (`tests/utils/`)
- **`quick_test.py`** - Basic connectivity validation
- **Run time**: ~5 seconds

## Prerequisites

1. **Server Running**: Make sure your FastAPI server is running:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Install Requests**: The tests use the `requests` library:
   ```bash
   pip install requests
   ```

3. **Database Setup**: For full testing, your Supabase database should be configured with the schema from `database.sql`

## 🚀 Running Tests

### Method 1: Development Tools (Recommended)
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run all tests
python scripts/dev-tools.py test

# Run specific test types
python scripts/dev-tools.py test unit         # Unit tests only
python scripts/dev-tools.py test integration # Integration tests only
python scripts/dev-tools.py test phase3      # Voice functionality tests
python scripts/dev-tools.py test voice       # Same as phase3

# Windows users can use the wrapper
dev test                    # All tests
dev test phase3            # Voice tests only
```

### Method 2: Pytest Directly
```bash
# All tests
pytest tests/ -v

# Specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/integration/test_phase3_voice.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Parallel execution (faster)
pytest tests/ -n auto
```

### Method 3: Individual Test Files
```bash
# Quick connectivity test
python tests/utils/quick_test.py

# Specific phase validation
python scripts/utilities/validate_phase3.py

# Advanced voice testing
python -m pytest tests/integration/test_phase3_comprehensive_edge_cases.py -v
```

## 📊 Test Coverage

### ✅ Phase 1: Core Infrastructure
#### API Endpoints
- `GET /` - Root endpoint
- `GET /api/v1/health/` - Health check
- `GET /api/v1/health/db` - Database health
- Authentication endpoints (register, login, user info)
- Chatbot CRUD operations
- Conversation management

#### Functionality
- User registration and authentication
- JWT token generation and validation
- Database connectivity and operations
- Error handling and data cleanup

### ✅ Phase 2: Text Chat Service
#### API Endpoints
- `POST /api/v1/chat` - Text chat completion
- `POST /api/v1/documents/upload` - Document processing
- `GET /api/v1/documents/` - Document management

#### Functionality
- RAG pipeline (Retrieve-Augment-Generate)
- Document ingestion and vectorization
- Embeddings generation (Groq + OpenAI fallback)
- LangChain agent with tool calling
- Vector similarity search

### ✅ Phase 3: Voice Chat Service
#### API Endpoints
- `POST /api/v1/voice/chat` - Complete voice pipeline
- `POST /api/v1/voice/transcribe` - Speech-to-text only
- `POST /api/v1/voice/synthesize` - Text-to-speech only
- `WS /api/v1/voice/ws/{session_id}` - WebSocket voice communication
- `GET /api/v1/voice/health` - Voice service health

#### Voice Functionality
- **STT (Speech-to-Text)**: Groq Whisper V3 integration
- **TTS (Text-to-Speech)**: Deepgram voice synthesis
- **Audio Processing**: Format conversion (WAV, MP3, OGG, WebM)
- **WebSocket Communication**: Real-time voice chat
- **Voice Configuration**: Voice selection, speed, pitch control
- **Session Management**: Multi-user voice session handling
- **Audio Validation**: Security and format validation
- **Performance Testing**: Load testing and optimization
- **Error Handling**: Graceful fallbacks and recovery

#### Advanced Voice Testing
- **Edge Cases**: Malformed audio, oversized files, network issues
- **Security**: Malicious file detection, input validation
- **Performance**: Concurrent sessions, large file processing
- **Integration**: Complete STT → LLM → TTS pipeline
- **WebSocket Lifecycle**: Connection, disconnection, error recovery
- **Audio Quality**: Compression ratios, format compatibility

### ⚠️ What's NOT Yet Tested (Future Phases)
- Frontend dashboard functionality
- Embeddable widget performance
- Payment processing and billing
- Advanced rate limiting with Redis
- Production deployment scenarios
- Cross-browser compatibility

## Expected Results

### Quick Test
```
🧪 Quick Phase 1 Test
==============================
✅ Root endpoint: Chatbot SaaS Platform API
✅ Health check: healthy
✅ Database health: healthy
✅ API documentation accessible
✅ Authentication protection working

🎯 Quick test completed!
```

### Comprehensive Test (Sample)
```
🧪 Starting Phase 1 Comprehensive Tests
==================================================
--- Server Connection ---
✅ Server is running and accessible

--- User Registration ---  
✅ User registered successfully: test_123@example.com

--- Create Chatbot ---
✅ Chatbot created: Test Chatbot (ID: abc-123)

🏁 Phase 1 Test Results:
✅ Passed: 13
❌ Failed: 0
📊 Total: 13
🎉 All tests passed! Phase 1 implementation is working correctly.
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Make sure the FastAPI server is running
   - Check that it's running on `http://localhost:8000`

2. **Database Health Fails**
   - Verify Supabase credentials in `.env`
   - Check that Supabase project is active
   - Ensure database schema is created

3. **Authentication Errors**
   - Verify JWT secret key is set
   - Check Supabase auth configuration

4. **Import Errors**
   - Install missing dependencies: `pip install requests`
   - Ensure virtual environment is activated

### Getting Help

If tests fail:
1. Check the detailed error messages
2. Verify your `.env` configuration
3. Confirm database schema is properly set up
4. Check server logs for detailed errors

## Next Steps

Once all Phase 1 tests pass:
1. Move on to Phase 2 implementation (Text Chatbot Service)
2. Add chat completion endpoints
3. Implement document processing and RAG functionality

## Test Data

The comprehensive test creates:
- A test user with random email
- A test chatbot
- A test conversation

All test data is automatically cleaned up after testing.