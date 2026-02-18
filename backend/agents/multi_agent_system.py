"""
MELUS - Advanced Multi-Agent System
Production-ready agent architecture for universal app generation
"""
from typing import Dict, List, Optional, Any
import json
import re
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AppType(Enum):
    """Application types that Melus can generate"""
    LANDING = "landing"
    SAAS = "saas"
    MARKETPLACE = "marketplace"
    API = "api"
    DASHBOARD = "dashboard"
    AI_TOOL = "ai_tool"
    MOBILE_WEB = "mobile_web"
    ECOMMERCE = "ecommerce"
    BLOG = "blog"
    PORTAL = "portal"
    CRM = "crm"
    CHAT = "chat"
    SOCIAL = "social"
    INVENTORY = "inventory"
    BOOKING = "booking"
    ANALYTICS = "analytics"
    PORTFOLIO = "portfolio"
    TASK_MANAGER = "task_manager"


class Complexity(Enum):
    """Project complexity levels"""
    SIMPLE = "simple"      # 1-3 pages, no auth, no DB
    MEDIUM = "medium"      # 3-7 pages, basic auth, simple DB
    COMPLEX = "complex"    # 7+ pages, full auth, complex DB, integrations


@dataclass
class ProjectClassification:
    """Result of project classification"""
    app_type: AppType
    complexity: Complexity
    requires_auth: bool
    requires_database: bool
    requires_payments: bool
    requires_ai: bool
    requires_realtime: bool
    estimated_pages: List[str]
    main_features: List[str]
    recommended_stack: Dict[str, str]
    estimated_credits: int


# Agent prompts optimized for production
PRODUCTION_AGENT_PROMPTS = {
    "classifier": """You are the Classifier Agent for Melus, an advanced app generation platform.

Analyze the user's request and classify the application type.

CLASSIFICATION RULES:
1. Identify the PRIMARY purpose of the app
2. Detect required features (auth, database, payments, AI, realtime)
3. Estimate complexity based on feature count
4. List expected pages/screens
5. Recommend optimal tech stack

OUTPUT FORMAT (JSON only):
{
    "app_type": "landing|saas|marketplace|api|dashboard|ai_tool|mobile_web|ecommerce|blog|portal|crm|chat|social|inventory|booking|analytics|portfolio|task_manager",
    "complexity": "simple|medium|complex",
    "requires_auth": true/false,
    "requires_database": true/false,
    "requires_payments": true/false,
    "requires_ai": true/false,
    "requires_realtime": true/false,
    "estimated_pages": ["page1", "page2", ...],
    "main_features": ["feature1", "feature2", ...],
    "recommended_stack": {
        "frontend": "react-vite",
        "styling": "tailwind",
        "backend": "express|fastapi|none",
        "database": "postgresql|mongodb|none",
        "auth": "jwt|oauth|none"
    },
    "reasoning": "Brief explanation of classification"
}""",

    "architect": """You are the Architecture Agent for Melus.

Based on the classification, design the complete project structure.

ARCHITECTURE RULES:
1. Follow standard project conventions
2. Separate concerns (components, pages, services, utils)
3. Include configuration files
4. Plan for scalability
5. Include Docker configuration

OUTPUT FORMAT (JSON only):
{
    "project_structure": {
        "frontend/": {
            "src/": {
                "components/": ["Component1.jsx", "Component2.jsx"],
                "pages/": ["Home.jsx", "Dashboard.jsx"],
                "services/": ["api.js", "auth.js"],
                "hooks/": ["useAuth.js"],
                "context/": ["AuthContext.jsx"],
                "utils/": ["helpers.js"],
                "styles/": ["globals.css"]
            },
            "public/": ["index.html", "favicon.ico"],
            "package.json": "dependencies",
            "vite.config.js": "config",
            ".env.example": "env vars"
        },
        "backend/": {
            "src/": {
                "routes/": ["auth.js", "api.js"],
                "models/": ["User.js"],
                "middleware/": ["auth.js"],
                "services/": ["database.js"],
                "utils/": ["helpers.js"]
            },
            "package.json": "dependencies",
            ".env.example": "env vars"
        },
        "docker-compose.yml": "container config",
        "README.md": "documentation"
    },
    "dependencies": {
        "frontend": ["react", "react-dom", "react-router-dom", "axios", "tailwindcss"],
        "backend": ["express", "cors", "dotenv", "jsonwebtoken"]
    },
    "environment_variables": {
        "frontend": ["VITE_API_URL"],
        "backend": ["DATABASE_URL", "JWT_SECRET", "PORT"]
    },
    "docker_services": ["frontend", "backend", "database"]
}""",

    "frontend_builder": """You are the Frontend Builder Agent for Melus.

Generate COMPLETE, PRODUCTION-READY React code.

CRITICAL RULES:
1. Generate COMPLETE code - NO placeholders, NO "// TODO", NO "..."
2. Use React 18+ with functional components and hooks
3. Use React Router v6 syntax: Routes, Route, useNavigate (NOT Switch, useHistory)
4. Use Tailwind CSS with DARK THEME (bg-gray-900, text-white)
5. Include proper error handling and loading states
6. Add accessibility attributes (aria-labels, roles)
7. Use semantic HTML elements
8. Include form validation where needed
9. Add smooth transitions and hover effects

REACT ROUTER V6 SYNTAX:
- <Routes> NOT <Switch>
- <Route path="/" element={<Component />} />
- useNavigate() NOT useHistory()
- <Link to="/path"> for navigation

OUTPUT FORMAT (JSON only):
{
    "files": {
        "src/App.jsx": "COMPLETE_CODE_HERE",
        "src/pages/Home.jsx": "COMPLETE_CODE_HERE",
        "src/components/Header.jsx": "COMPLETE_CODE_HERE"
    }
}

Generate beautiful, modern, production-ready code.""",

    "backend_builder": """You are the Backend Builder Agent for Melus.

Generate COMPLETE, PRODUCTION-READY backend code.

CRITICAL RULES:
1. Generate COMPLETE code - NO placeholders
2. Use Express.js with modern patterns
3. Include proper error handling middleware
4. Add input validation
5. Use async/await consistently
6. Include CORS configuration
7. Add rate limiting for security
8. Structure code in routes, controllers, services

OUTPUT FORMAT (JSON only):
{
    "files": {
        "src/index.js": "COMPLETE_SERVER_CODE",
        "src/routes/auth.js": "COMPLETE_AUTH_ROUTES",
        "src/routes/api.js": "COMPLETE_API_ROUTES",
        "src/middleware/auth.js": "COMPLETE_AUTH_MIDDLEWARE",
        "src/models/User.js": "COMPLETE_USER_MODEL"
    },
    "package_json": {
        "name": "app-backend",
        "scripts": {...},
        "dependencies": {...}
    }
}""",

    "integration": """You are the Integration Agent for Melus.

Connect frontend and backend, fix integration issues.

TASKS:
1. Verify API endpoints match frontend calls
2. Check data flow and state management
3. Ensure error handling is consistent
4. Verify authentication flow
5. Check CORS configuration

OUTPUT FORMAT (JSON only):
{
    "issues_found": ["issue1", "issue2"],
    "fixes": {
        "path/to/file.js": "COMPLETE_FIXED_CODE"
    },
    "api_service": "COMPLETE_API_SERVICE_CODE",
    "integration_notes": ["note1", "note2"]
}""",

    "debug": """You are the Debug Agent for Melus.

Analyze errors and fix code automatically.

DEBUG PROCESS:
1. Parse the error message
2. Identify the root cause
3. Locate the problematic code
4. Generate the complete fixed file
5. Explain the fix

COMMON ISSUES TO CHECK:
- Import/export mismatches
- React Router v5 vs v6 syntax
- Missing dependencies
- Undefined variables
- Async/await issues
- CORS problems

OUTPUT FORMAT (JSON only):
{
    "error_analysis": {
        "error_type": "syntax|runtime|import|dependency",
        "root_cause": "Description of what caused the error",
        "affected_files": ["file1.jsx", "file2.js"]
    },
    "fixes": {
        "path/to/file.jsx": "COMPLETE_FIXED_CODE_HERE"
    },
    "explanation": "Why this fix resolves the issue",
    "prevention_tips": ["tip1", "tip2"]
}

IMPORTANT: Output COMPLETE fixed files, not patches or diffs."""
}


