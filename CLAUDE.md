# Chatbot SaaS Platform - Claude Instructions

## Project Overview
A SaaS platform providing embeddable chatbot services with two main offerings:
1. **Text Chatbot Service**: RAG-enabled conversational AI with tool calling
2. **Voice Chatbot Service**: Speech-to-text and text-to-speech enabled conversational AI

## Tech Stack

### Backend Services
- **API Framework**: FastAPI (Python) - async support, AI/ML integrations
- **Agent Framework**: LangChain - MCP workflow and tool calling
- **Voice Processing**:
  - Groq (Whisper V3) for STT
  - Deepgram for TTS
- **LLM Integration**: ChatGroq API client

### Database & Storage
- **Vector Database**: Supabase (PostgreSQL + pgvector)
- **File Storage**: Google Drive API integration
- **Embeddings**: Groq embeddings API
- **User Data**: PostgreSQL (Supabase)

### Frontend/Dashboard
- **Framework**: Next.js 14
- **UI Components**: Tailwind CSS + shadcn/ui
- **Embeddable Widget**: TypeScript

### Infrastructure
- **Deployment**: Vercel (frontend) + Railway/Render (backend)
- **Authentication**: Supabase Auth
- **Payment**: Stripe integration
- **API Gateway**: FastAPI with rate limiting

## Architecture Principles
- **Modular Design**: Services should be easily replaceable (e.g., Groq → other STT/TTS providers)
- **Simple Structure**: Avoid over-engineering or excessive modularity
- **Clean Separation**: Clear boundaries between text and voice services

## Project Structure
```
chat-service/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── core/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
└── widget/
    └── src/
```

## Development Guidelines
- Use async/await patterns for FastAPI
- Implement proper error handling and logging
- Follow REST API conventions
- Use environment variables for all API keys and configs
- Implement proper authentication and authorization

## Testing Commands
- Backend: `pytest`
- Frontend: `npm test`
- Linting: `ruff check` (Python), `npm run lint` (TypeScript)