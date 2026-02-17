# Assistant Melus - Product Requirements Document

## Resumen
Assistant Melus es un clon completo de Emergent.sh, una plataforma de generación de aplicaciones impulsada por IA con arquitectura multi-agente.

## Problema que Resuelve
Proporcionar una plataforma donde los usuarios pueden describir aplicaciones en lenguaje natural y obtener código generado automáticamente por agentes especializados de IA.

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

### 4. Arquitectura Multi-Agente ✅
- **Agente Orquestador**: Analiza requisitos y coordina (50 créditos)
- **Agente de Diseño**: UI/UX, wireframes, modelos de datos (100 créditos)
- **Agente Frontend**: Código React/Vue/Svelte (150 créditos)
- **Agente Backend**: APIs FastAPI/Express (150 créditos)
- **Agente Database**: Esquemas SQL/NoSQL (100 créditos)
- **Agente Deploy**: Dockerfiles, CI/CD (200 créditos)

### 5. Chat con IA ✅
- Conversación en tiempo real con GPT-4o
- Múltiples modelos disponibles
- Fork de conversaciones
- Edición y regeneración de mensajes
- Rollback a mensajes anteriores
- Resumen de conversaciones
- Extracción de bloques de código

### 6. Panel de Administración ✅
- Dashboard con métricas en tiempo real
- Gestión de usuarios
- Historial de transacciones
- Análisis de ingresos
- Estado del sistema
- Configuración de costos de agentes

### 7. Generador de Aplicaciones ✅
- Consola de agentes en tiempo real
- Indicadores de progreso por agente
- Logs detallados de ejecución
- Descarga de código generado en ZIP

### 8. Entrada de Voz (Whisper) ✅
- Transcripción de audio a texto con OpenAI Whisper
- Soporte para español e inglés
- Costo: 25 créditos por transcripción

### 9. Sistema de Despliegue ✅
- Redeploy de proyectos (50 créditos)
- Descarga de código en ZIP
- Historial de deployments
- Estado de deployments

### 10. Integración con GitHub ✅
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

**Rutas modulares:**
- `/api/auth` - Autenticación
- `/api/credits` - Créditos y facturación
- `/api/admin` - Panel de administración
- `/api/agents` - Sistema multi-agente
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

### Integraciones EN PRODUCCIÓN
- OpenAI GPT-4o (via Emergent LLM Key)
- OpenAI Whisper (via Emergent LLM Key)
- Stripe Payments
- GitHub API (requiere OAuth credentials)

## Costos de Créditos
| Acción | Créditos |
|--------|----------|
| Chat con IA | ~50 (variable) |
| Agente Orquestador | 50 |
| Agente Diseño | 100 |
| Agente Frontend | 150 |
| Agente Backend | 150 |
| Agente Database | 100 |
| Agente Deploy | 200 |
| Transcripción voz | 25 |
| Redeploy | 50 |
| Push proyecto a GitHub | 100 |
| Push código a GitHub | 50 |

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
- Frontend: https://melus-preview-1.preview.emergentagent.com
- API: https://melus-preview-1.preview.emergentagent.com/api
