# Melus AI - Product Requirements Document

## Descripción
**Melus AI** es un motor de generación de aplicaciones completas similar a Emergent.sh.

**Idioma del usuario**: Español

---

## ✅ SISTEMA COMPLETO IMPLEMENTADO

### Pipeline de 5 Fases
1. **Planning** - Analiza requisitos, detecta tipo de proyecto
2. **Generation** - Genera código completo con GPT-4o
3. **Execution** - Configura proyecto
4. **Validation** - Valida código
5. **Completed** - Proyecto listo

### Sistema de Aprendizaje Continuo ✅
- Vector Memory Store con OpenAI embeddings (o fallback)
- Feedback System (ratings, descargas, etc.)
- Prompt Optimizer
- Metrics Tracker
- Learning Engine

### WebSocket Streaming ✅
- Logs en tiempo real
- Notificaciones de archivos creados
- Endpoint: `ws://host/api/ws/projects/{project_id}`

### Editor Monaco con Syntax Highlighting ✅ (NUEVO)
- Monaco Editor (VS Code engine)
- Soporte para 20+ lenguajes
- Tema oscuro personalizado
- Autocompletado
- Bracket matching
- Minimap

### Regeneración de Archivos Individuales ✅ (NUEVO)
- Click derecho o botón de varita mágica
- Modal con instrucciones opcionales
- Endpoint: `POST /api/pipeline/projects/{id}/regenerate-file`
- Regenera con GPT-4o manteniendo contexto

### Parseo de Código LLM Mejorado ✅ (NUEVO)
- 6 métodos de fallback para extraer JSON
- Manejo de markdown code blocks
- Fix automático de errores comunes
- Extracción manual de arrays de archivos

### WorkspacePage Integrado ✅
- Monaco Editor
- WebSocket para logs
- Rating de proyectos
- Regeneración de archivos

---

## Arquitectura

```
/app
├── backend/
│   ├── server.py
│   ├── pipeline_engine.py        # Parseo mejorado
│   ├── websocket_manager.py
│   ├── learning/
│   ├── routes/
│   │   ├── pipeline_api.py       # +regenerate-file endpoint
│   │   └── learning_api.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── MonacoCodeEditor.jsx  # NUEVO
│       │   └── ProjectRating.jsx
│       └── pages/
│           ├── HomePage.jsx
│           ├── LearningDashboard.jsx
│           └── WorkspacePage.jsx    # +Monaco +Regenerate
└── memory/PRD.md
```

---

## Stack Tecnológico

- **Frontend**: React, TailwindCSS, Monaco Editor, shadcn/ui
- **Backend**: FastAPI, WebSocket
- **LLM**: OpenAI GPT-4o via Emergent
- **Database**: MongoDB

---

## Completado

### Sesión Actual
- ✅ Monaco Editor con syntax highlighting
- ✅ Regeneración de archivos individuales
- ✅ Parseo de código LLM mejorado (6 métodos)
- ✅ Context menu en file explorer
- ✅ Modal de regeneración con instrucciones

### Sesiones Anteriores
- ✅ Sistema de Aprendizaje Continuo
- ✅ WebSocket streaming
- ✅ Pipeline de 5 fases
- ✅ Learning Dashboard

---

## Próximas Mejoras (P2)
- Export a GitHub
- Deploy automático
- Templates predefinidos

---

## Testing
- Usuario: test@test.com / Test123!
- Preview: `/api/pipeline/preview/{project_id}`
- Learning: `/learning`
- Workspace: `/workspace?project={id}`

---

## Changelog

### 2026-02-21
- ✅ Implementado Monaco Editor con syntax highlighting
- ✅ Implementada regeneración de archivos individuales
- ✅ Mejorado parseo de código LLM con 6 métodos de fallback
- ✅ Añadido context menu en file explorer
- ✅ Añadido modal de regeneración con instrucciones
- ✅ Configurada API key de OpenAI para embeddings (pendiente billing)
