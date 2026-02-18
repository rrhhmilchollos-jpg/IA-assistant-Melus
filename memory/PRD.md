# Melus AI - Product Requirements Document

> **Última actualización:** Diciembre 2025
> **Versión:** 2.2.0

---

## 1. Visión del Producto

**Melus AI** es un **Constructor Universal de Aplicaciones**, una plataforma de desarrollo autónoma que genera aplicaciones full-stack completas usando un sistema de **13 agentes especializados** de IA con preview en vivo.

### Objetivo
Competir directamente con Emergent.sh proporcionando una infraestructura autónoma de construcción y ejecución de software.

---

## 2. Usuarios Objetivo

- **Desarrolladores** que necesitan prototipar rápidamente
- **Emprendedores** sin conocimientos técnicos
- **Empresas** que buscan acelerar el desarrollo
- **Estudiantes** aprendiendo desarrollo web

---

## 3. Sistema de 13 Agentes Especializados

### 3.1 Agentes de Generación (Core)
| Agente | Costo | Descripción |
|--------|-------|-------------|
| **Classifier** | 25 | Analiza y clasifica el tipo de aplicación |
| **Architect** | 50 | Diseña estructura y arquitectura |
| **Frontend** | 150 | Genera código React completo |
| **Backend** | 150 | Genera APIs y lógica de servidor |
| **Integrator** | 75 | Conecta frontend con backend |

### 3.2 Agentes Especializados
| Agente | Costo | Descripción |
|--------|-------|-------------|
| **Design** | 100 | Define UI/UX y sistema de diseño |
| **Database** | 100 | Diseña esquemas y queries |
| **Testing** | 75 | Genera tests automatizados |
| **Security** | 50 | Analiza vulnerabilidades |
| **Deploy** | 50 | Genera configs de despliegue |

### 3.3 Agentes de Utilidad
| Agente | Costo | Descripción |
|--------|-------|-------------|
| **Debugger** | 30 | Corrige errores automáticamente (monetización) |
| **Optimizer** | 50 | Optimiza rendimiento |
| **Docs** | 25 | Genera documentación |

**Total por generación completa: ~930 créditos (Normal) / ~1860 créditos (Ultra)**

---

## 4. Funcionalidades Principales

### 4.1 Preview en Vivo con Sandpack ✅
- CodeSandbox Sandpack integrado
- Hot reload en tiempo real
- Explorador de archivos visual
- Editor de código con syntax highlighting

### 4.2 Sistema de Workspaces ✅
- Filesystem virtual por proyecto
- Sistema de Versionado/Snapshots
- Rollback a versiones anteriores
- WebSocket para logs en tiempo real

### 4.3 12 Templates Predefinidos ✅
| Template | Créditos | Descripción |
|----------|----------|-------------|
| E-Commerce Store | 450 | Tienda con catálogo, carrito, checkout |
| Blog Platform | 350 | Blog con artículos, categorías |
| Admin Dashboard | 500 | Panel con métricas y gráficos |
| Landing Page | 300 | Landing SaaS con hero y pricing |
| Task Manager | 400 | Gestión de tareas estilo Trello |
| Portfolio | 300 | Portfolio de desarrollador |
| CRM System | 550 | Pipeline de ventas y contactos |
| Chat Application | 450 | Mensajería en tiempo real |
| Social Network | 500 | Feed, perfiles, likes |
| Inventory System | 450 | Productos, stock, alertas |
| Booking System | 500 | Calendario y citas |
| Analytics Dashboard | 450 | Gráficos y reportes |

### 4.4 Ultra Mode ✅
- Toggle en UI para activar/desactivar
- **2x créditos = Máxima calidad**
- Prompts mejorados con mejores prácticas
- Error handling completo
- Accesibilidad incluida

### 4.5 Debug Agent (Fixer) ✅
- **Costo: 30 créditos por uso**
- Detecta errores automáticamente
- Analiza y corrige código
- Crea nueva versión después del fix

