import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Send,
  ChevronLeft,
  X,
  Code,
  Eye,
  Rocket,
  Check,
  Loader2,
  Zap,
  Download,
  Terminal,
  File,
  GitBranch,
  ArrowRight,
  Copy,
  RotateCcw,
  ExternalLink,
  Play,
  Square,
  Maximize2,
  Minimize2,
  MoreHorizontal,
  RefreshCw,
  Share2,
  Settings,
  Smartphone,
  Monitor,
  Tablet,
  Star,
  Wand2,
  FileCode,
  Trash2
} from 'lucide-react';
import CreditModal from '../components/CreditModal';
import ProjectRating from '../components/ProjectRating';
import MonacoCodeEditor from '../components/MonacoCodeEditor';
import { Toaster, toast } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const WS_BASE = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');

// File tree component with folder structure and regenerate option
const FileTree = ({ files, selectedFile, onSelectFile, onRegenerateFile, regeneratingFile }) => {
  const fileList = Object.keys(files || {}).sort();
  const [contextMenu, setContextMenu] = useState(null);
  
  // Group files by folder
  const structure = {};
  fileList.forEach(file => {
    const parts = file.split('/');
    if (parts.length > 1) {
      const folder = parts[0];
      if (!structure[folder]) structure[folder] = [];
      structure[folder].push(file);
    } else {
      if (!structure['root']) structure['root'] = [];
      structure['root'].push(file);
    }
  });

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop();
    const icons = {
      'js': { color: 'text-yellow-400', label: 'JS' },
      'jsx': { color: 'text-yellow-400', label: 'JSX' },
      'ts': { color: 'text-blue-400', label: 'TS' },
      'tsx': { color: 'text-blue-400', label: 'TSX' },
      'css': { color: 'text-blue-500', label: 'CSS' },
      'html': { color: 'text-orange-400', label: 'HTML' },
      'json': { color: 'text-yellow-300', label: 'JSON' },
      'py': { color: 'text-green-400', label: 'PY' },
      'md': { color: 'text-gray-400', label: 'MD' },
      'svg': { color: 'text-pink-400', label: 'SVG' },
      'png': { color: 'text-purple-400', label: 'IMG' },
      'jpg': { color: 'text-purple-400', label: 'IMG' }
    };
    return icons[ext] || { color: 'text-gray-400', label: '•' };
  };

  const handleContextMenu = (e, filename) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, file: filename });
  };

  // Close context menu on click outside
  useEffect(() => {
    const handleClick = () => setContextMenu(null);
    window.addEventListener('click', handleClick);
    return () => window.removeEventListener('click', handleClick);
  }, []);

  return (
    <div className="py-1 text-sm relative">
      {fileList.map((filename) => {
        const icon = getFileIcon(filename);
        const displayName = filename.split('/').pop();
        const isRegenerating = regeneratingFile === filename;
        
        return (
          <button
            key={filename}
            onClick={() => onSelectFile(filename)}
            onContextMenu={(e) => handleContextMenu(e, filename)}
            className={`w-full flex items-center gap-2 px-3 py-1.5 text-left transition-colors group ${
              selectedFile === filename 
                ? 'bg-[#37373d] text-white' 
                : 'text-gray-400 hover:bg-[#2a2d2e] hover:text-gray-200'
            }`}
            data-testid={`file-${filename}`}
          >
            {isRegenerating ? (
              <Loader2 size={12} className="animate-spin text-cyan-400" />
            ) : (
              <span className={`text-xs font-bold w-6 ${icon.color}`}>{icon.label}</span>
            )}
            <span className="truncate flex-1">{displayName}</span>
            {/* Regenerate button on hover */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRegenerateFile?.(filename);
              }}
              className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-gray-600 rounded transition-opacity"
              title="Regenerate file"
            >
              <Wand2 size={12} className="text-cyan-400" />
            </button>
          </button>
        );
      })}
      
      {/* Context Menu */}
      {contextMenu && (
        <div 
          className="fixed bg-[#252526] border border-gray-700 rounded-lg shadow-xl py-1 z-50 min-w-[160px]"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <button
            onClick={() => {
              onRegenerateFile?.(contextMenu.file);
              setContextMenu(null);
            }}
            className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-gray-300 hover:bg-[#37373d] transition-colors"
          >
            <Wand2 size={14} className="text-cyan-400" />
            Regenerate File
          </button>
          <button
            onClick={() => {
              navigator.clipboard.writeText(files[contextMenu.file] || '');
              toast.success('Copied to clipboard');
              setContextMenu(null);
            }}
            className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-gray-300 hover:bg-[#37373d] transition-colors"
          >
            <Copy size={14} />
            Copy Content
          </button>
        </div>
      )}
    </div>
  );
};

