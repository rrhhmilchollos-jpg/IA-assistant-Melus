"""
MelusAI Brain Engine
Sistema de clasificación de intención y selección de arquitectura
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import re
import os
import json
import logging

logger = logging.getLogger(__name__)


class ProjectType(str, Enum):
    WEB = "web"
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    GAME_2D = "game2d"
    GAME_3D = "game3d"
    MOBILE_APP = "mobile"
    API = "api"
    DASHBOARD = "dashboard"
    BLOG = "blog"
    PORTFOLIO = "portfolio"


class Architecture(str, Enum):
    NEXTJS_CMS = "nextjs_cms"
    NEXTJS_ECOMMERCE = "nextjs_ecommerce"
    SAAS_FULLSTACK = "saas_fullstack"
    PHASER_GAME = "phaser_game"
    THREEJS_GAME = "threejs_game"
    REACT_DASHBOARD = "react_dashboard"
    REACT_PORTFOLIO = "react_portfolio"
    FASTAPI_API = "fastapi_api"


@dataclass
class ProjectRequirements:
    """Extracted requirements from user prompt"""
    project_type: ProjectType
    architecture: Architecture
    name: str
    description: str
    features: List[str]
    monetization: Optional[str]
    target_audience: Optional[str]
    scale: str  # small, medium, large
    integrations: List[str]
    has_auth: bool
    has_payments: bool
    has_admin: bool
    has_analytics: bool
    is_multilingual: bool
    is_subscription: bool


# ============= INTENT CLASSIFICATION =============

# Keywords for each project type
PROJECT_KEYWORDS = {
    ProjectType.ECOMMERCE: [
        "tienda", "store", "shop", "ecommerce", "e-commerce", "vender", "productos",
        "carrito", "cart", "checkout", "pagos", "payments", "comprar", "buy",
        "inventario", "inventory", "catalogo", "catalog"
    ],
    ProjectType.SAAS: [
        "saas", "software", "plataforma", "platform", "suscripcion", "subscription",
        "usuarios", "users", "planes", "plans", "facturacion", "billing", "api",
        "dashboard", "panel", "admin", "roles", "permisos"
    ],
    ProjectType.GAME_2D: [
        "juego 2d", "game 2d", "2d game", "platformer", "arcade", "puzzle",
        "pixel", "sprite", "phaser", "canvas"
    ],
    ProjectType.GAME_3D: [
        "juego 3d", "game 3d", "3d game", "three.js", "threejs", "webgl",
        "3d", "unity", "unreal"
    ],
    ProjectType.DASHBOARD: [
        "dashboard", "panel", "analytics", "metricas", "graficos", "charts",
        "reportes", "reports", "admin panel", "backoffice"
    ],
    ProjectType.BLOG: [
        "blog", "articulos", "articles", "posts", "contenido", "content",
        "cms", "editor", "publicar", "publish"
    ],
    ProjectType.PORTFOLIO: [
        "portfolio", "portafolio", "cv", "curriculum", "personal", "freelance",
        "proyectos", "works", "showcase"
    ],
    ProjectType.API: [
        "api", "rest", "graphql", "backend", "endpoints", "microservicio"
    ],
    ProjectType.MOBILE_APP: [
        "app movil", "mobile app", "android", "ios", "react native", "flutter"
    ],
    ProjectType.WEB: [
        "web", "sitio", "website", "pagina", "landing", "empresa", "business"
    ]
}

# Feature keywords
FEATURE_KEYWORDS = {
    "auth": ["login", "registro", "usuarios", "autenticacion", "auth", "sesion", "cuenta"],
    "payments": ["pagos", "stripe", "paypal", "tarjeta", "pagar", "cobrar", "factura"],
    "admin": ["admin", "administrador", "panel", "backoffice", "gestion"],
    "analytics": ["analytics", "metricas", "estadisticas", "graficos", "reportes"],
    "multilingual": ["idiomas", "multilenguaje", "internacional", "traduccion", "i18n"],
    "subscription": ["suscripcion", "planes", "mensual", "anual", "premium", "pro"],
    "realtime": ["tiempo real", "realtime", "websocket", "chat", "notificaciones"],
    "search": ["busqueda", "search", "filtros", "buscar"],
    "social": ["social", "compartir", "likes", "comentarios", "seguidores"],
    "email": ["email", "correo", "newsletter", "notificaciones"]
}

# Architecture mapping
ARCHITECTURE_MAP = {
    ProjectType.ECOMMERCE: Architecture.NEXTJS_ECOMMERCE,
    ProjectType.SAAS: Architecture.SAAS_FULLSTACK,
    ProjectType.GAME_2D: Architecture.PHASER_GAME,
    ProjectType.GAME_3D: Architecture.THREEJS_GAME,
    ProjectType.DASHBOARD: Architecture.REACT_DASHBOARD,
    ProjectType.BLOG: Architecture.NEXTJS_CMS,
    ProjectType.PORTFOLIO: Architecture.REACT_PORTFOLIO,
    ProjectType.API: Architecture.FASTAPI_API,
    ProjectType.WEB: Architecture.NEXTJS_CMS,
    ProjectType.MOBILE_APP: Architecture.SAAS_FULLSTACK
}


class BrainEngine:
    """
    Central brain for MelusAI
    Handles intent classification and architecture selection
    """
    
    def __init__(self):
        self.llm_available = True
    
    def classify_intent(self, prompt: str) -> ProjectType:
        """Classify user intent into project type"""
        prompt_lower = prompt.lower()
        
        # Score each project type
        scores = {}
        for project_type, keywords in PROJECT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in prompt_lower)
            scores[project_type] = score
        
        # Get highest scoring type
        max_score = max(scores.values())
        if max_score > 0:
            for pt, score in scores.items():
                if score == max_score:
                    return pt
        
        # Default to web
        return ProjectType.WEB
    
    def extract_features(self, prompt: str) -> Dict[str, bool]:
        """Extract required features from prompt"""
        prompt_lower = prompt.lower()
        features = {}
        
        for feature, keywords in FEATURE_KEYWORDS.items():
            features[feature] = any(kw in prompt_lower for kw in keywords)
        
        return features
    
    def determine_scale(self, prompt: str) -> str:
        """Determine project scale"""
        prompt_lower = prompt.lower()
        
        large_indicators = ["empresa", "enterprise", "grande", "escalable", "millones", "internacional"]
        small_indicators = ["simple", "basico", "pequeno", "personal", "mvp", "prototipo"]
        
        if any(ind in prompt_lower for ind in large_indicators):
            return "large"
        elif any(ind in prompt_lower for ind in small_indicators):
            return "small"
        return "medium"
    
    def extract_integrations(self, prompt: str) -> List[str]:
        """Extract required integrations"""
        prompt_lower = prompt.lower()
        integrations = []
        
        integration_map = {
            "stripe": ["stripe", "pagos con tarjeta"],
            "paypal": ["paypal"],
            "google_auth": ["google login", "gmail", "google auth"],
            "facebook": ["facebook", "meta"],
            "twilio": ["sms", "twilio", "whatsapp"],
            "sendgrid": ["email", "sendgrid", "correo"],
            "aws_s3": ["archivos", "imagenes", "storage", "s3"],
            "firebase": ["firebase", "notificaciones push"],
            "analytics": ["google analytics", "analytics"],
            "maps": ["mapas", "google maps", "ubicacion"]
        }
        
        for integration, keywords in integration_map.items():
            if any(kw in prompt_lower for kw in keywords):
                integrations.append(integration)
        
        return integrations
    
    def analyze(self, prompt: str) -> ProjectRequirements:
        """Full analysis of user prompt"""
        project_type = self.classify_intent(prompt)
        features = self.extract_features(prompt)
        scale = self.determine_scale(prompt)
        integrations = self.extract_integrations(prompt)
        architecture = ARCHITECTURE_MAP.get(project_type, Architecture.NEXTJS_CMS)
        
        # Generate project name from prompt
        words = prompt.split()[:3]
        name = "-".join(w.lower() for w in words if w.isalnum())[:20] or "mi-proyecto"
        
        return ProjectRequirements(
            project_type=project_type,
            architecture=architecture,
            name=name,
            description=prompt,
            features=list(features.keys()),
            monetization="subscription" if features.get("subscription") else ("payments" if features.get("payments") else None),
            target_audience=None,
            scale=scale,
            integrations=integrations,
            has_auth=features.get("auth", False) or project_type in [ProjectType.SAAS, ProjectType.ECOMMERCE],
            has_payments=features.get("payments", False) or project_type == ProjectType.ECOMMERCE,
            has_admin=features.get("admin", False) or project_type in [ProjectType.SAAS, ProjectType.ECOMMERCE],
            has_analytics=features.get("analytics", False) or project_type in [ProjectType.SAAS, ProjectType.DASHBOARD],
            is_multilingual=features.get("multilingual", False),
            is_subscription=features.get("subscription", False)
        )
    
    def get_architecture_config(self, requirements: ProjectRequirements) -> Dict:
        """Get architecture configuration based on requirements"""
        configs = {
            Architecture.NEXTJS_ECOMMERCE: {
                "framework": "Next.js 14",
                "styling": "TailwindCSS",
                "database": "PostgreSQL",
                "auth": "NextAuth.js",
                "payments": "Stripe",
                "features": ["Product catalog", "Shopping cart", "Checkout", "Order management", "Admin panel"],
                "stack": ["React", "TypeScript", "Prisma", "Stripe SDK"]
            },
            Architecture.SAAS_FULLSTACK: {
                "framework": "Next.js 14",
                "styling": "TailwindCSS",
                "database": "PostgreSQL",
                "auth": "NextAuth.js + JWT",
                "payments": "Stripe Subscriptions",
                "features": ["User management", "Subscription plans", "Dashboard", "API", "Admin"],
                "stack": ["React", "TypeScript", "Prisma", "Stripe", "Redis"]
            },
            Architecture.PHASER_GAME: {
                "framework": "Phaser 3",
                "styling": "Canvas",
                "database": "None",
                "features": ["Game engine", "Physics", "Animations", "Sound", "Leaderboard"],
                "stack": ["TypeScript", "Phaser 3", "Webpack"]
            },
            Architecture.THREEJS_GAME: {
                "framework": "Three.js",
                "styling": "WebGL",
                "database": "None",
                "features": ["3D rendering", "Physics", "Controls", "Lighting"],
                "stack": ["TypeScript", "Three.js", "Cannon.js"]
            },
            Architecture.REACT_DASHBOARD: {
                "framework": "React + Vite",
                "styling": "TailwindCSS",
                "database": "PostgreSQL",
                "features": ["Charts", "Tables", "Filters", "Export", "Real-time"],
                "stack": ["React", "TypeScript", "Recharts", "TanStack Table"]
            },
            Architecture.REACT_PORTFOLIO: {
                "framework": "React + Vite",
                "styling": "TailwindCSS + Framer Motion",
                "database": "None",
                "features": ["Projects showcase", "Contact form", "Animations"],
                "stack": ["React", "TypeScript", "Framer Motion"]
            },
            Architecture.NEXTJS_CMS: {
                "framework": "Next.js 14",
                "styling": "TailwindCSS",
                "database": "PostgreSQL",
                "features": ["Blog", "Pages", "SEO", "Admin"],
                "stack": ["React", "TypeScript", "MDX", "Prisma"]
            },
            Architecture.FASTAPI_API: {
                "framework": "FastAPI",
                "styling": "N/A",
                "database": "PostgreSQL",
                "features": ["REST API", "OpenAPI docs", "Authentication", "Rate limiting"],
                "stack": ["Python", "FastAPI", "SQLAlchemy", "Pydantic"]
            }
        }
        
        return configs.get(requirements.architecture, configs[Architecture.NEXTJS_CMS])


# Global instance
brain_engine = BrainEngine()

def get_brain() -> BrainEngine:
    return brain_engine
