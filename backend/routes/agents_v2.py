"""Enhanced Multi-Agent System with Real Code Generation for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import logging
import os
import json
import re
import asyncio
import io
import zipfile
from datetime import datetime

from utils import generate_id, utc_now, get_authenticated_user
from emergentintegrations.llm.chat import LlmChat, UserMessage
from templates.app_templates import get_template, get_all_templates, TEMPLATES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/v2", tags=["agents-v2"])

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Agent costs
AGENT_COSTS = {
    "classifier": 25,
    "architect": 50,
    "frontend": 150,
    "backend": 150,
    "integrator": 75,
    "debugger": 50
}

# Enhanced Agent Prompts for Real Code Generation
AGENT_PROMPTS = {
    "classifier": """You are the Classifier Agent. Analyze the user's app request and classify it.

Output JSON only:
{
    "app_type": "landing|saas|dashboard|marketplace|api|blog|ecommerce|portfolio|tool",
    "complexity": "simple|medium|complex",
    "requires_auth": boolean,
    "requires_database": boolean,
    "requires_payments": boolean,
    "requires_ai": boolean,
    "main_features": ["feature1", "feature2"],
    "tech_stack": {
        "frontend": "react",
        "styling": "tailwind",
        "backend": "express|fastapi|none",
        "database": "mongodb|postgresql|none"
    },
    "estimated_pages": ["page1", "page2"],
    "summary": "Brief description"
}""",

    "architect": """You are the Architect Agent. Design the complete file structure for the application.

Based on the classification, output JSON:
{
    "structure": {
        "src/App.jsx": "Main app component",
        "src/components/Header.jsx": "Header component",
        "src/pages/Home.jsx": "Home page",
        ...
    },
    "dependencies": ["react", "react-dom", "react-router-dom"],
    "routes": [
        {"path": "/", "component": "Home", "protected": false},
        {"path": "/dashboard", "component": "Dashboard", "protected": true}
    ],
    "data_models": [
        {"name": "User", "fields": ["id", "email", "name"]}
    ]
}""",

    "frontend": """You are the Frontend Agent. Generate complete, working React code.

CRITICAL RULES:
1. Generate COMPLETE, WORKING code - no placeholders or "// TODO"
2. Use React functional components with hooks (useState, useEffect, useContext)
3. Use Tailwind CSS for styling - DARK THEME (bg-gray-900, text-white, etc.)
4. Make UI modern, polished, and beautiful
5. Include proper state management with Context API
6. Use React Router v6 syntax: Routes, Route, NOT Switch
7. For routing use: import { BrowserRouter, Routes, Route } from 'react-router-dom'

IMPORTANT - React Router v6 syntax:
- Use <Routes> instead of <Switch>
- Use <Route path="/" element={<Component />} /> NOT <Route component={Component} />
- Use useNavigate() for navigation, NOT useHistory()

Output JSON with COMPLETE file contents:
{
    "files": {
        "src/App.jsx": "COMPLETE CODE HERE",
        "src/components/Header.jsx": "COMPLETE CODE HERE",
        "src/pages/Home.jsx": "COMPLETE CODE HERE"
    }
}

Generate beautiful, production-ready React code.""",

    "backend": """You are the Backend Agent. Generate complete API code.

Output JSON:
{
    "files": {
        "server.js": "COMPLETE EXPRESS CODE",
        "routes/api.js": "COMPLETE ROUTE CODE",
        "models/User.js": "COMPLETE MODEL CODE"
    },
    "env_vars": ["DATABASE_URL", "JWT_SECRET"],
    "endpoints": [
        {"method": "GET", "path": "/api/users", "description": "Get all users"}
    ]
}""",

    "integrator": """You are the Integrator Agent. Connect frontend to backend and fix integration issues.

Check:
1. API calls match backend endpoints
2. Data flow is correct
3. Error handling exists
4. Loading states work

