# Melus AI - Changelog

## [2.1.0] - 2025-12-18

### Added
- **Debug Agent con 30 créditos**: El Debug Agent ahora cuesta 30 créditos por uso (antes 50) como estrategia de monetización
- **Sistema de Versionado Visual**: UI para ver historial de versiones y hacer rollback a versiones anteriores
- **Mejor captura de errores**: El preview de Sandpack ahora captura errores de compilación y logs de consola
- **Ultra Mode mejorado**: Toggle visible en la UI que duplica precios de todos los templates
- **Prompts mejorados para Debug Agent**: Análisis más preciso de errores con explicaciones detalladas

### Changed
- Actualizado el costo del Debug Agent de 50 a 30 créditos
- Mejorada la UI del generador con branding "Melus AI - Constructor Universal de Apps"
- El endpoint `/api/agents/v2/debug` ahora valida créditos antes de ejecutar y devuelve créditos restantes
- Generate-from-template ahora soporta Ultra Mode correctamente

### Fixed
- Los precios de Ultra Mode ahora se muestran correctamente en la UI (2x)
- El sistema de versiones se actualiza correctamente después de cada operación

---

## [2.0.0] - 2025-12-17

### Added
- **Preview en Vivo con Sandpack**: Integración completa de CodeSandbox Sandpack para preview en tiempo real
- **Sistema Multi-Agente v2**: 6 agentes especializados (Classifier, Architect, Frontend, Backend, Integrator, Debug)
- **12 Templates Predefinidos**: E-commerce, Blog, Dashboard, Landing, Task Manager, Portfolio, CRM, Chat, Social, Inventory, Booking, Analytics
- **Ultra Mode**: Modo premium que usa modelo más potente a 2x costo
- **GitHub OAuth**: Autenticación completa con GitHub
- **Sistema de Workspaces**: Filesystem virtual con persistencia
- **Descarga ZIP**: Exportar proyectos como archivos ZIP
- **WebSockets**: Logs de generación en tiempo real

### Changed
- Arquitectura completamente rediseñada para soportar generación multi-archivo
- Nueva UI del generador con explorador de archivos y editor de código

---

## [1.0.0] - 2025-12-15

### Added
- Sistema de autenticación (email/password + JWT)
- Sistema de créditos con Stripe
- Chat con IA (GPT-4o)
- Panel de administración
- Generador de apps básico
