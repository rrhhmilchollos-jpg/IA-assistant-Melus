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
  Code,
  FileCode,
  FolderOpen,
  Download,
  Github,
  Zap,
  User,
  Bot,
  Loader2,
  CheckCircle,
  AlertCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Play,
  Square,
  RotateCcw,
  Share2,
  Settings,
  Sparkles,
  Package
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
  const [projectName, setProjectName] = useState('');
  const [files, setFiles] = useState({});
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'code'
  const [showFiles, setShowFiles] = useState(true);
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
        
        // Add system message
        addMessage('system', `Proyecto "${data.name}" cargado. ¿En qué puedo ayudarte?`);
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
      addMessage('system', 'Error al cargar el proyecto. Por favor, intenta de nuevo.');
    }
  };

  const connectWebSocket = (wsId) => {
    const wsUrl = API_BASE.replace('http', 'ws') + `/ws/${wsId}`;
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWSMessage(data);
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const handleWSMessage = (data) => {
    switch (data.type) {
      case 'agent_start':
        setCurrentAgent(data.agent);
        addMessage('agent', `${data.agent} está trabajando...`, data.agent);
        break;
        
      case 'agent_complete':
        addMessage('agent', `${data.agent} completado ✓`, data.agent);
        break;
        
      case 'log':
        if (data.log?.message) {
          addMessage('agent', data.log.message, data.log.agent);
        }
        break;
        
      case 'files_updated':
        setFiles(data.files);
        break;
        
      case 'generation_complete':
        setIsGenerating(false);
        setCurrentAgent(null);
        setFiles(data.files);
        if (data.credits_used) {
          updateCredits(user?.credits - data.credits_used);
        }
        addMessage('system', `¡Proyecto generado! ${Object.keys(data.files).length} archivos creados.`);
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
      id: Date.now(),
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
      // If no workspace, create one and generate
      if (!workspaceId) {
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
          updateCredits(data.credits_remaining);
          
          // Update URL
          window.history.replaceState(null, '', `/workspace?workspace=${data.workspace_id}`);
          
          // Connect WebSocket for real-time updates
          connectWebSocket(data.workspace_id);
          
          addMessage('system', `¡Proyecto creado! ${Object.keys(data.files || {}).length} archivos generados.`);
        } else {
          throw new Error(data.detail || 'Error al generar');
        }
      } else {
        // Existing workspace - send modification request
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
          addMessage('system', 'Modificación aplicada.');
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
      }
    } catch (error) {
      console.error('Download error:', error);
    }
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

  return (
    <div className="h-screen flex flex-col bg-[#0a0a12] text-white" data-testid="workspace-page">
      {/* Header */}
      <header className="h-12 border-b border-gray-800 flex items-center justify-between px-4 bg-[#0d0d18]">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft size={18} />
            <span className="text-sm">Volver</span>
          </button>
          
          <div className="h-4 w-px bg-gray-700" />
          
          <div className="flex items-center gap-2">
            <Package size={16} className="text-purple-400" />
            <span className="font-medium">{projectName || 'Nuevo Proyecto'}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Credits */}
          <div className="flex items-center gap-2 px-3 py-1 bg-purple-500/20 rounded-full">
            <Zap size={14} className="text-yellow-400" />
            <span className="text-sm text-yellow-400">
              {user?.unlimited_credits ? '∞' : user?.credits?.toLocaleString() || 0}
            </span>
          </div>
          
          {/* Actions */}
          <button
            onClick={handleDownload}
            disabled={Object.keys(files).length === 0}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-50"
            title="Descargar proyecto"
          >
            <Download size={18} />
          </button>
          
          <button
            className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
            title="GitHub"
          >
            <Github size={18} />
          </button>
          
          <button
            className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
            title="Compartir"
          >
            <Share2 size={18} />
          </button>
        </div>
      </header>

      {/* Main Content - Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Chat & Files */}
        <div className="w-[400px] flex flex-col border-r border-gray-800 bg-[#0d0d18]">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <Sparkles size={32} className="mx-auto mb-3 text-purple-400" />
                <p className="text-sm">Describe lo que quieres crear y los agentes se pondrán a trabajar</p>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.type !== 'user' && (
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.type === 'error' ? 'bg-red-500/20' : 
                      msg.type === 'agent' ? 'bg-purple-500/20' : 'bg-cyan-500/20'
                    }`}>
                      {msg.type === 'error' ? (
                        <AlertCircle size={16} className="text-red-400" />
                      ) : msg.type === 'agent' ? (
                        <Bot size={16} className={AGENT_COLORS[msg.agent] || 'text-purple-400'} />
                      ) : (
                        <Bot size={16} className="text-cyan-400" />
                      )}
                    </div>
                  )}
                  
                  <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    msg.type === 'user' 
                      ? 'bg-purple-500/30 text-white' 
                      : msg.type === 'error'
                      ? 'bg-red-500/10 text-red-300 border border-red-500/30'
                      : 'bg-[#1a1a2e] text-gray-200'
                  }`}>
                    {msg.agent && msg.type === 'agent' && (
                      <span className={`text-xs font-medium ${AGENT_COLORS[msg.agent] || 'text-purple-400'}`}>
                        {msg.agent.toUpperCase()} AGENT
                      </span>
                    )}
                    <p className="text-sm">{msg.content}</p>
                    <span className="text-xs text-gray-500 mt-1 block">
                      {new Date(msg.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  
                  {msg.type === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                      <User size={16} className="text-white" />
                    </div>
                  )}
                </div>
              ))
            )}
            
            {/* Loading indicator */}
            {isGenerating && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <Loader2 size={16} className="text-purple-400 animate-spin" />
                </div>
                <div className="bg-[#1a1a2e] rounded-lg px-4 py-2">
                  <span className="text-sm text-gray-300">
                    {currentAgent ? `${currentAgent} trabajando...` : 'Procesando...'}
                  </span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Files Panel */}
          {showFiles && Object.keys(files).length > 0 && (
            <div className="h-48 border-t border-gray-800 overflow-y-auto">
              <div className="p-2 text-xs text-gray-500 font-medium uppercase flex items-center gap-2 border-b border-gray-800/50">
                <FolderOpen size={12} />
                Archivos ({Object.keys(files).length})
              </div>
              <div className="p-2">
                {renderFileTree(getFileTree())}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="p-4 border-t border-gray-800">
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
                className="w-full bg-[#1a1a2e] border border-gray-700 rounded-lg px-4 py-3 pr-12 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:border-purple-500/50 transition-colors"
                rows={3}
                disabled={isGenerating}
                data-testid="chat-input"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputMessage.trim() || isGenerating}
                className="absolute right-3 bottom-3 p-2 bg-purple-500 rounded-lg text-white hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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

        {/* Right Panel - Preview & Code */}
        <div className="flex-1 flex flex-col bg-[#0a0a12]">
          {/* Tabs */}
          <div className="h-10 border-b border-gray-800 flex items-center px-4 gap-2 bg-[#0d0d18]">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-colors ${
                activeTab === 'preview' 
                  ? 'bg-purple-500/20 text-purple-400' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Eye size={14} />
              Preview
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-colors ${
                activeTab === 'code' 
                  ? 'bg-purple-500/20 text-purple-400' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Code size={14} />
              Código
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            {Object.keys(files).length > 0 ? (
              <SandpackProvider
                template="react"
                files={sandpackFiles}
                theme="dark"
                options={{
                  externalResources: ['https://cdn.tailwindcss.com'],
                }}
              >
                <SandpackLayout style={{ height: '100%', border: 'none' }}>
                  {activeTab === 'preview' ? (
                    <SandpackPreview
                      showNavigator
                      showRefreshButton
                      style={{ height: '100%' }}
                    />
                  ) : (
                    <div className="flex h-full">
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
                  <p className="text-lg">Tu app aparecerá aquí</p>
                  <p className="text-sm mt-2">Describe tu aplicación y haz clic en "Enviar"</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkspacePage;
