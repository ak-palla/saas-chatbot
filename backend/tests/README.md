# Comprehensive Test Suite

This directory contains the complete testing infrastructure for the Chatbot SaaS platform, covering all implemented phases (1-3) with text and voice capabilities.

## 📁 Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   └── test_phase1.py      # Core infrastructure tests
├── integration/             # Integration tests for complete workflows
│   ├── test_phase1_complete.py                 # Phase 1 validation
│   ├── test_phase2_complete.py                 # Phase 2 text chat validation
│   ├── test_phase3_voice.py                    # Core voice functionality
│   ├── test_phase3_comprehensive_edge_cases.py # Advanced voice scenarios
│   └── test_phase3_complete_validation.py      # Master voice validation
├── utils/                   # Testing utilities and quick validation
│   └── quick_test.py       # Fast connectivity and basic validation
├── conftest.py             # Shared test configuration and fixtures
└── __init__.py             # Test package initialization
```

## 🚀 Running Tests

### Method 1: Development Tools (Recommended)
```bash
# All tests
python scripts/dev-tools.py test

# Specific test types
python scripts/dev-tools.py test unit         # Unit tests only
python scripts/dev-tools.py test integration # Integration tests only
python scripts/dev-tools.py test phase3      # Voice functionality tests
python scripts/dev-tools.py test voice       # Same as phase3

# Windows users
dev test phase3
```

### Method 2: Pytest Directly
```bash
# All tests with verbose output
pytest tests/ -v

# Specific categories
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # All integration tests
pytest tests/integration/test_phase3_voice.py -v  # Specific test file

# With coverage reporting
pytest tests/ --cov=app --cov-report=html

# Parallel execution for faster testing
pytest tests/ -n auto
```

### Method 3: Individual Validation
```bash
# Quick connectivity test (5 seconds)
python tests/utils/quick_test.py

# Phase 3 voice validation (30 seconds)
python scripts/utilities/validate_phase3.py

# Specific advanced voice testing
python -m pytest tests/integration/test_phase3_comprehensive_edge_cases.py -v
```

## 📊 Test Coverage Summary

### ✅ **Phase 1: Core Infrastructure** (Fully Tested)
- User authentication and JWT tokens
- Database connectivity and operations
- Chatbot and conversation CRUD operations
- API endpoint validation

### ✅ **Phase 2: Text Chat Service** (Fully Tested)  
- RAG pipeline (Retrieve-Augment-Generate)
- Document processing and vectorization
- Embeddings generation (Groq + OpenAI fallback)
- LangChain agent with tool calling

### ✅ **Phase 3: Voice Chat Service** (Fully Tested)
- **Core Voice Pipeline**: STT (Whisper V3) → LLM → TTS (Deepgram)
- **Audio Processing**: Format conversion, validation, optimization
- **WebSocket Communication**: Real-time voice chat sessions
- **Voice Configuration**: Voice selection, speed, pitch control
- **Advanced Scenarios**: Edge cases, security, performance testing
- **Error Handling**: Graceful fallbacks and recovery mechanisms

## 🧪 Test Types Explained

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Speed**: Very fast (~10 seconds)
- **Focus**: Core business logic, service methods, utility functions

### Integration Tests
- **Purpose**: Test complete workflows and API endpoints
- **Speed**: Moderate to slow (~60-120 seconds)
- **Focus**: End-to-end functionality, service integration, real API calls

### Voice-Specific Testing
- **STT Testing**: Audio transcription accuracy and performance
- **TTS Testing**: Voice synthesis quality and configuration
- **WebSocket Testing**: Real-time communication and session management
- **Audio Processing**: Format conversion, validation, security
- **Performance Testing**: Concurrent sessions, large file handling
- **Edge Cases**: Malformed data, network issues, resource limits

## 🔧 Test Configuration

### Prerequisites
1. **Virtual Environment**: Ensure `venv` is activated
2. **Dependencies**: All packages from `requirements.txt` installed
3. **FFmpeg**: Required for audio processing tests
4. **Environment Variables**: Proper API keys configured in `.env`
5. **Database**: Supabase connection and schema setup

### Environment Setup
The test suite automatically:
- Configures FFmpeg paths for audio processing
- Sets up mock services when external APIs are unavailable
- Handles missing dependencies gracefully
- Provides detailed error messages and troubleshooting

### Test Data Management
- **Automatic Cleanup**: All test data is cleaned up after execution
- **Isolation**: Tests don't interfere with each other
- **Mocking**: External services are mocked when appropriate
- **Real Integration**: Some tests use real APIs for validation

## 🚨 Troubleshooting

### Common Issues

**FFmpeg Not Available**
- Tests will automatically use mocks when FFmpeg is missing
- For full audio testing, install FFmpeg: `scoop install ffmpeg`

**API Key Issues**
- Set proper API keys in `.env` file
- Some tests will skip when keys are unavailable

**Database Connection Errors**  
- Verify Supabase credentials
- Check internet connectivity
- Ensure database schema is properly set up

**Import Errors**
- Activate virtual environment: `venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

### Getting Detailed Results
```bash
# Run with maximum verbosity
pytest tests/ -v -s

# Show test duration and slowest tests
pytest tests/ --durations=10

# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## ✅ Success Criteria

### All Tests Passing Indicates:
- **Phase 1**: Core infrastructure is stable and secure
- **Phase 2**: Text chat and RAG functionality working perfectly
- **Phase 3**: Voice chat pipeline fully operational with audio processing
- **Integration**: All services work together seamlessly
- **Production Ready**: Backend is ready for deployment

### Expected Test Results:
- **Unit Tests**: ~10-15 tests passing in <10 seconds
- **Integration Tests**: ~50+ tests passing in 60-120 seconds  
- **Voice Tests**: ~30+ voice-specific tests with audio processing
- **Overall**: 100+ tests covering complete platform functionality

For comprehensive testing documentation, see [`docs/TESTING.md`](../docs/TESTING.md).