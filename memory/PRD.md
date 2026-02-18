# Assistant Melus - Product Requirements Document

## Resumen
Assistant Melus es un clon completo de Emergent.sh, una plataforma de generación de aplicaciones impulsada por IA con arquitectura multi-agente y preview en vivo.

## Problema que Resuelve
Proporcionar una plataforma donde los usuarios pueden describir aplicaciones en lenguaje natural y obtener código generado automáticamente por agentes especializados de IA, con preview en tiempo real.

## Usuarios Objetivo
- Desarrolladores que necesitan prototipar rápidamente
- Emprendedores sin conocimientos técnicos
- Empresas que buscan acelerar el desarrollo

## Funcionalidades Principales - TODAS EN PRODUCCIÓN

### 1. Sistema de Autenticación ✅
- Registro con email/password
- Login con email/password
- Gestión de sesiones con JWT
- Rol de administrador

### 2. Sistema de Créditos ✅
- Balance de créditos por usuario
- Consumo por acción de agente
- Historial de transacciones
- Integración con Stripe para compras
- Paquetes de créditos configurables
- Códigos promocionales

### 3. Planes de Suscripción ✅
- Plan Free (100 créditos/mes)
- Plan Pro ($29.99 - 5000 créditos/mes)
- Plan Enterprise ($99.99 - 25000 créditos/mes)

### 4. Arquitectura Multi-Agente v2 ✅ [NUEVO]
Sistema de agentes mejorado con generación de código estructurado:

- **Classifier Agent** (25 créditos): Analiza tipo de app, complejidad, requisitos
- **Architect Agent** (50 créditos): Define estructura de archivos y dependencias
- **Frontend Agent** (150 créditos): Genera React/Tailwind con sintaxis correcta v6
- **Backend Agent** (150 créditos): Genera APIs Express/FastAPI
- **Integrator Agent** (75 créditos): Conecta frontend con backend
- **Debug Agent** (50 créditos): Corrige errores automáticamente

### 5. Preview en Vivo con Sandpack ✅ [NUEVO]
- Iframe con CodeSandbox integrado
- Hot reload en tiempo real
- Compilación de React en el navegador
- Sin necesidad de contenedores Docker
- Explorador de archivos visual
- Editor de código con syntax highlighting
- Múltiples pestañas de archivos

### 6. Sistema de Workspaces ✅ [NUEVO]
- Filesystem virtual por proyecto
- Versionado con snapshots
- Rollback a versiones anteriores
- WebSocket para actualizaciones en tiempo real
- Persistencia en MongoDB
- Recuperación de workspace al recargar

### 7. Chat con IA ✅
- Conversación en tiempo real con GPT-4o
- Múltiples modelos disponibles
- Fork de conversaciones
- Edición y regeneración de mensajes
- Rollback a mensajes anteriores
- Resumen de conversaciones
- Extracción de bloques de código

### 8. Panel de Administración ✅
- Dashboard con métricas en tiempo real
- Gestión de usuarios
- Historial de transacciones
- Análisis de ingresos
- Estado del sistema
- Configuración de costos de agentes

### 9. Generador de Aplicaciones v2 ✅ [MEJORADO]
- Consola de agentes en tiempo real con logs
- Preview en vivo mientras se genera
- Explorador de archivos integrado
- Editor de código con syntax highlighting
- Descarga de proyecto
- Auto-fix de errores con Debug Agent

### 10. Entrada de Voz (Whisper) ✅
- Transcripción de audio a texto con OpenAI Whisper
- Soporte para español e inglés
- Costo: 25 créditos por transcripción

### 11. Sistema de Despliegue ✅
- Redeploy de proyectos (50 créditos)
- Descarga de código en ZIP
- Historial de deployments
- Estado de deployments

### 12. Integración con GitHub ✅
- Botón "Connect GitHub" / "Save to GitHub" en la barra de acciones del chat
- Conectar cuenta de GitHub via OAuth
- Modal para crear repositorios desde la app
- Subir código de conversaciones a GitHub (50 créditos)
- Soporte para repos públicos y privados
- Ubicado junto a los botones Summarize y Ultra

## Arquitectura Técnica

### Backend (Refactorizado)
- Framework: FastAPI
- Base de datos: MongoDB
- Autenticación: JWT con X-Session-Token
- Pagos: Stripe
- WebSocket: Para logs en tiempo real

**Rutas modulares:**
- `/api/auth` - Autenticación
- `/api/credits` - Créditos y facturación
- `/api/admin` - Panel de administración
- `/api/agents` - Sistema multi-agente original
- `/api/agents/v2` - Sistema multi-agente mejorado [NUEVO]
- `/api/workspace` - Gestión de workspaces [NUEVO]
- `/api/projects` - Gestión de proyectos
- `/api/conversations` - Chat
- `/api/voice` - Transcripción de voz
- `/api/deploy` - Despliegue
- `/api/github` - Integración GitHub

### Frontend
- Framework: React
- Styling: TailwindCSS
- Componentes: shadcn/ui
- Estado: React Context
- Preview: @codesandbox/sandpack-react [NUEVO]

### Integraciones EN PRODUCCIÓN
- OpenAI GPT-4o (via Emergent LLM Key)
- OpenAI Whisper (via Emergent LLM Key)
- Stripe Payments
- GitHub API (requiere OAuth credentials)
- CodeSandbox Sandpack [NUEVO]

## Costos de Créditos
| Acción | Créditos |
|--------|----------|
| Chat con IA | ~50 (variable) |
| Classifier Agent | 25 |
| Architect Agent | 50 |
| Frontend Agent | 150 |
| Backend Agent | 150 |
| Integrator Agent | 75 |
| Debug Agent | 50 |
| Transcripción voz | 25 |
| Redeploy | 50 |
| Push proyecto a GitHub | 100 |
| Push código a GitHub | 50 |

**Generación completa de app: ~500 créditos**

## Configuración de GitHub
Para habilitar la integración con GitHub, añadir al `.env` del backend:
```
GITHUB_CLIENT_ID=tu_client_id
GITHUB_CLIENT_SECRET=tu_client_secret
```

Obtener credenciales en: https://github.com/settings/applications/new
- Callback URL: https://tu-dominio/api/github/auth/callback

## Credenciales de Prueba
- **Admin**: rrhh.milchollos@gmail.com / 19862210Des

## URLs
- Frontend: https://melus-platform.preview.emergentagent.com
- API: https://melus-platform.preview.emergentagent.com/api
- Generador de Apps: https://melus-platform.preview.emergentagent.com/generator

## Templates Predefinidos [ACTUALIZADO]
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

## Funcionalidades Adicionales [ACTUALIZADO]
- **Descarga ZIP**: Exportar proyecto completo como archivo ZIP
- **Persistencia de Workspace**: El último proyecto se recupera automáticamente
- **Selección de Templates**: Galería visual con 12 tipos de apps
- **App Personalizada**: Opción de describir app custom si no hay template adecuado
- **ULTRA MODE**: Modo premium con 2x créditos para máxima calidad de código
  - Prompts mejorados con mejores prácticas
  - Error handling completo
  - Accesibilidad incluida
  - Animaciones y loading states
