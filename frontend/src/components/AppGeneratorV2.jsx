import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  SandpackProvider,
  SandpackLayout,
  SandpackCodeEditor,
  SandpackPreview,
  SandpackFileExplorer,
  useSandpack,
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
  ArrowLeft
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Template icons mapping
const TEMPLATE_ICONS = {
  ecommerce: ShoppingCart,
  blog: FileText,
  dashboard: LayoutDashboard,
  landing: Rocket,
  taskmanager: CheckSquare,
  portfolio: User
};

// Agent icons mapping
const AGENT_ICONS = {
  classifier: Cpu,
  architect: FolderOpen,
  frontend: Code,
  backend: Server,
  integrator: Wrench,
  debugger: Bug,
  system: Zap
};

// Agent colors
const AGENT_COLORS = {
  classifier: 'text-purple-400',
  architect: 'text-blue-400',
  frontend: 'text-cyan-400',
  backend: 'text-green-400',
  integrator: 'text-yellow-400',
  debugger: 'text-orange-400',
  system: 'text-pink-400'
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

// Custom Preview component with error handling
const CustomPreview = ({ onError }) => {
  const { sandpack } = useSandpack();
  
  useEffect(() => {
    // Listen for errors
    const handleMessage = (e) => {
      if (e.data?.type === 'error') {
        onError?.(e.data.error);
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onError]);
  
  return (
    <SandpackPreview
      showNavigator
      showRefreshButton
      style={{ height: '100%' }}
    />
  );
};

const AppGeneratorV2 = () => {
  const { user, updateCredits } = useAuth();
  const [description, setDescription] = useState('');
  const [appName, setAppName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [logs, setLogs] = useState([]);
  const [files, setFiles] = useState({});
  const [workspaceId, setWorkspaceId] = useState(null);
  const [activeTab, setActiveTab] = useState('preview'); // preview, code, console
  const [expandedLogs, setExpandedLogs] = useState({});
  const [previewError, setPreviewError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [showTemplates, setShowTemplates] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
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
        setLogs([{
          agent: 'system',
          type: 'info',
          message: `Workspace cargado: ${data.name}`,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
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
    setLogs([]);
    setFiles({});
    setPreviewError(null);
    
    // Add initial log
    setLogs([{
      agent: 'system',
      type: 'info',
      message: `Iniciando generación de "${appName || 'Mi App'}"...`,
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
          name: appName || 'Mi App'
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Generation failed');
      }

      setWorkspaceId(data.workspace_id);
      setFiles(data.files);
      updateCredits(data.credits_remaining);
      
      // Save workspace ID to localStorage for persistence
      localStorage.setItem('melus_workspace_id', data.workspace_id);
      
      // Add success log
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'success',
        message: `¡App generada! ${Object.keys(data.files).length} archivos creados`,
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

  const handleDebug = async () => {
    if (!previewError || !workspaceId) return;
    
    const token = localStorage.getItem('session_token');
    
    try {
      setLogs(prev => [...prev, {
        agent: 'debugger',
        type: 'working',
        message: 'Analizando y corrigiendo error...',
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
          error: previewError
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setFiles(data.files);
        setPreviewError(null);
        updateCredits(data.credits_remaining);
      }
    } catch (error) {
      console.error('Debug error:', error);
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
    setFiles({});
    setPreviewError(null);
    
    const template = templates.find(t => t.id === templateId);
    setSelectedTemplate(template);
    
    setLogs([{
      agent: 'system',
      type: 'info',
      message: `Generando desde template: ${template?.name}...`,
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
          name: template?.name || 'Mi App'
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
      
      setLogs(prev => [...prev, {
        agent: 'system',
        type: 'success',
        message: `¡App generada! ${Object.keys(data.files).length} archivos creados`,
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
      }
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  // Start new project
  const handleNewProject = () => {
    setShowTemplates(true);
    setFiles({});
    setLogs([]);
    setWorkspaceId(null);
    setAppName('');
    setDescription('');
    setSelectedTemplate(null);
    localStorage.removeItem('melus_workspace_id');
  };

  // Convert files to Sandpack format
  const getSandpackFiles = () => {
    const sandpackFiles = {};
    
    Object.entries(files).forEach(([path, content]) => {
      // Ensure path starts with /
      const normalizedPath = path.startsWith('/') ? path : `/${path}`;
      sandpackFiles[normalizedPath] = {
        code: content,
        active: normalizedPath === '/src/App.jsx' || normalizedPath === '/src/App.js'
      };
    });
    
    // Ensure minimum files exist
    if (!sandpackFiles['/src/App.jsx'] && !sandpackFiles['/src/App.js']) {
      sandpackFiles['/src/App.jsx'] = {
        code: `export default function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <h1 className="text-3xl">Generating your app...</h1>
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
              <Sparkles className="w-6 h-6 text-purple-400" />
              <h1 className="text-xl font-bold">Crear Nueva App</h1>
            </div>
            <span className="text-sm text-gray-400">
              Créditos: <span className="text-purple-400 font-medium">{user?.credits || 0}</span>
            </span>
          </div>
        </div>

        {/* Templates Grid */}
        <div className="max-w-6xl mx-auto px-6 py-10">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-3">Elige una plantilla</h2>
            <p className="text-gray-400">Selecciona un tipo de app y genera código completo con un clic</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {templates.map((template) => {
              const Icon = TEMPLATE_ICONS[template.id] || Code;
              return (
                <div
                  key={template.id}
                  onClick={() => handleGenerateFromTemplate(template.id)}
                  className="group cursor-pointer bg-[#1a1a2e] border border-purple-500/20 rounded-xl p-6 hover:border-purple-500/50 hover:bg-[#1f1f3a] transition-all"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${template.color} flex items-center justify-center mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-purple-400 transition-colors">
                    {template.name}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4">
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
                    <span className="text-purple-400">~{template.estimated_credits} créditos</span>
                    <span className="text-gray-500 group-hover:text-purple-400 transition-colors">
                      Generar →
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Custom App Section */}
          <div className="border-t border-purple-500/20 pt-10">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold mb-2">¿Tienes algo específico en mente?</h3>
              <p className="text-gray-400 text-sm">Describe tu app y nuestros agentes la construirán</p>
            </div>
            <div className="max-w-2xl mx-auto">
              <input
                type="text"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                placeholder="Nombre de tu app"
                className="w-full bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-4 py-3 mb-3 focus:border-purple-500 outline-none"
              />
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe tu aplicación en detalle..."
                className="w-full h-32 bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-4 py-3 resize-none focus:border-purple-500 outline-none"
              />
              <button
                onClick={handleGenerate}
                disabled={!description.trim()}
                className="w-full mt-4 py-3 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium flex items-center justify-center gap-2 transition-all"
              >
                <Play className="w-5 h-5" />
                Generar App Personalizada
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
            <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              App Generator
            </h1>
            {workspaceId && (
              <span className="text-xs text-gray-500 font-mono">
                {workspaceId}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-400">
              Créditos: <span className="text-purple-400 font-medium">{user?.credits || 0}</span>
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
              placeholder="Describe tu aplicación en detalle... Ej: Una app de gestión de tareas con autenticación, donde los usuarios pueden crear proyectos, añadir tareas, marcarlas como completadas y ver estadísticas."
              className="w-full h-24 bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-3 py-2 text-sm resize-none focus:border-purple-500 outline-none"
              disabled={isGenerating}
            />
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !description.trim()}
              className={`w-full mt-3 py-2.5 rounded-lg font-medium flex items-center justify-center gap-2 transition-all ${
                isGenerating
                  ? 'bg-orange-500/20 text-orange-400'
                  : 'bg-purple-500 hover:bg-purple-600 text-white'
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
                  Generar App
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
                      ? 'bg-purple-500/30 ring-1 ring-purple-500'
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
                Consola
              </span>
              <span className="text-xs text-purple-400">{logs.length} eventos</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-xs">
              {logs.length === 0 ? (
                <div className="text-gray-600 text-center py-8">
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
                        log.type === 'error' ? 'bg-red-500/10' :
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
                          {JSON.stringify(log.data, null, 2)}
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
            
            {previewError && (
              <button
                onClick={handleDebug}
                className="px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 bg-orange-500/20 text-orange-400 hover:bg-orange-500/30"
              >
                <Bug className="w-4 h-4" />
                Auto-fix
              </button>
            )}
            
            {Object.keys(files).length > 0 && (
              <>
                <button
                  onClick={handleDownload}
                  className="px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 text-gray-400 hover:text-white hover:bg-white/5"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  className="px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 text-gray-400 hover:text-white hover:bg-white/5"
                >
                  <Github className="w-4 h-4" />
                </button>
              </>
            )}
          </div>

          {/* Preview/Code Area */}
          <div className="flex-1 overflow-hidden">
            {Object.keys(files).length === 0 ? (
              <div className="h-full flex items-center justify-center bg-[#0d0d1a]">
                <div className="text-center">
                  <Code className="w-16 h-16 text-purple-500/30 mx-auto mb-4" />
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
                      <CustomPreview onError={(err) => setPreviewError(err)} />
                    </div>
                  )}
                </SandpackLayout>
              </SandpackProvider>
            )}
          </div>

          {/* Error Bar */}
          {previewError && (
            <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/30 flex items-center justify-between">
              <div className="flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                <span className="truncate">{previewError}</span>
              </div>
              <button
                onClick={() => setPreviewError(null)}
                className="text-red-400 hover:text-red-300"
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
