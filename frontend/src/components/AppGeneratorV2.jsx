import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  SandpackProvider,
  SandpackLayout,
  SandpackCodeEditor,
  SandpackPreview,
  SandpackFileExplorer,
  useSandpack,
  SandpackConsole,
} from '@codesandbox/sandpack-react';
import { useAuth } from '../context/AuthContext';
import {
  Play,
  Square,
  RefreshCw,
  Download,
  Github,
  ChevronRight,
  ChevronDown,
  CheckCircle,
  Clock,
  AlertCircle,
  Cpu,
  Palette,
  Code,
  Server,
  Database,
  Wrench,
  Zap,
  FileCode,
  FolderOpen,
  Eye,
  Terminal,
  X,
  Maximize2,
  Minimize2,
  Bug,
  ShoppingCart,
  FileText,
  LayoutDashboard,
  Rocket,
  CheckSquare,
  User,
  Sparkles,
  ArrowLeft,
  Users,
  MessageCircle,
  Share2,
  Package,
  Calendar,
  BarChart3,
  Bolt,
  History,
  RotateCcw,
  Save,
  AlertTriangle,
  Info
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Template icons mapping
const TEMPLATE_ICONS = {
  ecommerce: ShoppingCart,
  blog: FileText,
  dashboard: LayoutDashboard,
  landing: Rocket,
  taskmanager: CheckSquare,
  portfolio: User,
  crm: Users,
  chat: MessageCircle,
  social: Share2,
  inventory: Package,
  booking: Calendar,
  analytics: BarChart3
};

// Agent icons mapping - All 13 Agents
const AGENT_ICONS = {
  // Core Generation
  classifier: Cpu,
  architect: FolderOpen,
  frontend: Code,
  backend: Server,
  integrator: Wrench,
  // Specialized
  design: Palette,
  database: Database,
  testing: CheckSquare,
  security: AlertTriangle,
  deploy: Rocket,
  // Utility
  debugger: Bug,
  optimizer: Zap,
  docs: FileText,
  system: Sparkles
};

// Agent colors - All agents
const AGENT_COLORS = {
  classifier: 'text-purple-400',
  architect: 'text-blue-400',
  design: 'text-pink-400',
  frontend: 'text-cyan-400',
  backend: 'text-green-400',
  database: 'text-amber-400',
  integrator: 'text-yellow-400',
  testing: 'text-lime-400',
  security: 'text-red-400',
  deploy: 'text-indigo-400',
  debugger: 'text-orange-400',
  optimizer: 'text-emerald-400',
  docs: 'text-slate-400',
  system: 'text-violet-400'
};

// Status icons
const getStatusIcon = (type) => {
  switch (type) {
    case 'success':
      return <CheckCircle className="w-4 h-4 text-green-400" />;
    case 'working':
      return <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />;
    case 'error':
      return <AlertCircle className="w-4 h-4 text-red-400" />;
    default:
      return <Zap className="w-4 h-4 text-purple-400" />;
  }
};

// Custom Preview component with enhanced error capture
const CustomPreview = ({ onError, onConsoleLog }) => {
  const { sandpack } = useSandpack();
  
  useEffect(() => {
    const handleMessage = (e) => {
      if (e.data?.type === 'error' || e.data?.type === 'console') {
        if (e.data.type === 'error') {
          onError?.(e.data.error || e.data.message);
        }
        if (e.data.log) {
          onConsoleLog?.(e.data.log);
        }
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onError, onConsoleLog]);
  
  // Capture Sandpack errors
  useEffect(() => {
    if (sandpack?.error) {
      onError?.(sandpack.error.message);
    }
  }, [sandpack?.error, onError]);
  
  return (
    <SandpackPreview
      showNavigator
      showRefreshButton
      showOpenInCodeSandbox={false}
      style={{ height: '100%' }}
    />
  );
};

// Version History Panel Component
const VersionHistoryPanel = ({ versions, currentVersion, onRollback, onClose }) => {
  return (
    <div className="absolute right-0 top-12 w-80 bg-[#1a1a2e] border border-purple-500/30 rounded-lg shadow-xl z-50 max-h-96 overflow-hidden">
      <div className="p-3 border-b border-purple-500/20 flex items-center justify-between">
        <h3 className="font-semibold flex items-center gap-2">
          <History className="w-4 h-4 text-purple-400" />
          Historial de Versiones
        </h3>
        <button onClick={onClose} className="text-gray-400 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="overflow-y-auto max-h-72">
        {versions?.length > 0 ? (
          versions.slice().reverse().map((v, idx) => (
            <div
              key={v.version}
              className={`p-3 border-b border-purple-500/10 hover:bg-white/5 ${
                v.version === currentVersion ? 'bg-purple-500/10' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-medium text-sm">
                    Versión {v.version}
                    {v.version === currentVersion && (
                      <span className="ml-2 text-xs bg-purple-500/30 text-purple-300 px-2 py-0.5 rounded">
                        Actual
                      </span>
                    )}
                  </span>
                  <p className="text-xs text-gray-400 mt-1">{v.message}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(v.created_at).toLocaleString('es-ES')}
                  </p>
                </div>
                {v.version !== currentVersion && (
                  <button
                    onClick={() => onRollback(v.version)}
                    className="px-2 py-1 text-xs bg-orange-500/20 text-orange-400 rounded hover:bg-orange-500/30 flex items-center gap-1"
                  >
                    <RotateCcw className="w-3 h-3" />
                    Restaurar
                  </button>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="p-4 text-center text-gray-500 text-sm">
            No hay versiones guardadas
          </div>
        )}
      </div>
    </div>
  );
};

const AppGeneratorV2 = () => {
  const { user, updateCredits } = useAuth();
  const [description, setDescription] = useState('');
  const [appName, setAppName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDebugging, setIsDebugging] = useState(false);
  const [logs, setLogs] = useState([]);
  const [consoleLogs, setConsoleLogs] = useState([]);
  const [files, setFiles] = useState({});
  const [workspaceId, setWorkspaceId] = useState(null);
  const [activeTab, setActiveTab] = useState('preview');
  const [expandedLogs, setExpandedLogs] = useState({});
  const [previewError, setPreviewError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  
  // Motor No Chat mode states
  const [executionMode, setExecutionMode] = useState('templates'); // 'templates' | 'motor'
  const [motorTemplate, setMotorTemplate] = useState(`Proyecto: Mi Aplicación

Objetivo: Describe tu aplicación aquí

# FRONTEND AGENT
- Framework: React con TailwindCSS
- Componentes: Header, Footer, Dashboard
- Páginas: Home, Login, Dashboard

# BACKEND AGENT
- Framework: FastAPI
- Endpoints: CRUD usuarios
- Autenticación: JWT

# DATABASE AGENT
- Motor: MongoDB
- Tablas: usuarios, datos

# DEPLOYMENT AGENT
- Plataforma: Vercel
- CI/CD: GitHub Actions`);
  const [templates, setTemplates] = useState([]);
  const [showTemplates, setShowTemplates] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [ultraMode, setUltraMode] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [versions, setVersions] = useState([]);
  const [currentVersion, setCurrentVersion] = useState(1);
  const logsEndRef = useRef(null);
  const wsRef = useRef(null);

  // Load templates on mount
  useEffect(() => {
    fetchTemplates();
  }, []);

  // Load last workspace from localStorage on mount
  useEffect(() => {
    const savedWorkspaceId = localStorage.getItem('melus_workspace_id');
    if (savedWorkspaceId) {
      loadWorkspace(savedWorkspaceId);
      setShowTemplates(false);
    }
  }, []);

  // Fetch available templates
  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agents/v2/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  // Load workspace files from backend
  const loadWorkspace = async (wsId) => {
    const token = localStorage.getItem('session_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE}/api/workspace/${wsId}`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const data = await response.json();
        setWorkspaceId(wsId);
        setFiles(data.files || {});
        setAppName(data.name || '');
        setDescription(data.description || '');
        setVersions(data.versions || []);
        setCurrentVersion(data.current_version || 1);
        setLogs([{
          agent: 'system',
          type: 'info',
          message: `Workspace cargado: ${data.name} (v${data.current_version})`,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
    }
  };

  // Fetch versions for current workspace
  const fetchVersions = async () => {
    if (!workspaceId) return;
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/workspace/${workspaceId}/versions`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const data = await response.json();
        setVersions(data.versions || []);
        setCurrentVersion(data.current_version || 1);
      }
    } catch (error) {
      console.error('Failed to fetch versions:', error);
    }
  };

  // Rollback to a specific version
  const handleRollback = async (version) => {
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/workspace/${workspaceId}/rollback/${version}`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files);
        setCurrentVersion(data.version);
        setShowVersions(false);
        setLogs(prev => [...prev, {
          agent: 'system',
          type: 'success',
          message: `Restaurado a versión ${version}`,
          timestamp: new Date().toISOString()
        }]);
        fetchVersions();
      }
    } catch (error) {
      console.error('Rollback failed:', error);
    }
  };

  // Check GitHub connection status
  const [githubConnected, setGithubConnected] = useState(false);
  const [githubUsername, setGithubUsername] = useState('');
  const [isPushingToGithub, setIsPushingToGithub] = useState(false);
  const [showGithubModal, setShowGithubModal] = useState(false);
  const [githubRepoName, setGithubRepoName] = useState('');
  const [githubPrivate, setGithubPrivate] = useState(false);

  // Check GitHub status on mount
  useEffect(() => {
    checkGithubStatus();
  }, []);

  const checkGithubStatus = async () => {
    const token = localStorage.getItem('session_token');
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/github/status`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const data = await response.json();
        setGithubConnected(data.connected);
        setGithubUsername(data.username || '');
      }
    } catch (error) {
      console.error('GitHub status check failed:', error);
    }
  };

  // Connect to GitHub
  const handleConnectGithub = async () => {
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/github/auth/login`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const data = await response.json();
        // Redirect to GitHub OAuth
        window.location.href = data.auth_url;
      }
    } catch (error) {
      console.error('GitHub connect failed:', error);
    }
  };

  // Push to GitHub
  const handlePushToGithub = async () => {
    if (!workspaceId) return;
    
    const token = localStorage.getItem('session_token');
    setIsPushingToGithub(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/agents/v2/push-to-github`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          workspace_id: workspaceId,
          repo_name: githubRepoName || appName.toLowerCase().replace(/\s+/g, '-'),
          private: githubPrivate
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Push failed');
      }
      
      updateCredits(data.credits_remaining);
      setShowGithubModal(false);
      
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'success',
        message: `Subido a GitHub: ${data.repo_url}`,
        timestamp: new Date().toISOString()
      }]);
      
      // Open repo in new tab
      window.open(data.repo_url, '_blank');
      
    } catch (error) {
      console.error('GitHub push error:', error);
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'error',
        message: `Error GitHub: ${error.message}`,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsPushingToGithub(false);
    }
  };

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (workspaceId) {
      const wsUrl = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');
      const ws = new WebSocket(`${wsUrl}/api/workspace/ws/${workspaceId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWSMessage(data);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket closed');
      };
      
      wsRef.current = ws;
      
      return () => {
        ws.close();
      };
    }
  }, [workspaceId]);

  // Scroll logs to bottom
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleWSMessage = useCallback((data) => {
    switch (data.type) {
      case 'log':
        setLogs(prev => [...prev, data.log]);
        if (data.log.type === 'working') {
          setCurrentAgent(data.log.agent);
        } else if (data.log.type === 'success' || data.log.type === 'error') {
          setCurrentAgent(null);
        }
        break;
      case 'files_updated':
        setFiles(data.files);
        if (data.version) {
          setCurrentVersion(data.version);
        }
        fetchVersions();
        break;
      case 'agent_start':
        setCurrentAgent(data.agent);
        break;
      case 'agent_complete':
      case 'agent_error':
        setCurrentAgent(null);
        break;
      case 'generation_complete':
        setFiles(data.files);
        setIsGenerating(false);
        fetchVersions();
        break;
      case 'rollback':
        setFiles(data.files);
        setCurrentVersion(data.version);
        break;
      default:
        break;
    }
  }, []);

  const handleGenerate = async () => {
    if (!description.trim()) return;
    
    const token = localStorage.getItem('session_token');
    if (!token) {
      alert('Sesión expirada. Por favor, inicia sesión de nuevo.');
      return;
    }

    setIsGenerating(true);
    setShowTemplates(false);
    setLogs([]);
    setConsoleLogs([]);
    setFiles({});
    setPreviewError(null);
    
    const modeLabel = ultraMode ? 'ULTRA MODE' : 'Normal';
    setLogs([{
      agent: 'system',
      type: 'info',
      message: `[${modeLabel}] Iniciando generación de "${appName || 'Mi App'}"...`,
      timestamp: new Date().toISOString()
    }]);

    try {
      const response = await fetch(`${API_BASE}/api/agents/v2/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          description,
          name: appName || 'Mi App',
          ultra_mode: ultraMode
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Generation failed');
      }

      setWorkspaceId(data.workspace_id);
      setFiles(data.files);
      updateCredits(data.credits_remaining);
      localStorage.setItem('melus_workspace_id', data.workspace_id);
      fetchVersions();
      
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'success',
        message: `App generada! ${Object.keys(data.files).length} archivos creados - ${data.credits_used} créditos`,
        timestamp: new Date().toISOString()
      }]);
      
    } catch (error) {
      console.error('Generation error:', error);
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'error',
        message: error.message,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsGenerating(false);
    }
  };

  // Enhanced Debug function with 30 credits
  const handleDebug = async () => {
    if (!previewError || !workspaceId) return;
    
    const token = localStorage.getItem('session_token');
    setIsDebugging(true);
    
    try {
      setLogs(prev => [...prev, {
        agent: 'debugger',
        type: 'working',
        message: 'Analizando error... (30 créditos)',
        timestamp: new Date().toISOString()
      }]);
      
      const response = await fetch(`${API_BASE}/api/agents/v2/debug`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          workspace_id: workspaceId,
          error: previewError,
          console_logs: consoleLogs
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Debug failed');
      }
      
      setFiles(data.files);
      setPreviewError(null);
      setCurrentVersion(data.version);
      updateCredits(data.credits_remaining);
      fetchVersions();
      
      setLogs(prev => [...prev, {
        agent: 'debugger',
        type: 'success',
        message: `Corregido! ${data.credits_used} créditos usados`,
        data: {
          analysis: data.error_analysis,
          explanation: data.explanation
        },
        timestamp: new Date().toISOString()
      }]);
      
    } catch (error) {
      console.error('Debug error:', error);
      setLogs(prev => [...prev, {
        agent: 'debugger',
        type: 'error',
        message: error.message,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsDebugging(false);
    }
  };

  // Generate from template
  const handleGenerateFromTemplate = async (templateId) => {
    const token = localStorage.getItem('session_token');
    if (!token) {
      alert('Sesión expirada. Por favor, inicia sesión de nuevo.');
      return;
    }

    setIsGenerating(true);
    setShowTemplates(false);
    setLogs([]);
    setConsoleLogs([]);
    setFiles({});
    setPreviewError(null);
    
    const template = templates.find(t => t.id === templateId);
    setSelectedTemplate(template);
    
    const modeLabel = ultraMode ? 'ULTRA MODE' : 'Normal';
    setLogs([{
      agent: 'system',
      type: 'info',
      message: `[${modeLabel}] Generando: ${template?.name}...`,
      timestamp: new Date().toISOString()
    }]);

    try {
      const response = await fetch(`${API_BASE}/api/agents/v2/generate-from-template`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          template_id: templateId,
          name: template?.name || 'Mi App',
          ultra_mode: ultraMode
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Generation failed');
      }

      setWorkspaceId(data.workspace_id);
      setFiles(data.files);
      setAppName(template?.name || '');
      updateCredits(data.credits_remaining);
      localStorage.setItem('melus_workspace_id', data.workspace_id);
      fetchVersions();
      
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'success',
        message: `App generada! ${Object.keys(data.files).length} archivos - ${data.credits_used} créditos`,
        timestamp: new Date().toISOString()
      }]);
      
    } catch (error) {
      console.error('Template generation error:', error);
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'error',
        message: error.message,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsGenerating(false);
    }
  };

  // Download as ZIP
  const handleDownload = async () => {
    if (!workspaceId) return;
    
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/agents/v2/download/${workspaceId}`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${appName || 'app'}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        setLogs(prev => [...prev, {
          agent: 'system',
          type: 'success',
          message: 'Proyecto descargado como ZIP',
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  // MOTOR NO CHAT - Execute complete project with all agents
  const handleExecuteMotor = async () => {
    if (!motorTemplate.trim()) return;
    
    const token = localStorage.getItem('session_token');
    if (!token) {
      alert('Sesión expirada. Por favor, inicia sesión de nuevo.');
      return;
    }

    setIsGenerating(true);
    setShowTemplates(false);
    setLogs([]);
    setConsoleLogs([]);
    setFiles({});
    setPreviewError(null);
    
    const modeLabel = ultraMode ? 'ULTRA MOTOR' : 'MOTOR';
    setLogs([{
      agent: 'system',
      type: 'info',
      message: `[${modeLabel}] MODO MOTOR INICIADO - Ejecutando TODOS los agentes...`,
      timestamp: new Date().toISOString()
    }]);

    try {
      const response = await fetch(`${API_BASE}/api/agents/v2/execute-project`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          template: motorTemplate,
          name: appName || 'Mi Proyecto Motor',
          ultra_mode: ultraMode
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Motor execution failed');
      }

      setWorkspaceId(data.workspace_id);
      setFiles(data.files);
      updateCredits(data.credits_remaining);
      localStorage.setItem('melus_workspace_id', data.workspace_id);
      fetchVersions();
      
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'success',
        message: `PROYECTO COMPLETO! ${data.files_count} archivos | ${data.credits_used} créditos | ${data.agents_executed?.length || 0} agentes`,
        timestamp: new Date().toISOString()
      }]);
      
    } catch (error) {
      console.error('Motor execution error:', error);
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'error',
        message: error.message,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsGenerating(false);
    }
  };

  // Start new project
  const handleNewProject = () => {
    setShowTemplates(true);
    setFiles({});
    setLogs([]);
    setConsoleLogs([]);
    setWorkspaceId(null);
    setAppName('');
    setDescription('');
    setSelectedTemplate(null);
    setVersions([]);
    setCurrentVersion(1);
    setPreviewError(null);
    localStorage.removeItem('melus_workspace_id');
  };

  // Handle console logs from preview
  const handleConsoleLog = (log) => {
    setConsoleLogs(prev => [...prev.slice(-50), log]);
  };

  // Convert files to Sandpack format
  const getSandpackFiles = () => {
    const sandpackFiles = {};
    
    Object.entries(files).forEach(([path, content]) => {
      const normalizedPath = path.startsWith('/') ? path : `/${path}`;
      sandpackFiles[normalizedPath] = {
        code: content,
        active: normalizedPath === '/src/App.jsx' || normalizedPath === '/src/App.js'
      };
    });
    
    if (!sandpackFiles['/src/App.jsx'] && !sandpackFiles['/src/App.js']) {
      sandpackFiles['/src/App.jsx'] = {
        code: `export default function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Melus AI</h1>
        <p className="text-gray-400">Generando tu aplicación...</p>
      </div>
    </div>
  );
}`,
        active: true
      };
    }
    
    if (!sandpackFiles['/src/index.js']) {
      sandpackFiles['/src/index.js'] = {
        code: `import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

createRoot(document.getElementById('root')).render(<App />);`
      };
    }
    
    return sandpackFiles;
  };

  // Template Selection View
  if (showTemplates && !isGenerating && Object.keys(files).length === 0) {
    return (
      <div className="bg-[#0a0a12] min-h-screen text-white">
        {/* Header */}
        <div className="border-b border-purple-500/20 bg-[#0d0d1a]">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Melus AI</h1>
                <p className="text-xs text-gray-500">Constructor Universal de Apps</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">
                Créditos: <span className="text-purple-400 font-bold">{user?.credits || 0}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Templates Grid */}
        <div className="max-w-6xl mx-auto px-6 py-10">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-3">Crea tu Aplicación</h2>
            <p className="text-gray-400">Elige una plantilla o usa el Motor para control total</p>
          </div>

          {/* Mode Tabs: Templates vs Motor */}
          <div className="flex justify-center gap-4 mb-8">
            <button
              onClick={() => setExecutionMode('templates')}
              data-testid="mode-templates"
              className={`px-6 py-3 rounded-xl border font-medium transition-all flex items-center gap-2 ${
                executionMode === 'templates'
                  ? 'bg-purple-500/20 border-purple-500 text-purple-400'
                  : 'bg-white/5 border-gray-700 text-gray-400 hover:border-purple-500/30'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              Templates
            </button>
            <button
              onClick={() => setExecutionMode('motor')}
              data-testid="mode-motor"
              className={`px-6 py-3 rounded-xl border font-medium transition-all flex items-center gap-2 ${
                executionMode === 'motor'
                  ? 'bg-gradient-to-r from-orange-500/20 to-red-500/20 border-orange-500 text-orange-400'
                  : 'bg-white/5 border-gray-700 text-gray-400 hover:border-orange-500/30'
              }`}
            >
              <Zap className="w-5 h-5" />
              Motor No Chat
            </button>
          </div>

          {/* Ultra Mode Toggle */}
          <div className="flex justify-center mb-8">
            <button
              onClick={() => setUltraMode(!ultraMode)}
              data-testid="ultra-mode-toggle"
              className={`flex items-center gap-3 px-6 py-3 rounded-xl border transition-all ${
                ultraMode
                  ? 'bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-yellow-500/50 text-yellow-400'
                  : 'bg-white/5 border-gray-700 text-gray-400 hover:border-yellow-500/30 hover:text-yellow-400'
              }`}
            >
              <Bolt className={`w-5 h-5 ${ultraMode ? 'animate-pulse' : ''}`} />
              <div className="text-left">
                <div className="font-semibold">ULTRA MODE</div>
                <div className="text-xs opacity-70">2x créditos = Máxima calidad</div>
              </div>
              <div className={`w-12 h-6 rounded-full relative transition-colors ${ultraMode ? 'bg-yellow-500' : 'bg-gray-700'}`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${ultraMode ? 'left-7' : 'left-1'}`} />
              </div>
            </button>
          </div>

          {/* MOTOR NO CHAT MODE */}
          {executionMode === 'motor' && (
            <div className="max-w-4xl mx-auto mb-12">
              <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-orange-400">MODO MOTOR (No Chat)</h3>
                    <p className="text-xs text-gray-400">Ejecución directa - TODOS los agentes en secuencia</p>
                  </div>
                </div>
                
                <p className="text-sm text-gray-300 mb-4">
                  Define tu proyecto con instrucciones directas para cada agente. 
                  Sin conversación, solo ejecución automática de los 11 agentes especializados.
                </p>

                <div className="bg-black/30 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-500 font-mono">PLANTILLA DE PROYECTO</span>
                    <span className="text-xs text-orange-400">~930 créditos (Normal) | ~1860 (Ultra)</span>
                  </div>
                  <textarea
                    value={motorTemplate}
                    onChange={(e) => setMotorTemplate(e.target.value)}
                    placeholder="Define tu proyecto con instrucciones para cada agente..."
                    className="w-full h-64 bg-transparent border-none outline-none text-sm font-mono text-gray-300 resize-none"
                    data-testid="motor-template-input"
                  />
                </div>

                <div className="flex items-center gap-4">
                  <input
                    type="text"
                    value={appName}
                    onChange={(e) => setAppName(e.target.value)}
                    placeholder="Nombre del proyecto"
                    className="flex-1 bg-black/30 border border-orange-500/30 rounded-lg px-4 py-2 text-sm focus:border-orange-500 outline-none"
                    data-testid="motor-name-input"
                  />
                  <button
                    onClick={handleExecuteMotor}
                    disabled={!motorTemplate.trim()}
                    data-testid="execute-motor-btn"
                    className={`px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-all ${
                      ultraMode
                        ? 'bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black'
                        : 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <Zap className="w-4 h-4" />
                    EJECUTAR MOTOR
                  </button>
                </div>

                <div className="mt-4 text-xs text-gray-500">
                  <strong>Agentes ejecutados:</strong> Classifier → Architect → Design → Database → Frontend → Backend → Integrator → Testing → Security → Deploy → Docs
                </div>
              </div>
            </div>
          )}

          {/* TEMPLATES MODE */}
          {executionMode === 'templates' && (
            <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {templates.map((template) => {
              const Icon = TEMPLATE_ICONS[template.id] || Code;
              const credits = ultraMode ? template.estimated_credits * 2 : template.estimated_credits;
              return (
                <div
                  key={template.id}
                  onClick={() => handleGenerateFromTemplate(template.id)}
                  data-testid={`template-${template.id}`}
                  className="group cursor-pointer bg-[#1a1a2e] border border-purple-500/20 rounded-xl p-6 hover:border-purple-500/50 hover:bg-[#1f1f3a] transition-all hover:scale-[1.02]"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${template.color} flex items-center justify-center mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-purple-400 transition-colors">
                    {template.name}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                    {template.description}
                  </p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {template.features?.slice(0, 3).map((feature, idx) => (
                      <span key={idx} className="text-xs bg-white/5 px-2 py-1 rounded text-gray-300">
                        {feature}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className={ultraMode ? 'text-yellow-400' : 'text-purple-400'}>
                      ~{credits} créditos
                      {ultraMode && <Bolt className="w-3 h-3 inline ml-1" />}
                    </span>
                    <span className="text-gray-500 group-hover:text-purple-400 transition-colors flex items-center gap-1">
                      Generar <ChevronRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Custom App Section */}
          <div className="border-t border-purple-500/20 pt-10">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold mb-2">App Personalizada</h3>
              <p className="text-gray-400 text-sm">Describe tu aplicación y los agentes la construirán</p>
            </div>
            <div className="max-w-2xl mx-auto">
              <input
                type="text"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                placeholder="Nombre de tu app"
                data-testid="app-name-input"
                className="w-full bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-4 py-3 mb-3 focus:border-purple-500 outline-none"
              />
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe tu aplicación en detalle... Ejemplo: Una plataforma de cursos online con videos, cuestionarios, progreso del estudiante y certificados."
                data-testid="app-description-input"
                className="w-full h-32 bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-4 py-3 resize-none focus:border-purple-500 outline-none"
              />
              <button
                onClick={handleGenerate}
                disabled={!description.trim()}
                data-testid="generate-custom-app-btn"
                className={`w-full mt-4 py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-all ${
                  ultraMode 
                    ? 'bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600'
                    : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {ultraMode ? <Bolt className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
                {ultraMode ? 'Generar con ULTRA MODE' : 'Generar App'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-[#0a0a12] min-h-screen text-white ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-[#0d0d1a]">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={handleNewProject}
              data-testid="back-btn"
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft size={18} />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold">Melus AI</h1>
                {workspaceId && (
                  <span className="text-xs text-gray-500">
                    v{currentVersion} • {workspaceId}
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Version History Button */}
            <div className="relative">
              <button
                onClick={() => {
                  fetchVersions();
                  setShowVersions(!showVersions);
                }}
                data-testid="version-history-btn"
                className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors flex items-center gap-2"
              >
                <History size={16} />
                <span className="hidden sm:inline">v{currentVersion}</span>
              </button>
              {showVersions && (
                <VersionHistoryPanel
                  versions={versions}
                  currentVersion={currentVersion}
                  onRollback={handleRollback}
                  onClose={() => setShowVersions(false)}
                />
              )}
            </div>
            
            <button
              onClick={handleNewProject}
              data-testid="new-project-btn"
              className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
            >
              + Nuevo
            </button>
            <span className="text-sm text-gray-400">
              <span className="text-purple-400 font-bold">{user?.credits || 0}</span> créditos
            </span>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/5"
            >
              {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-60px)]">
        {/* Left Panel - Input & Console */}
        <div className="w-[400px] border-r border-purple-500/20 flex flex-col">
          {/* Input Section */}
          <div className="p-4 border-b border-purple-500/20">
            <input
              type="text"
              value={appName}
              onChange={(e) => setAppName(e.target.value)}
              placeholder="Nombre de la app"
              className="w-full bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-3 py-2 text-sm mb-3 focus:border-purple-500 outline-none"
              disabled={isGenerating}
            />
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe tu aplicación..."
              className="w-full h-20 bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-3 py-2 text-sm resize-none focus:border-purple-500 outline-none"
              disabled={isGenerating}
            />
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !description.trim()}
              data-testid="generate-btn"
              className={`w-full mt-3 py-2.5 rounded-lg font-medium flex items-center justify-center gap-2 transition-all ${
                isGenerating
                  ? 'bg-orange-500/20 text-orange-400'
                  : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white'
              }`}
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generando...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Generar
                </>
              )}
            </button>
          </div>

          {/* Agent Status Bar */}
          <div className="px-4 py-2 border-b border-purple-500/20 bg-[#0d0d1a]/50">
            <div className="flex flex-wrap gap-2">
              {Object.entries(AGENT_ICONS).map(([agent, Icon]) => (
                <div
                  key={agent}
                  className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-all ${
                    currentAgent === agent
                      ? 'bg-purple-500/30 ring-1 ring-purple-500 scale-105'
                      : logs.some(l => l.agent === agent && l.type === 'success')
                      ? 'bg-green-500/20'
                      : 'bg-white/5'
                  }`}
                >
                  <Icon className={`w-3 h-3 ${
                    currentAgent === agent ? 'text-purple-400 animate-pulse' : 'text-gray-500'
                  }`} />
                  <span className="capitalize">{agent}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Console Logs */}
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="px-4 py-2 bg-[#1a1a2e] border-b border-purple-500/20 flex items-center justify-between">
              <span className="text-sm text-gray-400 flex items-center gap-2">
                <Terminal className="w-4 h-4" />
                Consola de Agentes
              </span>
              <span className="text-xs text-purple-400">{logs.length} eventos</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-xs">
              {logs.length === 0 ? (
                <div className="text-gray-600 text-center py-8">
                  <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  Describe tu app y haz clic en "Generar"
                </div>
              ) : (
                logs.map((log, idx) => {
                  const Icon = AGENT_ICONS[log.agent] || Zap;
                  const colorClass = AGENT_COLORS[log.agent] || 'text-gray-400';
                  
                  return (
                    <div
                      key={idx}
                      className={`p-2 rounded ${
                        log.type === 'error' ? 'bg-red-500/10 border border-red-500/20' :
                        log.type === 'success' ? 'bg-green-500/10' :
                        log.type === 'working' ? 'bg-yellow-500/10' :
                        'bg-white/5'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {getStatusIcon(log.type)}
                        <Icon className={`w-3.5 h-3.5 mt-0.5 ${colorClass}`} />
                        <div className="flex-1 min-w-0">
                          <span className={`${colorClass} font-medium`}>[{log.agent}]</span>
                          <span className={`ml-2 ${
                            log.type === 'error' ? 'text-red-400' :
                            log.type === 'success' ? 'text-green-400' :
                            'text-gray-300'
                          }`}>
                            {log.message}
                          </span>
                        </div>
                      </div>
                      {log.data && (
                        <button
                          onClick={() => setExpandedLogs(prev => ({
                            ...prev,
                            [idx]: !prev[idx]
                          }))}
                          className="mt-1 ml-6 text-gray-500 hover:text-gray-300 flex items-center gap-1"
                        >
                          {expandedLogs[idx] ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                          Ver detalles
                        </button>
                      )}
                      {log.data && expandedLogs[idx] && (
                        <pre className="mt-2 ml-6 p-2 bg-[#0a0a12] rounded text-gray-400 overflow-x-auto text-[10px]">
                          {typeof log.data === 'string' ? log.data : JSON.stringify(log.data, null, 2)}
                        </pre>
                      )}
                    </div>
                  );
                })
              )}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>

        {/* Right Panel - Preview */}
        <div className="flex-1 flex flex-col">
          {/* Tab Bar */}
          <div className="flex items-center gap-1 px-4 py-2 bg-[#1a1a2e] border-b border-purple-500/20">
            <button
              onClick={() => setActiveTab('preview')}
              data-testid="tab-preview"
              className={`px-4 py-1.5 rounded-lg text-sm flex items-center gap-2 transition-all ${
                activeTab === 'preview'
                  ? 'bg-purple-500/20 text-purple-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Eye className="w-4 h-4" />
              Preview
            </button>
            <button
              onClick={() => setActiveTab('code')}
              data-testid="tab-code"
              className={`px-4 py-1.5 rounded-lg text-sm flex items-center gap-2 transition-all ${
                activeTab === 'code'
                  ? 'bg-purple-500/20 text-purple-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <FileCode className="w-4 h-4" />
              Código
            </button>
            
            <div className="flex-1" />
            
            {/* Debug Button - 30 credits */}
            {previewError && (
              <button
                onClick={handleDebug}
                disabled={isDebugging}
                data-testid="debug-btn"
                className="px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 bg-orange-500/20 text-orange-400 hover:bg-orange-500/30 disabled:opacity-50"
              >
                {isDebugging ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Bug className="w-4 h-4" />
                )}
                Auto-fix (30 créditos)
              </button>
            )}
            
            {Object.keys(files).length > 0 && (
              <>
                <button
                  onClick={handleDownload}
                  data-testid="download-btn"
                  className="px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 text-gray-400 hover:text-white hover:bg-white/5"
                  title="Descargar ZIP"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => githubConnected ? setShowGithubModal(true) : handleConnectGithub()}
                  data-testid="github-btn"
                  className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 transition-all ${
                    githubConnected 
                      ? 'text-green-400 hover:bg-green-500/10' 
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                  title={githubConnected ? `GitHub: @${githubUsername}` : "Conectar GitHub"}
                >
                  <Github className="w-4 h-4" />
                  {githubConnected && <span className="text-xs">@{githubUsername}</span>}
                </button>
              </>
            )}
          </div>

          {/* GitHub Push Modal */}
          {showGithubModal && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[#1a1a2e] border border-purple-500/30 rounded-xl p-6 w-96 shadow-2xl">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Github className="w-5 h-5" />
                  Subir a GitHub
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-400 mb-1 block">Nombre del repositorio</label>
                    <input
                      type="text"
                      value={githubRepoName}
                      onChange={(e) => setGithubRepoName(e.target.value)}
                      placeholder={appName.toLowerCase().replace(/\s+/g, '-')}
                      className="w-full bg-[#0d0d1a] border border-purple-500/30 rounded-lg px-3 py-2 text-sm focus:border-purple-500 outline-none"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="private-repo"
                      checked={githubPrivate}
                      onChange={(e) => setGithubPrivate(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="private-repo" className="text-sm text-gray-400">Repositorio privado</label>
                  </div>
                  <div className="text-xs text-gray-500 bg-white/5 p-3 rounded-lg">
                    <p className="font-medium text-gray-400 mb-1">Costo: 50 créditos</p>
                    <p>Se creará un nuevo repositorio y se subirán todos los archivos del proyecto.</p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowGithubModal(false)}
                      className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handlePushToGithub}
                      disabled={isPushingToGithub}
                      className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {isPushingToGithub ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <Github className="w-4 h-4" />
                      )}
                      {isPushingToGithub ? 'Subiendo...' : 'Subir'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Preview/Code Area */}
          <div className="flex-1 overflow-hidden">
            {Object.keys(files).length === 0 ? (
              <div className="h-full flex items-center justify-center bg-[#0d0d1a]">
                <div className="text-center">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center mx-auto mb-4">
                    <Code className="w-10 h-10 text-purple-500/50" />
                  </div>
                  <h3 className="text-xl text-gray-400 mb-2">Tu app aparecerá aquí</h3>
                  <p className="text-gray-600 text-sm">
                    Describe tu aplicación y haz clic en "Generar"
                  </p>
                </div>
              </div>
            ) : (
              <SandpackProvider
                template="react"
                theme="dark"
                files={getSandpackFiles()}
                customSetup={{
                  dependencies: {
                    "react-router-dom": "^6.20.0",
                    "prop-types": "^15.8.1",
                    "lucide-react": "^0.294.0",
                    "axios": "^1.6.0"
                  }
                }}
                options={{
                  externalResources: [
                    "https://cdn.tailwindcss.com"
                  ],
                  recompileMode: "delayed",
                  recompileDelay: 500
                }}
              >
                <SandpackLayout style={{ height: '100%', border: 'none' }}>
                  {activeTab === 'code' ? (
                    <>
                      <SandpackFileExplorer style={{ height: '100%' }} />
                      <SandpackCodeEditor
                        showLineNumbers
                        showTabs
                        closableTabs
                        style={{ height: '100%', flex: 2 }}
                      />
                    </>
                  ) : (
                    <div style={{ width: '100%', height: '100%' }}>
                      <CustomPreview 
                        onError={(err) => setPreviewError(err)} 
                        onConsoleLog={handleConsoleLog}
                      />
                    </div>
                  )}
                </SandpackLayout>
              </SandpackProvider>
            )}
          </div>

          {/* Error Bar */}
          {previewError && (
            <div className="px-4 py-3 bg-red-500/10 border-t border-red-500/30 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-red-400 text-sm font-medium">Error detectado</p>
                <p className="text-red-300/70 text-xs mt-1 break-all">{previewError}</p>
              </div>
              <button
                onClick={() => setPreviewError(null)}
                className="text-red-400 hover:text-red-300 flex-shrink-0"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AppGeneratorV2;
