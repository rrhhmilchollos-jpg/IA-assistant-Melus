# Melus AI - Product Requirements Document

## Original Problem Statement
Build an AI application generator named "Melus AI" - a highly advanced, autonomous, multi-agent platform. The platform must be capable of hierarchical task planning, routing tasks to specialized agents, and generating complete applications including:
- **Web applications** (full-stack)
- **2D Games** (Phaser.js, PixiJS)
- **3D Games** (Three.js, Babylon.js)
- **Mobile applications** (React Native concepts)
- **Landing pages** and marketing sites

The frontend is a visual replica of the Emergent.sh website's light theme. The backend uses MongoDB for data persistence.

**User's preferred language**: Spanish

---

## Current Architecture

### Tech Stack
- **Frontend**: React, react-router-dom, axios, lucide-react, shadcn/ui, TailwindCSS
- **Backend**: FastAPI, Pydantic, Motor (MongoDB async driver)
- **Database**: MongoDB Atlas (persistent)
- **AI Integration**: OpenAI GPT-4o via Emergent LLM Key
- **Payments**: Stripe

### Directory Structure
```
/app
├── backend/
│   ├── server.py                    # Main FastAPI app
│   ├── orchestrator_models.py       # Pydantic models for orchestrator
│   ├── routes/
│   │   ├── orchestrator_api.py      # Multi-agent orchestrator with LLM integration
│   │   ├── auth.py                  # Authentication routes
│   │   └── ...                      # Other route files
│   └── .env                         # Environment variables
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── LandingPage.jsx      # Public landing page
│       │   ├── HomePage.jsx         # Post-login main page
│       │   ├── OrchestratorPage.jsx # Multi-agent dashboard with Tasks view
│       │   └── WorkspacePage.jsx    # IDE-style workspace
│       ├── context/
│       │   └── AuthContext.jsx      # Authentication context
│       └── components/              # UI components
└── memory/
    └── PRD.md                       # This file
```

---

## What's Been Implemented

### Date: 2026-02-20

#### Core Multi-Agent Code Generation System ✅
- [x] **10 Specialized AI Agents** with GPT-4o integration:
  - Strategic Planner - Creates execution plans and project structure
  - Architecture Agent - Designs system architecture and patterns
  - Research Agent - Gathers information and best practices
  - Content Creator - Documentation and text content
  - **Code Agent** - Generates real, production code
  - Automation Agent - CI/CD and deployment configs
  - QA Agent - Quality review and testing
  - Security Agent - Security audits
  - Optimization Agent - Performance improvements
  - Cost Controller - Budget management

#### LLM-Powered Task Execution ✅
- [x] Real OpenAI GPT-4o API calls via Emergent Integrations
- [x] Specialized system prompts per agent role
- [x] Context accumulation between tasks
- [x] File generation and parsing from LLM responses

#### Project Type Detection ✅
- [x] Automatic detection of project type from description:
  - `web_app` - Full-stack web applications
  - `game_2d` - 2D games (Phaser.js, PixiJS)
  - `game_3d` - 3D games (Three.js, Babylon.js)
  - `mobile_app` - Mobile applications
  - `landing_page` - Marketing/portfolio sites

#### Task Templates by Project Type ✅
- [x] **Web App**: Planning → Architecture → Backend → Frontend → Database → API → Testing → Security → Optimization
- [x] **2D Game**: Design Doc → Architecture → Engine Setup → Sprites → Game Logic → UI/Menu → Sound → Testing → Optimization
- [x] **3D Game**: Design → Architecture → Three.js Setup → Models → Camera → Physics → Lighting → Mechanics → Testing → WebGL Optimization
- [x] **Mobile App**: Planning → Architecture → React Native Setup → Screens → Navigation → State → API → Testing → Optimization
- [x] **Landing Page**: Planning → Design → HTML/CSS → Responsive → Animations → SEO → Performance

