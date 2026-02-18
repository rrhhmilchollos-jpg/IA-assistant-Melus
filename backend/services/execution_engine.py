"""
Melus AI - Motor de Ejecución No Chat
Sistema de agentes que ejecuta proyectos completos sin conversación
"""
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    INTEGRATION = "integration"
    TESTING = "testing"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    DESIGN = "design"
    DOCS = "docs"
    OPTIMIZER = "optimizer"

@dataclass
class AgentTask:
    """Tarea para un agente específico"""
    agent: AgentType
    instructions: List[str]
    framework: Optional[str] = None
    dependencies: List[str] = None
    priority: int = 1

@dataclass
class ProjectPlan:
    """Plan completo de proyecto"""
    name: str
    objective: str
    frontend: Optional[AgentTask] = None
    backend: Optional[AgentTask] = None
    database: Optional[AgentTask] = None
    integration: Optional[AgentTask] = None
    testing: Optional[AgentTask] = None
    security: Optional[AgentTask] = None
    deployment: Optional[AgentTask] = None
    additional_instructions: List[str] = None

def parse_project_template(template: str) -> ProjectPlan:
    """
    Parsea una plantilla de proyecto estilo Emergent.sh
    Extrae las instrucciones para cada agente
    """
    lines = template.strip().split('\n')
    
    project_name = ""
    objective = ""
    current_agent = None
    agent_instructions = {}
    additional = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            # Detectar sección de agente
            line_upper = line.upper()
            if 'FRONTEND' in line_upper:
                current_agent = 'frontend'
                agent_instructions[current_agent] = []
            elif 'BACKEND' in line_upper:
                current_agent = 'backend'
                agent_instructions[current_agent] = []
            elif 'DATABASE' in line_upper:
                current_agent = 'database'
                agent_instructions[current_agent] = []
            elif 'INTEGRATION' in line_upper:
                current_agent = 'integration'
                agent_instructions[current_agent] = []
            elif 'TESTING' in line_upper:
                current_agent = 'testing'
                agent_instructions[current_agent] = []
            elif 'SECURITY' in line_upper:
                current_agent = 'security'
                agent_instructions[current_agent] = []
            elif 'DEPLOYMENT' in line_upper or 'DEPLOY' in line_upper:
                current_agent = 'deployment'
                agent_instructions[current_agent] = []
            elif 'INSTRUCCIONES ADICIONALES' in line_upper or 'ADDITIONAL' in line_upper:
                current_agent = 'additional'
            continue
        
        # Detectar nombre del proyecto
        if line.lower().startswith('proyecto:'):
            project_name = line.split(':', 1)[1].strip()
            continue
        
        # Detectar objetivo
        if line.lower().startswith('objetivo:'):
            objective = line.split(':', 1)[1].strip()
            continue
        
        # Agregar instrucción al agente actual
        if current_agent and line.startswith('-'):
            instruction = line[1:].strip()
            if current_agent == 'additional':
                additional.append(instruction)
            else:
                agent_instructions.get(current_agent, []).append(instruction)
    
    # Construir plan
    plan = ProjectPlan(
        name=project_name or "Mi Proyecto",
        objective=objective or "Aplicación generada por Melus AI",
        additional_instructions=additional
    )
    
    # Asignar tareas a cada agente
    if 'frontend' in agent_instructions:
        plan.frontend = AgentTask(
            agent=AgentType.FRONTEND,
            instructions=agent_instructions['frontend']
        )
    
    if 'backend' in agent_instructions:
        plan.backend = AgentTask(
            agent=AgentType.BACKEND,
            instructions=agent_instructions['backend']
        )
    
    if 'database' in agent_instructions:
        plan.database = AgentTask(
            agent=AgentType.DATABASE,
            instructions=agent_instructions['database']
        )
    
    if 'integration' in agent_instructions:
        plan.integration = AgentTask(
            agent=AgentType.INTEGRATION,
            instructions=agent_instructions['integration']
        )
    
    if 'testing' in agent_instructions:
        plan.testing = AgentTask(
            agent=AgentType.TESTING,
            instructions=agent_instructions['testing']
        )
    
    if 'security' in agent_instructions:
        plan.security = AgentTask(
            agent=AgentType.SECURITY,
            instructions=agent_instructions['security']
        )
    
    if 'deployment' in agent_instructions:
        plan.deployment = AgentTask(
            agent=AgentType.DEPLOYMENT,
            instructions=agent_instructions['deployment']
        )
    
    return plan

