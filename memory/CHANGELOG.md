# Melus AI - Changelog

## [2.3.0] - 2025-12-18

### Added
- **MODO MOTOR (No Chat)**: Ejecución directa de proyectos sin conversación
  - Nuevo endpoint `/api/agents/v2/execute-project`
  - Parser de plantillas de proyecto estructuradas
  - Detección automática de modo (chat vs execution)
  - Ejecuta 11 agentes en secuencia automática
- **Plantilla de Proyecto**: Formato estructurado por agentes
  - FRONTEND AGENT, BACKEND AGENT, DATABASE AGENT, DEPLOY AGENT
  - Instrucciones directas sin conversación
- **Pestañas en UI**: Templates | Motor No Chat
- **Endpoint `/api/agents/v2/template`**: Devuelve formato de plantilla
- **Test suite**: 15 tests automatizados para Motor No Chat

### Changed
- UI actualizada con selector de modo (Templates vs Motor)
- Costos endpoint ahora incluye `modes: {execution, chat}`

---

## [2.2.0] - 2025-12-18

### Added
- **Sistema de 13 Agentes Especializados**
- **GitHub Push desde Workspace** (50 créditos)
- **Endpoint run-agent** para agentes individuales

---

## [2.1.0] - 2025-12-18

### Added
- **Debug Agent a 30 créditos**
- **Sistema de Versionado Visual**
- **Ultra Mode mejorado**

---

## [2.0.0] - 2025-12-17

### Added
- **Preview en Vivo con Sandpack**
- **Sistema Multi-Agente v2**
- **12 Templates Predefinidos**
- **GitHub OAuth**
- **Descarga ZIP**

---

## [1.0.0] - 2025-12-15

### Added
- Sistema de autenticación
- Sistema de créditos con Stripe
- Chat con IA
- Panel de administración
