# MelusAI - Product Requirements Document

## Overview
MelusAI es una plataforma SaaS de desarrollo de software con IA, diseñada como un clon de Emergent. Permite a los usuarios describir aplicaciones y que agentes de IA las construyan automáticamente.

## Core Architecture

### Tech Stack
- **Frontend:** React (CRA) - Target: Next.js
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (actual), PostgreSQL (target - esquemas definidos)
- **AI Integration:** emergentintegrations (OpenAI, Anthropic, Google, Sora)
- **Payments:** Stripe

### Project Structure
```
/app/
├── core/                    # Core AI logic
│   ├── brain_engine.py      # Central orchestrator
│   ├── agent_system.py      # Multi-agent system
│   ├── llm_manager.py       # LLM provider manager
│   ├── intent_classifier.py # Intent classification
│   └── code_templates.py    # Pre-built templates
├── backend/
│   ├── server.py            # Main FastAPI server
│   └── routes/
│       ├── brain_api.py     # Brain Engine API
│       ├── pipeline_api.py  # Project pipeline
│       ├── stripe_billing.py # Payments
│       └── auth_oauth.py    # Authentication
├── frontend/src/
│   ├── pages/
│   │   ├── BuilderPage.jsx     # Main builder (Emergent-style)
│   │   ├── LandingPageEmergent.jsx
│   │   ├── PricingPageNew.jsx
│   │   ├── DashboardPage.jsx
│   │   └── Success.jsx
│   └── context/
│       └── AuthContext.jsx
└── database/
    └── schemas.py           # PostgreSQL schemas (SQLAlchemy)
```

## Implemented Features

### ✅ Phase 1: Core Interface (Completed 24 Feb 2024)
1. **BuilderPage** - Interfaz principal similar a Emergent
   - Panel de chat izquierdo
   - Panel de code/preview derecho
   - Selector de modos de agente (E1, E1.5, E2, Pro)
   - Selector de modelos de IA
   - Explorador de archivos estilo VS Code
   - Terminal integrado
   - Preview responsivo (desktop/tablet/mobile)
   - Botones de Deploy, Download, Share

2. **Landing Page** - Diseño profesional
   - Hero section con animación de código
   - Features destacados
   - Testimonios
   - Footer con links

3. **Pricing Page** - Sistema de pagos
   - 3 planes: Free, Pro ($20/mes), Team ($50/mes)
   - Sistema de créditos (paquetes de compra)
   - FAQ integrado

4. **Backend APIs**
   - `/api/brain/models` - Lista de modelos disponibles
   - `/api/brain/modes` - Lista de modos de agente
   - `/api/brain/create-task` - Crear proyectos
   - `/api/stripe/create-checkout` - Checkout unificado

### AI Models Available
- **OpenAI:** GPT-4o, GPT-4o Mini, GPT-5.2 Codex, O3
- **Anthropic:** Claude 4 Sonnet, Claude 4.5 Opus, Claude 4.6 Opus/Sonnet
- **Google:** Gemini 3 Pro, Gemini 3 Flash, Gemini 2.5 Pro
- **Video:** Sora 2, Sora 2 Pro

### Agent Modes
- **E1:** Standard - Fast iterations
- **E1.5:** Enhanced - Better quality
- **E2:** Advanced - Multi-agent system
- **Pro:** Maximum quality
- **Prototype:** Frontend rapid prototyping
- **Mobile:** React Native focus

## Pending Tasks

### P0: Critical
- [ ] Test complete generation flow (create project -> generate -> preview)
- [ ] Fix any WebSocket connection issues
- [ ] Verify Stripe checkout flow

### P1: Important
- [ ] Database Migration (MongoDB → PostgreSQL)
- [ ] Frontend Migration (React → Next.js)
- [ ] Complete Stripe webhooks for subscription management

### P2: Future
- [ ] Docker sandbox for code execution
- [ ] GitHub integration improvements
- [ ] Team collaboration features
- [ ] Visual drag-and-drop editor
- [ ] Admin dashboard improvements

## API Endpoints

### Authentication
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user
- `GET /api/auth/google` - Google OAuth

### Brain Engine
- `GET /api/brain/models` - List AI models
- `GET /api/brain/modes` - List agent modes
- `POST /api/brain/create-task` - Create generation task
- `GET /api/brain/task/{id}` - Get task status
- `POST /api/brain/chat` - Quick chat with AI
- `POST /api/brain/classify` - Classify intent

### Projects
- `GET /api/pipeline/projects` - List user projects
- `POST /api/pipeline/projects` - Create project
- `GET /api/pipeline/projects/{id}` - Get project
- `GET /api/pipeline/preview/{id}` - Preview project

### Payments
- `POST /api/stripe/create-checkout` - Create checkout session
- `GET /api/stripe/verify-session/{id}` - Verify payment

## Test Credentials
- **Email:** demo@melusai.com
- **Password:** password

## Notes
- User authentication uses bcrypt for passwords
- Session tokens stored in localStorage
- Credits system: 50 free/month, unlimited for Pro
- All LLM calls use Emergent LLM Key

---
*Last Updated: 24 February 2024*
*Version: 3.0.0*
