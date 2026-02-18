# MELUS - ARQUITECTURA COMPLETA (CONSTRUCTOR UNIVERSAL)

> Documento Maestro - Última actualización: Diciembre 2025

---

## 1. VISIÓN DEL PRODUCTO

Melus no es un generador de código.  
Es una **infraestructura autónoma de construcción y ejecución de software**.

Debe incluir:
- Clasificación automática del proyecto
- Generación multiarchivo estructurada
- Sandbox real por proyecto
- Preview en vivo
- Logs en tiempo real
- Corrección automática de errores
- Versionado interno
- Deploy automático
- Exportación a repositorio

**Sin estos elementos no compite al nivel requerido.**

---

## 2. ARQUITECTURA GLOBAL (HÍBRIDA ESCALABLE)

### CAPA A — CONTROL PLANE (Cloud gestionado)

**Proveedor recomendado:** Google Cloud o Amazon Web Services

**Componentes:**
- API Backend (Node.js o FastAPI)
- PostgreSQL gestionado
- Redis gestionado
- Sistema de autenticación
- Sistema de facturación
- Gestión de proyectos
- Sistema de snapshots
- Orquestador de contenedores
- WebSocket server (logs y estado)

> Esta capa NO ejecuta código del usuario.

### CAPA B — EXECUTION LAYER (Servidores dedicados)

Servidores físicos o VPS dedicados para:
- Docker Engine
- Creación de contenedores por proyecto
- Ejecución de builds
- Dev servers
- Auto-fix
- Proxy dinámico

**Cada proyecto:**
- Contenedor aislado
- CPU limitada
- RAM limitada
- Timeout
- Sin acceso root
- Red restringida

### CAPA C — PROXY & PREVIEW

- Reverse proxy (Nginx/Caddy)
- Subdominio dinámico: `project-id.melus.app`

**Flujo:**
```
Prompt → Generación → Build → Contenedor → Puerto interno → Proxy → Iframe preview
```

Logs transmitidos vía WebSocket.

---

## 3. MOTOR UNIVERSAL DE CLASIFICACIÓN

Antes de generar código, el **Classifier Agent** analiza el prompt:

Detecta si es:
- Landing
- SaaS
- Marketplace
- API
- Dashboard
- AI Tool
- Mobile Web App
- E-commerce
- Blog
- Portal empresarial

**Devuelve:**
```json
{
  "type": "string",
  "complexity": "low|medium|high",
  "requires_auth": boolean,
  "requires_db": boolean,
  "requires_payments": boolean,
  "requires_ai": boolean
}
```

Esto define la arquitectura base.

---

## 4. SISTEMA DE PLANTILLAS BASE (ESTABILIDAD)

No se genera desde cero. Se parte de plantillas sólidas:

### Frontend Base
- React + Vite
- Next.js
- Tailwind

### Backend Base
- Express
- NestJS
- FastAPI

### Base de Datos
- PostgreSQL
- Prisma ORM

**Cada plantilla incluye:**
- Estructura limpia
- Auth base opcional
- Configuración Docker
- `.env` preparado
- Scripts definidos

> El agente modifica sobre estructura estable.

---

## 5. SISTEMA MULTI-AGENTE

### 1. Classifier Agent
Clasifica tipo de aplicación.

### 2. Architecture Agent
Selecciona plantilla y define estructura:
```
frontend/
backend/
docker-compose.yml
.env
```

### 3. Builder Agents
Generan funcionalidades reales en archivos separados:
```
FILE: frontend/src/pages/Dashboard.jsx
FILE: backend/routes/users.js
```

### 4. Integration Agent
Conecta frontend y backend.

### 5. Debug Agent
- Lee logs de compilación
- Corrige automáticamente errores
- Reintenta build

> **Este agente es OBLIGATORIO para competir.**

---

## 6. SISTEMA DE GENERACIÓN MULTIARCHIVO

**Formato interno estándar:**
```
FILE: path/to/file
CODE:
...
```

**El backend:**
1. Parsea archivos
2. Escribe en filesystem real
3. Ejecuta instalación dependencias
4. Ejecuta build
5. Inicia servidor dev

---

## 7. SANDBOX DE EJECUCIÓN

**Cada proyecto:**
- Docker container
- Límite CPU
- Límite RAM
- Sin privilegios root
- Sin acceso al host
- Sin acceso red interna
- Timeout procesos largos
- Sin comandos peligrosos

> **Seguridad obligatoria.**

---

## 8. BASE DE DATOS (MODELO UNIVERSAL)

**Modelo inicial:** PostgreSQL multi-tenant gestionado en cloud.

**Estructura:**
- Un schema por proyecto
- Aislamiento lógico
- Migraciones automáticas

> Más adelante: DB dedicada para clientes enterprise.

---

## 9. VERSIONADO INTERNO

**Cada modificación:**
- Snapshot completo del filesystem
- Guardado en almacenamiento cloud
- Metadata en base de datos

**Permite:**
- Rollback
- Comparar versiones
- Restaurar estado previo

---

## 10. EXPORTACIÓN A REPOSITORIO

**Integración con:** GitHub

**Permite:**
- Crear repo automáticamente
- Push de código
- Mantener sincronización

---

## 11. DEPLOY AUTOMÁTICO

**Opciones futuras:**
- Deploy a servidor propio
- Deploy a Vercel
- Deploy a VPS
- Deploy a contenedor dedicado

> Botón "Deploy Production".

---

## 12. ESCALABILIDAD

**Modelo híbrido:**
- Cloud → estado y control
- Servidores dedicados → ejecución pesada

**Escalado horizontal:**
- Añadir más nodos de ejecución
- Balanceo automático
- Redis como coordinador

> Más adelante: Kubernetes si escala masivamente.

---

## 13. ROADMAP DE IMPLEMENTACIÓN

### Fase 1 – Núcleo funcional
- [x] Sandbox real (Sandpack - simulado)
- [x] Preview en vivo
- [x] Generación multiarchivo
- [x] Plantillas base (12 templates)
- [x] Logs en tiempo real

### Fase 2 – Inteligencia avanzada
- [ ] Multi-agente completo (5 agentes)
- [ ] Debug automático (30 créditos)
- [ ] Versionado/Snapshots
- [ ] Export GitHub (OAuth completado)

### Fase 3 – Plataforma profesional
- [ ] Deploy automático
- [ ] Autoscaling
- [ ] Marketplace de plantillas
- [x] Modo Ultra (modelo avanzado - 2x créditos)

---

## 14. ERRORES QUE DEBES EVITAR

- Generar HTML suelto
- No aislar contenedores
- Permitir múltiples stacks sin control
- No limitar recursos
- No usar plantillas base
- No implementar Debug Agent

---

## 15. STACK BASE RECOMENDADO

**Inicial único para estabilidad:**
- Frontend: React + Vite
- Backend: Express
- DB: PostgreSQL
- ORM: Prisma
- Contenedores: Docker
- Proxy: Nginx
- Backend principal: FastAPI

> Luego se expande.

---

## 16. MONETIZACIÓN

### Sistema de Créditos
- Generación normal: X créditos
- **Ultra Mode**: 2x créditos (modelo más potente)
- **Debug Agent**: 30 créditos por uso

### Stripe Integration
- Sistema de pagos integrado
- Recarga de créditos

---

## CONCLUSIÓN

Melus como constructor universal requiere:
- Infraestructura real
- Sistema multi-agente
- Sandbox seguro
- Preview en vivo
- Corrección automática
- Arquitectura híbrida escalable

**Esto no es un MVP pequeño. Es una plataforma de desarrollo autónoma.**
