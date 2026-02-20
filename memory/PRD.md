# Melus AI - Product Requirements Document

## Original Problem Statement
Build **Melus AI** - un motor de generación de aplicaciones completas como Emergent.sh. La plataforma genera automáticamente:
- Páginas web completas (full-stack)
- Juegos 2D (Phaser.js, PixiJS)
- Juegos 3D (Three.js, Babylon.js)
- Aplicaciones móviles
- Landing pages y sitios marketing

**Idioma del usuario**: Español

---

## ✅ FUNCIONALIDADES COMPLETADAS

### Motor de Generación de Código
- [x] **10 Agentes AI especializados** con GPT-4o via Emergent LLM Key
- [x] **Generación automática de aplicaciones completas** en un solo paso
- [x] **Detección automática del tipo de proyecto** (web_app, game_2d, game_3d, mobile_app, landing_page)
- [x] **Persistencia en MongoDB** - Los proyectos no se pierden
- [x] **Guardado de archivos en disco** - Proyectos en `/app/generated_projects/`

### Interfaz del Orquestador
- [x] Dashboard con estadísticas (Objectives, Tasks, Agents, Cost)
- [x] Pestañas: Overview, Objectives, Tasks, Agents, Activity
- [x] Badges de tipo de proyecto (game 2d, landing page, etc.)
- [x] **Botón "Generate"** - Inicia la generación del proyecto
- [x] **Indicador "Generating..."** - Muestra progreso en tiempo real
- [x] **Botón "Preview"** - Vista previa del proyecto generado en iframe
- [x] **Botón "Download"** - Descarga el proyecto como ZIP
- [x] **Modal de archivos** - Ver todos los archivos generados
- [x] **Visor de código** - Ver contenido con sintaxis highlighting

### Backend API Completo
- `POST /api/orchestrator/objectives` - Crear proyecto
- `POST /api/orchestrator/objectives/{id}/start` - Generar aplicación
- `GET /api/orchestrator/objectives/{id}/files` - Listar archivos
- `GET /api/orchestrator/objectives/{id}/download` - Descargar ZIP
- `GET /api/orchestrator/preview/{id}` - Preview en iframe
- `GET /api/orchestrator/preview/{id}/{path}` - Servir archivos estáticos

---

## 🧪 PROYECTOS GENERADOS (Probados)

1. **SaaS Landing Page "CloudSync"** ✅
   - index.html (5KB)
   - styles.css (2.5KB)  
   - script.js (1.5KB)
   - Hero, Features, Pricing, Testimonials, FAQ, Footer

2. **Space Shooter 2D Game** (en progreso)
   - Phaser.js
   - Player/Enemy system

---

## Arquitectura Actual

```
/app
├── backend/
│   ├── server.py                    # FastAPI principal
│   ├── code_generator.py            # Motor de generación de proyectos
│   ├── orchestrator_models.py       # Modelos Pydantic
│   └── routes/
│       └── orchestrator_api.py      # API del orquestador con LLM
├── frontend/
│   └── src/pages/
│       └── OrchestratorPage.jsx     # Dashboard completo
├── generated_projects/              # Proyectos generados
│   └── saas_landing_page_obj_3b0c/  # Ejemplo generado
│       ├── index.html
│       ├── styles.css
│       └── script.js
└── memory/
    └── PRD.md
```

---

## Próximas Mejoras (Backlog)

### P0 - Crítico
1. Mejorar calidad del código generado (más contexto, mejor parsing)
2. Streaming de progreso durante generación

### P1 - Alta Prioridad  
3. Editor de código inline
4. Regenerar archivos individuales
5. Múltiples iteraciones de mejora

### P2 - Media Prioridad
6. Exportar a GitHub
7. Templates predefinidos
8. Historial de versiones

### P3 - Futuro
9. Colaboración en tiempo real
10. Deploy automático

---

## Notas Técnicas
- **LLM**: OpenAI GPT-4o via Emergent Integrations
- **Database**: MongoDB Atlas
- **Storage**: Archivos en disco local
- **Preview**: Served via FastAPI FileResponse
- **Download**: ZIP creado on-demand
