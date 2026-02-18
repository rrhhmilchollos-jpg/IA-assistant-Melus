# Melus AI - Changelog

## [2.2.0] - 2025-12-18

### Added
- **Sistema de 13 Agentes Especializados**: Expansión completa del sistema multi-agente
  - **Core (5):** Classifier, Architect, Frontend, Backend, Integrator
  - **Specialized (5):** Design, Database, Testing, Security, Deploy
  - **Utility (3):** Debugger (30 créditos), Optimizer, Docs
- **GitHub Push desde Workspace**: Nuevo endpoint para subir proyectos a GitHub (50 créditos)
- **Endpoint run-agent**: Permite ejecutar agentes individuales bajo demanda
- **UI mejorada**: Barra de estado muestra los 13 agentes con iconos y colores únicos
- **Modal de GitHub**: Interfaz para configurar nombre de repo y privacidad antes de push

### Changed
- Total de créditos por generación: ~930 (Normal) / ~1860 (Ultra)
- Categorización de agentes: generation, specialized, utility
- Prompts mejorados para todos los agentes con instrucciones más detalladas

---

## [2.1.0] - 2025-12-18

### Added
- **Debug Agent a 30 créditos**: Estrategia de monetización
- **Sistema de Versionado Visual**: UI con historial y rollback
- **Ultra Mode mejorado**: Toggle visible que duplica precios

### Fixed
- Precios de Ultra Mode se muestran correctamente (2x)
- Sistema de versiones se actualiza después de cada operación

---

## [2.0.0] - 2025-12-17

### Added
- **Preview en Vivo con Sandpack**: CodeSandbox integrado
- **Sistema Multi-Agente v2**: 6 agentes iniciales
- **12 Templates Predefinidos**
- **Ultra Mode**: 2x costo para mejor calidad
- **GitHub OAuth**: Autenticación completa
- **Sistema de Workspaces**: Filesystem virtual
- **Descarga ZIP**: Exportar proyectos
- **WebSockets**: Logs en tiempo real

---

## [1.0.0] - 2025-12-15

### Added
- Sistema de autenticación (email/password + JWT)
- Sistema de créditos con Stripe
- Chat con IA (GPT-4o)
- Panel de administración
- Generador de apps básico
