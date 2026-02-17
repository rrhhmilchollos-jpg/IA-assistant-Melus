# Available AI Models
AI_MODELS = {
    "gpt-4o": {
        "name": "GPT-4o",
        "provider": "openai",
        "description": "Más rápido y económico",
        "popular": True
    },
    "gpt-5.1": {
        "name": "GPT-5.1",
        "provider": "openai",
        "description": "El más avanzado de OpenAI",
        "popular": False
    },
    "claude-sonnet-4-5": {
        "name": "Claude Sonnet 4.5",
        "provider": "anthropic",
        "description": "Excelente para análisis",
        "popular": False
    },
    "gemini-2.5-pro": {
        "name": "Gemini 2.5 Pro",
        "provider": "gemini",
        "description": "Potente modelo de Google",
        "popular": False
    }
}

DEFAULT_MODEL = "gpt-4o"

# Admin emails
ADMIN_EMAILS = ["rrhh.milchollos@gmail.com"]

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "credits_per_month": 100,
        "features": [
            "100 créditos/mes",
            "Chat básico",
            "1 proyecto activo"
        ],
        "popular": False
    },
    "pro": {
        "name": "Pro",
        "price": 29.99,
        "credits_per_month": 5000,
        "features": [
            "5,000 créditos/mes",
            "Todos los agentes IA",
            "Proyectos ilimitados",
            "Soporte prioritario",
            "Exportación de código"
        ],
        "popular": True,
        "stripe_price_id": "price_pro_monthly"
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 99.99,
        "credits_per_month": 25000,
        "features": [
            "25,000 créditos/mes",
            "API dedicada",
            "Agentes personalizados",
            "Despliegue automático",
            "Soporte 24/7",
            "SLA garantizado"
        ],
        "popular": False,
        "stripe_price_id": "price_enterprise_monthly"
    }
}

# Credit packages configuration
CREDIT_PACKAGES = {
    "package_100": {
        "name": "100 créditos",
        "credits": 100,
        "price": 20.00,
        "popular": False,
        "bonus": 0
    },
    "package_250": {
        "name": "250 créditos",
        "credits": 250,
        "price": 50.00,
        "popular": False,
        "bonus": 0
    },
    "package_500": {
        "name": "500 créditos",
        "credits": 500,
        "price": 100.00,
        "popular": True,
        "bonus": 0
    },
    "package_3000": {
        "name": "3000 créditos",
        "credits": 3000,
        "price": 500.00,
        "popular": False,
        "bonus": 500,
        "base_credits": 2500
    },
    "package_6000": {
        "name": "6000 créditos",
        "credits": 6000,
        "price": 1000.00,
        "popular": False,
        "bonus": 1000,
        "base_credits": 5000
    }
}

# Promo codes
PROMO_CODES = {
    "VALENTINE20": {
        "discount": 0.20,
        "min_amount": 100.00,
        "active": True
    },
    "WELCOME10": {
        "discount": 0.10,
        "min_amount": 20.00,
        "active": True
    }
}

# Free credits for new users
FREE_CREDITS = 1000

# Credit to dollar ratio
CREDITS_PER_DOLLAR = 5

# Agent costs (credits per action)
AGENT_COSTS = {
    "orchestrator": 50,
    "design": 100,
    "frontend": 150,
    "backend": 150,
    "database": 100,
    "deploy": 200,
    "chat": 50
}