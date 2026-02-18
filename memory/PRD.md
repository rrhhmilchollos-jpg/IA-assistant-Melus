# Assistant Melus AI - Product Requirements Document

## Resumen
**Melus AI** es un Constructor Universal de Aplicaciones, un clon completo de Emergent.sh que genera aplicaciones full-stack usando un sistema multi-agente con preview en vivo.

## Problema que Resuelve
Proporcionar una plataforma donde los usuarios pueden describir aplicaciones en lenguaje natural y obtener código generado automáticamente por agentes especializados de IA, con preview en tiempo real y sistema de versionado.

## Usuarios Objetivo
- Desarrolladores que necesitan prototipar rápidamente
- Emprendedores sin conocimientos técnicos
- Empresas que buscan acelerar el desarrollo

---

## Funcionalidades Principales - TODAS EN PRODUCCIÓN

### 1. Sistema de Autenticación ✅
- Registro con email/password
- Login con email/password
- GitHub OAuth completo
- Gestión de sesiones con JWT
- Rol de administrador

### 2. Sistema de Créditos ✅
- Balance de créditos por usuario
- Consumo por acción de agente
- Historial de transacciones
- Integración con Stripe para compras
- Paquetes de créditos configurables

### 3. Arquitectura Multi-Agente v2 ✅
Sistema de 6 agentes especializados:

| Agente | Créditos Normal | Créditos Ultra |
|--------|----------------|----------------|
| Classifier | 25 | 50 |
| Architect | 50 | 100 |
| Frontend | 150 | 300 |
| Backend | 150 | 300 |
| Integrator | 75 | 150 |
| **Debug Agent** | **30** | 60 |

**Total generación: ~480 créditos (Normal) / ~960 créditos (Ultra)**

### 4. Preview en Vivo con Sandpack ✅
- CodeSandbox Sandpack integrado
- Hot reload en tiempo real
- Compilación de React en el navegador
- Explorador de archivos visual
- Editor de código con syntax highlighting

### 5. Sistema de Workspaces ✅
- Filesystem virtual por proyecto
- **Sistema de Versionado/Snapshots**
- **Rollback a versiones anteriores**
- WebSocket para actualizaciones en tiempo real
- Persistencia en MongoDB
- Recuperación automática al recargar

### 6. 12 Templates Predefinidos ✅
| Template | Descripción | Normal | Ultra |
|----------|-------------|--------|-------|
| E-Commerce Store | Tienda con catálogo, carrito, checkout | 450 | 900 |
| Blog Platform | Blog con artículos, categorías, comentarios | 350 | 700 |
| Admin Dashboard | Panel con métricas, gráficos, usuarios | 500 | 1000 |
| Landing Page | Landing SaaS con hero, features, pricing | 300 | 600 |
| Task Manager | Gestión de tareas estilo Trello | 400 | 800 |
| Portfolio | Portfolio de desarrollador con proyectos | 300 | 600 |
| CRM System | Pipeline de ventas, contactos, seguimiento | 550 | 1100 |
| Chat Application | Mensajería en tiempo real, conversaciones | 450 | 900 |
| Social Network | Feed, perfiles, likes, comentarios | 500 | 1000 |
| Inventory System | Productos, stock, categorías, alertas | 450 | 900 |
| Booking System | Calendario, citas, servicios, confirmaciones | 500 | 1000 |
| Analytics Dashboard | Gráficos, métricas, reportes en tiempo real | 450 | 900 |

### 7. Ultra Mode ✅
- Toggle en UI para activar/desactivar
- **2x créditos = Máxima calidad de código**
- Prompts mejorados con mejores prácticas
- Error handling completo
- Accesibilidad incluida
- Animaciones y loading states

### 8. Debug Agent (Fixer Agent) ✅
- **Costo: 30 créditos por uso** (monetización)
- Detecta errores de compilación automáticamente
- Analiza el código y corrige errores
- Aplica fixes y crea nueva versión
- Botón "Auto-fix" en la UI

### 9. Descarga ZIP ✅
- Exportar proyecto completo como archivo ZIP
- Incluye README generado automáticamente
- Estructura de carpetas correcta

### 10. Panel de Administración ✅
- Dashboard con métricas en tiempo real
- Gestión de usuarios
- Historial de transacciones
- Análisis de ingresos

---

## Arquitectura Técnica

### Backend (FastAPI)
```
/app/backend/
├── routes/
│   ├── agents_v2.py    # Sistema multi-agente v2
│   ├── workspace.py    # Workspaces y versionado
│   ├── auth.py         # Autenticación
│   ├── github.py       # GitHub OAuth
│   ├── billing.py      # Créditos y pagos
│   └── admin.py        # Panel admin
├── templates/
│   └── app_templates.py  # 12 templates
├── models.py
└── server.py
```

### Frontend (React)
```
/app/frontend/src/
├── components/
│   ├── AppGeneratorV2.jsx  # Generador principal
│   └── ui/                 # Shadcn components
├── pages/
│   ├── GeneratorPage.jsx
│   ├── Dashboard.jsx
│   └── AdminPanel.jsx
└── context/
    └── AuthContext.jsx
```

### Integraciones
- OpenAI GPT-4o (via Emergent LLM Key)
- Stripe Payments
- GitHub OAuth
- CodeSandbox Sandpack

---

## API Endpoints Principales

### Agentes v2
- `GET /api/agents/v2/costs` - Costos de agentes
- `GET /api/agents/v2/templates` - Lista de templates
- `POST /api/agents/v2/generate` - Generar app custom
- `POST /api/agents/v2/generate-from-template` - Generar desde template
- `POST /api/agents/v2/debug` - Debug Agent (30 créditos)
- `GET /api/agents/v2/download/{workspace_id}` - Descargar ZIP

### Workspaces
- `POST /api/workspace/create` - Crear workspace
- `GET /api/workspace/{id}` - Obtener workspace
- `GET /api/workspace/{id}/versions` - Historial de versiones
- `POST /api/workspace/{id}/rollback/{version}` - Rollback
- `WS /api/workspace/ws/{id}` - WebSocket para logs

---

## Credenciales de Prueba
- **Admin**: rrhh.milchollos@gmail.com / 19862210Des

## URLs
- Frontend: https://agent-labs.preview.emergentagent.com
- API: https://agent-labs.preview.emergentagent.com/api
- Generador: https://agent-labs.preview.emergentagent.com/generator

---

## Estado del Proyecto: Diciembre 2025

### Completado ✅
- [x] Sistema multi-agente v2 completo
- [x] Preview en vivo con Sandpack
- [x] 12 templates predefinidos
- [x] Ultra Mode (2x créditos)
- [x] Debug Agent (30 créditos)
- [x] Sistema de versionado/rollback
- [x] Descarga ZIP
- [x] GitHub OAuth
- [x] Panel de administración

### Próximas Tareas (Backlog)
- [ ] GitHub Export desde generador (crear repo + push)
- [ ] Deploy automático (Vercel/Netlify)
- [ ] Marketplace de templates
- [ ] Separación Control Plane / Execution Plane
- [ ] Contenedores Docker aislados por proyecto
