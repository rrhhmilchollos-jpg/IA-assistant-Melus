"""
MelusAI - Code Generation Engine
Generates complete projects with all files in a structured directory
"""
import os
import json
import zipfile
import shutil
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Base directory for generated projects
PROJECTS_DIR = Path("/app/generated_projects")
PROJECTS_DIR.mkdir(exist_ok=True)

# ============= PROJECT TEMPLATES =============

TEMPLATES = {
    "react_app": {
        "package.json": '''{
  "name": "{{PROJECT_NAME}}",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}''',
        "public/index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{PROJECT_NAME}}</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>''',
        "src/index.js": '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);''',
        "src/index.css": '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}'''
    },
    
    "html_game": {
        "index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{PROJECT_NAME}}</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div id="game-container"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/phaser/3.60.0/phaser.min.js"></script>
    <script type="module" src="scripts/main.js"></script>
</body>
</html>''',
        "styles/main.css": '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #1a1a2e;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  overflow: hidden;
}

#game-container {
  border: 2px solid #0f3460;
  border-radius: 8px;
  box-shadow: 0 0 30px rgba(15, 52, 96, 0.5);
}

canvas {
  display: block;
}'''
    },
    
    "landing_page": {
        "index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{PROJECT_NAME}}</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div id="app"></div>
    <script src="script.js"></script>
</body>
</html>''',
        "styles.css": '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  line-height: 1.6;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}'''
    }
}


class ProjectGenerator:
    """Generates and manages complete projects"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_project_directory(self, objective_id: str, project_name: str) -> Path:
        """Create a directory for the project"""
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        project_dir = PROJECTS_DIR / f"{safe_name}_{objective_id[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Store project path in objective
        await self.db.orchestrator_objectives.update_one(
            {"id": objective_id},
            {"$set": {"project_path": str(project_dir)}}
        )
        
        return project_dir
    
    async def initialize_project_structure(self, objective_id: str, project_type: str, project_name: str) -> Dict[str, Any]:
        """Initialize project with base template files"""
        project_dir = await self.create_project_directory(objective_id, project_name)
        
        # Select template based on project type
        template_map = {
            "web_app": "react_app",
            "game_2d": "html_game",
            "game_3d": "html_game",
            "mobile_app": "react_app",
            "landing_page": "landing_page"
        }
        
        template_name = template_map.get(project_type, "landing_page")
        template = TEMPLATES.get(template_name, {})
        
        created_files = []
        
        for file_path, content in template.items():
            # Replace placeholders
            content = content.replace("{{PROJECT_NAME}}", project_name)
            
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            created_files.append({
                "path": file_path,
                "content": content,
                "type": "template"
            })
        
        return {
            "project_dir": str(project_dir),
            "files_created": created_files,
            "template_used": template_name
        }
    
    async def save_generated_file(self, objective_id: str, file_path: str, content: str) -> bool:
        """Save a generated file to the project directory"""
        try:
            objective = await self.db.orchestrator_objectives.find_one({"id": objective_id})
            if not objective or not objective.get("project_path"):
                logger.error(f"No project path for objective {objective_id}")
                return False
            
            project_dir = Path(objective["project_path"])
            full_path = project_dir / file_path
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Saved file: {full_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False
    
    async def get_project_files(self, objective_id: str) -> List[Dict[str, Any]]:
        """Get all files in a project directory"""
        objective = await self.db.orchestrator_objectives.find_one({"id": objective_id})
        if not objective or not objective.get("project_path"):
            return []
        
        project_dir = Path(objective["project_path"])
        if not project_dir.exists():
            return []
        
        files = []
        for file_path in project_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_dir)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    files.append({
                        "path": str(relative_path),
                        "content": content,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    files.append({
                        "path": str(relative_path),
                        "content": None,
                        "error": str(e)
                    })
        
        return files
    
    async def create_zip(self, objective_id: str) -> Optional[str]:
        """Create a ZIP file of the project"""
        objective = await self.db.orchestrator_objectives.find_one({"id": objective_id})
        if not objective or not objective.get("project_path"):
            return None
        
        project_dir = Path(objective["project_path"])
        if not project_dir.exists():
            return None
        
        zip_path = PROJECTS_DIR / f"{project_dir.name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)
        
        return str(zip_path)
    
    async def get_preview_url(self, objective_id: str) -> Optional[str]:
        """Get URL to preview the project (for HTML projects)"""
        objective = await self.db.orchestrator_objectives.find_one({"id": objective_id})
        if not objective or not objective.get("project_path"):
            return None
        
        project_dir = Path(objective["project_path"])
        index_path = project_dir / "index.html"
        
        if index_path.exists():
            # Return relative path that can be served
            return f"/api/orchestrator/preview/{objective_id}"
        
        return None


# ============= COMPREHENSIVE CODE GENERATION PROMPTS =============

def get_full_app_prompt(project_type: str, description: str, project_name: str) -> str:
    """Get a comprehensive prompt to generate a complete application"""
    
    base_prompt = f"""Generate a COMPLETE, PRODUCTION-READY application.

