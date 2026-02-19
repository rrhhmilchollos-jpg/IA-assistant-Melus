import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  SandpackProvider,
  SandpackLayout,
  SandpackCodeEditor,
  SandpackPreview,
  SandpackFileExplorer,
} from '@codesandbox/sandpack-react';
import {
  Send,
  ArrowLeft,
  Eye,
  EyeOff,
  Code,
  FileCode,
  FolderOpen,
  Download,
  Github,
  Rocket,
  Zap,
  User,
  Bot,
  Loader2,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  X,
  Sparkles,
  Package,
  PanelRightClose,
  PanelRight
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Agent status colors
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
  system: 'text-violet-400'
};

const WorkspacePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, updateCredits } = useAuth();
  
  // Workspace state
  const [workspaceId, setWorkspaceId] = useState(searchParams.get('workspace') || null);
  const [projectName, setProjectName] = useState('Nuevo Proyecto');
  const [files, setFiles] = useState({});
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  
  // UI state - PREVIEW OCULTO POR DEFECTO
  const [showPreview, setShowPreview] = useState(false);
  const [previewTab, setPreviewTab] = useState('preview'); // 'preview' | 'code'
  const [expandedFolders, setExpandedFolders] = useState({});
  
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load workspace if ID provided
  useEffect(() => {
    if (workspaceId) {
      loadWorkspace(workspaceId);
      connectWebSocket(workspaceId);
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [workspaceId]);

  // Handle initial prompt from home page
  useEffect(() => {
    const initialPrompt = searchParams.get('prompt');
    if (initialPrompt && !workspaceId) {
      // Add welcome message
      addMessage('system', 'Bienvenido a MelusAI. Procesando tu solicitud...');
      handleSendMessage(initialPrompt);
    }
  }, []);

  const loadWorkspace = async (wsId) => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/workspace/${wsId}`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || {});
        setProjectName(data.name || 'Mi Proyecto');
        addMessage('system', `Proyecto "${data.name}" cargado. ¿En qué puedo ayudarte?`);
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
      addMessage('error', 'Error al cargar el proyecto. Por favor, intenta de nuevo.');
    }
  };

  const connectWebSocket = (wsId) => {
    try {
      const wsUrl = API_BASE.replace('http', 'ws') + `/ws/${wsId}`;
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWSMessage(data);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (e) {
      console.error('WebSocket connection failed:', e);
    }
  };

  const handleWSMessage = (data) => {
    switch (data.type) {
      case 'agent_start':
        setCurrentAgent(data.agent);
        addMessage('agent', `${data.agent} está trabajando...`, data.agent);
        break;
        
      case 'agent_complete':
        addMessage('agent', `${data.agent} completado`, data.agent);
        break;
        
      case 'log':
        if (data.log?.message) {
          addMessage('agent', data.log.message, data.log.agent);
        }
        break;
        
      case 'files_updated':
        setFiles(data.files);
        // Auto-abrir preview cuando hay archivos
        if (Object.keys(data.files).length > 0) {
          setShowPreview(true);
        }
        break;
        
      case 'generation_complete':
        setIsGenerating(false);
        setCurrentAgent(null);
        setFiles(data.files);
        if (data.credits_used) {
          updateCredits(user?.credits - data.credits_used);
        }
        addMessage('system', `¡Proyecto generado! ${Object.keys(data.files).length} archivos creados. Puedes ver el preview o seguir modificando.`);
        // Auto-abrir preview
        setShowPreview(true);
        break;
        
      case 'agent_error':
        addMessage('error', `Error en ${data.agent}: ${data.error}`);
        setIsGenerating(false);
        break;
        
      default:
        break;
    }
  };

  const addMessage = (type, content, agent = null) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      type,
      content,
      agent,
      timestamp: new Date().toISOString()
    }]);
  };

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isGenerating) return;
    
    // Add user message
    addMessage('user', messageText);
    setInputMessage('');
    setIsGenerating(true);
    
    const token = localStorage.getItem('session_token');
    
    try {
      if (!workspaceId) {
        // Create new project
        addMessage('system', 'Analizando tu solicitud...');
        
        const response = await fetch(`${API_BASE}/api/agents/v2/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': token
          },
          body: JSON.stringify({
            description: messageText,
            name: messageText.substring(0, 50),
            ultra_mode: false
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          setWorkspaceId(data.workspace_id);
          setFiles(data.files || {});
          setProjectName(data.name || 'Mi Proyecto');
          if (data.credits_remaining !== undefined) {
            updateCredits(data.credits_remaining);
          }
          
          // Update URL
          window.history.replaceState(null, '', `/workspace?workspace=${data.workspace_id}`);
          
          // Connect WebSocket
          connectWebSocket(data.workspace_id);
          
          const fileCount = Object.keys(data.files || {}).length;
          addMessage('system', `¡Proyecto creado! ${fileCount} archivos generados.`);
          
          // Auto-abrir preview si hay archivos
          if (fileCount > 0) {
            setShowPreview(true);
          }
        } else {
          throw new Error(data.detail || 'Error al generar');
        }
      } else {
        // Modify existing project
        addMessage('system', 'Procesando tu solicitud...');
        
        const response = await fetch(`${API_BASE}/api/agents/v2/modify`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': token
          },
          body: JSON.stringify({
            workspace_id: workspaceId,
            instruction: messageText
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          setFiles(data.files || files);
          addMessage('system', `Modificación aplicada. ${data.modified_files?.length || 0} archivos actualizados.`);
        } else {
          throw new Error(data.detail || 'Error al modificar');
        }
      }
    } catch (error) {
      console.error('Error:', error);
      addMessage('error', error.message || 'Error al procesar la solicitud');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!workspaceId || Object.keys(files).length === 0) return;
    
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/workspace/${workspaceId}/download`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${projectName || 'proyecto'}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        addMessage('system', 'Proyecto descargado correctamente.');
      }
    } catch (error) {
      console.error('Download error:', error);
      addMessage('error', 'Error al descargar el proyecto.');
    }
  };

  const handleDeploy = async () => {
    addMessage('system', 'Función de deploy próximamente disponible. Por ahora, puedes descargar el proyecto.');
  };

  // Organize files into folder structure
  const getFileTree = () => {
    const tree = {};
    Object.keys(files).forEach(path => {
      const parts = path.split('/');
      let current = tree;
      parts.forEach((part, idx) => {
        if (idx === parts.length - 1) {
          current[part] = { type: 'file', path };
        } else {
          if (!current[part]) {
            current[part] = { type: 'folder', children: {} };
          }
          current = current[part].children;
        }
      });
    });
    return tree;
  };

  const renderFileTree = (node, level = 0) => {
    return Object.entries(node).map(([name, item]) => {
      if (item.type === 'folder') {
        const isExpanded = expandedFolders[name] !== false;
        return (
          <div key={name}>
            <button
              onClick={() => setExpandedFolders(prev => ({ ...prev, [name]: !isExpanded }))}
              className="flex items-center gap-1 w-full px-2 py-1 text-sm text-gray-300 hover:bg-white/5 rounded"
              style={{ paddingLeft: `${level * 12 + 8}px` }}
            >
              {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              <FolderOpen size={14} className="text-yellow-400" />
              <span>{name}</span>
            </button>
            {isExpanded && renderFileTree(item.children, level + 1)}
          </div>
        );
      } else {
        return (
          <button
            key={name}
            className="flex items-center gap-1 w-full px-2 py-1 text-sm text-gray-400 hover:bg-white/5 hover:text-white rounded"
            style={{ paddingLeft: `${level * 12 + 24}px` }}
          >
            <FileCode size={14} className="text-cyan-400" />
            <span className="truncate">{name}</span>
          </button>
        );
      }
    });
  };

  // Format files for Sandpack
  const sandpackFiles = Object.entries(files).reduce((acc, [path, content]) => {
    acc[`/${path}`] = { code: content };
    return acc;
  }, {});

  const hasFiles = Object.keys(files).length > 0;

  return (
    <div className="h-screen flex flex-col bg-[#0a0a12] text-white" data-testid="workspace-page">
      {/* Header */}
      <header className="h-14 border-b border-gray-800 flex items-center justify-between px-4 bg-[#0d0d18]">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            data-testid="back-btn"
          >
            <ArrowLeft size={18} />
            <span className="text-sm">Volver</span>
          </button>
          
          <div className="h-5 w-px bg-gray-700" />
          
          <div className="flex items-center gap-2">
            <Package size={18} className="text-purple-400" />
            <span className="font-medium text-lg">{projectName}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Credits */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/20 rounded-full border border-purple-500/30">
            <Zap size={14} className="text-yellow-400" />
            <span className="text-sm font-medium text-yellow-400">
              {user?.unlimited_credits ? '∞' : user?.credits?.toLocaleString() || 0}
            </span>
          </div>
          
          {/* PREVIEW Button - Solo si hay archivos */}
          {hasFiles && (
            <button
              onClick={() => setShowPreview(!showPreview)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                showPreview 
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' 
                  : 'bg-gray-700 text-white hover:bg-gray-600'
              }`}
              data-testid="preview-btn"
            >
              {showPreview ? <EyeOff size={18} /> : <Eye size={18} />}
              <span>PREVIEW</span>
            </button>
          )}
          
          {/* Deploy Button */}
          <button
            onClick={handleDeploy}
            disabled={!hasFiles}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg text-white font-medium hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            data-testid="deploy-btn"
          >
            <Rocket size={18} />
            <span>Deploy</span>
          </button>
          
          {/* Download */}
          <button
            onClick={handleDownload}
            disabled={!hasFiles}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-50"
            title="Descargar proyecto"
            data-testid="download-btn"
          >
            <Download size={20} />
          </button>
          
          {/* GitHub */}
          <button
            className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
            title="GitHub"
          >
            <Github size={20} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel - Siempre visible, ancho dinámico */}
        <div 
          className={`flex flex-col border-r border-gray-800 bg-[#0d0d18] transition-all duration-300 ${
            showPreview ? 'w-1/2' : 'w-full'
          }`}
        >
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-500 max-w-md">
                  <Sparkles size={48} className="mx-auto mb-4 text-purple-400 opacity-50" />
                  <h3 className="text-xl font-medium text-white mb-2">¿Qué quieres crear?</h3>
                  <p className="text-sm">
                    Describe tu proyecto y los agentes de IA lo construirán automáticamente.
                    Solo responderán si necesitan más información.
                  </p>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.type !== 'user' && (
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.type === 'error' ? 'bg-red-500/20' : 
                      msg.type === 'agent' ? 'bg-purple-500/20' : 'bg-cyan-500/20'
                    }`}>
                      {msg.type === 'error' ? (
                        <AlertCircle size={18} className="text-red-400" />
                      ) : msg.type === 'agent' ? (
                        <Bot size={18} className={AGENT_COLORS[msg.agent] || 'text-purple-400'} />
                      ) : (
                        <Bot size={18} className="text-cyan-400" />
                      )}
                    </div>
                  )}
                  
                  <div className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                    msg.type === 'user' 
                      ? 'bg-gradient-to-r from-purple-500/40 to-pink-500/40 text-white' 
                      : msg.type === 'error'
                      ? 'bg-red-500/10 text-red-300 border border-red-500/30'
                      : 'bg-[#1a1a2e] text-gray-200 border border-gray-700/50'
                  }`}>
                    {msg.agent && msg.type === 'agent' && (
                      <span className={`text-xs font-bold uppercase ${AGENT_COLORS[msg.agent] || 'text-purple-400'}`}>
                        {msg.agent}
                      </span>
                    )}
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                    <span className="text-xs text-gray-500 mt-1 block">
                      {new Date(msg.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  
                  {msg.type === 'user' && (
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                      <User size={18} className="text-white" />
                    </div>
                  )}
                </div>
              ))
            )}
            
            {/* Loading indicator */}
            {isGenerating && (
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <Loader2 size={18} className="text-purple-400 animate-spin" />
                </div>
                <div className="bg-[#1a1a2e] rounded-2xl px-4 py-3 border border-gray-700/50">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-300">
                      {currentAgent ? `${currentAgent} trabajando...` : 'Procesando...'}
                    </span>
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Files Panel - Solo si hay archivos y preview está cerrado */}
          {hasFiles && !showPreview && (
            <div className="h-48 border-t border-gray-800 overflow-hidden">
              <div className="p-3 text-xs text-gray-400 font-medium uppercase flex items-center gap-2 border-b border-gray-800/50 bg-[#0a0a12]">
                <FolderOpen size={14} />
                Archivos del proyecto ({Object.keys(files).length})
              </div>
              <div className="p-2 overflow-y-auto h-[calc(100%-40px)]">
                {renderFileTree(getFileTree())}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="p-4 border-t border-gray-800 bg-[#0a0a12]">
            <div className="relative">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Escribe lo que quieres crear o modificar..."
                className="w-full bg-[#1a1a2e] border border-gray-700 rounded-xl px-4 py-3 pr-14 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:border-purple-500/50 transition-colors"
                rows={2}
                disabled={isGenerating}
                data-testid="chat-input"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputMessage.trim() || isGenerating}
                className="absolute right-3 bottom-3 p-2.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg text-white hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                data-testid="send-btn"
              >
                {isGenerating ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Send size={18} />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Preview Panel - Solo visible cuando showPreview es true */}
        {showPreview && (
          <div className="w-1/2 flex flex-col bg-[#0a0a12]">
            {/* Preview Header */}
            <div className="h-12 border-b border-gray-800 flex items-center justify-between px-4 bg-[#0d0d18]">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPreviewTab('preview')}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    previewTab === 'preview' 
                      ? 'bg-purple-500/20 text-purple-400' 
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <Eye size={16} />
                  Preview
                </button>
                <button
                  onClick={() => setPreviewTab('code')}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    previewTab === 'code' 
                      ? 'bg-purple-500/20 text-purple-400' 
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <Code size={16} />
                  Código
                </button>
              </div>
              
              <button
                onClick={() => setShowPreview(false)}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                title="Cerrar preview"
              >
                <X size={18} />
              </button>
            </div>

            {/* Preview Content */}
            <div className="flex-1 overflow-hidden">
              {hasFiles ? (
                <SandpackProvider
                  template="react"
                  files={sandpackFiles}
                  theme="dark"
                  options={{
                    externalResources: ['https://cdn.tailwindcss.com'],
                  }}
                >
                  <SandpackLayout style={{ height: '100%', border: 'none' }}>
                    {previewTab === 'preview' ? (
                      <SandpackPreview
                        showNavigator
                        showRefreshButton
                        style={{ height: '100%' }}
                      />
                    ) : (
                      <div className="flex h-full w-full">
                        <SandpackFileExplorer style={{ width: '200px' }} />
                        <SandpackCodeEditor
                          showTabs
                          showLineNumbers
                          style={{ flex: 1 }}
                        />
                      </div>
                    )}
                  </SandpackLayout>
                </SandpackProvider>
              ) : (
                <div className="flex-1 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <Code size={48} className="mx-auto mb-4 opacity-30" />
                    <p className="text-lg">Sin archivos aún</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkspacePage;
