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

### Sistema de Aprendizaje Continuo (NUEVO)
Implementado en `/app/backend/learning/`:

1. **Vector Memory Store** (`vector_memory.py`)
   - Almacena embeddings de prompts, código, errores y soluciones
   - Búsqueda semántica para contexto relevante
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

### Frontend Learning Dashboard
- Ruta: `/learning`
- Tabs: Overview, Memory, Metrics, Settings
- Visualización de métricas
- Configuración de aprendizaje automático

### Interfaz de Chat como Control de Proyectos
- El chat interpreta órdenes de proyecto (no conversación)
- `Usuario → Orden → Sistema ejecuta → Usuario ajusta`
- Barra de progreso visual de las 5 fases
- Toast notifications de estado

### Backend API Pipeline
```
POST /api/pipeline/projects - Crear proyecto
GET  /api/pipeline/projects - Listar proyectos del usuario
GET  /api/pipeline/projects/{id} - Detalles del proyecto
GET  /api/pipeline/projects/{id}/status - Estado (para polling)
POST /api/pipeline/projects/{id}/iterate - Modificación incremental
POST /api/pipeline/projects/{id}/chat - Chat de control
GET  /api/pipeline/projects/{id}/files - Listar archivos
GET  /api/pipeline/projects/{id}/download - Descargar ZIP
GET  /api/pipeline/preview/{id} - Preview HTML
POST /api/pipeline/projects/{id}/regenerate - Regenerar proyecto
```

### Persistencia
- MongoDB para proyectos, usuarios, estado, learning data
- Archivos en disco: `/app/generated_projects/`
- ZIP on-demand para descarga

---

## Arquitectura

```
/app
├── backend/
│   ├── server.py                    # FastAPI principal
│   ├── pipeline_engine.py           # Motor de 5 fases con LLM + Learning
│   ├── code_generator.py            # Generador de proyectos
│   ├── learning/                    # NUEVO: Sistema de aprendizaje
│   │   ├── __init__.py
│   │   ├── vector_memory.py         # Memoria vectorial
│   │   ├── feedback_system.py       # Sistema de feedback
│   │   ├── prompt_optimizer.py      # Optimización de prompts
│   │   ├── metrics_tracker.py       # Tracking de métricas
│   │   └── learning_engine.py       # Motor principal
│   ├── routes/
│   │   ├── pipeline_api.py          # API del pipeline
│   │   ├── learning_api.py          # NUEVO: API de aprendizaje
│   │   └── ...
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── HomePage.jsx         # Chat de control + progreso visual
│       │   ├── LearningDashboard.jsx # NUEVO: Dashboard de aprendizaje
│       │   └── WorkspacePage.jsx    # IDE con preview
│       └── components/
│           └── ProjectRating.jsx    # NUEVO: Componente de rating
├── generated_projects/              # Proyectos generados
└── memory/PRD.md
```

---

## Stack Tecnológico

- **Frontend**: React, TailwindCSS, shadcn/ui
- **Backend**: FastAPI, Pydantic, BackgroundTasks
- **LLM**: OpenAI GPT-4o via Emergent Integrations
- **Database**: MongoDB Atlas
- **Storage**: Disco local + ZIP

---

## Próximas Mejoras

### P0 - Crítico
1. ~~Sistema de Aprendizaje Continuo~~ ✅ COMPLETADO
2. Integrar embeddings reales de OpenAI para mejor búsqueda semántica

### P1 - Alta
3. Streaming de progreso vía WebSocket
4. Editor de código funcional en WorkspacePage
5. Regenerar archivos individuales

### P2 - Media
6. Export a GitHub
7. Deploy automático
8. Templates predefinidos

---

## Notas de Testing
- Usuario: test@test.com / Test123!
- Los proyectos se asocian al user_id del session_token
- Preview disponible en `/api/pipeline/preview/{project_id}`
- Learning Dashboard en `/learning`

---

## Changelog

### 2026-02-20
- ✅ Implementado Sistema de Aprendizaje Continuo completo
- ✅ Creado Vector Memory Store para embeddings
- ✅ Creado Feedback System con ratings y métricas implícitas
- ✅ Creado Prompt Optimizer para mejora automática
- ✅ Creado Metrics Tracker para seguimiento de rendimiento
- ✅ Creado Learning Engine como coordinador
- ✅ Creada API REST completa para Learning System
- ✅ Creado Learning Dashboard en frontend
- ✅ Integrado aprendizaje con pipeline de generación
- ✅ Añadido botón Learning System en HomePage
