# Melus AI - Product Requirements Document

## Original Problem Statement
Build an AI application generator named "Melus AI" - a highly advanced, autonomous, multi-agent platform. The platform must be capable of hierarchical task planning, routing tasks to specialized agents (e.g., Code Agent, Research Agent), using a persistent vector memory, and executing real-world tools (Git, APIs, code execution).

The frontend is a visual replica of the Emergent.sh website's light theme. The backend uses MongoDB for data persistence.

**User's preferred language**: Spanish

---

## Current Architecture

### Tech Stack
- **Frontend**: React, react-router-dom, axios, lucide-react, shadcn/ui, TailwindCSS
- **Backend**: FastAPI, Pydantic, Motor (MongoDB async driver)
- **Database**: MongoDB Atlas
- **AI Integration**: OpenAI GPT-4 (via Emergent LLM Key)
- **Payments**: Stripe

### Directory Structure
```
/app
├── backend/
│   ├── server.py                    # Main FastAPI app
│   ├── orchestrator_models.py       # Pydantic models for orchestrator
│   ├── routes/
│   │   ├── orchestrator_api.py      # Multi-agent orchestrator endpoints
│   │   ├── auth.py                  # Authentication routes
│   │   └── ...                      # Other route files
│   └── .env                         # Environment variables
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── LandingPage.jsx      # Public landing page
│       │   ├── HomePage.jsx         # Post-login main page
│       │   ├── OrchestratorPage.jsx # Multi-agent dashboard
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

#### Authentication System
- [x] Email/password login and registration
- [x] Google OAuth integration
- [x] GitHub OAuth integration
- [x] Session token management
- [x] Protected routes with AuthContext

#### UI/UX (Emergent.sh Light Theme Replica)
- [x] Landing Page with auth buttons and showcase carousel
- [x] HomePage with sidebar, project list, and prompt input
- [x] Agent mode selector (E1, E1.5, E2)
- [x] Credits display and modal
- [x] Orchestrator Dashboard with modern design

#### Multi-Agent Orchestrator System
- [x] **10 Specialized Agents** defined:
  - Cognitive: Planner, Research, Reasoning
  - Productive: Content, Code, Automation
  - Control: QA, Security, Optimization, Cost Control
- [x] **Orchestrator API** endpoints:
  - `POST /api/orchestrator/objectives` - Create new objective
  - `GET /api/orchestrator/objectives` - List all objectives
  - `POST /api/orchestrator/objectives/{id}/start` - Start objective
  - `POST /api/orchestrator/objectives/{id}/pause` - Pause objective
  - `GET /api/orchestrator/agents` - List all agents
  - `POST /api/orchestrator/agents/{id}/toggle` - Enable/disable agent
  - `GET /api/orchestrator/stats` - Dashboard statistics
  - `GET /api/orchestrator/activity` - Recent activity feed
  - `GET /api/orchestrator/tasks` - List tasks
- [x] **Task Auto-Generation** based on objective type:
  - Code: Planning → Architecture → Implementation → Testing → Security → Optimization
  - Content: Research → Planning → Writing → QA → SEO
  - Automation: Requirements → Design → Implementation → Testing
  - Research: Data Collection → Analysis → Report Generation
- [x] **Orchestrator Dashboard UI**:
  - Stats cards (Objectives, Tasks, Agents, Cost)
  - Agent cards with status indicators
  - Tabs: Overview, Objectives, Agents, Activity
  - New Objective modal with form
  - Auto Mode toggle

---

## Prioritized Backlog

### P0 (Critical - Next)
1. **Implement Actual LLM Integration for Task Execution**
   - Connect task execution to OpenAI GPT-4 via Emergent LLM Key
   - Add streaming responses for real-time feedback
   - Track token usage and costs per task

2. **Persist Orchestrator Data to MongoDB**
   - Currently using in-memory storage (resets on restart)
   - Need to save objectives, tasks, and agent metrics to MongoDB

### P1 (High Priority)
3. **Task Detail View**
   - Show task input/output data
   - Display execution logs
   - Allow manual retry of failed tasks

4. **Real-time WebSocket Updates**
   - Push task status updates to frontend
   - Live progress indicators during execution

5. **Agent Performance Dashboard**
   - Historical success rates
   - Cost per agent
   - Task completion times

### P2 (Medium Priority)
6. **Vector Memory Integration**
   - Add pgvector or similar for embeddings
   - Store project context for better agent decisions
   - Implement semantic search

7. **WorkspacePage Terminal Integration**
   - Connect WebSocket backend to frontend terminal
   - Show real-time code execution output

8. **Objective Templates**
   - Pre-defined templates for common tasks
   - Quick-start objectives

### P3 (Future)
9. **Git Integration**
   - Clone/push to repositories
   - Branch management
   - Commit history

10. **Code Sandbox Execution**
    - Secure code execution environment
    - File system access for agents
    - Package installation

---

## API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user
- `GET /api/auth/google` - Google OAuth redirect
- `GET /api/github/auth` - GitHub OAuth redirect

### Orchestrator
- `GET /api/orchestrator/stats` - Dashboard stats
- `GET /api/orchestrator/objectives` - List objectives
- `POST /api/orchestrator/objectives` - Create objective
- `POST /api/orchestrator/objectives/{id}/start` - Start objective
- `GET /api/orchestrator/agents` - List agents
- `GET /api/orchestrator/activity` - Recent activity

### Health
- `GET /api/health` - System health check

---

## Testing Notes
- User has explicitly requested NO automated testing agent
- Manual testing with curl and screenshots required
- Test user: test@test.com / Test123!

---

## Known Limitations
1. Orchestrator data is in-memory only (lost on restart)
2. Tasks show "queued" but don't actually execute LLM calls
3. WorkspacePage terminal not connected to WebSocket
4. Original project generation flow is deprecated
