# Melus AI - Product Requirements Document

## Descripción
**Melus AI** es una plataforma SaaS de generación de aplicaciones con IA, clon de Emergent.sh/Base44.

---

## ✅ IMPLEMENTADO COMPLETAMENTE

### AI Builder (Chat de creación)
- ✅ Chat interactivo en español
- ✅ **6 Agentes con LLM real (GPT-4o)**:
  - Planner: Analiza requisitos y crea plan
  - Researcher: Investiga best practices
  - Developer: Genera código completo
  - QA: Valida y puntúa código
  - Optimizer: Optimiza rendimiento
  - Cost Controller: Controla costos
- ✅ Generación de múltiples archivos (HTML, JSX, CSS)
- ✅ Mensajes en tiempo real de cada agente
- ✅ Vista de archivos generados
- ✅ Quick prompts predefinidos

### Sistema de Autenticación
- ✅ Login Email/Password
- ✅ Google OAuth autoalojado
- ✅ GitHub OAuth

### Landing Page
- ✅ Hero profesional
- ✅ Features, Pricing, FAQ
- ✅ Responsive design

### Otras funcionalidades
- ✅ Monaco Editor
- ✅ WebSocket streaming
- ✅ Sistema de aprendizaje

---

## Rutas

- `/` - Landing Page
- `/login` - Login
- `/home` - Dashboard
- `/build` - **AI Builder**
- `/agents` - Dashboard de agentes
- `/workspace` - Editor Monaco

---

## Testing verificado

```bash
# Pipeline completo funcionando:
Completed tasks: 3
  - planner: Create project plan (completed)
  - developer: Generate code (completed) - 6 files
  - qa: Validate code (completed) - Score: 85/100

# Mensajes de agentes:
  [planner] 🔍 Analyzing...
  [planner] ✅ Plan ready
  [developer] 💻 Generating code...
  [developer] ✅ Generated 6 files
  [qa] 🔎 Reviewing...
  [qa] ✅ Passed
```

---

## Credenciales Test
- Email: `demo@melusai.com` / `demo123`
- URL: https://melus-dev-studio.preview.emergentagent.com/build

---

## Changelog

### 2026-02-23
- ✅ Sistema Multi-Agente REAL con GPT-4o
- ✅ AI Builder generando código funcional
- ✅ 6 agentes comunicándose en tiempo real
- ✅ QA validando código automáticamente

---

## Próximas tareas
- Vista previa en vivo
- Sandbox Docker
- Billing Stripe
