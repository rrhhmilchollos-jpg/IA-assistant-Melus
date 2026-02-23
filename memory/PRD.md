# Melus AI - Product Requirements Document

## Descripción
**Melus AI** es una plataforma SaaS de generación de aplicaciones con IA, similar a Emergent.sh/Base44. Sistema multi-agente autónomo para desarrollo de software completo.

**Idioma del usuario**: Español

---

## ✅ IMPLEMENTADO

### Sistema de Autenticación
- ✅ Login con Email/Password
- ✅ Login con Google OAuth (autoalojado)
- ✅ Login con GitHub OAuth
- ✅ Sistema de sesiones con tokens

### Landing Page Profesional
- ✅ Hero con prompt input
- ✅ Sección de características
- ✅ Planes de precios
- ✅ FAQ interactivo
- ✅ Footer completo

### AI Builder (NUEVO)
- ✅ Chat interactivo para crear apps en lenguaje natural
- ✅ Generación de código con LLM
- ✅ Vista de archivos generados
- ✅ Quick prompts predefinidos
- ✅ Pestañas: Chat, Archivos, Vista Previa

### Sistema Multi-Agente
- ✅ 6 Agentes con LLM integrado:
  - Planner Agent (GPT-4o)
  - Researcher Agent (GPT-4o)
  - Developer Agent (GPT-4o)
  - QA Agent
  - Optimizer Agent
  - Cost Controller Agent
- ✅ Orchestrator central
- ✅ API REST + WebSocket

### Pipeline de Generación
- ✅ 5 fases: Planning → Generation → Execution → Validation → Completed
- ✅ WebSocket streaming de logs
- ✅ Monaco Editor con syntax highlighting

### Sistema de Aprendizaje
- ✅ Vector Memory Store
- ✅ OpenAI embeddings
- ✅ Learning Dashboard

---

## Rutas Disponibles

- `/` - Landing Page
- `/login` - Login con email/Google/GitHub
- `/register` - Registro
- `/home` - Dashboard principal
- `/build` - **AI Builder** (Chat para crear apps)
- `/workspace` - Editor de código con Monaco
- `/orchestrator` - Panel de orquestador
- `/agents` - Dashboard de agentes
- `/learning` - Dashboard de aprendizaje

---

## APIs

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/google`
- `GET /api/auth/me`

### Multi-Agent
- `GET /api/agents-v3/status`
- `POST /api/agents-v3/pipeline/start`
- `GET /api/agents-v3/tasks`

---

## Changelog

### 2026-02-23
- ✅ AI Builder completo con chat
- ✅ LLM integrado en agentes (Planner, Researcher, Developer)
- ✅ Agent Dashboard
- ✅ Quick prompts en español

### 2026-02-21
- ✅ Google OAuth funcionando
- ✅ Nueva Landing Page
- ✅ Sistema Multi-Agente base

---

## Testing

- Email: `demo@melusai.com` / `demo123`
- URL: https://melus-dev-studio.preview.emergentagent.com

---

## PRÓXIMAS TAREAS

- [ ] Vista previa en vivo del código
- [ ] Sandbox Docker para ejecución
- [ ] Sistema de billing con Stripe
- [ ] Deploy automático
