# Phase 2 Setup Guide

This guide covers setting up the Phase 2 Text Chatbot Service with RAG capabilities, document processing, and AI agent functionality.

## Prerequisites

1. **Phase 1 must be completed and working** - Run `python test_phase1_complete.py` to verify
2. **Required API Keys:**
   - Groq API key for LLM services
   - OpenAI API key (recommended for embeddings)
   - Supabase project with vector extension enabled
3. **Optional:**
   - Google Drive API credentials for document storage
   - Redis instance for rate limiting

## Installation Steps

### 1. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install new Phase 2 dependencies
pip install -r requirements.txt
```

New dependencies added for Phase 2:
- `PyPDF2==3.0.1` - PDF document processing
- `python-docx==1.1.0` - Word document processing
- `beautifulsoup4==4.12.2` - HTML parsing
- `markdown==3.5.1` - Markdown processing
- `google-api-python-client==2.108.0` - Google Drive integration
- `google-auth==2.23.4` - Google authentication

### 2. Environment Configuration

Update your `.env` file with the following new variables:

```env
# Existing Phase 1 variables...
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key

# New Phase 2 variables
OPENAI_API_KEY=your_openai_api_key  # Recommended for embeddings
DEEPGRAM_API_KEY=your_deepgram_key  # For future voice features
GOOGLE_DRIVE_CREDENTIALS_PATH=path/to/credentials.json  # Optional
REDIS_URL=redis://localhost:6379  # Optional, for rate limiting
```

### 3. Database Setup

Run the vector database setup SQL:

```bash
# Connect to your Supabase database and run:
psql -h your_supabase_host -U postgres -d postgres -f vector_setup.sql

# Or via Supabase SQL Editor, copy and paste the contents of vector_setup.sql
```

This will:
- Enable the vector extension
- Create vector similarity search functions
- Add necessary indexes for performance
- Add any missing columns to existing tables

### 4. Google Drive Setup (Optional)

If you want to use Google Drive for document storage:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Drive API
4. Create a Service Account
5. Download the credentials JSON file
6. Update `GOOGLE_DRIVE_CREDENTIALS_PATH` in your `.env` file

### 5. Start the Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing Phase 2

Run the comprehensive Phase 2 test suite:

```bash
python test_phase2_complete.py
```

This will test:
- Document upload and processing
- Vector embeddings generation
- Document search functionality
- Basic chat completion
- RAG-enabled chat completion
- Agent-based chat with tools
- Knowledge base statistics
- Conversation summarization

## API Endpoints

Phase 2 adds the following new endpoints:

### Document Management
- `POST /api/v1/documents/upload` - Upload and process documents
- `GET /api/v1/documents/chatbot/{chatbot_id}` - List documents for a chatbot
- `GET /api/v1/documents/{document_id}` - Get specific document
- `DELETE /api/v1/documents/{document_id}` - Delete document
- `POST /api/v1/documents/search/{chatbot_id}` - Search documents

### Chat Completion
- `POST /api/v1/chat/completions` - Generate AI responses
- `POST /api/v1/chat/completions/stream` - Streaming AI responses
- `GET /api/v1/chat/models` - List available AI models
- `GET /api/v1/chat/chatbot/{chatbot_id}/knowledge-stats` - Knowledge base stats
- `GET /api/v1/chat/chatbot/{chatbot_id}/tools` - List available tools
- `GET /api/v1/chat/conversations/{conversation_id}/summary` - Get conversation summary

## Features

### 1. Document Processing
- **Supported formats:** PDF, DOCX, TXT, HTML, Markdown
- **Text extraction:** Automatic content extraction from various formats
- **Chunking:** Intelligent text splitting for optimal embeddings
- **Deduplication:** Content hash-based duplicate detection

### 2. Vector Embeddings
- **Primary:** OpenAI text-embedding-ada-002 (recommended)
- **Fallback:** Groq embeddings (if available)
- **Storage:** Supabase pgvector with cosine similarity
- **Search:** Vector similarity search with configurable thresholds

### 3. RAG (Retrieval-Augmented Generation)
- **Context retrieval:** Automatic relevant document retrieval
- **Smart prompting:** Context-aware prompt enhancement
- **Source tracking:** Metadata about information sources
- **Fallback handling:** Graceful degradation when no context available

### 4. AI Agents with Tools
Advanced chatbots with access to tools:
- **Document Search:** Query uploaded knowledge base
- **Calculator:** Perform mathematical calculations
- **DateTime:** Get current date and time information
- **Knowledge Stats:** Information about the knowledge base

### 5. Conversation Management
- **History:** Full conversation tracking
- **Summarization:** AI-generated conversation summaries
- **Sessions:** Support for multiple conversation sessions
- **Metadata:** Rich metadata tracking for analytics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   Embedding     │    │   Vector Store  │
│   Service       │────│   Service       │────│   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   LLM Service   │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│ Message Service │──────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │ Agent Service   │
                        └─────────────────┘
```

## Troubleshooting

### Common Issues

1. **Embedding generation fails:**
   - Ensure OPENAI_API_KEY is set correctly
   - Check API quotas and limits
   - Verify internet connectivity

2. **Document upload fails:**
   - Check file size limits (10MB default)
   - Verify supported file formats
   - Check disk space and permissions

3. **Vector search returns no results:**
   - Ensure documents are processed (`processed: true`)
   - Check similarity thresholds
   - Verify embeddings are generated

4. **Agent tools not working:**
   - Check that documents are uploaded and processed
   - Verify chatbot ownership
   - Check tool configurations

### Performance Optimization

1. **Database Indexes:**
   - Ensure vector indexes are created (see vector_setup.sql)
   - Monitor query performance
   - Consider index tuning for large datasets

2. **Embedding Caching:**
   - Implement Redis caching for frequent embeddings
   - Cache document embeddings after processing
   - Use batch processing for multiple documents

3. **Rate Limiting:**
   - Configure Redis for distributed rate limiting
   - Adjust limits based on API quotas
   - Monitor API usage

## Security Considerations

1. **API Keys:** Store securely, never commit to repository
2. **File Uploads:** Validate file types and sizes
3. **Access Control:** Verify user ownership of chatbots/documents
4. **Content Filtering:** Implement content validation for safety
5. **Rate Limiting:** Protect against abuse and API overuse

## Next Steps

After Phase 2 is working:
1. **Phase 3:** Voice Chatbot Service (Speech-to-Text, Text-to-Speech)
2. **Phase 4:** Frontend Dashboard (Next.js interface)
3. **Phase 5:** Embeddable Widget (JavaScript widget)
4. **Phase 6:** Payment & Billing (Stripe integration)

## Support

- Check server logs for detailed error messages
- Use the test suite to isolate issues
- Monitor API usage and quotas
- Review Supabase logs for database issues