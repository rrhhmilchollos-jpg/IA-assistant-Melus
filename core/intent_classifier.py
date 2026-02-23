"""
MelusAI Intent Classifier
Classifies user prompts to select appropriate project templates and builders
"""
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of applications that can be generated"""
    WEB_APP = "web_app"
    SAAS_APP = "saas_app"
    ECOMMERCE = "ecommerce"
    LANDING_PAGE = "landing_page"
    DASHBOARD = "dashboard"
    API_SERVICE = "api_service"
    MOBILE_APP = "mobile_app"
    PORTFOLIO = "portfolio"
    BLOG = "blog"
    GAME_2D = "game2d"
    GAME_3D = "game3d"
    UNKNOWN = "unknown"


class ComplexityLevel(Enum):
    """Complexity levels for projects"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


@dataclass
class IntentResult:
    """Result of intent classification"""
    intent_type: IntentType
    confidence: float
    complexity: ComplexityLevel
    features: List[str]
    recommended_template: str
    recommended_builder: str
    extracted_entities: Dict[str, any]
    reasoning: str


class IntentClassifier:
    """
    Classifies user prompts to determine:
    1. What type of application they want
    2. What features they need
    3. Which template to use
    4. Which builder module should handle it
    """
    
    # Intent patterns with keywords and weights
    INTENT_PATTERNS: Dict[IntentType, Dict[str, List[str]]] = {
        IntentType.ECOMMERCE: {
            "keywords": [
                "tienda", "store", "shop", "ecommerce", "e-commerce",
                "carrito", "cart", "productos", "products", "venta",
                "checkout", "pago", "payment", "inventario", "inventory",
                "catálogo", "catalog", "orden", "order"
            ],
            "phrases": [
                "tienda online", "vender productos", "carrito de compras",
                "pasarela de pago", "online store", "sell products"
            ]
        },
        IntentType.SAAS_APP: {
            "keywords": [
                "saas", "suscripción", "subscription", "usuarios", "users",
                "planes", "plans", "dashboard", "analytics", "admin",
                "workspace", "team", "equipo", "billing", "facturación",
                "api", "integración", "multi-tenant", "inquilino"
            ],
            "phrases": [
                "software as a service", "plataforma saas", "gestión de usuarios",
                "panel de control", "sistema de suscripción"
            ]
        },
        IntentType.LANDING_PAGE: {
            "keywords": [
                "landing", "página de aterrizaje", "marketing", "conversión",
                "cta", "call to action", "hero", "presentación", "promoción"
            ],
            "phrases": [
                "landing page", "página de destino", "captar leads",
                "página de producto", "página promocional"
            ]
        },
        IntentType.DASHBOARD: {
            "keywords": [
                "dashboard", "panel", "métricas", "metrics", "gráficos",
                "charts", "reportes", "reports", "estadísticas", "analytics",
                "kpi", "indicadores", "monitoreo", "monitoring"
            ],
            "phrases": [
                "panel de control", "visualización de datos", "dashboard admin",
                "tablero de métricas", "centro de control"
            ]
        },
        IntentType.BLOG: {
            "keywords": [
                "blog", "artículos", "articles", "posts", "publicaciones",
                "cms", "contenido", "content", "editor", "markdown",
                "categorías", "tags", "etiquetas"
            ],
            "phrases": [
                "sistema de blog", "gestión de contenido", "publicar artículos",
                "blog personal", "blog empresarial"
            ]
        },
        IntentType.PORTFOLIO: {
            "keywords": [
                "portfolio", "portafolio", "proyectos", "projects", "trabajos",
                "galería", "gallery", "cv", "curriculum", "perfil"
            ],
            "phrases": [
                "portafolio personal", "mostrar proyectos", "portfolio web",
                "sitio personal", "cv online"
            ]
        },
        IntentType.API_SERVICE: {
            "keywords": [
                "api", "rest", "graphql", "endpoint", "servicio", "service",
                "backend", "microservicio", "webhook"
            ],
            "phrases": [
                "api rest", "servicio web", "backend api", "microservicio"
            ]
        },
        IntentType.WEB_APP: {
            "keywords": [
                "app", "aplicación", "application", "web", "sistema",
                "plataforma", "platform", "herramienta", "tool"
            ],
            "phrases": [
                "aplicación web", "web app", "sistema web", "plataforma web"
            ]
        }
    }
    
    # Feature detection patterns
    FEATURE_PATTERNS: Dict[str, List[str]] = {
        "authentication": [
            "auth", "login", "registro", "register", "usuario", "user",
            "sesión", "session", "oauth", "google", "facebook", "contraseña"
        ],
        "payments": [
            "pago", "payment", "stripe", "paypal", "tarjeta", "card",
            "checkout", "suscripción", "subscription", "factura", "invoice"
        ],
        "database": [
            "base de datos", "database", "db", "sql", "mongodb", "postgres",
            "almacenar", "store", "guardar", "save", "persistir"
        ],
        "file_upload": [
            "subir archivos", "upload", "imagen", "image", "archivo", "file",
            "documento", "document", "media", "fotos", "photos"
        ],
        "real_time": [
            "tiempo real", "real-time", "websocket", "chat", "notificaciones",
            "notifications", "live", "en vivo", "streaming"
        ],
        "search": [
            "búsqueda", "search", "filtro", "filter", "buscar", "encontrar"
        ],
        "crud": [
            "crear", "create", "leer", "read", "actualizar", "update",
            "eliminar", "delete", "listar", "list", "editar", "edit"
        ],
        "responsive": [
            "responsive", "móvil", "mobile", "tablet", "adaptable"
        ],
        "api_integration": [
            "api", "integración", "integration", "conectar", "connect",
            "terceros", "third-party", "externa", "external"
        ],
        "analytics": [
            "analytics", "métricas", "metrics", "estadísticas", "statistics",
            "reportes", "reports", "gráficos", "charts"
        ]
    }
    
    # Template mapping
    TEMPLATE_MAP: Dict[IntentType, Dict[str, str]] = {
        IntentType.ECOMMERCE: {
            "simple": "ecommerce-basic",
            "medium": "ecommerce-pro",
            "complex": "ecommerce-enterprise",
            "enterprise": "ecommerce-marketplace"
        },
        IntentType.SAAS_APP: {
            "simple": "saas-starter",
            "medium": "saas-pro",
            "complex": "saas-enterprise",
            "enterprise": "saas-platform"
        },
        IntentType.LANDING_PAGE: {
            "simple": "landing-minimal",
            "medium": "landing-sections",
            "complex": "landing-animated",
            "enterprise": "landing-enterprise"
        },
        IntentType.DASHBOARD: {
            "simple": "dashboard-basic",
            "medium": "dashboard-analytics",
            "complex": "dashboard-admin",
            "enterprise": "dashboard-enterprise"
        },
        IntentType.BLOG: {
            "simple": "blog-minimal",
            "medium": "blog-full",
            "complex": "blog-cms",
            "enterprise": "blog-magazine"
        },
        IntentType.PORTFOLIO: {
            "simple": "portfolio-minimal",
            "medium": "portfolio-creative",
            "complex": "portfolio-agency",
            "enterprise": "portfolio-studio"
        },
        IntentType.API_SERVICE: {
            "simple": "api-basic",
            "medium": "api-documented",
            "complex": "api-enterprise",
            "enterprise": "api-platform"
        },
        IntentType.WEB_APP: {
            "simple": "webapp-basic",
            "medium": "webapp-full",
            "complex": "webapp-advanced",
            "enterprise": "webapp-enterprise"
        }
    }
    
    # Builder mapping
    BUILDER_MAP: Dict[IntentType, str] = {
        IntentType.ECOMMERCE: "ecommerce-builder",
        IntentType.SAAS_APP: "saas-builder",
        IntentType.LANDING_PAGE: "web-builder",
        IntentType.DASHBOARD: "web-builder",
        IntentType.BLOG: "web-builder",
        IntentType.PORTFOLIO: "web-builder",
        IntentType.API_SERVICE: "api-builder",
        IntentType.WEB_APP: "web-builder",
        IntentType.MOBILE_APP: "mobile-builder",
        IntentType.UNKNOWN: "web-builder"
    }
    
    def __init__(self):
        self.history: List[IntentResult] = []
    
    def classify(self, prompt: str) -> IntentResult:
        """
        Classify a user prompt and return intent analysis
        """
        prompt_lower = prompt.lower()
        
        # Calculate scores for each intent type
        scores: Dict[IntentType, float] = {}
        
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            score = 0.0
            
            # Check keywords
            keywords = patterns.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in prompt_lower:
                    score += 1.0
            
            # Check phrases (higher weight)
            phrases = patterns.get("phrases", [])
            for phrase in phrases:
                if phrase.lower() in prompt_lower:
                    score += 2.0
            
            scores[intent_type] = score
        
        # Find the best matching intent
        best_intent = max(scores.items(), key=lambda x: x[1])
        intent_type = best_intent[0] if best_intent[1] > 0 else IntentType.WEB_APP
        
        # Calculate confidence
        total_score = sum(scores.values())
        confidence = best_intent[1] / total_score if total_score > 0 else 0.5
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        # If no clear winner, default to WEB_APP with lower confidence
        if best_intent[1] == 0:
            intent_type = IntentType.WEB_APP
            confidence = 0.5
        
        # Detect features
        features = self._detect_features(prompt_lower)
        
        # Determine complexity
        complexity = self._determine_complexity(prompt_lower, features)
        
        # Get recommended template
        templates = self.TEMPLATE_MAP.get(intent_type, self.TEMPLATE_MAP[IntentType.WEB_APP])
        recommended_template = templates.get(complexity.value, templates["medium"])
        
        # Get recommended builder
        recommended_builder = self.BUILDER_MAP.get(intent_type, "web-builder")
        
        # Extract entities
        entities = self._extract_entities(prompt)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(intent_type, features, complexity, confidence)
        
        result = IntentResult(
            intent_type=intent_type,
            confidence=confidence,
            complexity=complexity,
            features=features,
            recommended_template=recommended_template,
            recommended_builder=recommended_builder,
            extracted_entities=entities,
            reasoning=reasoning
        )
        
        self.history.append(result)
        logger.info(f"Classified prompt: {intent_type.value} (confidence: {confidence:.2f})")
        
        return result
    
    def _detect_features(self, prompt_lower: str) -> List[str]:
        """Detect required features from the prompt"""
        detected = []
        
        for feature, keywords in self.FEATURE_PATTERNS.items():
            for keyword in keywords:
                if keyword.lower() in prompt_lower:
                    if feature not in detected:
                        detected.append(feature)
                    break
        
        return detected
    
    def _determine_complexity(self, prompt_lower: str, features: List[str]) -> ComplexityLevel:
        """Determine project complexity based on prompt and features"""
        # Word count complexity
        word_count = len(prompt_lower.split())
        
        # Feature count complexity
        feature_count = len(features)
        
        # Calculate complexity score
        score = 0
        
        # Word count impact
        if word_count > 100:
            score += 3
        elif word_count > 50:
            score += 2
        elif word_count > 20:
            score += 1
        
        # Feature count impact
        score += feature_count
        
        # Check for enterprise keywords
        enterprise_keywords = [
            "enterprise", "empresarial", "escala", "scale", "multi-tenant",
            "microservicios", "microservices", "alta disponibilidad"
        ]
        for kw in enterprise_keywords:
            if kw in prompt_lower:
                score += 2
        
        # Determine level
        if score >= 8:
            return ComplexityLevel.ENTERPRISE
        elif score >= 5:
            return ComplexityLevel.COMPLEX
        elif score >= 2:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.SIMPLE
    
    def _extract_entities(self, prompt: str) -> Dict[str, any]:
        """Extract named entities from the prompt"""
        entities = {}
        
        # Extract potential app name (quoted text)
        name_match = re.search(r'["\']([^"\']+)["\']', prompt)
        if name_match:
            entities["app_name"] = name_match.group(1)
        
        # Extract numbers (for quantities, prices, etc.)
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Extract colors mentioned
        colors = re.findall(r'\b(rojo|azul|verde|negro|blanco|gris|red|blue|green|black|white|gray|purple|cyan)\b', prompt.lower())
        if colors:
            entities["colors"] = list(set(colors))
        
        # Extract tech stack mentions
        tech_patterns = [
            "react", "vue", "angular", "next", "nuxt", "svelte",
            "python", "node", "django", "fastapi", "express",
            "postgres", "mongodb", "mysql", "redis",
            "tailwind", "bootstrap", "material"
        ]
        tech_found = [t for t in tech_patterns if t in prompt.lower()]
        if tech_found:
            entities["tech_stack"] = tech_found
        
        return entities
    
    def _generate_reasoning(
        self,
        intent_type: IntentType,
        features: List[str],
        complexity: ComplexityLevel,
        confidence: float
    ) -> str:
        """Generate explanation of classification decision"""
        reasoning_parts = []
        
        # Intent reasoning
        intent_names = {
            IntentType.ECOMMERCE: "tienda online/e-commerce",
            IntentType.SAAS_APP: "aplicación SaaS",
            IntentType.LANDING_PAGE: "landing page",
            IntentType.DASHBOARD: "dashboard/panel de control",
            IntentType.BLOG: "blog/sistema de contenido",
            IntentType.PORTFOLIO: "portfolio/portafolio",
            IntentType.API_SERVICE: "servicio API",
            IntentType.WEB_APP: "aplicación web",
            IntentType.MOBILE_APP: "aplicación móvil"
        }
        
        reasoning_parts.append(
            f"Tipo detectado: {intent_names.get(intent_type, 'aplicación web')} "
            f"(confianza: {confidence*100:.0f}%)"
        )
        
        # Features reasoning
        if features:
            reasoning_parts.append(f"Características requeridas: {', '.join(features)}")
        
        # Complexity reasoning
        complexity_names = {
            ComplexityLevel.SIMPLE: "simple",
            ComplexityLevel.MEDIUM: "medio",
            ComplexityLevel.COMPLEX: "complejo",
            ComplexityLevel.ENTERPRISE: "empresarial"
        }
        reasoning_parts.append(f"Nivel de complejidad: {complexity_names.get(complexity, 'medio')}")
        
        return " | ".join(reasoning_parts)


# Singleton instance
_classifier_instance: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get or create the singleton IntentClassifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()
    return _classifier_instance
