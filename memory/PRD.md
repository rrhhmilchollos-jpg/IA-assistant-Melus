# Assistant Melus - Product Requirements Document

## Overview
Assistant Melus es un clon completo del asistente AI de Emergent.sh, con UI/UX idéntica y tema oscuro profesional.

## Original Problem Statement
Crear un MVP funcional y listo para producción de un clon de asistente AI como Emergent, llamado "Assistant Melus".

## Core Requirements

### 1. Authentication System
- [x] Sistema de registro con email/password
- [x] Login con email/password
- [x] Gestión de sesiones con tokens en localStorage
- [x] Protección de rutas autenticadas
- [x] UI con tema oscuro

### 2. Credit-Based System
- [x] 1,000 créditos gratuitos para nuevos usuarios
- [x] Integración con Stripe para compra de créditos
- [x] Paquetes de créditos configurables
- [x] Sistema de códigos promocionales
- [x] Historial de transacciones

### 3. Chat Features
- [x] Chat en tiempo real con modelos AI
- [x] Selección de modelo AI (GPT-4o, etc.)
- [x] Conversaciones múltiples con tabs
- [x] Fork de conversaciones
- [x] Edición de mensajes
- [x] Regeneración de respuestas
- [x] Contador de tokens
- [x] Botones Rollback/Copy en mensajes

### 4. UI/UX - Clon de Emergent.sh
- [x] **Tema oscuro completo** (#0d0d1a, #1a1a2e)
- [x] **Header estilo Emergent:**
  - Home button con icono
  - Tabs de proyectos con punto verde de estado
  - Botón "+" para nuevo proyecto
  - Créditos en badge dorado
  - Botón verde "Comprar créditos"
  - Botones Code, Preview, Redeploy
  - Avatar de usuario circular
- [x] **PromptBox estilo Emergent:**
  - Input "Message Agent"
  - Botones: Attachment, Save, Summarize, Ultra
  - Micrófono y botón enviar
  - Budget display (0 / 10,000)
  - "Powered by gpt-4o"
- [x] **Chat Messages:**
  - Avatares circulares para user/assistant
  - Timestamps y modelo
  - Botones Rollback/Copy on hover
  - Bloques de código expandibles (estilo terminal verde)

## Tech Stack
- **Frontend:** React 18, TailwindCSS, shadcn/ui
- **Backend:** FastAPI, Python, Motor (async MongoDB)
- **Database:** MongoDB
- **Authentication:** Custom JWT-like tokens
- **Payments:** Stripe
- **AI:** Emergent LLM Key (OpenAI GPT-4o)

## Color Palette
```css
--bg-primary: #0d0d1a
--bg-secondary: #1a1a2e
--bg-input: #1a1a2e (gray-800)
--border: gray-700/800
--text-primary: white
--text-secondary: gray-400
--accent-purple: purple-600
--accent-yellow: yellow-400/500
--accent-green: green-500/600
--code-block-bg: #1a3a2a (green tinted)
```

## API Endpoints

### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`

### Conversations
- `GET /api/conversations`
- `POST /api/conversations`
- `DELETE /api/conversations/{id}`
- `GET /api/conversations/{id}/messages`
- `POST /api/conversations/{id}/messages`

### Messages
- `PUT /api/messages/{id}`
- `POST /api/messages/{id}/regenerate`

### Credits
- `GET /api/credits`
- `GET /api/credits/packages`
- `POST /api/credits/checkout`
- `GET /api/credits/transactions`

## Completed Work (Feb 2026)

### Session 1 - Core Development
- Full-stack foundation
- Email/password authentication
- Stripe integration
- AI chat integration

### Session 2 - Bug Fixes
- Fixed registration flow
- Fixed session token management
- Fixed ChatArea message display

### Session 3 - UI Clone (Current)
- **Complete UI redesign to match Emergent.sh**
- Dark theme implementation
- New Header with project tabs
- New PromptBox with action buttons
- New ChatMessage with code blocks
- Updated Login/Register pages

## Deployment Status
- [x] All services running
- [x] Environment variables configured
- [x] CORS configured
- [x] Ready for production

## Pending/Future Tasks

### P1 - High Priority
1. Implement file attachments (Attachment button functional)
2. Implement Save functionality
3. Implement Summarize functionality
4. Implement Ultra mode

### P2 - Medium Priority
1. Code view button (show generated code)
2. Preview button (show app preview)
3. Redeploy button functionality
4. Dark mode toggle (light/dark)

### P3 - Low Priority
1. Voice input (Mic button)
2. Keyboard shortcuts
3. Conversation export
4. Mobile responsive improvements
