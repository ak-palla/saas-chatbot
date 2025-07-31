---

**Prompt for Claude:**

You are a **Senior Frontend Architect & AI SaaS Solutions Engineer** with expertise in:

* Scalable **Next.js + TypeScript** frontend systems
* Real-time **LLM-powered dashboards** (voice/text/chat/analytics)
* Integrating with **FastAPI**, **Supabase**, and **WebSockets**
* Designing accessible, production-ready B2B/B2C AI SaaS platforms

---

I’m currently at **Phase 4** of an AI Chatbot SaaS product. The **backend (Phases 1–3)** is **fully complete and production-ready**, with all services using **real APIs** and tested with **live data**. The backend includes:

* **Voice + Text AI Chat Pipelines**:

  * STT: Groq Whisper
  * LLM: ChatGroq
  * TTS: Deepgram
* **FastAPI backend** with Supabase (Auth, vector DB, file storage)
* Real-time WebSocket support for chat and voice
* Audio processing with FFmpeg and pydub
* 100+ test cases, production monitoring, error handling, and usage tracking

---

### ✅ Frontend Stack:

* Next.js 14 (App Router), TypeScript
* Tailwind CSS, shadcn/ui
* Supabase client SDK
* WebSocket-based real-time communication
* All services are integrated with production backend APIs

---

### 🔍 Please review and provide technical feedback on the following:

**1. Component Architecture & Maintainability**

* Is the frontend modular and reusable?
* Are custom hooks, components, and layout logic well-structured?
* Are file/folder patterns aligned with modern scalable standards?

**2. Integration Soundness**

* How robustly is the frontend connected to:

  * Supabase Auth (login, sessions, protected routes)
  * FastAPI endpoints (chatbot, document, voice APIs)
  * WebSocket services (chat/voice messaging)?
* How are async states and errors handled across API calls and streams?

**3. Real-Time & Voice UX**

* Evaluate the STT → LLM → TTS pipeline from UI:

  * Is voice recording, preview, and playback smooth?
  * Does latency or reconnection logic work well?
  * Is WebSocket UI feedback clear and reliable?

**4. Dashboard UX/UI**

* Analyze chatbot management flows:

  * Prompt/appearance configuration
  * Document upload and processing
  * Usage analytics (including large datasets, e.g. 1000+ rows)
  * Widget preview and embed code generation
* Is the UI on par with tools like OpenAI, Hugging Face, LangChain?

**5. Performance & Responsiveness**

* Simulate heavy usage:

  * Many concurrent sessions
  * Real-time log streaming and updates
* Suggest improvements like:

  * Virtualization
  * Debouncing
  * Skeleton loaders or Suspense

**6. Accessibility (a11y) and Theming**

* Keyboard navigation support
* Screen reader compatibility
* Contrast ratios and dark/light theme toggling

**7. Security & Production Readiness**

* Any frontend-side security concerns?

  * Supabase token exposure
  * API misconfigurations
  * SSR/CSR edge cases
* Is SEO, SSR setup, and analytics/CDN integration production-ready?

**8. Final Recommendations**

* What **specific** changes or improvements would you prioritize before launch?
* Are any **tests missing** (unit, integration, E2E)?
* Any **refactors or polish** needed for better user/dev experience?

---
