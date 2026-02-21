# Melus AI - Product Requirements Document

## Descripción
**Melus AI** es una plataforma SaaS de generación de aplicaciones con IA, similar a Emergent.sh. Sistema multi-agente autónomo para desarrollo de software completo.

**Idioma del usuario**: Español

---

## ✅ IMPLEMENTADO

### Sistema de Autenticación (FASE 1 Completada)
- ✅ Login con Email/Password
- ✅ Login con Google OAuth (autoalojado)
- ✅ Login con GitHub OAuth
- ✅ Sistema de sesiones con tokens
- ✅ Logout funcional

### Landing Page Profesional (NUEVA)
- ✅ Hero con prompt input
- ✅ Sección de características (6 features)
- ✅ Sección "How It Works" (4 pasos)
- ✅ Planes de precios (Free/Pro/Enterprise)
- ✅ FAQ interactivo
- ✅ Footer completo
- ✅ Navegación responsive

### Sistema Multi-Agente (NUEVO - FASE 1)
- ✅ 6 Agentes especializados:
  - Planner Agent (planificación)
  - Researcher Agent (investigación)
  - Developer Agent (desarrollo)
  - QA Agent (testing)
  - Optimizer Agent (optimización)
  - Cost Controller Agent (control de costos)
- ✅ Orchestrator central
- ✅ Sistema de tareas y mensajes
- ✅ API REST para interacción
- ✅ WebSocket para actualizaciones en tiempo real

### Pipeline de Generación
- ✅ 5 fases: Planning → Generation → Execution → Validation → Completed
- ✅ WebSocket streaming de logs
- ✅ Monaco Editor con syntax highlighting
- ✅ Regeneración de archivos individuales

### Sistema de Aprendizaje Continuo
- ✅ Vector Memory Store
- ✅ OpenAI embeddings
- ✅ Feedback System
- ✅ Metrics Tracker
- ✅ Learning Dashboard

---

## Arquitectura Actual

```
/app
├── backend/
│   ├── server.py                    # FastAPI server
│   ├── multi_agent_system.py        # NUEVO: Sistema multi-agente
│   ├── pipeline_engine.py
│   ├── websocket_manager.py
│   ├── learning/
│   └── routes/
│       ├── auth_oauth.py            # Auth autoalojado
│       ├── multi_agent_api.py       # NUEVO: API multi-agente
│       ├── pipeline_api.py
│       └── learning_api.py
├── frontend/
│   └── src/
│       ├── App.js
│       ├── pages/
│       │   ├── LandingPageNew.jsx   # NUEVO: Landing profesional
│       │   ├── Login.jsx            # Actualizado con OAuth
│       │   ├── HomePage.jsx
│       │   └── WorkspacePage.jsx
│       └── context/
│           └── AuthContext.jsx
└── memory/PRD.md
```

---

## Stack Tecnológico

- **Frontend**: React, TailwindCSS, Monaco Editor, shadcn/ui
- **Backend**: FastAPI, WebSocket, Multi-Agent System
- **LLM**: OpenAI GPT-4o via Emergent
- **Database**: MongoDB
- **Auth**: OAuth 2.0 (Google, GitHub) autoalojado

---

## APIs Implementadas

### Auth
- `POST /api/auth/register` - Registro con email
- `POST /api/auth/login` - Login con email
- `GET /api/auth/google` - Iniciar OAuth Google
- `GET /api/auth/google/callback` - Callback Google
- `GET /api/auth/me` - Usuario actual
- `POST /api/auth/logout` - Cerrar sesión

### Multi-Agent System (NUEVO)
- `GET /api/agents-v3/status` - Estado del sistema
- `GET /api/agents-v3/agents` - Lista de agentes
- `GET /api/agents-v3/agents/{type}` - Estado de un agente
- `POST /api/agents-v3/pipeline/start` - Iniciar pipeline
- `POST /api/agents-v3/task` - Crear tarea
- `GET /api/agents-v3/tasks` - Listar tareas
- `GET /api/agents-v3/messages` - Mensajes entre agentes
- `GET /api/agents-v3/costs` - Tracking de costos
- `WS /api/agents-v3/ws/{project_id}` - WebSocket updates

---

## PRÓXIMAS TAREAS

### P1 - En Progreso
- [ ] Integrar LLM real en los agentes (actualmente skeleton)
- [ ] Dashboard visual de agentes en tiempo real
- [ ] Conectar multi-agente con pipeline existente

### P2 - Próximo
- [ ] Sandbox aislado con Docker
- [ ] Deploy automático
- [ ] Sistema de versionado (diffs, rollbacks)

### P3 - Futuro
- [ ] Billing con Stripe (planes)
- [ ] API keys para B2B
- [ ] Templates predefinidos
- [ ] Blog auto-generado (SEO)

---

## Changelog

### 2026-02-21 (Sesión Actual)
- ✅ Google OAuth funcionando (autoalojado)
- ✅ Nueva Landing Page profesional estilo Emergent
- ✅ Sistema Multi-Agente base (6 agentes + orchestrator)
- ✅ API REST para multi-agente
- ✅ Login page actualizada con OAuth buttons
- ✅ Página de login con Google y GitHub

### 2026-02-20
- ✅ Monaco Editor con syntax highlighting
- ✅ Regeneración de archivos individuales
- ✅ Sistema de aprendizaje continuo
- ✅ WebSocket streaming

---

## Testing

### Credenciales
- Email: `demo@melusai.com` / `demo123`
- Preview URL: https://melus-dev-studio.preview.emergentagent.com

### Endpoints de prueba
- Health: `/api/health`
- Auth status: `/api/auth/status`
- Agents: `/api/agents-v3/status`

---

## Notas Importantes

1. **Google OAuth**: Requiere que el usuario añada la URI de callback en Google Cloud Console
2. **Multi-Agente**: Sistema base implementado, falta integrar LLM real
3. **Sin Facebook**: Usuario decidió no implementar Facebook OAuth
