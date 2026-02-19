# Melus AI - Product Requirements Document

> **Última actualización:** Diciembre 2025
> **Versión:** 3.2.0 - MARKETPLACE & EXPERT AGENTS

---

## 1. Visión del Producto

**Melus AI** es un **Constructor Universal de Aplicaciones** que funciona **idénticamente a Emergent.sh**, proporcionando una plataforma de desarrollo autónoma que genera aplicaciones full-stack completas usando un sistema de **13 agentes especializados** de IA + **8 Expert Agents** para tipos específicos de proyectos.

### Características Principales
- **HomePage Completa**: Interfaz principal con todos los controles funcionales
- **Marketplace Estilo Vercel**: 8 agentes especializados con categorías
- **Expert Agents**: Agentes especializados por tipo de proyecto
- **GitHub Deploy**: Push directo de proyectos a GitHub
- **13 Agentes Core**: Cada uno con rol específico
- **Preview en Vivo**: CodeSandbox Sandpack integrado
- **Sistema de Versionado**: Snapshots y rollback

---

## 2. Estado Actual - Actualizado Diciembre 2025

### ✅ Completado en esta sesión

#### Tareas A, B, C (Todas completadas)

**A) GitHub Deploy:**
- [x] Endpoint `/api/github/push-workspace` funcional
- [x] Push de archivos a repositorio GitHub
- [x] UI de deploy en WorkspacePage

**B) Marketplace Estilo Vercel:**
- [x] Nueva UI en `/marketplace` con 8 agentes especializados
- [x] Categorías: Todos, Desarrollo, IA & ML, Backend, Diseño, Seguridad
- [x] Tabs: "Agentes Especializados" y "Templates de la Comunidad"
- [x] Botón "Usar" navega a /home con agente seleccionado
- [x] Publicar Templates desde workspaces

**C) Expert Agents:**
- [x] 8 agentes especializados con prompts optimizados
- [x] Endpoint `/api/agents/v2/expert-agents` lista todos
- [x] Endpoint `/api/agents/v2/generate-expert` genera proyectos

#### Sesión Anterior
- [x] **HomePage Funcional Completa** (todos los controles)
- [x] **Ruta /generator OCULTA**
- [x] **Backend voice/transcribe** - Soporta FormData y JSON
- [x] **data-testid agregados**

### Testing Completado
- **Iteration 5:** HomePage 100% (11/11 features)
- **Iteration 6:** A/B/C features 100% (15/15 backend + UI tests)
- **Bug corregido:** LlmChat constructor en generate-expert

---

## 3. Expert Agents (8 Agentes Especializados)

| Agente | Costo | Categoría | Capacidades |
|--------|-------|-----------|-------------|
| Game Developer | 200 | Desarrollo | Canvas, Física, Animaciones |
| Mobile App | 250 | Desarrollo | PWA, Responsive, Touch, Offline |
| E-commerce | 300 | Desarrollo | Carrito, Productos, Checkout |
| Dashboard Admin | 250 | Desarrollo | Gráficos, Tablas, Analytics |
| SaaS App | 350 | Desarrollo | Auth, Suscripciones, API |
| AI Application | 300 | IA & ML | Chat LLM, Embeddings, Prompts |
| Portfolio Creator | 150 | Desarrollo | Animaciones, Galería, Contacto |
| API Builder | 200 | Backend | REST, GraphQL, Swagger |

---

## 4. Sistema de 13 Agentes Core

### 4.1 Agentes Core (Generación)
| Agente | Costo | Función |
|--------|-------|---------|
| Classifier | 25 | Clasifica tipo de aplicación |
| Architect | 50 | Diseña estructura y arquitectura |
| Frontend | 150 | Genera código React completo |
| Backend | 150 | Genera APIs y servidor |
| Integrator | 75 | Conecta frontend con backend |

### 4.2 Agentes Especializados
| Agente | Costo | Función |
|--------|-------|---------|
| Design | 100 | UI/UX y sistema de diseño |
| Database | 100 | Esquemas y queries |
| Testing | 75 | Tests automatizados |
| Security | 50 | Análisis de vulnerabilidades |
| Deploy | 50 | Configuración de despliegue |

### 4.3 Agentes de Utilidad
| Agente | Costo | Función |
|--------|-------|---------|
| Debugger | 30 | Corrección de errores (monetización) |
| Optimizer | 50 | Optimización de rendimiento |
| Docs | 25 | Generación de documentación |

---

## 4. Plantilla de Proyecto (Modo Motor)

```
Proyecto: [Nombre]
Objetivo: [Descripción]

# FRONTEND AGENT
- Framework: React con TailwindCSS
- Componentes: [Lista]
- Páginas: [Lista]

# BACKEND AGENT
- Framework: FastAPI
- Endpoints: [Lista]
- Autenticación: JWT

# DATABASE AGENT
- Motor: MongoDB
- Tablas: [Lista]

# INTEGRATION AGENT
- Servicios: Stripe, OAuth

# TESTING AGENT
- Unit tests
- Integration tests

# SECURITY AGENT
- Validación de inputs
- Protección de endpoints

# DEPLOYMENT AGENT
- Plataforma: Vercel/Docker
- CI/CD: GitHub Actions
```

