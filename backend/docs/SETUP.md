# Chatbot SaaS Backend Setup Guide

This comprehensive guide covers everything you need to set up and run the Chatbot SaaS backend with full text and voice capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for future frontend development)
- Git

### 1. Clone and Setup
```bash
git clone <your-repo>
cd chat_service/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install FFmpeg (Required for Voice Features)
FFmpeg is required for audio processing in voice chat functionality.

**Option 1: Using Scoop (Windows - Recommended)**
```bash
# Install Scoop
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Install FFmpeg
scoop install ffmpeg
```

**Option 2: Manual Download**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH

**Option 3: Using Package Managers**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS with Homebrew
brew install ffmpeg

# Conda
conda install -c conda-forge ffmpeg
```

### 3. Environment Configuration
Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
# Database (Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Services
GROQ_API_KEY=your_groq_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
HUGGINGFACE_API_KEY=your_huggingface_key

# Google Drive (Optional)
GOOGLE_DRIVE_CREDENTIALS_PATH=google-drive-credentials.json

# Security
SECRET_KEY=your_secret_key_here
```

### 4. Database Setup
Run the database setup script:
```bash
python scripts/database/setup_database.py
```

### 5. Validate Setup
Use the development tools to validate your setup:
```bash
python scripts/dev-tools.py validate
```

### 6. Start Development Server
```bash
python scripts/dev-tools.py server
```

The server will start at http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## 🔧 Development Tools

Use the integrated development tools for common tasks:

```bash
# Set up environment
python scripts/dev-tools.py setup

# Install dependencies
python scripts/dev-tools.py install

# Run tests
python scripts/dev-tools.py test              # All tests
python scripts/dev-tools.py test phase3       # Voice functionality tests
python scripts/dev-tools.py test integration  # Integration tests

# Start server
python scripts/dev-tools.py server            # With auto-reload
python scripts/dev-tools.py server --no-reload

# Validate complete setup
python scripts/dev-tools.py validate
```

**Windows Users**: You can use the `dev.bat` wrapper:
```bash
dev setup
dev test phase3
dev server
```

## 📊 API Keys Setup

### Supabase Database
1. Create a project at https://supabase.com
2. Go to Settings → API
3. Copy your URL and anon key
4. Copy your service role key (for server operations)

### Groq (STT & LLM)
1. Sign up at https://console.groq.com/
2. Create an API key
3. Add to your `.env` file

### Deepgram (TTS)
1. Sign up at https://console.deepgram.com/
2. Create an API key
3. Add to your `.env` file

### HuggingFace (Embeddings)
1. Sign up at https://huggingface.co/
2. Create an access token at https://huggingface.co/settings/tokens
3. Add to your `.env` file

### Google Drive (Optional)
For document ingestion capabilities:
1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable Google Drive API
4. Create service account credentials
5. Download JSON file and save as `google-drive-credentials.json`

## 🧪 Testing

### Running Tests
```bash
# All tests
python scripts/dev-tools.py test

# Specific test types
python scripts/dev-tools.py test unit
python scripts/dev-tools.py test integration
python scripts/dev-tools.py test phase3       # Voice functionality
python scripts/dev-tools.py test voice        # Same as phase3

# Using pytest directly
pytest tests/integration/ -v
pytest tests/unit/ -v
```

### Test Coverage
- **Unit Tests**: Core service logic
- **Integration Tests**: API endpoints and workflows
- **Phase 3 Tests**: Complete voice functionality pipeline
- **Edge Case Tests**: Error handling and security validation

## 🎙️ Voice Features

The backend includes complete voice chat capabilities:

### Supported Features
- **Speech-to-Text**: Groq Whisper V3 integration
- **Text-to-Speech**: Deepgram voice synthesis
- **Audio Processing**: Format conversion (WAV, MP3, OGG, WebM)
- **WebSocket Support**: Real-time voice communication
- **Voice Configuration**: Voice selection, speed, pitch control
- **Session Management**: Multi-user voice session handling

### Voice API Endpoints
- `POST /api/v1/voice/chat` - Complete voice chat (STT → LLM → TTS)
- `POST /api/v1/voice/transcribe` - Speech-to-text only
- `POST /api/v1/voice/synthesize` - Text-to-speech only
- `WS /api/v1/voice/ws/{session_id}` - WebSocket voice communication
- `GET /api/v1/voice/health` - Voice service health check

## 🐛 Troubleshooting

### Common Issues

**FFmpeg Not Found**
```
RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
```
- Install FFmpeg using one of the methods above
- Restart your terminal after installation
- For Windows: Ensure FFmpeg is in your PATH

**Database Connection Errors**
- Verify your Supabase URL and keys in `.env`
- Check that your Supabase project is active
- Run database setup: `python scripts/database/setup_database.py`

**Import Errors**
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check Python version (3.11+ required)

**API Key Errors**
- Verify all API keys are correctly set in `.env`
- Check that keys have proper permissions
- For Groq: Ensure you have credits/quota available

### Getting Help
1. Check the API documentation at http://localhost:8000/docs
2. Run validation: `python scripts/dev-tools.py validate`
3. Check logs for detailed error messages
4. Verify all services are properly configured

## 📚 Next Steps

After setup is complete:
1. **Explore API**: Visit http://localhost:8000/docs to test endpoints
2. **Run Tests**: Ensure everything works with `dev test`
3. **Voice Testing**: Test voice features with `dev test phase3`
4. **Development**: Start building your chatbot configurations
5. **Frontend**: Proceed to Phase 4 (Frontend Dashboard) development

Your chatbot SaaS backend is now ready for development with full text and voice capabilities! 🚀