def detect_execution_mode(prompt: str) -> str:
    """
    Detecta si el prompt es modo chat o modo ejecución
    
    Modo Ejecución (No Chat):
    - Contiene palabras como "Genera", "Construye", "Implementa", "Crea"
    - Tiene estructura de plantilla con agentes
    - No tiene preguntas
    
    Modo Chat:
    - Tiene preguntas con "?"
    - Palabras como "¿Qué opinas?", "¿Cómo puedo?", "sugiere"
    """
    prompt_lower = prompt.lower()
    
    # Indicadores de modo EJECUCIÓN
    execution_keywords = [
        'genera', 'construye', 'implementa', 'crea', 'desarrolla',
        'build', 'create', 'implement', 'generate', 'develop',
        'frontend agent', 'backend agent', 'database agent',
        'despliega', 'deploy', 'exporta', 'export'
    ]
    
    # Indicadores de modo CHAT
    chat_keywords = [
        '¿qué opinas', 'qué opinas', 'sugiere', 'recomienda',
        '¿cómo puedo', 'como puedo', '¿qué debería', 'que deberia',
        'what do you think', 'suggest', 'recommend', 'how can i'
    ]
    
    # Contar indicadores
    execution_score = sum(1 for kw in execution_keywords if kw in prompt_lower)
    chat_score = sum(1 for kw in chat_keywords if kw in prompt_lower)
    
    # Si tiene estructura de plantilla, es ejecución
    if '# FRONTEND' in prompt or '# BACKEND' in prompt or 'AGENT' in prompt.upper():
        execution_score += 5
    
    # Si tiene signos de pregunta, más probable chat
    if '?' in prompt:
        chat_score += 2
    
    return 'execution' if execution_score > chat_score else 'chat'

def build_agent_prompt(agent_type: str, task: AgentTask, project_context: dict) -> str:
    """
    Construye el prompt específico para cada agente
    """
    base_prompts = {
        'frontend': """Eres el FRONTEND AGENT de Melus AI.
Tu trabajo es generar código frontend COMPLETO y FUNCIONAL.

REGLAS ESTRICTAS:
1. Genera código COMPLETO - NO usar "...", "// TODO", o placeholders
2. Usa React 18 con hooks modernos
3. Usa TailwindCSS para estilos (tema oscuro por defecto)
4. React Router v6 para navegación
5. Código limpio, comentado y production-ready
6. Incluir estados de carga y manejo de errores
7. Diseño responsive y accesible

INSTRUCCIONES ESPECÍFICAS:
{instructions}

CONTEXTO DEL PROYECTO:
{context}

GENERA todos los archivos necesarios en formato JSON:
{{
    "files": {{
        "src/App.jsx": "CÓDIGO COMPLETO",
        "src/components/Header.jsx": "CÓDIGO COMPLETO",
        ...
    }}
}}""",

        'backend': """Eres el BACKEND AGENT de Melus AI.
Tu trabajo es generar código backend COMPLETO y FUNCIONAL.

REGLAS ESTRICTAS:
1. Genera código COMPLETO - NO usar "...", "// TODO", o placeholders
2. FastAPI o Express según especificación
3. Endpoints RESTful bien estructurados
4. Validación de datos con Pydantic/Joi
5. Manejo de errores robusto
6. Código documentado con docstrings

INSTRUCCIONES ESPECÍFICAS:
{instructions}

CONTEXTO DEL PROYECTO:
{context}

GENERA todos los archivos en formato JSON:
{{
    "files": {{
        "server.py": "CÓDIGO COMPLETO",
        "routes/api.py": "CÓDIGO COMPLETO",
        ...
    }},
    "endpoints": [
        {{"method": "GET", "path": "/api/users", "description": "..."}}
    ]
}}""",

        'database': """Eres el DATABASE AGENT de Melus AI.
Tu trabajo es diseñar esquemas de base de datos COMPLETOS.

REGLAS ESTRICTAS:
1. Esquemas normalizados y optimizados
2. Índices apropiados para consultas frecuentes
3. Relaciones claras entre tablas
4. Datos de prueba (seed data)
5. Migraciones si aplica

INSTRUCCIONES ESPECÍFICAS:
{instructions}

CONTEXTO DEL PROYECTO:
{context}

GENERA en formato JSON:
{{
    "database_type": "postgresql|mongodb|mysql",
    "schemas": {{
        "users": {{
            "fields": {{}},
            "indexes": [],
            "relations": []
        }}
    }},
    "migrations": [],
    "seed_data": {{}}
}}""",

        'integration': """Eres el INTEGRATION AGENT de Melus AI.
Tu trabajo es integrar servicios externos de forma COMPLETA.

SERVICIOS SOPORTADOS:
- Stripe (pagos)
- Google OAuth
- GitHub OAuth
- SendGrid (emails)
- Twilio (SMS)
- Firebase
- AWS S3

REGLAS ESTRICTAS:
1. Código de integración COMPLETO y funcional
2. Manejo de errores y reintentos
3. Variables de entorno para credenciales
4. Documentación de configuración

INSTRUCCIONES ESPECÍFICAS:
{instructions}

CONTEXTO DEL PROYECTO:
{context}

GENERA en formato JSON:
{{
    "files": {{
        "services/stripe.js": "CÓDIGO COMPLETO",
        "services/auth.js": "CÓDIGO COMPLETO"
    }},
    "env_vars": ["STRIPE_KEY", "GOOGLE_CLIENT_ID"],
    "setup_instructions": []
}}""",

        'testing': """Eres el TESTING AGENT de Melus AI.
Tu trabajo es generar tests COMPLETOS y EJECUTABLES.

TIPOS DE TESTS:
1. Unit tests (componentes, funciones)
2. Integration tests (APIs, servicios)
3. E2E tests (flujos de usuario)

REGLAS ESTRICTAS:
1. Usar Jest/Pytest según el stack
2. Cobertura mínima 80%
3. Tests para casos edge
4. Mocks para servicios externos

INSTRUCCIONES ESPECÍFICAS:
{instructions}

CONTEXTO DEL PROYECTO:
{context}

GENERA en formato JSON:
{{
    "files": {{
        "tests/unit/components.test.js": "CÓDIGO COMPLETO",
        "tests/integration/api.test.js": "CÓDIGO COMPLETO"
    }},
    "coverage_config": {{}},
    "test_commands": ["npm test", "pytest"]
}}""",

        'security': """Eres el SECURITY AGENT de Melus AI.
Tu trabajo es analizar y asegurar el código.

VERIFICACIONES:
1. XSS vulnerabilities
2. SQL/NoSQL injection
3. CSRF protection
4. Auth/authorization
5. Secrets exposure
6. Dependencies vulnerabilities

INSTRUCCIONES ESPECÍFICAS:
{instructions}

CONTEXTO DEL PROYECTO:
{context}

GENERA en formato JSON:
{{
    "vulnerabilities": [
        {{"severity": "high|medium|low", "file": "", "issue": "", "fix": ""}}
    ],
    "fixes": {{
        "file.js": "CÓDIGO CORREGIDO"
    }},
    "security_headers": {{}},
    "recommendations": []
}}""",

        'deployment': """Eres el DEPLOYMENT AGENT de Melus AI.
Tu trabajo es configurar despliegue COMPLETO.

PLATAFORMAS SOPORTADAS:
- Vercel
- Netlify
- Railway
- Docker
- AWS
- Google Cloud

REGLAS ESTRICTAS:
1. Configs completas y funcionales
2. CI/CD pipelines
3. Variables de entorno
4. Health checks
5. Logs y monitoreo

INSTRUCCIONES ESPECÍFICAS:
{instructions}

CONTEXTO DEL PROYECTO:
{context}

GENERA en formato JSON:
{{
    "files": {{
        "Dockerfile": "CONTENIDO COMPLETO",
        "docker-compose.yml": "CONTENIDO COMPLETO",
        "vercel.json": "CONTENIDO COMPLETO",
        ".github/workflows/deploy.yml": "CONTENIDO COMPLETO"
    }},
    "deployment_steps": [],
    "env_vars": {{}}
}}"""
    }
    
    prompt_template = base_prompts.get(agent_type, base_prompts['frontend'])
    
    instructions_str = '\n'.join(f"- {i}" for i in (task.instructions if task else []))
    context_str = json.dumps(project_context, indent=2, ensure_ascii=False)
    
    return prompt_template.format(
        instructions=instructions_str or "Generar según contexto del proyecto",
        context=context_str
    )