### 4.6 GitHub Integration ✅
- GitHub OAuth para login
- Push de workspace a GitHub (50 créditos)
- Crear repositorios nuevos
- Repositorios públicos o privados

### 4.7 Descarga ZIP ✅
- Exportar proyecto completo
- README generado automáticamente

---

## 5. Arquitectura Técnica

### 5.1 Backend (FastAPI)
```
/app/backend/
├── routes/
│   ├── agents_v2.py    # 13 agentes especializados
│   ├── workspace.py    # Workspaces y versionado
│   ├── github.py       # GitHub OAuth y push
│   ├── auth.py         # Autenticación
│   └── billing.py      # Créditos y pagos
├── templates/
│   └── app_templates.py
└── server.py
```

### 5.2 Frontend (React)
```
/app/frontend/src/
├── components/
│   ├── AppGeneratorV2.jsx  # Generador con 13 agentes
│   └── ui/                 # Shadcn components
├── pages/
└── context/
```

### 5.3 Base de Datos (MongoDB)
```javascript
// Users
{ user_id, email, credits, is_admin, github_token }

// Workspaces
{ workspace_id, user_id, files, versions[], current_version }

// GitHub Connections
{ user_id, github_token, github_username }
```

---

## 6. API Endpoints

### 6.1 Agentes v2
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/agents/v2/costs` | Costos de 13 agentes |
| GET | `/api/agents/v2/agents` | Lista de agentes |
| POST | `/api/agents/v2/run-agent` | Ejecutar agente individual |
| POST | `/api/agents/v2/generate` | Generar app completa |
| POST | `/api/agents/v2/generate-from-template` | Generar desde template |
| POST | `/api/agents/v2/debug` | Debug Agent (30 créditos) |
| GET | `/api/agents/v2/download/{id}` | Descargar ZIP |
| POST | `/api/agents/v2/push-to-github` | Push a GitHub (50 créditos) |

### 6.2 Workspaces
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/workspace/create` | Crear workspace |
| GET | `/api/workspace/{id}` | Obtener workspace |
| GET | `/api/workspace/{id}/versions` | Historial versiones |
| POST | `/api/workspace/{id}/rollback/{v}` | Rollback |
| WS | `/api/workspace/ws/{id}` | WebSocket logs |

### 6.3 GitHub
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/github/auth/login` | Iniciar OAuth |
| GET | `/api/github/auth/callback` | Callback OAuth |
| GET | `/api/github/status` | Estado conexión |
| GET | `/api/github/repos` | Listar repos |

---

## 7. Integraciones

- **OpenAI GPT-4o** - Via Emergent LLM Key
- **Stripe** - Sistema de pagos
- **GitHub** - OAuth y push
- **CodeSandbox Sandpack** - Preview en vivo

---

## 8. Estado del Proyecto

### Completado ✅
- [x] Sistema de 13 agentes especializados
- [x] Preview en vivo con Sandpack
- [x] 12 templates predefinidos
- [x] Ultra Mode (2x créditos)
- [x] Debug Agent (30 créditos)
- [x] Sistema de versionado/rollback
- [x] Descarga ZIP
- [x] GitHub OAuth completo
- [x] GitHub push desde workspace
- [x] Panel de administración

### Backlog (Próximas tareas)
- [ ] Deploy automático (Vercel/Netlify)
- [ ] Marketplace de templates
- [ ] Control Plane / Execution Plane separados
- [ ] Contenedores Docker aislados
- [ ] Multi-región y autoscaling

---

## 9. Credenciales de Prueba

| Tipo | Email | Password |
|------|-------|----------|
| Admin | rrhh.milchollos@gmail.com | 19862210Des |

---

## 10. URLs

- **Frontend:** https://agent-labs.preview.emergentagent.com
- **API:** https://agent-labs.preview.emergentagent.com/api
- **Generador:** https://agent-labs.preview.emergentagent.com/generator