Output JSON:
{
    "fixes": {
        "src/services/api.js": "COMPLETE API SERVICE CODE"
    },
    "integration_notes": ["Note about integration"]
}""",

    "debugger": """You are the Debug Agent. Find and fix errors in the code.

Analyze the error and code, then output:
{
    "error_analysis": "What caused the error",
    "fixes": {
        "path/to/file.jsx": "CORRECTED COMPLETE CODE"
    },
    "explanation": "Why this fix works"
}

IMPORTANT: Output complete fixed files, not patches."""
}


async def run_agent_v2(
    agent_type: str, 
    task: str, 
    context: dict, 
    db,
    workspace_id: str = None,
    ultra_mode: bool = False
) -> dict:
    """Execute an agent and optionally broadcast progress"""
    from routes.workspace import get_connection_manager
    
    if agent_type not in AGENT_PROMPTS:
        raise ValueError(f"Unknown agent: {agent_type}")
    
    manager = get_connection_manager()
    
    # Broadcast start
    if workspace_id:
        await manager.broadcast(workspace_id, {
            "type": "agent_start",
            "agent": agent_type,
            "task": task[:100],
            "ultra_mode": ultra_mode
        })
    
    try:
        # Ultra mode uses more powerful model and enhanced prompts
        system_prompt = AGENT_PROMPTS[agent_type]
        if ultra_mode:
            system_prompt = f"""[ULTRA MODE - MAXIMUM QUALITY]

{system_prompt}

ULTRA MODE REQUIREMENTS:
- Generate exceptionally high-quality, production-ready code
- Include comprehensive error handling
- Add detailed comments explaining complex logic
- Use best practices and modern patterns
- Ensure accessibility (ARIA labels, semantic HTML)
- Add loading states and smooth animations
- Include form validation where applicable"""
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"agent_{agent_type}_{generate_id('t')}",
            system_message=system_prompt
        )
        
        # Ultra mode uses gpt-4o, regular uses gpt-4o-mini for cost savings
        model = "gpt-4o" if ultra_mode else "gpt-4o"
        chat.with_model("openai", model)
        
        # Build comprehensive prompt
        context_str = json.dumps(context, indent=2, default=str) if context else "{}"
        prompt = f"""Task: {task}

Context:
{context_str}

Generate your response as valid JSON."""

        response = await chat.send_message(UserMessage(text=prompt))
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"raw_response": response}
        
        # Broadcast completion
        if workspace_id:
            await manager.broadcast(workspace_id, {
                "type": "agent_complete",
                "agent": agent_type,
                "success": True
            })
        
        return {
            "agent": agent_type,
            "result": result,
            "credits_used": AGENT_COSTS.get(agent_type, 50),
            "timestamp": utc_now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent {agent_type} failed: {e}")
        
        if workspace_id:
            await manager.broadcast(workspace_id, {
                "type": "agent_error",
                "agent": agent_type,
                "error": str(e)
            })
        
        raise


@router.post("/generate")
async def generate_app_v2(request: Request):
    """Generate a complete application with live preview"""
    from routes.workspace import get_connection_manager
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    description = body.get("description", "")
    app_name = body.get("name", "My App")
    workspace_id = body.get("workspace_id")
    
    if not description:
        raise HTTPException(status_code=400, detail="Description required")
    
    # Calculate estimated cost
    total_cost = sum(AGENT_COSTS.values())
    if user_doc["credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Need {total_cost} credits, you have {user_doc['credits']}"
        )
    
    manager = get_connection_manager()
    
    # Create workspace if not provided
    if not workspace_id:
        workspace_id = generate_id("ws")
        workspace = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "name": app_name,
            "description": description,
            "template": "react-vite",
            "files": {},
            "versions": [],
            "current_version": 0,
            "status": "generating",
            "build_logs": [],
            "created_at": utc_now(),
            "updated_at": utc_now()
        }
        await db.workspaces.insert_one(workspace)
    
    total_credits_used = 0
    all_files = {}
    
    try:
        # STEP 1: Classify the app
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "classifier",
                "type": "working",
                "message": "Analyzing app requirements...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        classifier_result = await run_agent_v2(
            "classifier",
            f"Classify this app: {description}",
            {"app_name": app_name, "description": description},
            db,
            workspace_id
        )
        total_credits_used += classifier_result["credits_used"]
        classification = classifier_result["result"]
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "classifier",
                "type": "success",
                "message": f"Classified as: {classification.get('app_type', 'app')} ({classification.get('complexity', 'medium')})",
                "data": classification,
                "timestamp": utc_now().isoformat()
            }
        })
        
        # STEP 2: Design architecture
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "working",
                "message": "Designing file structure...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        architect_result = await run_agent_v2(
            "architect",
            f"Design architecture for: {description}",
            {"classification": classification},
            db,
            workspace_id
        )
        total_credits_used += architect_result["credits_used"]
        architecture = architect_result["result"]
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "success",
                "message": f"Designed {len(architecture.get('structure', {}))} files",
                "data": architecture,
                "timestamp": utc_now().isoformat()
            }
        })
        
        # STEP 3: Generate Frontend
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "working",
                "message": "Generating React components...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        frontend_result = await run_agent_v2(
            "frontend",
            f"""Generate complete React frontend for: {description}
            
