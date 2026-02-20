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

### Interfaz de Chat como Control de Proyectos
- El chat interpreta órdenes de proyecto (no conversación)
- `Usuario → Orden → Sistema ejecuta → Usuario ajusta`
- Barra de progreso visual de las 5 fases
- Toast notifications de estado

### Iteración Incremental
- Endpoint `/api/pipeline/projects/{id}/chat` para modificaciones
- Solo modifica archivos necesarios (no regenera todo)
- Detecta comandos: add, fix, change, modify

### Backend API
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
- MongoDB para proyectos, usuarios, estado
- Archivos en disco: `/app/generated_projects/`
- ZIP on-demand para descarga

### WorkspacePage
- Carga proyectos del pipeline
- Preview en iframe
- Chat para iteraciones
- Editor de código (en progreso)

---

## Arquitectura

```
/app
├── backend/
│   ├── server.py                    # FastAPI principal
│   ├── pipeline_engine.py           # Motor de 5 fases con LLM
│   ├── code_generator.py            # Generador de proyectos
│   ├── routes/
│   │   ├── pipeline_api.py          # API del pipeline
│   │   ├── orchestrator_api.py      # API del orquestador
│   │   └── ...
├── frontend/
│   └── src/pages/
│       ├── HomePage.jsx             # Chat de control + progreso visual
│       ├── WorkspacePage.jsx        # IDE con preview
│       ├── OrchestratorPage.jsx     # Dashboard de agentes
│       └── ...
├── generated_projects/              # Proyectos generados
└── memory/PRD.md
```

---

## Proyectos Generados (Probados)

1. **Todo App** - React con local storage (9 archivos)
2. **SaaS Landing Page** - CloudSync (3 archivos)
3. **Calculator** - Glass effect design (13 archivos)
4. **Weather App** - Con API simulada (7 archivos)
5. **Counter App** - Simple + y - (en proceso)

---

## Stack Tecnológico

- **Frontend**: React, TailwindCSS, shadcn/ui
- **Backend**: FastAPI, Motor (MongoDB async)
- **LLM**: OpenAI GPT-4o via Emergent Integrations
- **Database**: MongoDB Atlas
- **Storage**: Disco local + ZIP

---

## Próximas Mejoras

### P0 - Crítico
1. Mejorar parseo de código generado por LLM
2. Streaming de progreso vía WebSocket

### P1 - Alta
3. Editor de código funcional en WorkspacePage
4. Regenerar archivos individuales
5. Corrección automática más robusta

### P2 - Media
6. Export a GitHub
7. Deploy automático
8. Templates predefinidos

---

## Notas de Testing
- Usuario: test@test.com / Test123!
- Los proyectos se asocian al user_id del session_token
- Preview disponible en `/api/pipeline/preview/{project_id}`
