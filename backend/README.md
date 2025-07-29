# Chatbot SaaS Backend

FastAPI backend for the Chatbot SaaS platform providing text and voice chatbot services.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Supabase account
- Redis server (local or cloud)
- API keys for: Groq, Deepgram

### 2. Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   # Method 1: Use the batch script (Windows)
   install_deps.bat
   
   # Method 2: Manual installation
   pip install -r requirements.txt
   python fix_and_test.py
   ```

### 3. Database Setup

1. **Create Supabase project:** https://supabase.com/dashboard

2. **Enable extensions in Supabase SQL Editor:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Run database schema:**
   - Copy the contents of `database.sql`
   - Execute in Supabase SQL Editor
   - Verify all tables are created

### 4. Environment Configuration

1. **Copy and update `.env` file:**
   - Update `SUPABASE_URL` with your project URL
   - Add your `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY`
   - Add API keys for OpenAI, Groq, Deepgram
   - Set a secure `SECRET_KEY` for JWT

2. **Required API Keys:**
   - **Supabase:** Project Settings → API → URL & Keys
   - **Groq:** https://console.groq.com/keys (for LLM, embeddings, and STT)
   - **Deepgram:** https://console.deepgram.com/ (for TTS)

### 5. Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API:** http://localhost:8000
- **Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health

## Testing

### Quick Testing
```bash
# Run all tests (Windows)
run_tests.bat

# Or run individual tests
python tests/test_diagnostics.py  # Diagnostic tool
python tests/quick_test.py        # Quick validation
python tests/test_phase1.py       # Comprehensive testing
```

### Test Coverage
- ✅ **13/13 endpoints tested**
- ✅ **Full authentication flow**
- ✅ **CRUD operations for all models**
- ✅ **Error handling and edge cases**

For detailed testing information, see [`tests/README.md`](tests/README.md)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Chatbots
- `GET /api/v1/chatbots/` - List user's chatbots
- `POST /api/v1/chatbots/` - Create new chatbot
- `GET /api/v1/chatbots/{id}` - Get chatbot details
- `PUT /api/v1/chatbots/{id}` - Update chatbot
- `DELETE /api/v1/chatbots/{id}` - Delete chatbot

### Conversations
- `POST /api/v1/conversations/` - Create conversation
- `GET /api/v1/conversations/chatbot/{id}` - Get chatbot conversations
- `GET /api/v1/conversations/{id}` - Get conversation details
- `DELETE /api/v1/conversations/{id}` - Delete conversation

### Health
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/db` - Database health check

## Development

### Project Structure
```
backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core functionality (auth, config, db)
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic (to be added in Phase 2)
│   └── main.py        # FastAPI app
├── tests/             # Test suite
│   ├── test_phase1.py       # Comprehensive testing
│   ├── quick_test.py        # Quick validation
│   ├── test_diagnostics.py  # Diagnostic tool
│   └── README.md           # Test documentation
├── database.sql       # Database schema
├── requirements.txt   # Dependencies
├── .env              # Environment variables
├── run_tests.bat     # Test runner (Windows)
├── TEST_README.md    # Testing guide
└── README.md         # This file
```

### Next Steps (Phase 2)
- Implement Groq embeddings integration
- Add RAG pipeline with vector search
- Create chat completion endpoints
- Add document upload and processing
- Implement LangChain agent with tool calling

## Troubleshooting

### Common Issues
1. **Import errors:** Make sure virtual environment is activated
2. **Database connection:** Verify Supabase credentials in `.env`
3. **Rate limiting errors:** Check Redis connection
4. **Authentication errors:** Verify JWT secret key is set

### Dependencies with compilation issues on Windows
If you encounter Rust compilation errors, try:
1. Install Visual Studio Build Tools
2. Use WSL2 for development
3. Use Docker for containerized development