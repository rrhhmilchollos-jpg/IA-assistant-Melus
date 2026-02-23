# Melus AI - Product Requirements Document

## Descripción
**Melus AI** - Clon completo de Emergent.sh con sistema multi-agente real.

---

## ✅ TODO IMPLEMENTADO

### 1. AI Builder (Chat)
- ✅ Chat en español para crear apps
- ✅ 6 Agentes con GPT-4o real
- ✅ Generación de código completo
- ✅ Vista de archivos generados
- ✅ Vista previa en vivo con iframe
- ✅ Quick prompts

### 2. Sistema Multi-Agente
- ✅ Planner Agent - Planificación
- ✅ Developer Agent - Código
- ✅ QA Agent - Validación
- ✅ Researcher Agent
- ✅ Optimizer Agent
- ✅ Cost Controller Agent
- ✅ Comunicación entre agentes

### 3. Stripe Billing
- ✅ Planes: Free ($0), Pro ($29), Enterprise ($99)
- ✅ Checkout de suscripciones
- ✅ Paquetes de créditos (5K, 25K, 100K)
- ✅ Webhooks
- ✅ Gestión de créditos

### 4. Vista Previa en Vivo
- ✅ API de preview `/api/preview/{project_id}`
- ✅ Render de React con Babel
- ✅ Soporte TailwindCSS
- ✅ Iframe integrado

### 5. Autenticación
- ✅ Email/Password
- ✅ Google OAuth
- ✅ GitHub OAuth

### 6. Landing Page
- ✅ Hero profesional
- ✅ Features
- ✅ Pricing
- ✅ FAQ

---

## APIs

### Billing
- `GET /api/billing/plans`
- `GET /api/billing/credits`
- `POST /api/billing/checkout/subscription`
- `POST /api/billing/checkout/credits`
- `POST /api/billing/webhook`

### Preview
- `GET /api/preview/{project_id}`
- `GET /api/preview/{project_id}/{path}`

### Multi-Agent
- `GET /api/agents-v3/status`
- `POST /api/agents-v3/pipeline/start`
- `GET /api/agents-v3/tasks`
- `GET /api/agents-v3/messages`

---

## Rutas Frontend

- `/` - Landing
- `/login` - Login
- `/home` - Dashboard
- `/build` - AI Builder
- `/pricing` - Planes Stripe
- `/agents` - Dashboard agentes

---

## Credenciales Test
- Email: `demo@melusai.com` / `demo123`
- URL: https://melus-dev-studio.preview.emergentagent.com

---

## Stripe Keys (ya configurados)
- API Key: ✅ Configurada en .env
- Publishable Key: ✅ Configurada

---

## Changelog

### 2026-02-23
- ✅ Stripe Billing completo
- ✅ Vista previa en vivo
- ✅ Página de Pricing con planes
- ✅ Sistema multi-agente con LLM real
- ✅ AI Builder con generación de código
