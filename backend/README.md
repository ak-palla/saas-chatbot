# 🤖 Chatbot SaaS Platform - Backend

> **A powerful, scalable backend for embeddable chatbot services with RAG capabilities**

[![Phase 2 Complete](https://img.shields.io/badge/Phase%202-Complete-brightgreen)]()
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)]()
[![Supabase](https://img.shields.io/badge/Database-Supabase-green)]()
[![HuggingFace](https://img.shields.io/badge/Embeddings-HuggingFace-yellow)]()

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <your-repo>
cd chat_service/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp config/.env.template .env
# Edit .env with your API keys

# 5. Start the server
uvicorn app.main:app --reload
```

## 📁 Project Structure

```
backend/
├── 📁 app/                         # Core application
│   ├── 📁 api/                     # API endpoints
│   │   └── 📁 api_v1/
│   │       ├── api.py              # Main router
│   │       └── 📁 endpoints/       # Individual endpoints
│   ├── 📁 core/                    # Core configuration
│   │   ├── auth.py                 # Authentication
│   │   ├── config.py               # Settings
│   │   ├── database.py             # Database connection
│   │   └── middleware.py           # Custom middleware
│   ├── 📁 models/                  # Pydantic models
│   ├── 📁 services/                # Business logic
│   │   ├── agent_service.py        # LangChain agents
│   │   ├── document_service.py     # Document processing
│   │   ├── embedding_service.py    # HuggingFace embeddings
│   │   ├── llm_service.py          # Groq LLM integration
│   │   └── vector_store_service.py # Vector database ops
│   └── main.py                     # FastAPI app
├── 📁 docs/                        # Documentation
├── 📁 scripts/                     # Utility scripts
│   ├── 📁 database/                # Database schemas
│   └── 📁 utilities/               # Maintenance scripts
├── 📁 tests/                       # Test suite
│   ├── 📁 integration/             # Integration tests
│   ├── 📁 unit/                    # Unit tests
│   └── 📁 utils/                   # Test utilities
├── 📁 config/                      # Configuration templates
├── requirements.txt                # Dependencies
└── .gitignore                      # Git ignore rules
```

## ✨ Features

### 🎯 Phase 2 Complete (Current)
- ✅ **Document Management**: Upload PDF, TXT, DOCX, HTML, Markdown
- ✅ **Vector Embeddings**: HuggingFace Sentence Transformers (cost-free!)
- ✅ **Smart Search**: Vector similarity search with pgvector
- ✅ **Chat Completion**: Groq LLM integration (multiple models)
- ✅ **RAG Pipeline**: Retrieval-Augmented Generation ready
- ✅ **Agent Framework**: LangChain agents with custom tools
- ✅ **Google Drive**: Optional backup integration
- ✅ **Authentication**: JWT-based auth with Supabase
- ✅ **RESTful API**: Complete CRUD operations

### 🔮 Coming Soon
- **Phase 3**: Voice chat (STT/TTS) with Deepgram
- **Phase 4**: Widget & frontend interface
- **Phase 5**: Advanced analytics & monitoring
- **Phase 6**: Payment processing with Stripe

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI | High-performance async API |
| **Database** | Supabase (PostgreSQL) | User data & metadata |
| **Vector DB** | pgvector | Similarity search |
| **Embeddings** | HuggingFace | Local, cost-free embeddings |
| **LLM** | Groq API | Fast inference |
| **Agent Framework** | LangChain | Tool calling & workflows |
| **Authentication** | Supabase Auth | JWT-based auth |
| **File Storage** | Google Drive (optional) | Document backup |
| **Document Processing** | PyPDF2, python-docx, BeautifulSoup | Multi-format support |

## 🏃‍♂️ Development

### Prerequisites
- Python 3.11 or higher
- Supabase account
- Groq API key
- HuggingFace account (optional)

### Setup Instructions

1. **Environment Configuration**
   ```bash
   cp config/.env.template .env
   ```
   Fill in your API keys (see [Configuration Guide](docs/QUICK_START.md))

2. **Database Setup**
   ```sql
   -- Run in Supabase SQL Editor
   \i scripts/database/database.sql
   \i scripts/database/vector_setup.sql
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

### 🧪 Testing

Run the comprehensive test suite:

```bash
# Full integration tests
python tests/integration/test_phase2_complete.py

# Phase 1 tests
python tests/integration/test_phase1_complete.py

# Quick verification
python tests/utils/quick_test.py
```

**Current Test Status**: ✅ **100% Pass Rate** (11/11 tests)

### 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables

```env
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
GROQ_API_KEY=your_groq_key

# Optional
HUGGINGFACE_API_TOKEN=your_hf_token
GOOGLE_DRIVE_CREDENTIALS_PATH=./google-credentials.json
```

See [config/.env.template](config/.env.template) for complete configuration.

### 🤖 AI Models

**Embeddings (HuggingFace)**:
- `all-MiniLM-L6-v2` (384D) - Default, fast, good quality
- `all-mpnet-base-v2` (768D) - High quality, slower
- `all-MiniLM-L12-v2` (384D) - Balanced performance

**LLM (Groq)**:
- `mixtral-8x7b-32768` - High quality, large context
- `llama2-70b-4096` - Balanced performance
- `gemma-7b-it` - Fast, good for simple tasks

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/QUICK_START.md) | Get up and running in 5 minutes |
| [Database Setup](docs/DATABASE_SETUP.md) | Complete database configuration |
| [HuggingFace Setup](docs/HUGGINGFACE_SETUP.md) | Local embeddings configuration |
| [Google Drive Setup](docs/GOOGLE_DRIVE_SETUP.md) | Optional file backup |
| [Testing Guide](docs/TESTING.md) | Test suite documentation |
| [Phase 2 Summary](docs/PHASE2_SUMMARY.md) | Current feature overview |

## 🚀 Deployment

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Recommended Platforms**:
- Railway
- Render
- Google Cloud Run
- AWS ECS

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📈 Performance

- **Response Time**: < 500ms (typical)
- **Throughput**: 1000+ requests/minute
- **Embedding Generation**: ~10ms per document chunk
- **Vector Search**: < 100ms for similarity queries
- **Cost**: $0/month for embeddings (HuggingFace local)

## 🔒 Security

- JWT-based authentication
- API rate limiting
- Input validation & sanitization
- SQL injection protection
- Secure file upload handling
- Environment variable security

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [docs/](docs/)

## 🏆 Achievements

- ✅ **Phase 1**: Complete backend infrastructure
- ✅ **Phase 2**: RAG-enabled chatbots with local embeddings
- 🔄 **Phase 3**: Voice capabilities (in progress)

---

<div align="center">

**Built with ❤️ for the future of conversational AI**

[Documentation](docs/) • [API Reference](http://localhost:8000/docs) • [Support](https://github.com/your-repo/issues)

</div>