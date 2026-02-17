# Assistant Melus - Product Requirements Document

## Overview
Assistant Melus es un clon completo del asistente AI de Emergent.sh, desarrollado con React (frontend) y FastAPI (backend) con MongoDB.

## Original Problem Statement
Crear un MVP funcional y listo para producción de un clon de asistente AI como Emergent, llamado "Assistant Melus".

## Core Requirements

### 1. Authentication System
- [x] Sistema de registro con email/password (no Google OAuth)
- [x] Login con email/password
- [x] Gestión de sesiones con tokens JWT-like almacenados en localStorage
- [x] Protección de rutas autenticadas

### 2. Credit-Based System
- [x] 1,000 créditos gratuitos para nuevos usuarios
- [x] Integración con Stripe para compra de créditos
- [x] Paquetes de créditos configurables
- [x] Sistema de códigos promocionales
- [x] Historial de transacciones

### 3. Chat Features
- [x] Chat en tiempo real con modelos AI (usando Emergent LLM Key)
- [x] Selección de modelo AI (GPT-4o, GPT-5.1, Claude, Gemini)
- [x] Conversaciones múltiples
- [x] Fork de conversaciones
- [x] Edición de mensajes de usuario
- [x] Regeneración de respuestas AI
- [x] Contador de tokens utilizados

### 4. Workspace UI
- [x] Dashboard estilo workspace similar a Emergent.sh
- [x] Tabla de proyectos/conversaciones
- [x] Pestañas Workspace/Chat
- [x] Header con créditos y perfil de usuario

## Tech Stack
- **Frontend:** React 18, TailwindCSS, shadcn/ui, react-router-dom, axios
- **Backend:** FastAPI, Python, Motor (async MongoDB)
- **Database:** MongoDB
- **Authentication:** Custom JWT-like tokens
- **Payments:** Stripe
- **AI:** Emergent LLM Key (OpenAI GPT-4o)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Crear cuenta
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual
- `POST /api/auth/logout` - Cerrar sesión

### Conversations
- `GET /api/conversations` - Listar conversaciones
- `POST /api/conversations` - Crear conversación (soporta fork)
- `DELETE /api/conversations/{id}` - Eliminar conversación
- `GET /api/conversations/{id}/messages` - Obtener mensajes
- `POST /api/conversations/{id}/messages` - Enviar mensaje

### Messages
- `PUT /api/messages/{id}` - Editar mensaje
- `POST /api/messages/{id}/regenerate` - Regenerar respuesta

### Credits
- `GET /api/credits` - Obtener balance
- `GET /api/credits/packages` - Listar paquetes
- `POST /api/credits/checkout` - Crear sesión de pago
- `GET /api/credits/transactions` - Historial de transacciones

## Database Schema

### Users
```json
{
  "user_id": "string",
  "email": "string",
  "name": "string",
  "password_hash": "string",
  "picture": "string",
  "credits": "number",
  "credits_used": "number",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Conversations
```json
{
  "conversation_id": "string",
  "user_id": "string",
  "title": "string",
  "model": "string",
  "forked_from": "string|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Messages
```json
{
  "message_id": "string",
  "conversation_id": "string",
  "user_id": "string",
  "role": "user|assistant",
  "content": "string",
  "model": "string|null",
  "tokens_used": "number",
  "edited": "boolean",
  "original_content": "string|null",
  "timestamp": "datetime"
}
```

## Completed Work (Feb 2026)

### Session 1 - Core Development
- Built complete full-stack foundation
- Implemented email/password authentication (replaced Google OAuth)
- Created JWT-like session management with localStorage
- Integrated Emergent LLM Key for AI responses
- Integrated Stripe for payments
- Built workspace UI similar to Emergent.sh
- Created custom pricing modal

### Session 2 - Bug Fixes & Optimization
- Fixed registration flow session management
- Updated ProtectedRoute to skip check for authenticated users
- Improved AuthContext with proper token management
- Fixed ChatArea message display with forwardRef
- Optimized conversations query (removed N+1 pattern)
- Increased FREE_CREDITS from 10 to 1000
- Added data-testid attributes for testing
- Verified all features working end-to-end

## Deployment Status
- [x] Deployment health check passed
- [x] All environment variables properly configured
- [x] CORS configuration correct
- [x] Supervisor configuration valid

## Pending/Future Tasks

### P1 - High Priority
1. Implement file attachments (adjuntos) in chat
2. Add message export functionality
3. Add conversation search

### P2 - Medium Priority
1. Refactor server.py into modules (auth.py, chat.py, billing.py)
2. Add dark mode support
3. Improve mobile responsiveness

### P3 - Low Priority
1. Add keyboard shortcuts
2. Add message reactions
3. Implement conversation sharing
