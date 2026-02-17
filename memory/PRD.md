# Assistant Melus - Product Requirements Document

## Overview
Assistant Melus es un clon completo y profesional del asistente AI de Emergent.sh, con todas las funcionalidades avanzadas implementadas.

## Funcionalidades Implementadas ✅

### 1. Authentication System
- [x] Registro con email/password
- [x] Login con email/password
- [x] Gestión de sesiones con tokens en localStorage
- [x] Protección de rutas autenticadas
- [x] UI con tema oscuro profesional

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
- [x] Bloques de código con syntax highlighting

### 4. UI/UX - Clon de Emergent.sh
- [x] Tema oscuro completo (#0d0d1a, #1a1a2e)
- [x] Header con tabs de proyectos
- [x] Créditos en badge dorado
- [x] Botones Code, Preview, Redeploy
- [x] PromptBox con todos los botones
- [x] Chat Messages con estilo terminal

### 5. Funcionalidades Avanzadas (NUEVAS)

#### 📎 Adjuntar Archivos (Attachments)
- [x] Upload de archivos (imágenes, PDFs, código)
- [x] Preview de archivos adjuntados
- [x] Almacenamiento persistente
- [x] Límite de 10MB por archivo

#### 💾 Save
- [x] Guardar/marcar conversaciones
- [x] Toggle de estado guardado
- [x] Persistencia en base de datos

#### 📝 Summarize
- [x] Resumen AI de la conversación
- [x] Extracción de puntos clave
- [x] Costo de 50 créditos

#### ⚡ Ultra Mode
- [x] Toggle para modo de alto rendimiento
- [x] Indicador visual en PromptBox
- [x] Multiplicador de costo 1.5x-2x

#### 🎤 Voice Input (Micrófono)
- [x] Grabación de audio del navegador
- [x] Transcripción a texto (placeholder)
- [x] Indicador de grabación activa

#### 💻 Code Viewer
- [x] Extracción de bloques de código
- [x] Modal con syntax highlighting
- [x] Copiar código individual
- [x] Filtro por lenguaje
- [x] Timestamps por bloque

#### 👁️ Preview Panel
- [x] Información del proyecto
- [x] Estadísticas (mensajes, modelo)
- [x] Fechas de creación y última actividad
- [x] Resumen si existe
- [x] Estados: Ultra, Saved

#### 🔄 Redeploy
- [x] Trigger de redeploy
- [x] Registro de acciones
- [x] Feedback visual

#### ⏪ Rollback
- [x] Rollback a mensaje específico
- [x] Elimina mensajes posteriores
- [x] Feedback con contador

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
- `POST /api/conversations/{id}/save` (NEW)
- `GET /api/conversations/{id}/export` (NEW)
- `POST /api/conversations/{id}/summarize` (NEW)
- `POST /api/conversations/{id}/ultra` (NEW)
- `GET /api/conversations/{id}/code` (NEW)
- `GET /api/conversations/{id}/preview` (NEW)
- `POST /api/conversations/{id}/redeploy` (NEW)

### Messages
- `PUT /api/messages/{id}`
- `POST /api/messages/{id}/regenerate`
- `POST /api/messages/{id}/rollback` (NEW)

### Attachments (NEW)
- `POST /api/attachments/upload`
- `GET /api/attachments/{id}`
- `GET /api/conversations/{id}/attachments`

### Voice (NEW)
- `POST /api/voice/transcribe`

### Credits
- `GET /api/credits`
- `GET /api/credits/packages`
- `POST /api/credits/checkout`
- `GET /api/credits/transactions`

## Tech Stack
- **Frontend:** React 18, TailwindCSS, shadcn/ui
- **Backend:** FastAPI, Python, Motor (async MongoDB)
- **Database:** MongoDB
- **Payments:** Stripe
- **AI:** Emergent LLM Key (OpenAI GPT-4o)
- **Storage:** Local filesystem (/app/uploads)

## Deployment Status
- [x] All services running
- [x] Environment variables configured
- [x] All features tested
- [x] Ready for production

## Próximas Mejoras Potenciales
1. Integración real con Whisper API para transcripción de voz
2. Export a PDF de conversaciones
3. Compartir conversaciones públicamente
4. Themes personalizables
5. Keyboard shortcuts
6. Mobile responsive improvements