#### MongoDB Persistence ✅
- [x] Objectives stored in `orchestrator_objectives` collection
- [x] Tasks stored in `orchestrator_tasks` collection
- [x] Agents stored in `orchestrator_agents` collection
- [x] Generated files tracked per task

#### Orchestrator Dashboard UI ✅
- [x] Overview tab with statistics
- [x] **Objectives tab** with project type badges and action buttons
- [x] **Tasks tab** with execute buttons and file count indicators
- [x] Agents tab with toggle and stats
- [x] Activity tab with recent actions
- [x] **Generated Files modal** - View all generated files
- [x] **Code Viewer modal** - View file content with syntax highlighting
- [x] Copy Code functionality

---

## Working Features (Tested)

1. ✅ Create new objective with project type auto-detection
2. ✅ Start objective → Creates phase-specific tasks
3. ✅ Execute individual tasks with GPT-4o
4. ✅ Code Agent generates real files (HTML, CSS, JS)
5. ✅ View generated files in modal
6. ✅ View file content with code viewer
7. ✅ Data persists in MongoDB across restarts

---

## Prioritized Backlog

### P0 (Critical - Next)
1. **Auto-execute all tasks in sequence**
   - Currently tasks execute one at a time manually
   - Need to run all tasks automatically when auto_mode is enabled

2. **Improve Code Generation Quality**
   - Add more context between tasks
   - Better parsing of generated files
   - Handle larger code outputs

### P1 (High Priority)
3. **Download Generated Project**
   - Bundle all generated files as ZIP
   - Proper folder structure

4. **Real-time Task Progress**
   - WebSocket for live updates
   - Progress indicators during execution

5. **Project Preview**
   - Render generated HTML/games in iframe
   - Live preview of generated code

### P2 (Medium Priority)
6. **Edit Generated Code**
   - Inline code editor in file viewer
   - Save changes back to task

7. **Regenerate Task**
   - Re-run specific task with different prompt
   - Keep context from previous tasks

8. **Export to GitHub**
   - Push generated project to repository
   - Create proper .gitignore and README

### P3 (Future)
9. **Template Library**
   - Pre-made project templates
   - Clone and customize

10. **Collaborative Editing**
    - Multiple users on same project
    - Real-time sync

---

## API Endpoints Summary

### Orchestrator (Full CRUD)
- `GET /api/orchestrator/stats` - Dashboard stats
- `GET /api/orchestrator/objectives` - List objectives
- `POST /api/orchestrator/objectives` - Create objective
- `GET /api/orchestrator/objectives/{id}` - Get objective details
- `POST /api/orchestrator/objectives/{id}/start` - Start objective
- `POST /api/orchestrator/objectives/{id}/pause` - Pause objective
- `POST /api/orchestrator/objectives/{id}/resume` - Resume objective
- `GET /api/orchestrator/objectives/{id}/files` - Get generated files
- `GET /api/orchestrator/tasks` - List tasks (optional objective_id filter)
- `GET /api/orchestrator/tasks/{id}` - Get task details
- `POST /api/orchestrator/tasks/{id}/execute` - Execute task with LLM
- `GET /api/orchestrator/agents` - List agents
- `POST /api/orchestrator/agents/{id}/toggle` - Toggle agent status
- `GET /api/orchestrator/activity` - Recent activity

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user

---

## Testing Notes
- Test user: test@test.com / Test123!
- Manual testing with curl and screenshots (per user request)
- LLM integration verified with real GPT-4o calls

---

## Known Limitations
1. Auto-mode doesn't auto-execute yet (must click Execute per task)
2. Large code outputs may be truncated in storage
3. No ZIP download for generated projects yet
4. No live preview of generated apps

---

## Recent Session Summary

Successfully implemented:
1. MongoDB persistence for orchestrator data
2. Real LLM integration with GPT-4o via Emergent key
3. Code generation that creates actual files
4. Task execution with context accumulation
5. File viewer modals with code display
6. Project type detection and task templates
