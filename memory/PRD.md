# MelusAI - Product Requirements Document

## Arquitectura v3.0 - Multi-Model AI System

---

## Estado Actual: ✅ Fase 3 COMPLETADA

### ✅ Multi-Model LLM Support
| Provider | Modelos | Estado |
|----------|---------|--------|
| **OpenAI** | GPT-5.2 Codex, GPT-5.1, GPT-4o, O3 | ✅ Activo |
| **Anthropic** | Claude 4.6 Opus, Claude 4.6 Sonnet, Claude 4.5 | ✅ Activo |
| **Google** | Gemini 3 Pro, Gemini 3 Flash, Gemini 2.5 Pro | ✅ Activo |
| **Sora** | Sora 2, Sora 2 Pro (Video) | ✅ Activo |

### ✅ Agent Modes
| Modo | Descripción | Modelo Default | Focus |
|------|-------------|----------------|-------|
| **E-1** | Estable y meticuloso | GPT-4o | Fullstack |
| **E-1.5** | Equilibrado | Claude 4 Sonnet | Fullstack |
| **E-2** | Meticuloso y persistente | Claude 4.6 Opus | Fullstack |
| **Pro** | Máxima calidad | GPT-5.2 Codex | Fullstack |
| **Prototipo** | Solo Frontend | Gemini 3 Flash | Frontend |
| **Móvil** | Apps móviles | Claude 4.5 Sonnet | Mobile |

### ✅ Sistema Multi-Agente (6 Agentes)
| Agente | Función | LLM | Estado |
|--------|---------|-----|--------|
| 🏗 **Architect** | Define arquitectura | Multi-model | ✅ |
| 💻 **Coder** | Genera código | Multi-model | ✅ |
| 🎨 **Designer** | Personaliza UI | GPT-4o | ✅ |
| 🔐 **Security** | Seguridad | - | ✅ |
| 🚀 **Deployer** | Docker/CI | - | ✅ |
| 🎬 **Video** | Sora 2 | Sora 2 | ✅ NEW |

---

## API Endpoints

### Models & Modes
```
GET  /api/brain/models          - Lista 17 modelos AI
GET  /api/brain/modes           - Lista 6 modos de agente
POST /api/brain/set-model       - Cambiar modelo
POST /api/brain/set-mode        - Cambiar modo
POST /api/brain/generate-video  - Generar video (Sora 2)
```

### Generation
```
POST /api/brain/analyze         - Clasificar intent
POST /api/brain/generate        - Generar proyecto completo
GET  /api/brain/project/{id}    - Estado + archivos
GET  /api/brain/agents/status   - Estado multi-agente
```

---

## Modelos Disponibles (17 total)

### OpenAI (5)
- `gpt-5.2-codex` - Best for code generation
- `gpt-5.1` - Recommended model
- `gpt-4o` - Fast multimodal
- `o3` - Advanced reasoning (PRO)
- `sora-2` - Video generation

### Anthropic Claude (8)
- `claude-4.6-opus` - Most Advanced
- `claude-4.6-opus-1m` - 1M Context (PRO)
- `claude-4.6-opus-fast` - 6x Faster (PRO)
- `claude-4.6-sonnet` - 200k Context
- `claude-4.6-sonnet-1m` - 1M Context (PRO)
- `claude-4.5-opus` - Advanced
- `claude-4.5-sonnet` - 200k Context
- `claude-4-sonnet` - Recommended

### Google Gemini (3)
- `gemini-3-pro` - Latest
- `gemini-3-flash` - Fast
- `gemini-2.5-pro` - Recommended

---

## Templates (9 tipos)

| Template | Tecnología | Archivos |
|----------|------------|----------|
| Todo/Tasks | React | 1 |
| E-commerce | React | 1 |
| Dashboard | React | 1 |
| Landing Page | React | 1 |
| SaaS App | React | 1 |
| **Game 2D** | **Phaser.js** | 2 |
| **Game 3D** | **Three.js** | 2 |

---

## Estructura del Proyecto

```
/app/
├── api-gateway/
│   └── brain_routes.py        # ✅ Multi-model endpoints
├── core/
│   ├── brain_engine.py        # ✅ Multi-model support
│   ├── intent_classifier.py   # ✅ 11 intents
│   ├── code_templates.py      # ✅ 9 templates
│   ├── agent_system.py        # ✅ 6 agents
│   └── llm_manager.py         # ✅ NEW: 17 models
├── database/
│   └── schemas/models.py      # ✅ PostgreSQL ready
└── backend/
    └── server.py              # ✅ v3.0
```

---

## Testing Verificado

### API Tests
- ✅ `/api/brain/models` - 17 modelos listados
- ✅ `/api/brain/modes` - 6 modos listados
- ✅ `/api/brain/set-model` - Cambio de modelo OK
- ✅ `/api/brain/set-mode` - Cambio de modo OK
- ✅ Generación con PRO mode - 12 archivos

### Generación
- ✅ E-commerce PRO: 12 archivos (8 APIs + Frontend + Config)
- ✅ SaaS: 13 archivos
- ✅ Dashboard: 9 archivos
- ✅ Games: 2-4 archivos

---

## Backlog

### ✅ COMPLETADO
- [x] Multi-model LLM support (17 modelos)
- [x] 6 Agent modes
- [x] VideoAgent con Sora 2
- [x] LLM Manager con providers
- [x] API endpoints para modelos/modos

### P1 - Próximo
- [ ] Migración PostgreSQL
- [ ] Sandbox Docker
- [ ] Webhooks Stripe

### P2 - Futuro
- [ ] Next.js frontend
- [ ] Editor visual
- [ ] Marketplace templates

---

## Credenciales Test

- **Email**: demo@melusai.com
- **Password**: demo123
- **URL**: https://melus-ai-dev.preview.emergentagent.com

---

## Changelog

### 2024-02-23 - Sesión 3
- ✅ Multi-model LLM support (GPT, Claude, Gemini)
- ✅ 6 Agent modes (E-1, E-1.5, E-2, Pro, Prototype, Mobile)
- ✅ Sora 2 video generation
- ✅ LLM Manager con 17 modelos
- ✅ VideoAgent nuevo agente

### 2024-02-23 - Sesión 2
- ✅ Sistema Multi-Agente (5 agentes)
- ✅ GPT-4o personalización
- ✅ Templates Game 2D/3D

### 2024-02-23 - Sesión 1
- ✅ Brain Engine v1.0
- ✅ Intent Classifier

---

*Última actualización: 23 de Febrero, 2024*