// Tab component for code editor
const EditorTabs = ({ files, selectedFile, onSelectFile, onCloseFile, onRegenerateFile }) => {
  const openFiles = selectedFile ? [selectedFile] : [];
  
  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop();
    const colors = {
      'js': 'text-yellow-400',
      'jsx': 'text-yellow-400',
      'css': 'text-blue-500',
      'html': 'text-orange-400',
      'json': 'text-yellow-300'
    };
    return colors[ext] || 'text-gray-400';
  };
  
  return (
    <div className="h-9 bg-[#252526] flex items-center border-b border-[#1e1e1e]">
      {openFiles.map(file => (
        <div
          key={file}
          className="flex items-center gap-2 px-3 h-full bg-[#1e1e1e] border-t-2 border-cyan-500 text-sm text-white"
        >
          <span className={`text-xs ${getFileIcon(file)}`}>●</span>
          <span>{file.split('/').pop()}</span>
          <button 
            onClick={() => onCloseFile?.(file)}
            className="p-0.5 hover:bg-gray-700 rounded"
          >
            <X size={12} />
          </button>
        </div>
      ))}
    </div>
  );
};

// Preview device frame selector
const DeviceSelector = ({ device, onChange }) => {
  const devices = [
    { id: 'desktop', icon: Monitor, label: 'Desktop' },
    { id: 'tablet', icon: Tablet, label: 'Tablet' },
    { id: 'mobile', icon: Smartphone, label: 'Mobile' }
  ];
  
  return (
    <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
      {devices.map(d => {
        const Icon = d.icon;
        return (
          <button
            key={d.id}
            onClick={() => onChange(d.id)}
            className={`p-1.5 rounded transition-colors ${
              device === d.id 
                ? 'bg-white text-gray-800 shadow-sm' 
                : 'text-gray-400 hover:text-gray-600'
            }`}
            title={d.label}
          >
            <Icon size={16} />
          </button>
        );
      })}
    </div>
  );
};

const WorkspacePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, updateCredits } = useAuth();
  
  // Workspace state
  const [workspaceId, setWorkspaceId] = useState(searchParams.get('workspace') || null);
  const [projectId, setProjectId] = useState(searchParams.get('project') || null);
  const [projectName, setProjectName] = useState('New Project');
  const [files, setFiles] = useState({});
  const [selectedFile, setSelectedFile] = useState(null);
  const [projectPhase, setProjectPhase] = useState(null);
  const [projectPlan, setProjectPlan] = useState(null);
  
  // Chat/Agent state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  const [agentThinking, setAgentThinking] = useState(false);
  
  // UI state
  const [rightPanelMode, setRightPanelMode] = useState('preview'); // 'code' | 'preview'
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [previewDevice, setPreviewDevice] = useState('desktop');
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [terminalOutput, setTerminalOutput] = useState(['$ Ready']);
  
  // Deploy state
  const [githubStatus, setGithubStatus] = useState(null);
  const [deployLoading, setDeployLoading] = useState(false);
  const [repoName, setRepoName] = useState('');
  
  // Regenerate state
  const [regeneratingFile, setRegeneratingFile] = useState(null);
  const [showRegenerateModal, setShowRegenerateModal] = useState(false);
  const [regeneratePrompt, setRegeneratePrompt] = useState('');
  const [fileToRegenerate, setFileToRegenerate] = useState(null);
  
  const messagesEndRef = useRef(null);
  const hasInitialized = useRef(false);
  const inputRef = useRef(null);
  const wsRef = useRef(null);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // WebSocket connection for real-time logs
  const connectWebSocket = useCallback((projId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    try {
      const ws = new WebSocket(`${WS_BASE}/api/ws/projects/${projId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setTerminalOutput(prev => [...prev, '$ Connected to project stream']);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'log') {
            const levelIcon = {
              'info': '●',
              'success': '✓',
              'warning': '⚠',
              'error': '✗',
              'phase': '►',
              'file': '📄'
            }[data.level] || '●';
            
            setTerminalOutput(prev => [...prev, `$ ${levelIcon} ${data.message}`]);
          } else if (data.type === 'phase_update') {
            setCurrentStep(data.status);
            setProjectPhase(data.phase);
          } else if (data.type === 'file_created') {
            setTerminalOutput(prev => [...prev, `$ Created: ${data.file_path}`]);
          } else if (data.type === 'complete') {
            setTerminalOutput(prev => [...prev, '$ ✓ Project ready!']);
            // Reload project files
            if (projectId) {
              loadPipelineProject(projectId);
            }
          } else if (data.type === 'error') {
            setTerminalOutput(prev => [...prev, `$ ✗ Error: ${data.error_message}`]);
            toast.error(data.error_message);
          }
        } catch (e) {
          console.error('WebSocket message parse error:', e);
        }
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, [projectId]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Load project from pipeline if projectId provided
  useEffect(() => {
    if (projectId && !hasInitialized.current) {
      hasInitialized.current = true;
      loadPipelineProject(projectId);
    }
  }, [projectId]);

  // Handle initial prompt (legacy)
  useEffect(() => {
    if (hasInitialized.current) return;
    const initialPrompt = searchParams.get('prompt');
    if (initialPrompt && !workspaceId && !projectId) {
      hasInitialized.current = true;
      handleSendMessage(initialPrompt);
    }
  }, []);

  // Load workspace if ID provided (legacy)
  useEffect(() => {
    if (workspaceId && !projectId) {
      loadWorkspace(workspaceId);
    }
  }, [workspaceId]);

  // Load project from pipeline API
  const loadPipelineProject = async (projId) => {
    const token = localStorage.getItem('session_token');
    try {
      // Get project details
      const response = await fetch(`${API_BASE}/api/pipeline/projects/${projId}`, {
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        const project = await response.json();
        
        // Set project info
        setProjectName(project.plan?.project_name || 'My Project');
        setProjectPhase(project.phase);
        setProjectPlan(project.plan);
        setFiles(project.files || {});
        
        // Select first file
        const fileNames = Object.keys(project.files || {});
        if (fileNames.length > 0) {
          setSelectedFile(fileNames[0]);
        }
        
        // Connect to WebSocket for real-time updates
        connectWebSocket(projId);
        
        // Add welcome message
        addMessage('assistant', `✅ Project loaded: **${project.plan?.project_name || 'Your Project'}**

📁 ${fileNames.length} files generated
🏗️ Status: ${project.phase}

You can now:
- **Preview** your project on the right panel
- **Edit** any file directly
- **Ask me** to add features or fix issues

What would you like to do next?`);

        // Switch to preview mode
        setRightPanelMode('preview');
      }
    } catch (error) {
      console.error('Failed to load project:', error);
      toast.error('Failed to load project');
    }
  };

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
        }
        
        // Add welcome message
        if (data.prompt) {
          addMessage('user', data.prompt);
          addMessage('assistant', `Project loaded with ${fileNames.length} files.`);
        }
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
    }
  };

  const addMessage = (role, content, type = 'text') => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
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
    setAgentThinking(true);
    
    addMessage('user', messageText);
    
    const token = localStorage.getItem('session_token');
    
    try {
      // Use pipeline for project iteration
      if (projectId) {
        setCurrentStep('Processing your request...');
        
        const response = await fetch(`${API_BASE}/api/pipeline/projects/${projectId}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': token
          },
          body: JSON.stringify({
            content: messageText,
            role: 'user'
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          addMessage('assistant', `🔄 ${data.message}

I'm working on your request. This may take a moment...`);
          
          // Poll for completion
          let attempts = 0;
          while (attempts < 30) {
            await new Promise(r => setTimeout(r, 2000));
            attempts++;
            
            const statusResponse = await fetch(`${API_BASE}/api/pipeline/projects/${projectId}/status`, {
              headers: { 'X-Session-Token': token }
            });
            
            const status = await statusResponse.json();
            setCurrentStep(status.status);
            
            if (status.phase === 'completed') {
              // Reload project files
              await loadPipelineProject(projectId);
              addMessage('assistant', '✅ Changes applied successfully! Check the preview.');
              break;
            } else if (status.phase === 'failed') {
              addMessage('assistant', '❌ Failed to apply changes. Please try again.');
              break;
            }
          }
        } else {
          addMessage('assistant', `Error: ${data.error || 'Failed to process request'}`);
        }
      } else if (!workspaceId) {
        // New project generation (legacy)
        setCurrentStep('Analyzing your request...');
        addMessage('assistant', 'Starting to build your app...', 'progress');
        
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
        setTerminalOutput(prev => [...prev, `$ Creating project: ${startData.name || 'app'}`, '$ Initializing workspace...']);
        
        // Poll for status
        let completed = false;
        while (!completed) {
          await new Promise(r => setTimeout(r, 2000));
          
          const statusResponse = await fetch(`${API_BASE}/api/agents/v2/generation-status/${jobId}`, {
            headers: { 'X-Session-Token': token }
          });
          
          const statusData = await statusResponse.json();
          
          if (statusData.current_step) {
            setCurrentStep(statusData.current_step);
            setTerminalOutput(prev => [...prev, `$ ${statusData.current_step}`]);
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
            }
            
            setTerminalOutput(prev => [...prev, `$ ✓ Generated ${fileNames.length} files`, '$ Ready to preview']);
            addMessage('assistant', `I've created your app with ${fileNames.length} files. You can view the code on the right panel or preview it live.`);
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Generation failed');
          }
        }
      } else {
        // Modify existing project
        setCurrentStep('Processing your changes...');
        setTerminalOutput(prev => [...prev, `$ Modifying project...`]);
        
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
          const modCount = data.modified_files?.length || 0;
          setTerminalOutput(prev => [...prev, `$ ✓ Modified ${modCount} files`]);
          addMessage('assistant', `Done! I've updated ${modCount} file${modCount !== 1 ? 's' : ''}.`);
        } else {
          throw new Error(data.detail || 'Modification error');
        }
      }
    } catch (error) {
      addMessage('assistant', `Sorry, I encountered an error: ${error.message}`);
      setTerminalOutput(prev => [...prev, `$ Error: ${error.message}`]);
    } finally {
      setIsAgentRunning(false);
      setAgentThinking(false);
      setCurrentStep('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDeploy = () => {
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
        toast.success('Pushed to GitHub!');
        setTerminalOutput(prev => [...prev, `$ ✓ Pushed to GitHub: ${data.repo_url}`]);
        addMessage('assistant', `Your code is now on GitHub: ${data.repo_url}`);
      } else {
        throw new Error(data.detail || 'Push failed');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setDeployLoading(false);
    }
  };

  // Regenerate a single file
  const handleRegenerateFile = (filename) => {
    setFileToRegenerate(filename);
    setRegeneratePrompt('');
    setShowRegenerateModal(true);
  };

  const executeRegenerateFile = async () => {
    if (!fileToRegenerate || !projectId) return;
    
    setShowRegenerateModal(false);
    setRegeneratingFile(fileToRegenerate);
    setTerminalOutput(prev => [...prev, `$ Regenerating ${fileToRegenerate}...`]);
    
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/pipeline/projects/${projectId}/regenerate-file`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          file_path: fileToRegenerate,
          instruction: regeneratePrompt || `Improve and fix this file: ${fileToRegenerate}`
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // Update the file content
        setFiles(prev => ({
          ...prev,
          [fileToRegenerate]: data.content
        }));
        
        setTerminalOutput(prev => [...prev, `$ ✓ Regenerated ${fileToRegenerate}`]);
        toast.success(`File regenerated: ${fileToRegenerate}`);
        addMessage('assistant', `✅ Regenerated **${fileToRegenerate}**\n\n${data.summary || 'File has been updated.'}`);
      } else {
        throw new Error(data.error || 'Failed to regenerate file');
      }
    } catch (error) {
      setTerminalOutput(prev => [...prev, `$ ✗ Error: ${error.message}`]);
      toast.error(error.message);
    } finally {
      setRegeneratingFile(null);
      setFileToRegenerate(null);
    }
  };

  const handleDownload = () => {
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
    a.download = `${projectName.replace(/\s+/g, '_')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('Downloaded!');
  };

  const copyCode = () => {
    if (selectedFile && files[selectedFile]) {
      navigator.clipboard.writeText(files[selectedFile]);
      toast.success('Copied to clipboard');
    }
  };

  const displayCredits = () => {
    if (user?.unlimited_credits || user?.is_owner) return '∞';
    return user?.credits?.toFixed?.(1) || 0;
  };

  const hasFiles = Object.keys(files).length > 0;

  return (
    <div className="h-screen flex flex-col bg-[#f5f5f5]" data-testid="workspace-page">
      <Toaster />
      
      {/* Header */}
      <header className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          {/* Back button */}
          <button
            onClick={() => navigate('/home')}
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            data-testid="back-btn"
          >
            <ChevronLeft size={20} />
          </button>
          
          {/* Logo */}
          <span className="text-lg tracking-tight text-gray-800 font-light">
            melus<span className="font-normal">AI</span>
          </span>
          
          {/* Separator */}
          <div className="h-5 w-px bg-gray-200" />
          
          {/* Project name */}
          <span className="text-sm text-gray-600">{projectName}</span>
        </div>
        
        {/* Right side actions */}
        <div className="flex items-center gap-2">
          {/* Share */}
          <button 
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Share"
          >
            <Share2 size={18} />
          </button>
          
          {/* Download */}
          <button
            onClick={handleDownload}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            data-testid="download-btn"
            title="Download"
          >
            <Download size={18} />
          </button>
          
          {/* Deploy */}
          <button
            onClick={handleDeploy}
            className="flex items-center gap-2 px-4 py-1.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full text-sm font-medium transition-colors"
            data-testid="deploy-btn"
          >
            <Rocket size={14} />
            Deploy
          </button>
          
          {/* Credits */}
          <button
            onClick={() => setIsCreditModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            data-testid="credits-btn"
          >
            <Zap size={14} className="text-yellow-500" />
            <span className="text-sm font-medium">{displayCredits()}</span>
          </button>
        </div>
      </header>

      {/* Main Content - Two Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Chat */}
        <div className="w-1/2 flex flex-col bg-white border-r border-gray-200">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-xl mx-auto py-8 px-6">
              {messages.length === 0 && !isAgentRunning && (
                <div className="text-center py-16">
                  <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-cyan-100 to-blue-100 flex items-center justify-center">
                    <svg viewBox="0 0 24 24" className="w-6 h-6 text-cyan-600" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5z" />
                      <path d="M2 17l10 5 10-5" />
                      <path d="M2 12l10 5 10-5" />
                    </svg>
                  </div>
                  <h1 className="text-2xl font-medium text-gray-800 mb-2">
                    What do you want to build?
                  </h1>
                  <p className="text-gray-500">
                    Describe your app and I'll create it for you
                  </p>
                </div>
              )}
              
              {messages.map((msg) => (
                <div key={msg.id} className="mb-6">
                  <div className="flex items-start gap-3">
                    {/* Avatar */}
                    {msg.role === 'assistant' ? (
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                        <svg viewBox="0 0 24 24" className="w-4 h-4 text-white" fill="currentColor">
                          <path d="M12 2L2 7l10 5 10-5-10-5z" />
                        </svg>
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 text-sm font-medium text-gray-600">
                        {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                      </div>
                    )}
                    
                    {/* Message */}
                    <div className="flex-1 pt-1">
                      <div className="text-xs text-gray-400 mb-1">
                        {msg.role === 'assistant' ? 'AI' : 'You'}
                      </div>
                      {msg.type === 'progress' ? (
                        <div className="flex items-center gap-2 text-gray-500">
                          <Loader2 size={14} className="animate-spin" />
                          <span className="text-sm">{msg.content}</span>
                        </div>
                      ) : (
                        <p className="text-gray-700 text-sm leading-relaxed">{msg.content}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Agent thinking indicator */}
              {agentThinking && (
                <div className="mb-6">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                      <Loader2 size={14} className="animate-spin text-white" />
                    </div>
                    <div className="flex-1 pt-1">
                      <div className="text-xs text-gray-400 mb-1">AI</div>
                      <p className="text-gray-500 text-sm">{currentStep || 'Thinking...'}</p>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>
          
          {/* Chat Input */}
          <div className="p-4 border-t border-gray-100">
            <div className="max-w-xl mx-auto">
              <div className="relative">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={hasFiles ? "Ask me to make changes..." : "Describe the app you want to build..."}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 pr-12 text-gray-800 placeholder-gray-400 text-sm resize-none outline-none focus:border-gray-300 focus:ring-2 focus:ring-gray-100 transition-all"
                  data-testid="chat-input"
                  rows={1}
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!inputMessage.trim() || isAgentRunning}
                  className="absolute bottom-2.5 right-2.5 p-1.5 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 text-white rounded-lg transition-colors"
                  data-testid="send-btn"
                >
                  {isAgentRunning ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <ArrowRight size={16} />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right Panel - Code/Preview */}
        <div className="w-1/2 flex flex-col bg-[#1e1e1e]">
          {/* Panel Header */}
          <div className="h-10 bg-[#252526] border-b border-[#1e1e1e] flex items-center justify-between px-3 flex-shrink-0">
            <div className="flex items-center gap-1">
              <button
                onClick={() => setRightPanelMode('code')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded text-sm transition-colors ${
                  rightPanelMode === 'code'
                    ? 'bg-[#1e1e1e] text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
                data-testid="code-tab"
              >
                <Code size={14} />
                Code
              </button>
              <button
                onClick={() => setRightPanelMode('preview')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded text-sm transition-colors ${
                  rightPanelMode === 'preview'
                    ? 'bg-[#1e1e1e] text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
                data-testid="preview-tab"
              >
                <Eye size={14} />
                Preview
              </button>
            </div>
            
            {/* Actions */}
            <div className="flex items-center gap-1">
              {rightPanelMode === 'code' && selectedFile && (
                <button
                  onClick={copyCode}
                  className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
                  title="Copy code"
                >
                  <Copy size={14} />
                </button>
              )}
              {rightPanelMode === 'preview' && (
                <DeviceSelector device={previewDevice} onChange={setPreviewDevice} />
              )}
              <button
                onClick={() => setTerminalOpen(!terminalOpen)}
                className={`p-1.5 rounded transition-colors ${
                  terminalOpen ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                title="Toggle terminal"
              >
                <Terminal size={14} />
              </button>
            </div>
          </div>
          
          {/* Content Area */}
          <div className="flex-1 flex overflow-hidden">
            {rightPanelMode === 'code' ? (
              <>
                {/* File Explorer */}
                <div className="w-48 bg-[#252526] border-r border-[#1e1e1e] overflow-y-auto flex-shrink-0">
                  <div className="px-3 py-2 text-xs text-gray-500 uppercase font-medium">Explorer</div>
                  {hasFiles ? (
                    <FileTree
                      files={files}
                      selectedFile={selectedFile}
                      onSelectFile={setSelectedFile}
                    />
                  ) : (
                    <div className="px-3 py-2 text-sm text-gray-500">No files</div>
                  )}
                </div>
                
                {/* Code Editor */}
                <div className="flex-1 flex flex-col overflow-hidden">
                  {selectedFile ? (
                    <>
                      <EditorTabs
                        files={files}
                        selectedFile={selectedFile}
                        onSelectFile={setSelectedFile}
                      />
                      <div className="flex-1 overflow-hidden">
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
                  ) : (
                    <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                      {hasFiles ? 'Select a file to view' : 'Generate a project to see code'}
                    </div>
                  )}
                </div>
              </>
            ) : (
              /* Preview Mode */
              <div className="flex-1 flex flex-col bg-gray-100">
                {/* Preview toolbar */}
                <div className="h-10 bg-white border-b border-gray-200 flex items-center justify-between px-3">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded-full bg-red-400" />
                      <div className="w-3 h-3 rounded-full bg-yellow-400" />
                      <div className="w-3 h-3 rounded-full bg-green-400" />
                    </div>
                    <div className="ml-4 px-3 py-1 bg-gray-100 rounded text-xs text-gray-500 flex items-center gap-2">
                      <span>{projectId ? `preview.melus.ai/${projectId?.slice(0, 8)}` : 'preview.melus.ai'}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {/* Rating component */}
                    {projectId && projectPhase === 'completed' && (
                      <div className="flex items-center gap-2 mr-2 px-2 py-1 bg-gray-50 rounded-lg">
                        <span className="text-xs text-gray-400">Rate:</span>
                        <ProjectRating projectId={projectId} />
                      </div>
                    )}
                    <button 
                      onClick={() => {
                        const iframe = document.getElementById('preview-iframe');
                        if (iframe) iframe.src = iframe.src;
                      }}
                      className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                      title="Refresh preview"
                    >
                      <RefreshCw size={14} />
                    </button>
                    <button 
                      onClick={() => projectId && window.open(`${API_BASE}/api/pipeline/preview/${projectId}`, '_blank')}
                      className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                      title="Open in new tab"
                    >
                      <ExternalLink size={14} />
                    </button>
                  </div>
                </div>
                
                {/* Preview content */}
                <div className="flex-1 flex items-center justify-center p-4">
                  <div 
                    className={`bg-white rounded-lg shadow-lg overflow-hidden transition-all ${
                      previewDevice === 'desktop' ? 'w-full h-full' :
                      previewDevice === 'tablet' ? 'w-[768px] h-full' :
                      'w-[375px] h-full'
                    }`}
                  >
                    {projectId && hasFiles ? (
                      <iframe
                        id="preview-iframe"
                        src={`${API_BASE}/api/pipeline/preview/${projectId}`}
                        className="w-full h-full border-0"
                        title="Project Preview"
                        sandbox="allow-scripts allow-same-origin"
                      />
                    ) : hasFiles ? (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <div className="text-center">
                          <Eye size={48} className="mx-auto mb-4 text-gray-300" />
                          <p className="text-sm">Preview not available</p>
                          <p className="text-xs text-gray-300 mt-1">View your code in the Code tab</p>
                        </div>
                      </div>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm">
                        Generate a project first
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Terminal Panel */}
          {terminalOpen && (
            <div className="h-40 bg-[#1e1e1e] border-t border-gray-700 flex-shrink-0">
              <div className="h-7 bg-[#252526] flex items-center justify-between px-3 border-b border-gray-700">
                <span className="text-xs text-gray-400">Terminal</span>
                <button
                  onClick={() => setTerminalOpen(false)}
                  className="p-0.5 text-gray-400 hover:text-white"
                >
                  <X size={12} />
                </button>
              </div>
              <div className="p-3 font-mono text-xs text-gray-300 overflow-y-auto h-[calc(100%-28px)]">
                {terminalOutput.map((line, i) => (
                  <div key={i} className={line.includes('✓') ? 'text-green-400' : line.includes('Error') ? 'text-red-400' : ''}>
                    {line}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Credit Modal */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
      
      {/* Deploy Modal */}
      {showDeployModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Deploy to GitHub</h3>
            
            {githubStatus?.connected ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-600 text-sm bg-green-50 px-3 py-2 rounded-lg">
                  <Check size={16} />
                  Connected as <span className="font-medium">{githubStatus.username}</span>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-600 mb-1.5">Repository Name</label>
                  <input
                    type="text"
                    value={repoName}
                    onChange={(e) => setRepoName(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-gray-800 text-sm focus:outline-none focus:border-gray-300 focus:ring-2 focus:ring-gray-100"
                    placeholder="my-awesome-app"
                    data-testid="repo-name-input"
                  />
                </div>
                
                <div className="flex gap-3 pt-2">
                  <button
                    onClick={() => setShowDeployModal(false)}
                    className="flex-1 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl text-sm font-medium transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handlePushToGithub}
                    disabled={deployLoading || !repoName.trim()}
                    className="flex-1 px-4 py-2.5 bg-gray-900 hover:bg-gray-800 text-white disabled:opacity-50 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2"
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
              <div className="text-center py-6">
                <div className="w-12 h-12 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                  <GitBranch size={24} className="text-gray-400" />
                </div>
                <p className="text-gray-600 mb-4">Connect your GitHub account to deploy</p>
                <button
                  onClick={() => window.open(`${API_BASE}/api/github/auth/login`, '_blank')}
                  className="px-6 py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-xl text-sm font-medium transition-colors"
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
