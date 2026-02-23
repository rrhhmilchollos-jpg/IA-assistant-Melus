# MelusAI - Product Requirements Document

## Arquitectura v3.0 - Brain Engine & Multi-Agent System

---

## Estado Actual: ✅ Fase 1 COMPLETADA

### ✅ Brain Engine
- `/app/core/brain_engine.py` - Motor central de orquestación
- `/app/core/intent_classifier.py` - Clasificador de intenciones (11 tipos)
- `/app/core/code_templates.py` - Templates pre-construidos (7 tipos)
- `/app/core/agent_system.py` - Sistema Multi-Agente (5 agentes)

### ✅ Sistema Multi-Agente Implementado
| Agente | Función | Estado |
|--------|---------|--------|
| 🏗 **Architect** | Define estructura, selecciona tecnologías | ✅ Activo |
| 💻 **Coder** | Genera código basado en templates | ✅ Activo |
| 🎨 **Designer** | Aplica estilos y personalización | ✅ Activo |
| 🔐 **Security** | Añade validaciones y seguridad | ✅ Activo |
| 🚀 **Deployer** | Prepara Docker y CI/CD | ✅ Activo |

### ✅ Clasificación de Intenciones (11 tipos)
- `web_app` - Aplicación web general
- `saas_app` - Plataforma SaaS
- `ecommerce` - Tienda online
- `dashboard` - Panel de control
- `landing_page` - Página de marketing
- `blog` - Sistema de contenido
- `portfolio` - Portafolio
- `api_service` - Servicio API
- `game2d` - Juegos 2D (Phaser.js)
- `game3d` - Juegos 3D (Three.js)
- `mobile_app` - App móvil

### ✅ Templates Pre-construidos
| Template | Tecnología | Archivos |
|----------|------------|----------|
| Todo/Tasks | React + TailwindCSS | App.jsx (4,959 chars) |
| E-commerce | React + TailwindCSS | App.jsx (7,934 chars) |
| Dashboard | React + TailwindCSS | App.jsx (6,800 chars) |
| Landing Page | React + TailwindCSS | App.jsx (5,500 chars) |
| SaaS App | React + TailwindCSS | App.jsx (7,200 chars) |
| Game 2D | Phaser.js | index.html + game.js (8,619 chars) |
| Game 3D | Three.js | index.html + game3d.js (10,923 chars) |

### ✅ API Endpoints Brain Engine
```
POST /api/brain/analyze     - Analiza intent sin generar
POST /api/brain/generate    - Genera proyecto completo
GET  /api/brain/project/{id}      - Estado del proyecto
GET  /api/brain/project/{id}/files - Archivos generados
GET  /api/brain/agents/status     - Estado multi-agente
GET  /api/brain/templates   - Lista templates
GET  /api/brain/intents     - Lista intents
WS   /api/brain/ws/{id}     - WebSocket tiempo real
```

---

## Estructura del Monorepo

```
/app/
├── api-gateway/           # ✅ Rutas del Brain Engine
│   ├── __init__.py
│   └── brain_routes.py
├── apps/                  # 🔄 Builders (estructura lista)
│   ├── web-builder/
│   ├── saas-builder/
│   ├── ecommerce-builder/
│   ├── game2d-builder/
│   └── game3d-builder/
├── core/                  # ✅ Motor central
│   ├── __init__.py
│   ├── brain_engine.py
│   ├── intent_classifier.py
│   ├── code_templates.py
│   └── agent_system.py    # ✅ NEW: 5 agentes
├── database/              # ✅ Schemas PostgreSQL
│   ├── __init__.py
│   ├── config.py
│   └── schemas/models.py
├── services/              # 🔄 Microservicios (pendiente)
├── backend/               # ✅ API FastAPI
└── frontend/              # ✅ React App
```

---

## Funcionalidades Existentes

### ✅ Autenticación
- Email/Password
- Google OAuth
- GitHub OAuth
- Sesiones JWT

### ✅ Billing
- Integración Stripe
- Planes: Free, Pro, Enterprise
- Checkout funcional

### ✅ UI
- Landing page profesional (español)
- AI Builder con chat
- Vista previa en vivo

---

## Backlog Priorizado

### P0 - COMPLETADO ✅
- [x] Brain Engine básico
- [x] Intent Classifier (11 tipos)
- [x] Sistema Multi-Agente (5 agentes)
- [x] Templates pre-construidos (7 templates)
- [x] Game templates (Phaser + Three.js)
- [x] API endpoints

### P1 - Alta Prioridad (Próximo)
- [ ] Migración PostgreSQL (ejecutar migrations)
- [ ] Sandbox Docker para ejecución segura
- [ ] Integración GPT-4o para personalización de templates
- [ ] Sistema de versioning de archivos

### P2 - Media Prioridad
- [ ] Migración frontend a Next.js
- [ ] Builders especializados completos
- [ ] Admin Dashboard
- [ ] Deploy automatizado

### P3 - Baja Prioridad
- [ ] Editor visual drag & drop
- [ ] Marketplace de templates
- [ ] Sistema de plugins
- [ ] Analytics avanzados

---

## Testing Verificado

### Backend API
- ✅ `/api/brain/analyze` - Clasificación correcta
- ✅ `/api/brain/generate` - Generación funcional
- ✅ `/api/brain/agents/status` - Multi-agente operativo
- ✅ Game 2D (Phaser.js) - 2 archivos generados
- ✅ Game 3D (Three.js) - 2 archivos generados

### Frontend
- ✅ Landing page visible
- ✅ Login/Auth funcionando
- ✅ AI Builder accesible

---

## Credenciales Test

- **Email**: demo@melusai.com
- **Password**: demo123
- **URL**: https://melus-ai-dev.preview.emergentagent.com

---

## Tecnologías

| Componente | Actual | Objetivo |
|------------|--------|----------|
| Frontend | React + TailwindCSS | Next.js |
| Backend | FastAPI | FastAPI + Microservicios |
| Database | MongoDB | PostgreSQL |
| Games 2D | Phaser.js | ✅ Implementado |
| Games 3D | Three.js | ✅ Implementado |
| LLM | GPT-4o | GPT-4o + Personalización |

---

## Changelog

### 2024-02-23 (Sesión Actual)
- ✅ Brain Engine v1.0 implementado
- ✅ Intent Classifier con 11 tipos de aplicación
- ✅ Sistema Multi-Agente con 5 agentes especializados
- ✅ Templates pre-construidos (7 tipos incluyendo games)
- ✅ Game 2D template (Phaser.js) - Juego de plataformas completo
- ✅ Game 3D template (Three.js) - Experiencia 3D interactiva
- ✅ API Gateway con nuevos endpoints
- ✅ Schemas PostgreSQL preparados

---

*Última actualización: 23 de Febrero, 2024*
