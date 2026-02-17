# Assistant Melus - Product Requirements Document

## Resumen
Assistant Melus es un clon completo de Emergent.sh, una plataforma de generación de aplicaciones impulsada por IA con arquitectura multi-agente.

## Problema que Resuelve
Proporcionar una plataforma donde los usuarios pueden describir aplicaciones en lenguaje natural y obtener código generado automáticamente por agentes especializados de IA.

## Usuarios Objetivo
- Desarrolladores que necesitan prototipar rápidamente
- Emprendedores sin conocimientos técnicos
- Empresas que buscan acelerar el desarrollo

## Funcionalidades Principales

### 1. Sistema de Autenticación
- ✅ Registro con email/password
- ✅ Login con email/password
- ✅ Gestión de sesiones con JWT
- ✅ Rol de administrador

### 2. Sistema de Créditos
- ✅ Balance de créditos por usuario
- ✅ Consumo por acción de agente
- ✅ Historial de transacciones
- ✅ Integración con Stripe para compras
- ✅ Paquetes de créditos configurables
- ✅ Códigos promocionales

### 3. Planes de Suscripción
- ✅ Plan Free (100 créditos/mes)
- ✅ Plan Pro ($29.99 - 5000 créditos/mes)
- ✅ Plan Enterprise ($99.99 - 25000 créditos/mes)

### 4. Arquitectura Multi-Agente
- ✅ **Agente Orquestador**: Analiza requisitos y coordina
- ✅ **Agente de Diseño**: UI/UX, wireframes, modelos de datos
- ✅ **Agente Frontend**: Código React/Vue/Svelte
- ✅ **Agente Backend**: APIs FastAPI/Express
- ✅ **Agente Database**: Esquemas SQL/NoSQL
- ✅ **Agente Deploy**: Dockerfiles, CI/CD

### 5. Chat con IA
- ✅ Conversación en tiempo real con GPT-4o
- ✅ Múltiples modelos disponibles
- ✅ Fork de conversaciones
- ✅ Edición y regeneración de mensajes
- ✅ Rollback a mensajes anteriores
- ✅ Resumen de conversaciones
- ✅ Extracción de bloques de código

### 6. Panel de Administración
- ✅ Dashboard con métricas en tiempo real
- ✅ Gestión de usuarios
- ✅ Historial de transacciones
- ✅ Análisis de ingresos
- ✅ Estado del sistema
- ✅ Configuración de costos de agentes

### 7. Generador de Aplicaciones
- ✅ Consola de agentes en tiempo real
- ✅ Indicadores de progreso por agente
- ✅ Logs detallados de ejecución
- ✅ Descarga de código generado

## Arquitectura Técnica

### Backend
- Framework: FastAPI
- Base de datos: MongoDB
- Autenticación: JWT con X-Session-Token
- Pagos: Stripe

### Frontend
- Framework: React
- Styling: TailwindCSS
- Componentes: shadcn/ui
- Estado: React Context

### Integraciones
- OpenAI GPT-4o (via Emergent LLM Key)
- Stripe Payments

## Estado del Proyecto

### Completado ✅
- Sistema de autenticación completo
- Sistema de créditos con Stripe
- Chat con IA funcional
- Arquitectura multi-agente
- Panel de administración
- Generador de aplicaciones
- UI clonada de Emergent.sh

### En Progreso 🔄
- Integración de entrada de voz (Whisper)
- Funcionalidad de despliegue automático

### Pendiente 📋
- Preview en tiempo real de aplicaciones
- Integración con GitHub para guardar proyectos
- Sistema de plantillas predefinidas

## Credenciales de Prueba
- **Admin**: rrhh.milchollos@gmail.com / 19862210Des

## URLs
- Frontend: https://melus-preview-1.preview.emergentagent.com
- API: https://melus-preview-1.preview.emergentagent.com/api