# Base templates for different app types
BASE_TEMPLATES = {
    "react-vite": {
        "package.json": """{
  "name": "{{APP_NAME}}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "vite": "^5.0.0"
  }
}""",
        "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})""",
        "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}""",
        "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}""",
        "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{APP_NAME}}</title>
  </head>
  <body class="bg-gray-900">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",
        "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
        "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-gray-900 text-white antialiased;
}"""
    },
    "express-backend": {
        "package.json": """{
  "name": "{{APP_NAME}}-backend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}""",
        "src/index.js": """import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

export default app;""",
        ".env.example": """PORT=8000
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-secret-key"""
    }
}


# Docker templates for production
DOCKER_TEMPLATES = {
    "docker-compose.yml": """version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/appdb
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
""",
    "frontend/Dockerfile": """FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
""",
    "backend/Dockerfile": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8000
CMD ["node", "src/index.js"]
""",
    "frontend/nginx.conf": """server {
    listen 3000;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
"""
}


def get_agent_prompt(agent_type: str, ultra_mode: bool = False) -> str:
    """Get the appropriate prompt for an agent"""
    base_prompt = PRODUCTION_AGENT_PROMPTS.get(agent_type, "")
    
    if ultra_mode:
        ultra_additions = """

[ULTRA MODE ENABLED - MAXIMUM QUALITY]
Additional requirements:
- Generate exceptionally polished, production-ready code
- Include comprehensive error handling for all edge cases
- Add detailed JSDoc/docstring comments
- Implement full accessibility (WCAG 2.1 AA)
- Add micro-animations and transitions
- Include loading skeletons
- Optimize for performance
- Add proper TypeScript-style prop validation"""
        return base_prompt + ultra_additions
    
    return base_prompt


def get_base_template(template_type: str, app_name: str) -> Dict[str, str]:
    """Get base template files with app name substituted"""
    template = BASE_TEMPLATES.get(template_type, {})
    result = {}
    
    for path, content in template.items():
        result[path] = content.replace("{{APP_NAME}}", app_name)
    
    return result


def get_docker_templates(app_name: str) -> Dict[str, str]:
    """Get Docker configuration templates"""
    result = {}
    for path, content in DOCKER_TEMPLATES.items():
        result[path] = content.replace("{{APP_NAME}}", app_name)
    return result
