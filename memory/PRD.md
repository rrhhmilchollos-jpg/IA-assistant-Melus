# Melus AI - Product Requirements Document

> **Última actualización:** Diciembre 2025
> **Versión:** 2.3.0

---

## 1. Visión del Producto

**Melus AI** es un **Constructor Universal de Aplicaciones** que funciona **idénticamente a Emergent.sh**, proporcionando una plataforma de desarrollo autónoma que genera aplicaciones full-stack completas usando un sistema de **13 agentes especializados** de IA.

### Características Principales
- **Modo Motor (No Chat)**: Ejecución directa de proyectos sin conversación
- **13 Agentes Especializados**: Cada uno con rol específico
- **Preview en Vivo**: CodeSandbox Sandpack integrado
- **Sistema de Versionado**: Snapshots y rollback
- **GitHub Integration**: OAuth y push de proyectos

---

## 2. Modos de Ejecución

### 2.1 Modo Templates (Conversacional)
- Seleccionar de 12 templates predefinidos
- Generar apps con descripción libre
- Ideal para usuarios que quieren guía

### 2.2 MODO MOTOR (No Chat) - NUEVO
- **Ejecución directa** sin conversación
- Usa **plantilla de proyecto** estructurada por agentes
- Ejecuta **TODOS los 11 agentes** en secuencia automática
- Ideal para usuarios técnicos que saben exactamente lo que quieren

**Flujo del Motor:**
```
Classifier → Architect → Design → Database → Frontend → Backend → Integrator → Testing → Security → Deploy → Docs
```

**Costo Motor:**
- Normal: ~930 créditos
- Ultra: ~1860 créditos

---

## 3. Sistema de 13 Agentes Especializados

### 3.1 Agentes Core (Generación)
| Agente | Costo | Función |
|--------|-------|---------|
| Classifier | 25 | Clasifica tipo de aplicación |
| Architect | 50 | Diseña estructura y arquitectura |
| Frontend | 150 | Genera código React completo |
| Backend | 150 | Genera APIs y servidor |
| Integrator | 75 | Conecta frontend con backend |

### 3.2 Agentes Especializados
| Agente | Costo | Función |
|--------|-------|---------|
| Design | 100 | UI/UX y sistema de diseño |
| Database | 100 | Esquemas y queries |
| Testing | 75 | Tests automatizados |
| Security | 50 | Análisis de vulnerabilidades |
| Deploy | 50 | Configuración de despliegue |

### 3.3 Agentes de Utilidad
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
- [x] Preview en vivo con Sandpack
- [x] 12 templates predefinidos
- [x] Ultra Mode (2x créditos)
- [x] Debug Agent (30 créditos)
- [x] Sistema de versionado/rollback
- [x] Descarga ZIP
- [x] GitHub OAuth completo
- [x] GitHub push desde workspace (50 créditos)
- [x] Panel de administración

### Backlog
- [ ] Deploy automático (Vercel/Netlify)
- [ ] Marketplace de templates
- [ ] Contenedores Docker aislados

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

- **Frontend:** https://motor-no-chat.preview.emergentagent.com
- **Generador:** https://motor-no-chat.preview.emergentagent.com/generator
- **API:** https://motor-no-chat.preview.emergentagent.com/api

---

## 10. Comparación con Emergent.sh

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