The app should have these pages: {json.dumps(classification.get('estimated_pages', []))}
Features needed: {json.dumps(classification.get('main_features', []))}
Make it beautiful with Tailwind CSS dark theme.""",
            {
                "classification": classification,
                "architecture": architecture,
                "app_name": app_name
            },
            db,
            workspace_id
        )
        total_credits_used += frontend_result["credits_used"]
        
        frontend_files = frontend_result["result"].get("files", {})
        all_files.update(frontend_files)
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "success",
                "message": f"Generated {len(frontend_files)} frontend files",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Update workspace with files
        await manager.broadcast(workspace_id, {
            "type": "files_updated",
            "files": all_files
        })
        
        # STEP 4: Generate backend if needed
        if classification.get("requires_database") or classification.get("requires_auth"):
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "backend",
                    "type": "working",
                    "message": "Generating API endpoints...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            backend_result = await run_agent_v2(
                "backend",
                f"Generate backend API for: {description}",
                {
                    "classification": classification,
                    "architecture": architecture
                },
                db,
                workspace_id
            )
            total_credits_used += backend_result["credits_used"]
            
            backend_files = backend_result["result"].get("files", {})
            # Prefix backend files
            for path, content in backend_files.items():
                all_files[f"backend/{path}"] = content
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "backend",
                    "type": "success",
                    "message": f"Generated {len(backend_files)} backend files",
                    "timestamp": utc_now().isoformat()
                }
            })
        
        # STEP 5: Integration
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "integrator",
                "type": "working",
                "message": "Connecting components...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        integrator_result = await run_agent_v2(
            "integrator",
            "Verify and fix integration between frontend and backend",
            {
                "files": all_files,
                "classification": classification
            },
            db,
            workspace_id
        )
        total_credits_used += integrator_result["credits_used"]
        
        # Apply integration fixes
        integration_fixes = integrator_result["result"].get("fixes", {})
        all_files.update(integration_fixes)
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "integrator",
                "type": "success",
                "message": "Integration complete",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Add base files for Sandpack
        base_files = {
            "package.json": json.dumps({
                "name": app_name.lower().replace(" ", "-"),
                "private": True,
                "version": "0.0.1",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0"
                }
            }, indent=2),
            "public/index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900">
    <div id="root"></div>
</body>
</html>""",
            "src/index.js": """import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(document.getElementById('root'));
root.render(<App />);"""
        }
        
        # Merge base files (don't overwrite generated)
        for path, content in base_files.items():
            if path not in all_files:
                all_files[path] = content
        
        # Update workspace in DB
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "files": all_files,
                    "status": "completed",
                    "current_version": 1,
                    "classification": classification,
                    "architecture": architecture,
                    "updated_at": utc_now()
                },
                "$push": {
                    "versions": {
                        "version": 1,
                        "files": all_files,
                        "created_at": utc_now(),
                        "message": "Initial generation"
                    }
                }
            }
        )
        
        # Deduct credits
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "credits": -total_credits_used,
                    "credits_used": total_credits_used
                }
            }
        )
        
        # Final broadcast
        await manager.broadcast(workspace_id, {
            "type": "generation_complete",
            "files": all_files,
            "workspace_id": workspace_id,
            "credits_used": total_credits_used
        })
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "success",
                "message": f"✨ App generated! {len(all_files)} files, {total_credits_used} credits used",
                "timestamp": utc_now().isoformat()
            }
        })
        
        return {
            "workspace_id": workspace_id,
            "files": all_files,
            "classification": classification,
            "credits_used": total_credits_used,
            "credits_remaining": user_doc["credits"] - total_credits_used
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "error",
                "message": f"Error: {str(e)}",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Update workspace status
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug")
async def debug_code(request: Request):
    """Debug code and fix errors"""
    from routes.workspace import get_connection_manager
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    error_message = body.get("error", "")
    file_path = body.get("file_path", "")
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    # Get workspace
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = workspace.get("files", {})
    manager = get_connection_manager()
    
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": {
            "agent": "debugger",
            "type": "working",
            "message": f"Analyzing error: {error_message[:50]}...",
            "timestamp": utc_now().isoformat()
        }
    })
    
    # Run debug agent
    debug_result = await run_agent_v2(
        "debugger",
        f"Fix this error: {error_message}",
        {
            "error": error_message,
            "file_path": file_path,
            "files": files
        },
        db,
        workspace_id
    )
    
    # Apply fixes
    fixes = debug_result["result"].get("fixes", {})
    files.update(fixes)
    
    # Update workspace
    new_version = workspace.get("current_version", 0) + 1
    await db.workspaces.update_one(
        {"workspace_id": workspace_id},
        {
            "$set": {
                "files": files,
                "current_version": new_version,
                "updated_at": utc_now()
            },
            "$push": {
                "versions": {
                    "version": new_version,
                    "files": files,
                    "created_at": utc_now(),
                    "message": f"Debug fix: {error_message[:50]}"
                }
            }
        }
    )
    
    # Deduct credits
    credits_used = debug_result["credits_used"]
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": -credits_used, "credits_used": credits_used}}
    )
    
    await manager.broadcast(workspace_id, {
        "type": "files_updated",
        "files": files
    })
    
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": {
            "agent": "debugger",
            "type": "success",
            "message": f"Fixed {len(fixes)} files",
            "data": debug_result["result"].get("explanation"),
            "timestamp": utc_now().isoformat()
        }
    })
    
    return {
        "fixes": fixes,
        "explanation": debug_result["result"].get("explanation", ""),
        "credits_used": credits_used,
        "files": files
    }