---

## 5. Funcionalidades Implementadas

### ✅ Completado
- [x] Sistema de 13 agentes especializados
- [x] **MODO MOTOR (No Chat)** - Ejecución directa
- [x] Plantilla de proyecto estructurada
- [x] Preview en vivo con Sandpack - **FUNCIONANDO**
- [x] 12 templates predefinidos
- [x] Ultra Mode (2x créditos)
- [x] Debug Agent (30 créditos)
- [x] Sistema de versionado/rollback - **FUNCIONAL**
- [x] Descarga ZIP
- [x] GitHub OAuth completo
- [x] GitHub push desde workspace (50 créditos)
- [x] Panel de administración
- [x] **Nueva UI HomePage** - Interfaz simplificada estilo Emergent.sh
- [x] **Nueva UI WorkspacePage** - Clon exacto de interfaz Emergent.sh
- [x] Botones de sugerencia funcionando
- [x] Navegación HomePage → WorkspacePage con prompt
- [x] Sistema de créditos ILIMITADO para Owner
- [x] **Fix: Generación de código con saltos de línea correctos**
- [x] **Fix: Dependencias base (lucide-react, prop-types)**
- [x] **Fix: Prompt mejorado para evitar imports CSS externos**
- [x] **Backend Asíncrono** - Generación con BackgroundTasks + polling
- [x] **GitHub Deploy Modal** - UI completa para subir a GitHub
- [x] **Vercel Deploy** - Preparación de proyecto para Vercel con ZIP
- [x] **Sistema de Rollback UI** - Modal con historial de versiones
- [x] **Documentación GitHub** - Instrucciones de configuración OAuth
- [x] **Marketplace de Templates** - Publicar, buscar, descargar templates
- [x] **Expert Agents** - 8 agentes especializados (Game, Mobile, E-commerce, etc.)
- [x] **Docker Sandbox Service** - Estructura para ejecución aislada

### Backlog (Opcional)
- [ ] Integración directa con Vercel API
- [ ] Autenticación social (Google, GitHub)
- [ ] Soporte para Vue/Angular/Svelte

---

## 6. API Endpoints

### Motor No Chat
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/agents/v2/template` | Obtener formato de plantilla |
| POST | `/api/agents/v2/execute-project` | Ejecutar proyecto completo |

### Agentes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/agents/v2/costs` | Costos y modos |
| GET | `/api/agents/v2/agents` | Lista de 13 agentes |
| POST | `/api/agents/v2/run-agent` | Ejecutar agente individual |
| POST | `/api/agents/v2/generate` | Generar (modo chat) |
| POST | `/api/agents/v2/debug` | Debug Agent (30 créditos) |

---

## 7. Arquitectura Técnica

### Backend (FastAPI)
```
/app/backend/
├── routes/
│   └── agents_v2.py    # 13 agentes + Motor
├── services/
│   └── execution_engine.py  # Parser de plantillas
└── templates/
```

### Frontend (React)
```
/app/frontend/src/components/
└── AppGeneratorV2.jsx  # UI con modo Motor
```

---

## 8. Credenciales de Prueba

| Tipo | Email | Password |
|------|-------|----------|
| Admin | rrhh.milchollos@gmail.com | 19862210Des |

---

## 9. URLs

- **Frontend:** https://melus-homepage-fix.preview.emergentagent.com
- **HomePage:** https://melus-homepage-fix.preview.emergentagent.com/home
- **Workspace:** https://melus-homepage-fix.preview.emergentagent.com/workspace
- **API:** https://melus-homepage-fix.preview.emergentagent.com/api

> **NOTA:** La ruta /generator ha sido OCULTA por solicitud del usuario.

---

## 10. Próximas Tareas

### P1 - Pendientes
- [ ] **Implementar lógica completa de GitHub Deploy** - UI existe, falta lógica backend
- [ ] **Expert Agents backend logic** - Scaffolding existe

### P2 - Futuro
- [ ] Deploy funcional a Vercel (actualmente descarga ZIP)
- [ ] Ejecución sandboxed con Docker
- [ ] Backend del Marketplace de templates
- [ ] Sistema de versionado para Rollback

---

## 11. Comparación con Emergent.sh

| Característica | Emergent.sh | Melus AI |
|---------------|-------------|----------|
| Multi-agentes | ✅ | ✅ 13 agentes |
| Modo No Chat | ✅ | ✅ Motor |
| Preview en vivo | ✅ | ✅ Sandpack |
| Tests automáticos | ✅ | ✅ Testing Agent |
| Deploy automático | ✅ | ⏳ Próximamente |
| GitHub export | ✅ | ✅ |
| Sistema de créditos | ✅ | ✅ |
| Debug/Fixer | ✅ | ✅ 30 créditos |