Project Name: {project_name}
Project Type: {project_type}
Description: {description}

You MUST generate ALL files needed for a working application. Output as JSON:

{{
    "files": [
        {{"path": "relative/path/to/file.ext", "content": "COMPLETE file content"}}
    ],
    "instructions": "How to run the project"
}}

CRITICAL RULES:
1. Generate COMPLETE code - no placeholders, no TODOs, no "// add code here"
2. Every file must be fully functional
3. Include ALL imports and dependencies
4. Add proper error handling
5. Make it production-ready
6. Use modern best practices
"""
    
    type_specific = {
        "web_app": """
For this React Web Application, generate:
- src/App.jsx - Main application component with full UI
- src/components/*.jsx - All needed components (at least 3-5)
- src/styles/*.css - Complete styling
- src/hooks/*.js - Custom hooks if needed
- src/utils/*.js - Utility functions
- src/api/*.js - API integration if needed

The app should be visually appealing with:
- Modern UI design
- Responsive layout
- Smooth animations
- Professional styling""",
        
        "game_2d": """
For this 2D Game (using Phaser 3), generate:
- scripts/main.js - Game initialization and config
- scripts/scenes/BootScene.js - Asset loading
- scripts/scenes/MenuScene.js - Main menu
- scripts/scenes/GameScene.js - Main gameplay
- scripts/scenes/GameOverScene.js - Game over screen
- scripts/objects/Player.js - Player class
- scripts/objects/Enemy.js - Enemy class (if applicable)
- scripts/utils/constants.js - Game constants

The game should have:
- Complete game loop
- Score system
- Lives/health system
- Game over condition
- Restart functionality
- Basic sound effects (use Web Audio or Phaser audio)""",
        
        "game_3d": """
For this 3D Game (using Three.js), generate:
- scripts/main.js - Three.js initialization
- scripts/scene.js - Scene setup
- scripts/player.js - Player controls
- scripts/environment.js - Environment/level
- scripts/physics.js - Basic physics
- scripts/ui.js - HUD/UI overlay
- scripts/utils.js - Helper functions

The game should have:
- 3D rendering with proper lighting
- Camera controls
- Player movement
- Collision detection
- Score/progress tracking""",
        
        "landing_page": """
For this Landing Page, generate:
- index.html - Complete HTML structure
- styles.css - Full CSS with:
  - Hero section
  - Features section
  - Testimonials (if applicable)
  - CTA sections
  - Footer
  - Responsive design
  - Animations
- script.js - JavaScript for:
  - Smooth scrolling
  - Animations on scroll
  - Interactive elements
  - Form handling (if applicable)

Make it visually stunning with:
- Modern gradient backgrounds
- Professional typography
- Engaging animations
- Mobile-first responsive design""",
        
        "mobile_app": """
For this Mobile-First Web App, generate:
- src/App.jsx - Main app with navigation
- src/screens/*.jsx - All app screens (at least 3-4)
- src/components/*.jsx - Reusable components
- src/styles/*.css - Mobile-optimized styles
- src/hooks/*.js - State management hooks
- src/services/*.js - API/data services

Optimize for mobile:
- Touch-friendly UI
- Bottom navigation
- Swipe gestures
- Mobile-first CSS
- Fast loading"""
    }
    
    return base_prompt + type_specific.get(project_type, type_specific["web_app"])


def get_enhancement_prompt(current_files: List[str], task_type: str, description: str) -> str:
    """Get prompt to enhance/add to existing code"""
    
    return f"""You are enhancing an existing project.

Current files in project: {', '.join(current_files)}

Task: {task_type}
Requirements: {description}

Add or modify files to implement this enhancement. Output as JSON:
{{
    "files": [
        {{"path": "file/path.ext", "content": "COMPLETE file content", "action": "create|update"}}
    ]
}}

Rules:
1. Only output files that need to be created or modified
2. Include COMPLETE file content (not partial updates)
3. Maintain consistency with existing code style
4. Add proper integration with existing components"""