@router.get("/costs")
async def get_costs():
    """Get agent costs"""
    return {
        "costs": AGENT_COSTS,
        "total": sum(AGENT_COSTS.values())
    }


@router.get("/templates")
async def list_templates():
    """Get all available app templates"""
    return {
        "templates": get_all_templates()
    }


@router.get("/templates/{template_id}")
async def get_template_details(template_id: str):
    """Get a specific template details"""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"id": template_id, **template}


@router.post("/generate-from-template")
async def generate_from_template(request: Request):
    """Generate an app from a predefined template"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    template_id = body.get("template_id")
    app_name = body.get("name", "My App")
    
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Use template's prompt for generation
    description = template["prompt"]
    
    # Calculate cost
    total_cost = template.get("estimated_credits", 500)
    if user_doc["credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Need {total_cost} credits, you have {user_doc['credits']}"
        )
    
    # Call the main generate function logic (reuse)
    # For now, just call the generate endpoint internally
    body["description"] = description
    body["name"] = app_name
    
    # Create workspace
    from routes.workspace import get_connection_manager
    manager = get_connection_manager()
    
    workspace_id = generate_id("ws")
    workspace = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": app_name,
        "description": f"Generated from template: {template['name']}",
        "template": template_id,
        "files": {},
        "versions": [],
        "current_version": 0,
        "status": "generating",
        "build_logs": [],
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.workspaces.insert_one(workspace)
    
    # Start generation (reuse the logic)
    # This is a simplified version - in production you'd call the full generate function
    total_credits_used = 0
    all_files = {}
    
    try:
        # Log start
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "info",
                "message": f"Generating from template: {template['name']}",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # STEP 1: Skip classifier (we know the type from template)
        classification = {
            "app_type": template_id,
            "complexity": "medium",
            "requires_auth": False,
            "requires_database": False,
            "main_features": template.get("features", []),
            "summary": template.get("description", "")
        }
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "classifier",
                "type": "success",
                "message": f"Using template: {template['name']}",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # STEP 2: Architect
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "working",
                "message": "Designing architecture...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        architect_result = await run_agent_v2(
            "architect",
            f"Design architecture for: {description}",
            {"classification": classification, "template": template_id},
            db,
            workspace_id
        )
        total_credits_used += architect_result["credits_used"]
        architecture = architect_result["result"]
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "success",
                "message": f"Architecture designed",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # STEP 3: Frontend
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "working",
                "message": "Generating React components...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        frontend_result = await run_agent_v2(
            "frontend",
            description,
            {"classification": classification, "architecture": architecture, "app_name": app_name},
            db,
            workspace_id
        )
        total_credits_used += frontend_result["credits_used"]
        
        frontend_files = frontend_result["result"].get("files", {})
        all_files.update(frontend_files)
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "success",
                "message": f"Generated {len(frontend_files)} files",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Add base files
        base_files = {
            "package.json": json.dumps({
                "name": app_name.lower().replace(" ", "-"),
                "private": True,
                "version": "0.0.1",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0"
                }
            }, indent=2),
            "public/index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900">
    <div id="root"></div>
</body>
</html>""",
            "src/index.js": """import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(document.getElementById('root'));
root.render(<App />);"""
        }
        
        for path, content in base_files.items():
            if path not in all_files:
                all_files[path] = content
        
        # Update workspace
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "files": all_files,
                    "status": "completed",
                    "current_version": 1,
                    "updated_at": utc_now()
                },
                "$push": {
                    "versions": {
                        "version": 1,
                        "files": all_files,
                        "created_at": utc_now(),
                        "message": f"Generated from template: {template['name']}"
                    }
                }
            }
        )
        
        # Deduct credits
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -total_credits_used, "credits_used": total_credits_used}}
        )
        
        await manager.broadcast(workspace_id, {
            "type": "generation_complete",
            "files": all_files,
            "workspace_id": workspace_id,
            "credits_used": total_credits_used
        })
        
        return {
            "workspace_id": workspace_id,
            "files": all_files,
            "template": template_id,
            "credits_used": total_credits_used,
            "credits_remaining": user_doc["credits"] - total_credits_used
        }
        
    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{workspace_id}")
async def download_project_zip(request: Request, workspace_id: str):
    """Download workspace as ZIP file"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = workspace.get("files", {})
    app_name = workspace.get("name", "app").lower().replace(" ", "-")
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, content in files.items():
            # Normalize path
            normalized_path = file_path.lstrip('/')
            full_path = f"{app_name}/{normalized_path}"
            zip_file.writestr(full_path, content)
        
        # Add README
        readme_content = f"""# {workspace.get('name', 'Generated App')}

{workspace.get('description', 'Generated with Assistant Melus')}

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run development server:
   ```bash
   npm start
   ```

## Generated by Assistant Melus

This project was automatically generated using AI agents.
"""
        zip_file.writestr(f"{app_name}/README.md", readme_content)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={app_name}.zip"
        }
    )

