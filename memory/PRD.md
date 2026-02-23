# MelusAI - Product Requirements Document

## Arquitectura v3.0 - Brain Engine & Monorepo

---

## Estado Actual

### ✅ Fase 1 COMPLETADA - Infraestructura Core

#### Brain Engine (Implementado)
- `/app/core/brain_engine.py` - Motor central de orquestación
- `/app/core/intent_classifier.py` - Clasificador de intenciones con IA
- `/app/core/code_templates.py` - Templates pre-construidos

#### Clasificación de Intenciones
El sistema clasifica automáticamente los prompts de usuarios en:
- `ecommerce` - Tiendas online, carritos, productos
- `saas_app` - Aplicaciones SaaS con suscripciones
- `dashboard` - Paneles de control con métricas
- `landing_page` - Páginas de aterrizaje/marketing
- `blog` - Sistemas de contenido
- `portfolio` - Portafolios personales
- `api_service` - Servicios API
- `web_app` - Aplicaciones web generales

#### Templates Pre-construidos
Cada tipo de aplicación tiene un template profesional:
- **Todo App**: Lista de tareas con filtros, animaciones y diseño moderno
- **E-commerce**: Tienda con carrito, productos y checkout
- **Dashboard**: Panel con KPIs, gráficos y actividad reciente
- **Landing Page**: Página de marketing con hero, features y CTA
- **SaaS App**: Aplicación con sidebar, dashboard y workspace

#### API Endpoints Brain Engine
- `POST /api/brain/analyze` - Analiza intent sin generar
- `POST /api/brain/generate` - Genera proyecto completo
- `GET /api/brain/project/{id}` - Estado del proyecto
- `GET /api/brain/project/{id}/files` - Archivos generados
- `GET /api/brain/templates` - Lista templates disponibles
- `GET /api/brain/intents` - Lista tipos de intent
- `WS /api/brain/ws/{id}` - WebSocket para actualizaciones

### ✅ Funcionalidades Existentes (Mantenidas)

#### Autenticación
- ✅ Email/Password
- ✅ Google OAuth
- ✅ GitHub OAuth
- ✅ Sesiones con JWT

#### Interfaz de Usuario
- ✅ Landing Page profesional (español)
- ✅ AI Builder con chat
- ✅ Vista previa en vivo
- ✅ Árbol de archivos

#### Billing
- ✅ Integración Stripe
- ✅ Planes: Free, Pro, Enterprise
- ✅ Paquetes de créditos
- ✅ Webhooks

---

## Estructura del Monorepo

```
/app/
├── api-gateway/           # ✅ Rutas del Brain Engine
│   ├── __init__.py
│   └── brain_routes.py
├── apps/                  # 🔄 Builders especializados (pendiente)
│   ├── web-builder/
│   ├── saas-builder/
│   └── ecommerce-builder/
├── core/                  # ✅ Motor central
│   ├── __init__.py
│   ├── brain_engine.py
│   ├── intent_classifier.py
│   └── code_templates.py
├── database/              # ✅ Schemas PostgreSQL (preparados)
│   ├── __init__.py
│   ├── config.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py
│   └── migrations/
├── services/              # 🔄 Microservicios (pendiente)
│   ├── auth-service/
│   ├── billing-service/
│   └── deployment-service/
├── backend/               # ✅ API FastAPI (existente)
└── frontend/              # ✅ React App (existente)
```

---

## Backlog Priorizado

### P0 - Crítico (Completado Parcialmente)
- [x] Brain Engine básico
- [x] Intent Classifier
- [x] Templates pre-construidos
- [x] API endpoints Brain Engine
- [ ] Migración a PostgreSQL (schemas listos, migración pendiente)
- [ ] Migración frontend a Next.js

### P1 - Alta Prioridad
- [ ] Sandbox Docker para ejecución segura
- [ ] Webhooks Stripe completos
- [ ] Sistema de versioning de archivos
- [ ] Integración LLM para personalización de templates

### P2 - Media Prioridad  
- [ ] Builders especializados (apps/)
- [ ] Admin Dashboard
- [ ] Sistema de deployment automático
- [ ] CI/CD Pipeline

### P3 - Baja Prioridad
- [ ] Marketplace de templates
- [ ] Sistema de plugins
- [ ] Integración con repositorios Git
- [ ] Analytics avanzados

---

## Credenciales de Test

- **Email**: demo@melusai.com
- **Password**: demo123
- **URL**: https://melus-ai-dev.preview.emergentagent.com

---

## Tecnologías

| Componente | Actual | Objetivo |
|------------|--------|----------|
| Frontend | React + TailwindCSS | Next.js + TailwindCSS |
| Backend | FastAPI | FastAPI + Microservicios |
| Base de Datos | MongoDB | PostgreSQL |
| Auth | JWT + OAuth | JWT + OAuth |
| Payments | Stripe | Stripe |
| LLM | GPT-4o (Emergent) | GPT-4o (Emergent) |

---

## Changelog

### 2024-02-23
- Implementado Brain Engine v1.0
- Creado Intent Classifier con patrones en español/inglés
- Añadidos 5 templates pre-construidos profesionales
- Integrado con sistema existente manteniendo compatibilidad
- Preparados schemas PostgreSQL con SQLAlchemy

---

*Última actualización: 23 de Febrero, 2024*