# Plantilla de ejemplo para usuarios
PROJECT_TEMPLATE = """
# ========================================
# PLANTILLA DE PROYECTO MELUS AI
# Modo Motor (No Chat) - Ejecución Directa
# ========================================

Proyecto: [Nombre de tu proyecto]

Objetivo: [Descripción clara de lo que hace la aplicación]

# FRONTEND AGENT
- Framework: React con TailwindCSS
- Componentes: [Lista de componentes necesarios]
- Páginas: [Home, Dashboard, Login, etc.]
- Funcionalidades: [Formularios, tablas, gráficos, etc.]

# BACKEND AGENT
- Framework: FastAPI / Express
- Endpoints: [CRUD de usuarios, productos, etc.]
- Autenticación: JWT / OAuth2
- Lógica especial: [Notificaciones, cálculos, etc.]

# DATABASE AGENT
- Motor: PostgreSQL / MongoDB
- Tablas: [usuarios, productos, pedidos, etc.]
- Relaciones: [user -> orders, etc.]

# INTEGRATION AGENT
- Stripe: [Pagos, suscripciones]
- OAuth: [Google, GitHub]
- Otros: [SendGrid, Twilio, etc.]

# TESTING AGENT
- Unit tests para componentes
- Integration tests para APIs
- E2E tests para flujos críticos

# SECURITY AGENT
- Validar inputs
- Proteger endpoints sensibles
- Sanitizar datos

# DEPLOYMENT AGENT
- Plataforma: Vercel / Docker / AWS
- CI/CD: GitHub Actions
- Dominio: [tu-dominio.com]

# INSTRUCCIONES ADICIONALES
- No interactuar como chat
- Ejecutar todo automáticamente
- Exportar código completo al finalizar
- Código limpio y documentado
"""

def get_project_template() -> str:
    """Retorna la plantilla de proyecto para usuarios"""
    return PROJECT_TEMPLATE
