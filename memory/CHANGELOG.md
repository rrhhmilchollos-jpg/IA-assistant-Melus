# Assistant Melus - Changelog

## [2.1.0] - 2026-02-17

### Verified
- **Sistema completo funcionando sin errores**
  - Dashboard con chat: ✅ Operativo
  - Generador de aplicaciones: ✅ Operativo
  - Panel de administración: ✅ Operativo
  - APIs de autenticación: ✅ Operativo
  - APIs de admin: ✅ Operativo

### Note
- **Integración GitHub**: Backend completamente implementado. Pendiente configurar `GITHUB_CLIENT_ID` y `GITHUB_CLIENT_SECRET` en el `.env` del backend para activar OAuth.

---

## [2.0.0] - 2026-02-17

### Added
- **Arquitectura Multi-Agente Completa**
  - Agente Orquestador para análisis de proyectos
  - Agente de Diseño para UI/UX y wireframes
  - Agente Frontend para código React
  - Agente Backend para APIs FastAPI
  - Agente Database para esquemas de BD
  - Agente Deploy para configuración de despliegue

- **Panel de Administración**
  - Dashboard con métricas en tiempo real
  - Gestión de usuarios (listar, editar, eliminar)
  - Historial de transacciones
  - Gráfico de ingresos (30 días)
  - Estado del sistema (MongoDB, API)
  - Configuración de costos de agentes

- **Generador de Aplicaciones**
  - Consola de agentes en tiempo real
  - Indicadores de estado por agente
  - Logs detallados de ejecución
  - Descarga de código generado

- **Sistema de Suscripciones**
  - Plan Free (100 créditos/mes)
  - Plan Pro ($29.99 - 5000 créditos/mes)  
  - Plan Enterprise ($99.99 - 25000 créditos/mes)

- **Tracking de Uso de Créditos**
  - Consumo por tipo de agente
  - Historial detallado de uso

### Changed
- **Refactorización del Backend**
  - `server.py` dividido en routers modulares:
    - `routes/auth.py` - Autenticación
    - `routes/billing.py` - Créditos y Stripe
    - `routes/admin.py` - Panel de admin
    - `routes/agents.py` - Sistema multi-agente
    - `routes/projects.py` - Gestión de proyectos
    - `routes/chat.py` - Conversaciones

- **API Client del Frontend**
  - Nuevas APIs: agentsAPI, projectsAPI, adminAPI
  - Función clearSessionToken exportada

- **Header Mejorado**
  - Botón "Generar App" añadido
  - Botón "Admin" para administradores
  - Enlaces en menú de usuario

### Fixed
- Referencias a `advancedAPI` eliminadas
- Importación de `clearSessionToken` corregida
- `getCurrentUser` añadido a authAPI

---

## [1.5.0] - 2026-02-16

### Added
- Funcionalidades avanzadas de chat:
  - Code Viewer modal
  - Preview Panel
  - Message Rollback
  - Conversation Summarize
  - Save/Bookmark conversations
- Sistema de adjuntos de archivos
- Botón Ultra Mode (placeholder)

### Fixed
- Bug de login loop con cookies cross-site
- Session management migrado a localStorage

---

## [1.0.0] - 2026-02-15

### Added
- Sistema de autenticación email/password
- Sistema de créditos con Stripe
- Chat con IA usando GPT-4o
- UI clonada de Emergent.sh (modo oscuro)
- Gestión de conversaciones
- Selección de modelos de IA
