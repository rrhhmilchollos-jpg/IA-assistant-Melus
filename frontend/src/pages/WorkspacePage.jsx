import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Send,
  Home,
  X,
  Code,
  Eye,
  Rocket,
  Check,
  Copy,
  Save,
  Sparkles,
  Loader2,
  Zap,
  Download,
  Terminal,
  File,
  ChevronLeft,
  GitBranch,
  ArrowRight
} from 'lucide-react';
import CreditModal from '../components/CreditModal';
import { Toaster, toast } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Simple code editor
const CodeEditor = ({ code, filename, onChange }) => {
  return (
    <div className="h-full flex flex-col bg-gray-50">
      <textarea
        value={code || ''}
        onChange={(e) => onChange?.(e.target.value)}
        className="flex-1 w-full bg-transparent text-gray-800 font-mono text-sm p-4 resize-none outline-none leading-6"
        spellCheck={false}
        data-testid="code-editor"
      />
    </div>
  );
};

// File tree component
const FileTree = ({ files, selectedFile, onSelectFile }) => {
  const fileList = Object.keys(files || {}).sort();
  
  const getIcon = (filename) => {
    if (filename.endsWith('.jsx') || filename.endsWith('.js')) {
      return <span className="text-yellow-500 text-xs font-bold">JS</span>;
    }
    if (filename.endsWith('.css')) {
      return <span className="text-blue-500 text-xs font-bold">CSS</span>;
    }
    if (filename.endsWith('.html')) {
      return <span className="text-orange-500 text-xs font-bold">HTML</span>;
    }
    if (filename.endsWith('.json')) {
      return <span className="text-yellow-600 text-xs font-bold">{ }</span>;
    }
    return <File size={14} className="text-gray-400" />;
  };

  return (
    <div className="py-2">
      {fileList.map((filename) => (
        <button
          key={filename}
          onClick={() => onSelectFile(filename)}
          className={`w-full flex items-center gap-2 px-3 py-1.5 text-sm text-left transition-colors ${
            selectedFile === filename 
              ? 'bg-cyan-50 text-cyan-700 border-l-2 border-cyan-500' 
              : 'text-gray-600 hover:bg-gray-100'
          }`}
          data-testid={`file-${filename}`}
        >
          <span className="w-5 flex justify-center">{getIcon(filename)}</span>
          <span className="truncate">{filename}</span>
        </button>
      ))}
    </div>
  );
};

const WorkspacePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, updateCredits } = useAuth();
  
  // Workspace state
  const [workspaceId, setWorkspaceId] = useState(searchParams.get('workspace') || null);
  const [projectName, setProjectName] = useState('New Project');
  const [files, setFiles] = useState({});
  const [selectedFile, setSelectedFile] = useState(null);
  
  // Chat/Agent state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  
  // UI state
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  const [rightPanelMode, setRightPanelMode] = useState('code');
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
  const [showDeployModal, setShowDeployModal] = useState(false);
  
  // Deploy state
  const [githubStatus, setGithubStatus] = useState(null);
  const [deployLoading, setDeployLoading] = useState(false);
  const [repoName, setRepoName] = useState('');
  
  const messagesEndRef = useRef(null);
  const hasInitialized = useRef(false);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle initial prompt
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

  // Check GitHub status
  useEffect(() => {
    const checkGithub = async () => {
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
        console.error('GitHub status error:', error);
      }
    };
    checkGithub();
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
        setProjectName(data.name || 'My Project');
        
        const fileNames = Object.keys(data.files || {});
        if (fileNames.length > 0) {
          setSelectedFile(fileNames[0]);
          setRightPanelOpen(true);
          setRightPanelMode('code');
        }
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
    }
  };

  const addMessage = (role, content, type = 'text') => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      role,
      content,
      type,
      timestamp: new Date()
    }]);
  };

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isAgentRunning) return;
    
    setInputMessage('');
    setIsAgentRunning(true);
    
    addMessage('user', messageText);
    addMessage('assistant', 'Analyzing request...', 'progress');
    
    const token = localStorage.getItem('session_token');
    
    try {
      if (!workspaceId) {
        setCurrentStep('Starting generation...');
        
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
          throw new Error(startData.detail || 'Generation error');
        }
        
        const jobId = startData.job_id;
        const wsId = startData.workspace_id;
        
        setWorkspaceId(wsId);
        window.history.replaceState(null, '', `/workspace?workspace=${wsId}`);
        
        let completed = false;
        while (!completed) {
          await new Promise(r => setTimeout(r, 2000));
          
          const statusResponse = await fetch(`${API_BASE}/api/agents/v2/generation-status/${jobId}`, {
            headers: { 'X-Session-Token': token }
          });
          
          const statusData = await statusResponse.json();
          
          if (statusData.current_step) {
            setCurrentStep(statusData.current_step);
          }
          
          if (statusData.status === 'completed') {
            completed = true;
            setFiles(statusData.files || {});
            setProjectName(startData.name || 'My Project');
            
            if (statusData.credits_remaining !== undefined) {
              updateCredits(statusData.credits_remaining);
            }
            
            const fileNames = Object.keys(statusData.files || {});
            if (fileNames.length > 0) {
              setSelectedFile(fileNames[0]);
              setRightPanelOpen(true);
              setRightPanelMode('code');
            }
            
            addMessage('assistant', `Project created with ${fileNames.length} files. You can view and edit the code in the right panel.`);
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Generation failed');
          }
        }
      } else {
        setCurrentStep('Processing modification...');
        
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
          addMessage('assistant', `Modified ${data.modified_files?.length || 0} files.`);
        } else {
          throw new Error(data.detail || 'Modification error');
        }
      }
    } catch (error) {
      addMessage('assistant', `Error: ${error.message}`);
    } finally {
      setIsAgentRunning(false);
      setCurrentStep('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDeploy = async () => {
    if (!workspaceId || Object.keys(files).length === 0) {
      toast.error('No project to deploy');
      return;
    }
    setRepoName(projectName.toLowerCase().replace(/[^a-z0-9]/g, '-').slice(0, 50));
    setShowDeployModal(true);
  };

  const handlePushToGithub = async () => {
    if (!repoName.trim()) return;
    
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
          private: false
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setShowDeployModal(false);
        toast.success('Pushed to GitHub successfully!');
        addMessage('assistant', `Project pushed to GitHub: ${data.repo_url}`);
      } else {
        throw new Error(data.detail || 'Push failed');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setDeployLoading(false);
    }
  };

  const handleDownload = async () => {
    if (Object.keys(files).length === 0) {
      toast.error('No files to download');
      return;
    }
    
    const content = Object.entries(files)
      .map(([name, code]) => `// === ${name} ===\n${code}`)
      .join('\n\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName.replace(/\s+/g, '_')}_code.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('Code downloaded');
  };

  const displayCredits = () => {
    if (user?.unlimited_credits || user?.is_owner) return '∞';
    return user?.credits?.toFixed?.(1) || 0;
  };

  const hasFiles = Object.keys(files).length > 0;

  return (
    <div className="h-screen flex flex-col bg-[#f8f9fa] text-gray-800" data-testid="workspace-page">
      <Toaster />
      
      {/* Header */}
      <header className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          {/* Home button */}
          <button
            onClick={() => navigate('/home')}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            data-testid="home-btn"
          >
            <Home size={18} />
          </button>
          
          {/* Logo */}
          <span className="text-lg font-light tracking-tight text-gray-800">
            melus<span className="font-normal">AI</span>
          </span>
          
          {/* Project name */}
          <div className="flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-lg ml-2">
            <span className="w-2 h-2 rounded-full bg-cyan-500"></span>
            <span className="text-sm font-medium text-gray-700 truncate max-w-[200px]">{projectName}</span>
          </div>
        </div>
        
        {/* Center - Mode toggles */}
        <div className="flex items-center gap-1 bg-gray-100 rounded-full p-1">
          <button
            onClick={() => {
              setRightPanelOpen(true);
              setRightPanelMode('code');
            }}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm transition-colors ${
              rightPanelOpen && rightPanelMode === 'code'
                ? 'bg-white text-gray-800 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="code-btn"
          >
            <Code size={16} />
            Code
          </button>
          <button
            onClick={() => {
              setRightPanelOpen(true);
              setRightPanelMode('preview');
            }}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm transition-colors ${
              rightPanelOpen && rightPanelMode === 'preview'
                ? 'bg-white text-gray-800 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="preview-btn"
          >
            <Eye size={16} />
            Preview
          </button>
          <button
            onClick={() => {
              setRightPanelOpen(true);
              setRightPanelMode('terminal');
            }}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm transition-colors ${
              rightPanelOpen && rightPanelMode === 'terminal'
                ? 'bg-white text-gray-800 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            data-testid="terminal-btn"
          >
            <Terminal size={16} />
            Terminal
          </button>
        </div>
        
        {/* Right side */}
        <div className="flex items-center gap-2">
          {/* Download */}
          <button
            onClick={handleDownload}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            data-testid="download-btn"
            title="Download code"
          >
            <Download size={18} />
          </button>
          
          {/* Deploy */}
          <button
            onClick={handleDeploy}
            className="flex items-center gap-2 px-4 py-1.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full text-sm font-medium transition-colors"
            data-testid="deploy-btn"
          >
            <Rocket size={16} />
            Deploy
          </button>
          
          {/* Credits */}
          <button
            onClick={() => setIsCreditModalOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
            data-testid="credits-btn"
          >
            <Zap size={14} className="text-yellow-500" />
            <span className="text-sm font-medium text-gray-700">{displayCredits()}</span>
          </button>
          
          {/* User */}
          <button className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm">
            {user?.name?.charAt(0)?.toUpperCase() || 'U'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Chat/Agent */}
        <div className="flex-1 flex flex-col min-w-[400px] bg-white border-r border-gray-200">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-2xl mx-auto space-y-4">
              {messages.length === 0 && !isAgentRunning && (
                <div className="text-center py-20">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-100 to-blue-100 flex items-center justify-center">
                    <Sparkles size={32} className="text-cyan-500" />
                  </div>
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">
                    What do you want to build?
                  </h2>
                  <p className="text-gray-500">
                    Describe your app and AI agents will create it
                  </p>
                </div>
              )}
              
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-bold text-white">AI</span>
                    </div>
                  )}
                  
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user' 
                      ? 'bg-gray-900 text-white' 
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {msg.type === 'progress' ? (
                      <div className="flex items-center gap-2">
                        <Loader2 size={16} className="animate-spin" />
                        <span>{msg.content}</span>
                      </div>
                    ) : (
                      <p className="text-sm leading-relaxed">{msg.content}</p>
                    )}
                  </div>
                  
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-bold text-white">{user?.name?.charAt(0)?.toUpperCase() || 'U'}</span>
                    </div>
                  )}
                </div>
              ))}
              
              {isAgentRunning && currentStep && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                    <Loader2 size={14} className="animate-spin text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <p className="text-sm text-gray-600">{currentStep}</p>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>
          
          {/* Input Area */}
          <div className="p-4 border-t border-gray-100">
            <div className="max-w-2xl mx-auto">
              <div className="relative bg-gray-50 border border-gray-200 rounded-2xl overflow-hidden focus-within:border-gray-300 focus-within:shadow-sm transition-all">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={workspaceId ? "Ask to modify your project..." : "Describe what you want to build..."}
                  className="w-full bg-transparent text-gray-800 placeholder-gray-400 resize-none outline-none p-4 pr-14 min-h-[56px] max-h-[120px]"
                  data-testid="chat-input"
                  rows={1}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!inputMessage.trim() || isAgentRunning}
                  className="absolute bottom-3 right-3 p-2 bg-gray-900 hover:bg-gray-800 text-white disabled:opacity-30 disabled:cursor-not-allowed rounded-lg transition-colors"
                  data-testid="send-btn"
                >
                  {isAgentRunning ? (
                    <Loader2 size={18} className="animate-spin" />
                  ) : (
                    <ArrowRight size={18} />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right Panel - Code/Preview/Terminal */}
        {rightPanelOpen && (
          <div className="w-1/2 flex flex-col bg-white">
            {/* Panel Header */}
            <div className="h-10 bg-gray-50 border-b border-gray-200 flex items-center justify-between px-4">
              <div className="flex items-center gap-2 text-gray-600">
                {rightPanelMode === 'code' && <><Code size={14} /> Code Editor</>}
                {rightPanelMode === 'preview' && <><Eye size={14} /> Preview</>}
                {rightPanelMode === 'terminal' && <><Terminal size={14} /> Terminal</>}
              </div>
              <button
                onClick={() => setRightPanelOpen(false)}
                className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded transition-colors"
                data-testid="close-panel-btn"
              >
                <X size={16} />
              </button>
            </div>
            
            {/* Panel Content */}
            <div className="flex-1 flex overflow-hidden">
              {rightPanelMode === 'code' && (
                <>
                  {/* File Explorer */}
                  <div className="w-48 border-r border-gray-200 overflow-y-auto bg-white">
                    <div className="px-3 py-2 text-xs text-gray-400 uppercase font-medium">Files</div>
                    {hasFiles ? (
                      <FileTree 
                        files={files} 
                        selectedFile={selectedFile}
                        onSelectFile={setSelectedFile}
                      />
                    ) : (
                      <div className="px-3 py-4 text-sm text-gray-400">
                        No files yet
                      </div>
                    )}
                  </div>
                  
                  {/* Editor */}
                  <div className="flex-1 flex flex-col">
                    {selectedFile && (
                      <>
                        {/* File tabs */}
                        <div className="h-9 bg-gray-50 border-b border-gray-200 flex items-center px-2">
                          <div className="flex items-center gap-2 px-3 py-1 bg-white rounded-t border border-b-0 border-gray-200 text-sm text-gray-700">
                            <span>{selectedFile}</span>
                            <button className="text-gray-400 hover:text-gray-600">
                              <X size={12} />
                            </button>
                          </div>
                        </div>
                        
                        {/* Code area */}
                        <div className="flex-1 overflow-auto">
                          <CodeEditor
                            code={files[selectedFile]}
                            filename={selectedFile}
                            onChange={(newCode) => {
                              setFiles(prev => ({
                                ...prev,
                                [selectedFile]: newCode
                              }));
                            }}
                          />
                        </div>
                      </>
                    )}
                    
                    {!selectedFile && hasFiles && (
                      <div className="flex-1 flex items-center justify-center text-gray-400">
                        Select a file to edit
                      </div>
                    )}
                    
                    {!hasFiles && (
                      <div className="flex-1 flex items-center justify-center text-gray-400">
                        Generate a project to see code
                      </div>
                    )}
                  </div>
                </>
              )}
              
              {rightPanelMode === 'preview' && (
                <div className="flex-1 flex items-center justify-center bg-gray-50">
                  {hasFiles ? (
                    <div className="text-center">
                      <Eye size={48} className="mx-auto mb-4 text-gray-300" />
                      <p className="text-gray-500 mb-4">Preview coming soon</p>
                      <button
                        onClick={() => setRightPanelMode('code')}
                        className="text-cyan-600 hover:text-cyan-700 text-sm"
                      >
                        View code instead →
                      </button>
                    </div>
                  ) : (
                    <p className="text-gray-400">Generate a project first</p>
                  )}
                </div>
              )}
              
              {rightPanelMode === 'terminal' && (
                <div className="flex-1 bg-gray-900 p-4 font-mono text-sm">
                  <div className="text-green-400">
                    $ melus-ai workspace {workspaceId || 'new'}
                  </div>
                  <div className="text-gray-400 mt-2">
                    Terminal functionality coming soon...
                  </div>
                </div>
              )}
            </div>
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Deploy to GitHub</h3>
            
            {githubStatus?.connected ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <Check size={16} />
                  Connected as {githubStatus.username}
                </div>
                
                <div>
                  <label className="block text-sm text-gray-500 mb-1">Repository Name</label>
                  <input
                    type="text"
                    value={repoName}
                    onChange={(e) => setRepoName(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-gray-300"
                    placeholder="my-project"
                    data-testid="repo-name-input"
                  />
                </div>
                
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowDeployModal(false)}
                    className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handlePushToGithub}
                    disabled={deployLoading || !repoName.trim()}
                    className="flex-1 px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white disabled:opacity-50 rounded-lg transition-colors flex items-center justify-center gap-2"
                    data-testid="push-github-btn"
                  >
                    {deployLoading ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <GitBranch size={16} />
                    )}
                    Push to GitHub
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-gray-500 mb-4">Connect your GitHub account to deploy</p>
                <button
                  onClick={() => window.open(`${API_BASE}/api/github/auth/login`, '_blank')}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                >
                  Connect GitHub
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkspacePage;
