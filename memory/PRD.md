# Melus AI - Product Requirements Document

## Descripción
**Melus AI** es un motor de generación de aplicaciones completas similar a Emergent.sh. Genera automáticamente:
- Páginas web (full-stack)
- Juegos 2D (Phaser.js) y 3D (Three.js)
- Landing pages y portfolios
- Aplicaciones móviles

**Idioma del usuario**: Español

---

## ✅ SISTEMA COMPLETO IMPLEMENTADO

### Pipeline de 5 Fases
1. **Planning** - Analiza requisitos, detecta tipo de proyecto, define estructura
2. **Generation** - Genera código completo con GPT-4o
3. **Execution** - Configura proyecto, crea package.json/requirements.txt
4. **Validation** - Valida código, detecta errores
5. **Completed** - Proyecto listo para preview/download

### Sistema de Aprendizaje Continuo ✅
Implementado en `/app/backend/learning/`:

1. **Vector Memory Store** (`vector_memory.py`)
   - Almacena embeddings de prompts, código, errores y soluciones
   - Búsqueda semántica para contexto relevante
   - Soporta OpenAI embeddings (text-embedding-3-small) o fallback hash-based
   - Puntuación de calidad por entrada

2. **Feedback System** (`feedback_system.py`)
   - Rating explícito de usuarios (1-5 estrellas)
   - Feedback implícito (descargas, previews, iteraciones)
   - Scoring automático de proyectos

3. **Prompt Optimizer** (`prompt_optimizer.py`)
   - Tracking de versiones de prompts
   - Análisis de rendimiento
   - Sugerencias de mejora automáticas

4. **Metrics Tracker** (`metrics_tracker.py`)
   - Tiempo de generación
   - Archivos generados
   - Tasa de errores
   - Puntuación de validación

5. **Learning Engine** (`learning_engine.py`)
   - Coordina todos los subsistemas
   - Aprende de generaciones exitosas
   - Proporciona contexto mejorado

### WebSocket Streaming ✅
Implementado en `/app/backend/websocket_manager.py`:
- Streaming en tiempo real de logs del pipeline
- Notificaciones de creación de archivos
- Actualizaciones de fase en vivo
- Conexión: `ws://host/api/ws/projects/{project_id}`

### WorkspacePage Integrado ✅
- Carga proyectos del pipeline
- Conecta a WebSocket para logs en tiempo real
- Sistema de rating integrado
- Editor de código con preview
- Terminal para ver logs

### API de Aprendizaje
```
POST /api/learning/initialize - Inicializar sistema
GET  /api/learning/stats - Estadísticas completas
POST /api/learning/feedback/rating - Enviar rating
GET  /api/learning/context/enhanced - Contexto mejorado
POST /api/learning/optimize/run - Ejecutar optimización
GET  /api/learning/settings - Configuración
PUT  /api/learning/settings - Actualizar configuración
GET  /api/learning/metrics/* - Métricas detalladas
GET  /api/learning/prompts/* - Rendimiento de prompts
```

### Frontend
- **HomePage** - Chat de control + progreso visual + botón Learning System
- **LearningDashboard** (`/learning`) - Visualiza métricas, memoria, feedback
- **WorkspacePage** (`/workspace`) - IDE completo con preview, código y terminal
- **ProjectRating** - Componente de rating por estrellas

---

## Arquitectura

```
/app
├── backend/
│   ├── server.py                    # FastAPI con WebSocket
│   ├── pipeline_engine.py           # Motor de 5 fases + streaming
│   ├── websocket_manager.py         # NUEVO: WebSocket streaming
│   ├── code_generator.py            # Generador de proyectos
│   ├── learning/                    # Sistema de aprendizaje
│   │   ├── __init__.py
│   │   ├── vector_memory.py         # Memoria vectorial + OpenAI embeddings
│   │   ├── feedback_system.py       # Sistema de feedback
│   │   ├── prompt_optimizer.py      # Optimización de prompts
│   │   ├── metrics_tracker.py       # Tracking de métricas
│   │   └── learning_engine.py       # Motor principal
│   ├── routes/
│   │   ├── pipeline_api.py          # API del pipeline
│   │   ├── learning_api.py          # API de aprendizaje
│   │   └── ...
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── HomePage.jsx         # Chat de control + progreso
│       │   ├── LearningDashboard.jsx # Dashboard de aprendizaje
│       │   └── WorkspacePage.jsx    # IDE con WebSocket + rating
│       └── components/
│           └── ProjectRating.jsx    # Componente de rating
├── generated_projects/              # Proyectos generados
└── memory/PRD.md
```

---

## Stack Tecnológico

- **Frontend**: React, TailwindCSS, shadcn/ui, WebSocket client
- **Backend**: FastAPI, Pydantic, BackgroundTasks, WebSocket
- **LLM**: OpenAI GPT-4o via Emergent Integrations
- **Embeddings**: OpenAI text-embedding-3-small (opcional)
- **Database**: MongoDB Atlas
- **Storage**: Disco local + ZIP

---

## Próximas Mejoras

### P1 - Alta
1. Editor de código funcional completo en WorkspacePage
2. Regenerar archivos individuales
3. Mejorar parseo de código LLM

### P2 - Media
4. Export a GitHub
5. Deploy automático
6. Templates predefinidos

---

## Notas de Testing
- Usuario: test@test.com / Test123!
- Los proyectos se asocian al user_id del session_token
- Preview disponible en `/api/pipeline/preview/{project_id}`
- Learning Dashboard en `/learning`
- WebSocket en `ws://host/api/ws/projects/{project_id}`

---

## Changelog

### 2026-02-20 (Sesión 2)
- ✅ Integrado OpenAI embeddings (text-embedding-3-small) en Vector Memory
- ✅ Implementado WebSocket streaming para logs en tiempo real
- ✅ Integrado WorkspacePage con pipeline y WebSocket
- ✅ Añadido sistema de rating en WorkspacePage
- ✅ Añadido botón "Learning System" en HomePage
- ✅ Stream de notificaciones de archivos creados

### 2026-02-20 (Sesión 1)
- ✅ Implementado Sistema de Aprendizaje Continuo completo
- ✅ Creado Vector Memory Store para embeddings
- ✅ Creado Feedback System con ratings y métricas implícitas
- ✅ Creado Prompt Optimizer para mejora automática
- ✅ Creado Metrics Tracker para seguimiento de rendimiento
- ✅ Creado Learning Engine como coordinador
- ✅ Creada API REST completa para Learning System
- ✅ Creado Learning Dashboard en frontend
