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
  Home,
  Plus,
  X,
  Code,
  Eye,
  Rocket,
  Check,
  ChevronRight,
  Copy,
  RotateCw,
  RotateCcw,
  Paperclip,
  Save,
  Sparkles,
  Mic,
  Square,
  Loader2,
  CreditCard,
  Zap,
  ShoppingCart,
  History,
  Download
} from 'lucide-react';
import CreditModal from '../components/CreditModal';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const WorkspacePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, updateCredits } = useAuth();
  
  // Workspace state
  const [workspaceId, setWorkspaceId] = useState(searchParams.get('workspace') || null);
  const [projectName, setProjectName] = useState('Nuevo Proyecto');
  const [files, setFiles] = useState({});
  
  // Chat/Agent logs state
  const [logs, setLogs] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  
  // UI state
  const [activeView, setActiveView] = useState(null); // null | 'code' | 'preview'
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
  const [tabs, setTabs] = useState([
    { id: 'current', name: projectName, active: true }
  ]);
  
  const logsEndRef = useRef(null);
  const wsRef = useRef(null);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Handle initial prompt - with guard to prevent duplicate execution
  const hasInitialized = useRef(false);
  useEffect(() => {
    if (hasInitialized.current) return;
    const initialPrompt = searchParams.get('prompt');
    if (initialPrompt && !workspaceId) {
      hasInitialized.current = true;
      handleSendMessage(initialPrompt);
    }
  }, []);

  // Load workspace if ID provided
  useEffect(() => {
    if (workspaceId) {
      loadWorkspace(workspaceId);
    }
  }, [workspaceId]);

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
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
    }
  };

  const addLog = (type, content, command = null) => {
    const timestamp = new Date().toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    
    setLogs(prev => [...prev, {
      id: Date.now() + Math.random(),
      type, // 'message' | 'command' | 'processing'
      content,
      command,
      timestamp,
      completed: type === 'command'
    }]);
  };

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isAgentRunning) return;
    
    setInputMessage('');
    setIsAgentRunning(true);
    setCurrentStep('Analizando solicitud...');
    
    addLog('message', messageText);
    
    const token = localStorage.getItem('session_token');
    
    try {
      if (!workspaceId) {
        // Start async generation
        addLog('command', 'Iniciando generación asíncrona...', '$ generate --async');
        
        const startResponse = await fetch(`${API_BASE}/api/agents/v2/generate-async`, {
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
        
        const startData = await startResponse.json();
        
        if (!startResponse.ok) {
          throw new Error(startData.detail || 'Error al iniciar generación');
        }
        
        const jobId = startData.job_id;
        const wsId = startData.workspace_id;
        
        setWorkspaceId(wsId);
        window.history.replaceState(null, '', `/workspace?workspace=${wsId}`);
        
        addLog('command', 'Clasificando tipo de proyecto...', '$ classify --type auto');
        
        // Poll for status
        let completed = false;
        while (!completed) {
          await new Promise(r => setTimeout(r, 2000)); // Poll every 2 seconds
          
          const statusResponse = await fetch(`${API_BASE}/api/agents/v2/generation-status/${jobId}`, {
            headers: { 'X-Session-Token': token }
          });
          
          const statusData = await statusResponse.json();
          
          if (statusData.current_step) {
            setCurrentStep(statusData.current_step);
          }
          
          // Update logs based on progress
          if (statusData.progress >= 25 && !logs.find(l => l.content?.includes('arquitectura'))) {
            addLog('command', 'Diseñando arquitectura...', '$ architect --analyze');
          }
          if (statusData.progress >= 60 && !logs.find(l => l.content?.includes('React'))) {
            addLog('command', 'Generando código React...', '$ frontend --generate');
          }
          if (statusData.progress >= 80 && !logs.find(l => l.content?.includes('Integrando'))) {
            addLog('command', 'Integrando componentes...', '$ integrator --connect');
          }
          
          if (statusData.status === 'completed') {
            completed = true;
            setFiles(statusData.files || {});
            setProjectName(startData.name || 'Mi Proyecto');
            
            if (statusData.credits_remaining !== undefined) {
              updateCredits(statusData.credits_remaining);
            }
            
            addLog('command', `Proyecto generado: ${Object.keys(statusData.files || {}).length} archivos`, '$ generate --complete');
            addLog('message', 'Proyecto creado exitosamente. Puedes ver el código o el preview usando los botones de arriba.');
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Error en la generación');
          }
        }
      } else {
        // Modificar proyecto existente
        addLog('command', 'Procesando modificación...', '$ modify --apply');
        
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
          addLog('command', `Modificación aplicada: ${data.modified_files?.length || 0} archivos`, '$ update --complete');
        } else {
          throw new Error(data.detail || 'Error al modificar');
        }
      }
    } catch (error) {
      console.error('Error:', error);
      addLog('message', `Error: ${error.message}`);
    } finally {
      setIsAgentRunning(false);
      setCurrentStep('');
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
  };

  const [showRollbackModal, setShowRollbackModal] = useState(false);
  const [versions, setVersions] = useState([]);
  const [rollbackLoading, setRollbackLoading] = useState(false);

  const handleRollback = async () => {
    if (!workspaceId) {
      addLog('message', 'No hay proyecto para hacer rollback.');
      return;
    }
    
    // Load versions
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/workspace/${workspaceId}/versions`, {
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        const data = await response.json();
        setVersions(data.versions || []);
        setShowRollbackModal(true);
      }
    } catch (error) {
      addLog('message', `Error cargando versiones: ${error.message}`);
    }
  };

  const executeRollback = async (version) => {
    setRollbackLoading(true);
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/workspace/${workspaceId}/rollback/${version}`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setFiles(data.files || {});
        setShowRollbackModal(false);
        addLog('command', `Rollback a versión ${version}`, '$ git checkout v' + version);
        addLog('message', `✅ Proyecto restaurado a versión ${version}`);
      } else {
        throw new Error(data.detail || 'Error en rollback');
      }
    } catch (error) {
      addLog('message', `Error: ${error.message}`);
    } finally {
      setRollbackLoading(false);
    }
  };

  const [showDeployModal, setShowDeployModal] = useState(false);
  const [githubStatus, setGithubStatus] = useState(null);
  const [deployLoading, setDeployLoading] = useState(false);
  const [repoName, setRepoName] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [deployTarget, setDeployTarget] = useState('github'); // 'github' | 'vercel'

  // Check GitHub connection status
  useEffect(() => {
    const checkGithubStatus = async () => {
      const token = localStorage.getItem('session_token');
      try {
        const response = await fetch(`${API_BASE}/api/github/status`, {
          headers: { 'X-Session-Token': token }
        });
        if (response.ok) {
          const data = await response.json();
          setGithubStatus(data);
        }
      } catch (error) {
        console.error('Error checking GitHub status:', error);
      }
    };
    checkGithubStatus();
  }, []);

  const handleDeploy = () => {
    if (!workspaceId || Object.keys(files).length === 0) {
      addLog('message', 'No hay proyecto para desplegar. Genera un proyecto primero.');
      return;
    }
    setRepoName(projectName.toLowerCase().replace(/[^a-z0-9]/g, '-').slice(0, 50));
    setDeployTarget('github');
    setShowDeployModal(true);
  };

  const handleGithubConnect = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/github/auth/login`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await response.json();
      if (data.auth_url) {
        window.open(data.auth_url, '_blank');
      }
    } catch (error) {
      addLog('message', `Error conectando GitHub: ${error.message}`);
    }
  };

  const handlePushToGithub = async () => {
    if (!repoName.trim()) {
      addLog('message', 'Por favor ingresa un nombre para el repositorio.');
      return;
    }

    setDeployLoading(true);
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/github/push-workspace`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          workspace_id: workspaceId,
          repo_name: repoName,
          create_new: true,
          private: isPrivate
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setShowDeployModal(false);
        addLog('command', `Subido a GitHub: ${data.repo_name}`, '$ git push origin main');
        addLog('message', `✅ Proyecto subido exitosamente! URL: ${data.repo_url}`);
        if (data.credits_used > 0) {
          updateCredits(data.credits_remaining);
        }
      } else {
        throw new Error(data.detail || 'Error al subir a GitHub');
      }
    } catch (error) {
      addLog('message', `Error: ${error.message}`);
    } finally {
      setDeployLoading(false);
    }
  };

  // Format files for Sandpack
  const sandpackFiles = Object.entries(files).reduce((acc, [path, content]) => {
    acc[`/${path}`] = { code: content };
    return acc;
  }, {});

  const hasFiles = Object.keys(files).length > 0;

  return (
    <div className="h-screen flex flex-col bg-[#0f1419] text-white" data-testid="workspace-page">
      {/* Header con tabs - Estilo Emergent */}
      <header className="bg-[#1a1f26] border-b border-gray-700/50">
        {/* Top bar con tabs */}
        <div className="flex items-center justify-between h-11 px-2">
          <div className="flex items-center gap-1">
            {/* Home button */}
            <button
              onClick={() => navigate('/home')}
              className="flex items-center gap-2 px-3 py-1.5 text-gray-400 hover:text-white hover:bg-white/5 rounded transition-colors"
            >
              <Home size={16} />
              <span className="text-sm">Home</span>
            </button>
            
            {/* Project tabs */}
            <div className="flex items-center">
              <button className="flex items-center gap-2 px-3 py-1.5 bg-[#0f1419] text-white rounded-t border-t border-l border-r border-gray-700/50 text-sm">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                {projectName.length > 20 ? projectName.substring(0, 20) + '...' : projectName}
                <X size={14} className="text-gray-500 hover:text-white" />
              </button>
              <button className="p-1.5 text-gray-500 hover:text-white hover:bg-white/5 rounded transition-colors ml-1">
                <Plus size={16} />
              </button>
            </div>
          </div>
          
          {/* Right side - Credits and buttons */}
          <div className="flex items-center gap-3">
            {/* Credits */}
            <div className="flex items-center gap-2 px-3 py-1 bg-[#2a3441] rounded-full">
              <Zap size={14} className="text-yellow-400" />
              <span className="text-sm font-medium text-white">
                {user?.unlimited_credits ? '∞' : (user?.credits || 0).toFixed(2)}
              </span>
            </div>
            
            {/* Comprar créditos - Header button */}
            <button 
              onClick={() => setIsCreditModalOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-green-500 hover:bg-green-600 rounded-full text-sm font-medium text-white transition-colors"
            >
              <CreditCard size={14} />
              Comprar créditos
            </button>
            
            {/* User avatar */}
            <button className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-white font-bold text-sm">
              {user?.name?.charAt(0)?.toUpperCase() || 'U'}
            </button>
          </div>
        </div>
        
        {/* Secondary bar con Comprar créditos/Code/Preview/Deploy */}
        <div className="flex items-center justify-end gap-2 px-4 py-2 border-t border-gray-700/30">
          {/* Comprar créditos - PRINCIPAL */}
          <button
            onClick={() => setIsCreditModalOpen(true)}
            className="flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 rounded text-sm font-medium text-white transition-colors"
          >
            <ShoppingCart size={16} />
            Comprar créditos
          </button>
          
          <div className="w-px h-6 bg-gray-700 mx-1"></div>
          
          <button
            onClick={() => setActiveView(activeView === 'code' ? null : 'code')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              activeView === 'code' 
                ? 'bg-white text-black' 
                : 'bg-[#2a3441] text-white hover:bg-[#3a4451]'
            }`}
          >
            <Code size={16} />
            Code
          </button>
          
          <button
            onClick={() => setActiveView(activeView === 'preview' ? null : 'preview')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              activeView === 'preview' 
                ? 'bg-white text-black' 
                : 'bg-[#2a3441] text-white hover:bg-[#3a4451]'
            }`}
          >
            <Eye size={16} />
            Preview
          </button>
          
          <button
            onClick={handleDeploy}
            className="flex items-center gap-2 px-4 py-1.5 bg-amber-500 hover:bg-amber-600 rounded text-sm font-medium text-black transition-colors"
          >
            <Rocket size={16} />
            Deploy
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Agent Chat/Logs Area */}
        <div className={`flex flex-col bg-[#0f1419] transition-all duration-300 ${
          activeView ? 'w-1/2' : 'w-full'
        }`}>
          {/* Logs Area con fondo de ondas */}
          <div 
            className="flex-1 overflow-y-auto px-6 py-4"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 50 Q 25 30, 50 50 T 100 50' fill='none' stroke='%23ffffff' stroke-opacity='0.02' stroke-width='1'/%3E%3C/svg%3E")`,
              backgroundSize: '200px 100px'
            }}
          >
            <div className="max-w-3xl mx-auto space-y-6">
              {logs.length === 0 && !isAgentRunning && (
                <div className="text-center text-gray-500 py-20">
                  <Sparkles size={48} className="mx-auto mb-4 opacity-30" />
                  <p className="text-lg">Describe lo que quieres crear</p>
                  <p className="text-sm mt-2">Los agentes trabajarán automáticamente</p>
                </div>
              )}
              
              {logs.map((log) => (
                <div key={log.id} className="space-y-3">
                  {log.type === 'message' && (
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 rounded-full bg-gray-500 mt-2 flex-shrink-0"></div>
                      <p className="text-gray-300 leading-relaxed">{log.content}</p>
                    </div>
                  )}
                  
                  {log.type === 'command' && (
                    <div className="space-y-2">
                      <div className="flex items-start gap-3">
                        <div className="w-2 h-2 rounded-full bg-gray-500 mt-2 flex-shrink-0"></div>
                        <p className="text-gray-300">{log.content}</p>
                      </div>
                      
                      {log.command && (
                        <div className="ml-5 bg-[#1a2b1a] border border-green-900/50 rounded-lg overflow-hidden">
                          <div className="flex items-center justify-between px-4 py-3">
                            <div className="flex items-center gap-3">
                              <Check size={16} className="text-green-500" />
                              <code className="text-green-400 text-sm font-mono">{log.command}</code>
                            </div>
                            <ChevronRight size={18} className="text-gray-500" />
                          </div>
                        </div>
                      )}
                      
                      <div className="ml-5 flex items-center gap-4 text-xs text-gray-500">
                        <span>{log.timestamp}</span>
                        <button 
                          onClick={handleRollback}
                          className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                        >
                          <RotateCw size={12} />
                          Rollback
                        </button>
                        <button 
                          onClick={() => handleCopy(log.command || log.content)}
                          className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                        >
                          <Copy size={12} />
                          Copy
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Processing indicator */}
              {isAgentRunning && (
                <div className="flex items-start gap-3">
                  <Loader2 size={16} className="text-gray-400 animate-spin mt-1" />
                  <p className="text-gray-400">{currentStep || 'Processing next step...'}</p>
                </div>
              )}
              
              <div ref={logsEndRef} />
            </div>
          </div>

          {/* Input Area - Estilo Emergent */}
          <div className="border-t border-gray-700/50 bg-[#0f1419] p-4">
            <div className={`rounded-lg border-2 transition-colors ${
              isAgentRunning 
                ? 'border-green-500 bg-[#0a1a0a]' 
                : 'border-gray-700 bg-[#1a1f26] focus-within:border-cyan-500'
            }`}>
              {/* Agent status */}
              {isAgentRunning && (
                <div className="px-4 py-2 border-b border-gray-700/50">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    <span className="text-green-500 text-sm font-medium">Agent is running...</span>
                  </div>
                </div>
              )}
              
              {/* Input field */}
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Message Agent"
                className="w-full bg-transparent px-4 py-3 text-white placeholder-gray-500 outline-none"
                disabled={isAgentRunning}
                data-testid="message-input"
              />
              
              {/* Bottom toolbar */}
              <div className="flex items-center justify-between px-4 py-2 border-t border-gray-700/30">
                <div className="flex items-center gap-2">
                  <button className="p-2 text-gray-500 hover:text-white hover:bg-white/5 rounded transition-colors">
                    <Paperclip size={18} />
                  </button>
                  
                  <button className="flex items-center gap-2 px-3 py-1.5 text-gray-400 hover:text-white hover:bg-white/5 rounded text-sm transition-colors">
                    <Save size={14} />
                    Save
                  </button>
                  
                  <button className="flex items-center gap-2 px-3 py-1.5 text-gray-400 hover:text-white hover:bg-white/5 rounded text-sm transition-colors">
                    <Sparkles size={14} />
                    Summarize
                  </button>
                  
                  <button className="flex items-center gap-2 px-3 py-1.5 text-gray-400 hover:text-white hover:bg-white/5 rounded text-sm transition-colors">
                    <Zap size={14} />
                    Ultra
                  </button>
                </div>
                
                <div className="flex items-center gap-2">
                  <button className="p-2 text-gray-500 hover:text-white hover:bg-white/5 rounded-full transition-colors">
                    <Mic size={18} />
                  </button>
                  <button 
                    onClick={() => isAgentRunning ? null : handleSendMessage()}
                    className={`p-2 rounded-full transition-colors ${
                      isAgentRunning 
                        ? 'bg-red-500 text-white' 
                        : 'bg-gray-700 text-white hover:bg-gray-600'
                    }`}
                  >
                    {isAgentRunning ? <Square size={18} /> : <Send size={18} />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Code/Preview Panel */}
        {activeView && (
          <div className="w-1/2 border-l border-gray-700/50 bg-[#1a1f26]">
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
                  {activeView === 'preview' ? (
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
              <div className="flex-1 flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <Code size={48} className="mx-auto mb-4 opacity-30" />
                  <p className="text-lg">Sin archivos aún</p>
                  <p className="text-sm mt-2">Genera un proyecto primero</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Credit Modal */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
      
      {/* Deploy Modal */}
      {showDeployModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-[#1a1f26] border border-gray-700 rounded-xl p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white">Desplegar Proyecto</h3>
              <button 
                onClick={() => setShowDeployModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            
            {/* Deploy Target Tabs */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setDeployTarget('github')}
                className={`flex-1 py-2 px-4 rounded-lg flex items-center justify-center gap-2 ${
                  deployTarget === 'github' 
                    ? 'bg-gray-800 border border-cyan-500 text-white' 
                    : 'bg-gray-800/50 text-gray-400 hover:text-white'
                }`}
              >
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
                GitHub
              </button>
              <button
                onClick={() => setDeployTarget('vercel')}
                className={`flex-1 py-2 px-4 rounded-lg flex items-center justify-center gap-2 ${
                  deployTarget === 'vercel' 
                    ? 'bg-gray-800 border border-cyan-500 text-white' 
                    : 'bg-gray-800/50 text-gray-400 hover:text-white'
                }`}
              >
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
                  <path d="M24 22.525H0l12-21.05 12 21.05z"/>
                </svg>
                Vercel
              </button>
            </div>
            
            {deployTarget === 'github' ? (
              // GitHub Deploy Content
              !githubStatus?.connected ? (
                <div className="text-center py-6">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
                    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-white">
                      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                    </svg>
                  </div>
                  <p className="text-gray-300 mb-4">Conecta tu cuenta de GitHub para subir proyectos</p>
                  <button
                    onClick={handleGithubConnect}
                    className="px-6 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg flex items-center gap-2 mx-auto"
                  >
                    Conectar GitHub
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                    <img src={githubStatus.avatar} alt="" className="w-8 h-8 rounded-full" />
                    <div>
                      <p className="text-green-400 text-sm font-medium">Conectado como</p>
                      <p className="text-white">{githubStatus.username}</p>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-gray-400 text-sm mb-2">Nombre del repositorio</label>
                    <input
                      type="text"
                      value={repoName}
                      onChange={(e) => setRepoName(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-'))}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 outline-none"
                      placeholder="mi-proyecto"
                    />
                  </div>
                  
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isPrivate}
                      onChange={(e) => setIsPrivate(e.target.checked)}
                      className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-cyan-500"
                    />
                    <span className="text-gray-300">Repositorio privado</span>
                  </label>
                  
                  <div className="flex items-center justify-between text-sm text-gray-400 border-t border-gray-700 pt-4">
                    <span>Costo: 50 créditos</span>
                    <span>{Object.keys(files).length} archivos</span>
                  </div>
                  
                  <button
                    onClick={handlePushToGithub}
                    disabled={deployLoading || !repoName.trim()}
                    className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 text-white rounded-lg font-medium flex items-center justify-center gap-2"
                  >
                    {deployLoading ? (
                      <>
                        <Loader2 size={18} className="animate-spin" />
                        Subiendo...
                      </>
                    ) : (
                      <>
                        <Rocket size={18} />
                        Subir a GitHub
                      </>
                    )}
                  </button>
                </div>
              )
            ) : (
              // Vercel Deploy Content
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-gray-900 to-gray-800 rounded-lg border border-gray-700">
                  <div className="flex items-center gap-3 mb-3">
                    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-white">
                      <path d="M24 22.525H0l12-21.05 12 21.05z"/>
                    </svg>
                    <div>
                      <p className="text-white font-medium">Deploy a Vercel</p>
                      <p className="text-gray-400 text-sm">Hosting gratuito y rápido</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2 text-sm text-gray-300">
                  <p className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs">1</span>
                    Descarga el ZIP del proyecto
                  </p>
                  <p className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs">2</span>
                    Ve a vercel.com/new
                  </p>
                  <p className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs">3</span>
                    Sube la carpeta y despliega
                  </p>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-400 border-t border-gray-700 pt-4">
                  <span>Costo: 100 créditos</span>
                  <span>{Object.keys(files).length} archivos</span>
                </div>
                
                <button
                  onClick={async () => {
                    setDeployLoading(true);
                    const token = localStorage.getItem('session_token');
                    try {
                      const response = await fetch(`${API_BASE}/api/deploy/vercel`, {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                          'X-Session-Token': token
                        },
                        body: JSON.stringify({
                          workspace_id: workspaceId,
                          project_name: projectName
                        })
                      });
                      
                      const data = await response.json();
                      
                      if (response.ok) {
                        // Download ZIP
                        window.open(`${API_BASE}${data.download_url}&token=${token}`, '_blank');
                        setShowDeployModal(false);
                        addLog('command', 'Proyecto preparado para Vercel', '$ vercel --prod');
                        addLog('message', `✅ Descarga el ZIP y súbelo a vercel.com/new`);
                        if (data.credits_used > 0) {
                          updateCredits(data.credits_remaining);
                        }
                      } else {
                        throw new Error(data.detail || 'Error al preparar deploy');
                      }
                    } catch (error) {
                      addLog('message', `Error: ${error.message}`);
                    } finally {
                      setDeployLoading(false);
                    }
                  }}
                  disabled={deployLoading}
                  className="w-full py-3 bg-gradient-to-r from-white to-gray-200 hover:from-gray-100 hover:to-gray-300 disabled:opacity-50 text-black rounded-lg font-medium flex items-center justify-center gap-2"
                >
                  {deployLoading ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Preparando...
                    </>
                  ) : (
                    <>
                      <Download size={18} />
                      Descargar para Vercel
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Rollback Modal */}
      {showRollbackModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-[#1a1f26] border border-gray-700 rounded-xl p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white">Historial de Versiones</h3>
              <button 
                onClick={() => setShowRollbackModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            
            {versions.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <History size={48} className="mx-auto mb-3 opacity-50" />
                <p>No hay versiones anteriores</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {versions.map((v, i) => (
                  <div 
                    key={v.version}
                    className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800"
                  >
                    <div>
                      <p className="text-white font-medium">Versión {v.version}</p>
                      <p className="text-gray-400 text-sm">{v.message || 'Sin mensaje'}</p>
                      <p className="text-gray-500 text-xs">{new Date(v.created_at).toLocaleString()}</p>
                    </div>
                    <button
                      onClick={() => executeRollback(v.version)}
                      disabled={rollbackLoading}
                      className="px-3 py-1.5 bg-amber-500/20 text-amber-400 hover:bg-amber-500/30 rounded-lg text-sm flex items-center gap-1"
                    >
                      {rollbackLoading ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <RotateCcw size={14} />
                      )}
                      Restaurar
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkspacePage;
