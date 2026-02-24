import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Send,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
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
  Folder,
  FolderOpen,
  GitBranch,
  ArrowRight,
  Copy,
  RotateCcw,
  ExternalLink,
  Play,
  Maximize2,
  Minimize2,
  RefreshCw,
  Share2,
  Settings,
  Smartphone,
  Monitor,
  Tablet,
  Wand2,
  Plus,
  MessageSquare,
  Clock,
  MoreHorizontal,
  Trash2,
  Edit3,
  Save,
  Upload,
  Menu,
  PanelLeftClose,
  PanelLeft,
  Bot,
  User,
  Sparkles,
  FileCode,
  FileJson,
  FileText,
  Image,
  Cpu,
  Search
} from 'lucide-react';
import { Toaster, toast } from '../components/ui/sonner';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const WS_BASE = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');

// Available AI Models
const AI_MODELS = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', description: 'Fast & efficient', icon: '⚡' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI', description: 'Budget friendly', icon: '💡' },
  { id: 'gpt-5.2-codex', name: 'GPT-5.2 Codex', provider: 'OpenAI', description: 'Best for code', icon: '🚀', premium: true },
  { id: 'o3', name: 'O3 Reasoning', provider: 'OpenAI', description: 'Advanced reasoning', icon: '🧠', premium: true },
  { id: 'claude-4-sonnet', name: 'Claude 4 Sonnet', provider: 'Anthropic', description: 'Balanced', icon: '🎯' },
  { id: 'claude-4.5-opus', name: 'Claude 4.5 Opus', provider: 'Anthropic', description: 'Most capable', icon: '👑', premium: true },
  { id: 'claude-4.6-opus', name: 'Claude 4.6 Opus', provider: 'Anthropic', description: 'Latest Opus', icon: '🔮', premium: true },
  { id: 'gemini-3-pro', name: 'Gemini 3 Pro', provider: 'Google', description: 'Multimodal', icon: '✨' },
  { id: 'gemini-3-flash', name: 'Gemini 3 Flash', provider: 'Google', description: 'Ultra fast', icon: '💨' },
];

// Agent Modes
const AGENT_MODES = [
  { id: 'e1', name: 'E1', description: 'Standard - Fast iterations' },
  { id: 'e1.5', name: 'E1.5', description: 'Enhanced - Better quality' },
  { id: 'e2', name: 'E2', description: 'Advanced - Multi-agent system' },
  { id: 'pro', name: 'Pro', description: 'Maximum quality' },
];

// File icon helper
const getFileIcon = (filename) => {
  const ext = filename.split('.').pop().toLowerCase();
  const icons = {
    js: { icon: FileCode, color: 'text-yellow-400' },
    jsx: { icon: FileCode, color: 'text-yellow-400' },
    ts: { icon: FileCode, color: 'text-blue-400' },
    tsx: { icon: FileCode, color: 'text-blue-400' },
    css: { icon: FileText, color: 'text-blue-500' },
    scss: { icon: FileText, color: 'text-pink-400' },
    html: { icon: FileCode, color: 'text-orange-400' },
    json: { icon: FileJson, color: 'text-yellow-300' },
    py: { icon: FileCode, color: 'text-green-400' },
    md: { icon: FileText, color: 'text-gray-400' },
    svg: { icon: Image, color: 'text-pink-400' },
    png: { icon: Image, color: 'text-purple-400' },
    jpg: { icon: Image, color: 'text-purple-400' },
    env: { icon: FileText, color: 'text-gray-500' },
  };
  return icons[ext] || { icon: File, color: 'text-gray-400' };
};

// Chat Message Component
const ChatMessage = ({ message, isUser }) => {
  const [copied, setCopied] = useState(false);

  const copyContent = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`group flex gap-3 py-4 px-4 hover:bg-[#1a1a1a] transition-colors ${isUser ? '' : 'bg-[#0d0d0d]'}`}>
      <div className={`w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-gradient-to-br from-blue-500 to-cyan-500' 
          : 'bg-gradient-to-br from-emerald-500 to-teal-500'
      }`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-medium text-gray-400">
            {isUser ? 'You' : 'Melus AI'}
          </span>
          <span className="text-xs text-gray-600">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        
        <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
        
        {message.files && message.files.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.files.map((file, i) => (
              <div key={i} className="flex items-center gap-2 px-2 py-1 bg-[#252525] rounded text-xs text-gray-400">
                <FileCode className="w-3 h-3 text-cyan-400" />
                <span>{file}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <button
        onClick={copyContent}
        className="opacity-0 group-hover:opacity-100 p-1.5 text-gray-500 hover:text-white hover:bg-[#333] rounded transition-all"
      >
        {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
      </button>
    </div>
  );
};

// File Tree Component
const FileTreeItem = ({ name, path, isFolder, isExpanded, onToggle, onSelect, isSelected, depth = 0, children }) => {
  const { icon: IconComponent, color } = getFileIcon(name);
  
  return (
    <div>
      <button
        onClick={() => isFolder ? onToggle(path) : onSelect(path)}
        className={`w-full flex items-center gap-1.5 py-1 px-2 text-sm hover:bg-[#2d2d2d] transition-colors ${
          isSelected ? 'bg-[#37373d] text-white' : 'text-gray-400'
        }`}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        {isFolder ? (
          <>
            <ChevronRight className={`w-3.5 h-3.5 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
            {isExpanded ? (
              <FolderOpen className="w-4 h-4 text-yellow-400" />
            ) : (
              <Folder className="w-4 h-4 text-yellow-400" />
            )}
          </>
        ) : (
          <>
            <span className="w-3.5" />
            <IconComponent className={`w-4 h-4 ${color}`} />
          </>
        )}
        <span className="truncate">{name}</span>
      </button>
      {isFolder && isExpanded && children}
    </div>
  );
};

// Model Selector Component
const ModelSelector = ({ selectedModel, onSelect, isPremiumUser }) => {
  const [isOpen, setIsOpen] = useState(false);
  const selected = AI_MODELS.find(m => m.id === selectedModel) || AI_MODELS[0];

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <button className="flex items-center gap-2 px-3 py-1.5 bg-[#252525] hover:bg-[#333] border border-[#333] rounded-lg text-sm transition-colors">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span className="text-gray-300">{selected.name}</span>
          <ChevronDown className="w-3.5 h-3.5 text-gray-500" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-64 bg-[#1e1e1e] border-[#333] p-1">
        {AI_MODELS.map(model => (
          <DropdownMenuItem
            key={model.id}
            onClick={() => {
              if (model.premium && !isPremiumUser) {
                toast.error('Upgrade to Pro for this model');
                return;
              }
              onSelect(model.id);
            }}
            className={`flex items-center gap-3 px-3 py-2 cursor-pointer rounded ${
              selectedModel === model.id ? 'bg-[#333]' : 'hover:bg-[#2a2a2a]'
            }`}
          >
            <span className="text-lg">{model.icon}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm text-white">{model.name}</span>
                {model.premium && (
                  <span className="px-1.5 py-0.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-[10px] rounded font-medium">
                    PRO
                  </span>
                )}
              </div>
              <div className="text-xs text-gray-500">{model.description}</div>
            </div>
            {selectedModel === model.id && <Check className="w-4 h-4 text-cyan-400" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

// Device Selector for Preview
const DeviceSelector = ({ device, onChange }) => {
  const devices = [
    { id: 'desktop', icon: Monitor, width: '100%' },
    { id: 'tablet', icon: Tablet, width: '768px' },
    { id: 'mobile', icon: Smartphone, width: '375px' },
  ];

  return (
    <div className="flex items-center gap-0.5 bg-[#252525] rounded-lg p-0.5">
      {devices.map(d => {
        const Icon = d.icon;
        return (
          <button
            key={d.id}
            onClick={() => onChange(d.id)}
            className={`p-1.5 rounded transition-colors ${
              device === d.id
                ? 'bg-[#333] text-white'
                : 'text-gray-500 hover:text-gray-300'
            }`}
            title={d.id}
          >
            <Icon size={14} />
          </button>
        );
      })}
    </div>
  );
};

// Main Builder Page Component
const BuilderPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, updateCredits } = useAuth();

  // Project state
  const [projectId, setProjectId] = useState(searchParams.get('project') || null);
  const [projectName, setProjectName] = useState('New Project');
  const [files, setFiles] = useState({});
  const [selectedFile, setSelectedFile] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState(new Set(['src']));

  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentPhase, setCurrentPhase] = useState('');

  // UI state
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [rightPanel, setRightPanel] = useState('preview'); // 'code' | 'preview'
  const [previewDevice, setPreviewDevice] = useState('desktop');
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [terminalLogs, setTerminalLogs] = useState(['$ Ready']);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [agentMode, setAgentMode] = useState('e1');

  // Projects list
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const wsRef = useRef(null);
  const hasInitialized = useRef(false);

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  // Load project if ID provided
  useEffect(() => {
    if (projectId && !hasInitialized.current) {
      hasInitialized.current = true;
      loadProject(projectId);
    }
  }, [projectId]);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load projects list
  const loadProjects = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/pipeline/projects`, {
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        const data = await response.json();
        setProjects(data || []);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoadingProjects(false);
    }
  };

  // Load specific project
  const loadProject = async (projId) => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/pipeline/projects/${projId}`, {
        headers: { 'X-Session-Token': token }
      });

      if (response.ok) {
        const project = await response.json();
        setProjectName(project.plan?.project_name || 'My Project');
        setFiles(project.files || {});

        // Select first file
        const fileNames = Object.keys(project.files || {});
        if (fileNames.length > 0) {
          setSelectedFile(fileNames[0]);
        }

        // Add welcome message
        addMessage('assistant', `Project loaded: **${project.plan?.project_name || 'Your Project'}**\n\n📁 ${fileNames.length} files\n🔧 Status: ${project.phase}\n\nYou can edit files, preview your app, or ask me to make changes.`);

        // Connect WebSocket
        connectWebSocket(projId);
      }
    } catch (error) {
      console.error('Failed to load project:', error);
      toast.error('Failed to load project');
    }
  };

  // WebSocket connection
  const connectWebSocket = useCallback((projId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const ws = new WebSocket(`${WS_BASE}/api/ws/projects/${projId}`);

      ws.onopen = () => {
        setTerminalLogs(prev => [...prev, '$ Connected to project stream']);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'log') {
            const icon = data.level === 'success' ? '✓' : data.level === 'error' ? '✗' : '●';
            setTerminalLogs(prev => [...prev, `$ ${icon} ${data.message}`]);
          } else if (data.type === 'file_created') {
            setTerminalLogs(prev => [...prev, `$ Created: ${data.file_path}`]);
          } else if (data.type === 'complete') {
            setTerminalLogs(prev => [...prev, '$ ✓ Ready!']);
            loadProject(projId);
          }
        } catch (e) {
          console.error('WS parse error:', e);
        }
      };

      ws.onclose = () => console.log('WS disconnected');
      wsRef.current = ws;
    } catch (error) {
      console.error('WS connection error:', error);
    }
  }, []);

  // Cleanup
  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Add message helper
  const addMessage = (role, content, extra = {}) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      role,
      content,
      timestamp: new Date(),
      ...extra
    }]);
  };

  // Send message
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isGenerating) return;

    const userMsg = inputMessage.trim();
    setInputMessage('');
    addMessage('user', userMsg);
    setIsGenerating(true);
    setCurrentPhase('Processing...');

    const token = localStorage.getItem('session_token');

    try {
      if (projectId) {
        // Modify existing project
        const response = await fetch(`${API_BASE}/api/pipeline/projects/${projectId}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': token
          },
          body: JSON.stringify({
            content: userMsg,
            model: selectedModel,
            mode: agentMode
          })
        });

        const data = await response.json();

        if (response.ok) {
          addMessage('assistant', `Working on your request...\n\n${data.message || ''}`);
          setTerminalLogs(prev => [...prev, `$ ${data.type || 'Processing'}: ${data.message || userMsg}`]);

          // Poll for completion
          await pollProjectStatus(projectId);
        } else {
          throw new Error(data.error || 'Request failed');
        }
      } else {
        // Create new project using Brain API
        setCurrentPhase('Analyzing intent...');
        setTerminalLogs(prev => [...prev, '$ Creating project...']);
        setTerminalLogs(prev => [...prev, `$ Model: ${selectedModel}`]);
        setTerminalLogs(prev => [...prev, `$ Mode: ${agentMode}`]);

        // Use the new Brain API for project creation
        const response = await fetch(`${API_BASE}/api/brain/create-task`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': token
          },
          body: JSON.stringify({
            prompt: userMsg,
            model: selectedModel,
            mode: agentMode
          })
        });

        const data = await response.json();

        if (response.ok) {
          const newProjectId = data.project_id;
          setProjectId(newProjectId);
          window.history.replaceState(null, '', `/builder?project=${newProjectId}`);
          toast.info('Building your project...');
          
          setTerminalLogs(prev => [...prev, `$ Project ID: ${newProjectId}`]);
          addMessage('assistant', `Starting project generation...\n\n🧠 Model: ${selectedModel}\n⚡ Mode: ${agentMode}\n📋 Analyzing your request...`);

          // Try to connect WebSocket
          try {
            connectWebSocket(newProjectId);
          } catch (e) {
            console.log('WebSocket not available, using polling');
          }
          
          // Poll for completion using Brain API
          await pollBrainTaskStatus(newProjectId);
        } else {
          throw new Error(data.error || 'Failed to create project');
        }
      }
    } catch (error) {
      console.error('Send error:', error);
      addMessage('assistant', `Sorry, there was an error: ${error.message}`);
      setTerminalLogs(prev => [...prev, `$ Error: ${error.message}`]);
    } finally {
      setIsGenerating(false);
      setCurrentPhase('');
    }
  };

  // Poll brain task status
  const pollBrainTaskStatus = async (taskId) => {
    const token = localStorage.getItem('session_token');
    let attempts = 0;

    while (attempts < 60) {
      await new Promise(r => setTimeout(r, 2000));
      attempts++;

      try {
        const response = await fetch(`${API_BASE}/api/brain/task/${taskId}`, {
          headers: { 'X-Session-Token': token }
        });

        if (response.ok) {
          const status = await response.json();
          setCurrentPhase(status.status || status.phase);
          setTerminalLogs(prev => [...prev, `$ Phase: ${status.phase}`]);

          if (status.phase === 'complete' || status.phase === 'completed') {
            // Load the project files
            await loadProjectFromPipeline(taskId);
            loadProjects();
            
            const filesCount = status.files_count || 0;
            addMessage('assistant', `✅ Project generated successfully!\n\n📁 ${filesCount} files created\n🎯 Intent: ${status.intent?.type || 'web_app'}\n\nYou can now preview your app or edit the code.`);
            toast.success('Project ready!');
            return;
          } else if (status.phase === 'error') {
            throw new Error('Generation failed: ' + (status.errors?.join(', ') || 'Unknown error'));
          }
        }
      } catch (error) {
        console.error('Poll error:', error);
        if (attempts > 5) {
          addMessage('assistant', `Error checking status: ${error.message}`);
          return;
        }
      }
    }
    
    addMessage('assistant', 'Generation is taking longer than expected. Please check back in a moment.');
  };

  // Load project from pipeline API
  const loadProjectFromPipeline = async (projId) => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/pipeline/projects/${projId}`, {
        headers: { 'X-Session-Token': token }
      });

      if (response.ok) {
        const project = await response.json();
        setProjectName(project.plan?.project_name || 'My Project');
        setFiles(project.files || {});

        // Select first file
        const fileNames = Object.keys(project.files || {});
        if (fileNames.length > 0) {
          setSelectedFile(fileNames[0]);
        }
        
        setTerminalLogs(prev => [...prev, `$ Loaded ${fileNames.length} files`]);
      }
    } catch (error) {
      console.error('Failed to load project:', error);
    }
  };

  // Poll project status
  const pollProjectStatus = async (projId) => {
    const token = localStorage.getItem('session_token');
    let attempts = 0;

    while (attempts < 60) {
      await new Promise(r => setTimeout(r, 2000));
      attempts++;

      try {
        const response = await fetch(`${API_BASE}/api/pipeline/projects/${projId}/status`, {
          headers: { 'X-Session-Token': token }
        });

        if (response.ok) {
          const status = await response.json();
          setCurrentPhase(status.status || status.phase);

          if (status.phase === 'completed') {
            await loadProject(projId);
            loadProjects();
            addMessage('assistant', '✅ Done! Your project is ready. Check the preview or edit the code.');
            toast.success('Project ready!');
            return;
          } else if (status.phase === 'failed') {
            throw new Error('Generation failed');
          }
        }
      } catch (error) {
        console.error('Poll error:', error);
        return;
      }
    }
  };

  // Key handler
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Toggle folder
  const toggleFolder = (path) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  // Build file tree structure
  const buildFileTree = () => {
    const tree = {};
    Object.keys(files).forEach(filepath => {
      const parts = filepath.split('/');
      let current = tree;
      parts.forEach((part, i) => {
        if (i === parts.length - 1) {
          current[part] = { type: 'file', path: filepath };
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

  // Render file tree
  const renderTree = (tree, depth = 0, parentPath = '') => {
    return Object.entries(tree)
      .sort(([, a], [, b]) => {
        if (a.type === 'folder' && b.type !== 'folder') return -1;
        if (a.type !== 'folder' && b.type === 'folder') return 1;
        return 0;
      })
      .map(([name, item]) => {
        const path = parentPath ? `${parentPath}/${name}` : name;
        if (item.type === 'folder') {
          return (
            <FileTreeItem
              key={path}
              name={name}
              path={path}
              isFolder
              isExpanded={expandedFolders.has(path)}
              onToggle={toggleFolder}
              onSelect={() => {}}
              depth={depth}
            >
              {renderTree(item.children, depth + 1, path)}
            </FileTreeItem>
          );
        }
        return (
          <FileTreeItem
            key={item.path}
            name={name}
            path={item.path}
            isFolder={false}
            onSelect={setSelectedFile}
            isSelected={selectedFile === item.path}
            depth={depth}
          />
        );
      });
  };

  // Download project
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

  // Create new project
  const handleNewProject = () => {
    setProjectId(null);
    setProjectName('New Project');
    setFiles({});
    setSelectedFile(null);
    setMessages([]);
    setTerminalLogs(['$ Ready']);
    window.history.replaceState(null, '', '/builder');
    hasInitialized.current = false;
  };

  // Display credits
  const displayCredits = () => {
    if (user?.unlimited_credits || user?.is_owner) return '∞';
    return user?.credits?.toFixed?.(1) || 0;
  };

  const hasFiles = Object.keys(files).length > 0;
  const fileTree = buildFileTree();

  return (
    <div className="h-screen flex bg-[#0a0a0a] text-white" data-testid="builder-page">
      <Toaster />

      {/* Left Sidebar - Projects & Chat */}
      <aside className={`${sidebarOpen ? 'w-80' : 'w-0'} flex flex-col bg-[#111] border-r border-[#222] transition-all duration-200 overflow-hidden`}>
        {/* Sidebar Header */}
        <div className="h-12 flex items-center justify-between px-3 border-b border-[#222]">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">Melus AI</span>
          </div>
          <button
            onClick={handleNewProject}
            className="p-1.5 hover:bg-[#222] rounded-lg transition-colors"
            title="New project"
          >
            <Plus className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        {/* Agent Mode Selector */}
        <div className="p-3 border-b border-[#222]">
          <div className="flex items-center gap-1 bg-[#1a1a1a] rounded-lg p-0.5">
            {AGENT_MODES.map(mode => (
              <button
                key={mode.id}
                onClick={() => setAgentMode(mode.id)}
                className={`flex-1 px-2 py-1.5 rounded-md text-xs font-medium transition-all ${
                  agentMode === mode.id
                    ? 'bg-[#333] text-white'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
                title={mode.description}
              >
                {mode.name}
              </button>
            ))}
          </div>
        </div>

        {/* Projects List */}
        <div className="flex-shrink-0 max-h-48 overflow-y-auto border-b border-[#222]">
          <div className="p-2">
            <div className="text-xs text-gray-500 uppercase px-2 py-1 font-medium">Projects</div>
            {loadingProjects ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
              </div>
            ) : projects.length === 0 ? (
              <div className="text-center py-4 text-xs text-gray-500">
                No projects yet
              </div>
            ) : (
              projects.slice(0, 5).map(proj => (
                <button
                  key={proj.id}
                  onClick={() => {
                    setProjectId(proj.id);
                    window.history.replaceState(null, '', `/builder?project=${proj.id}`);
                    hasInitialized.current = false;
                    loadProject(proj.id);
                  }}
                  className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left transition-colors ${
                    projectId === proj.id ? 'bg-[#252525] text-white' : 'text-gray-400 hover:bg-[#1a1a1a]'
                  }`}
                >
                  <FolderOpen className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm truncate flex-1">
                    {proj.plan?.project_name || proj.prompt?.slice(0, 25) || 'Untitled'}
                  </span>
                  {proj.phase === 'completed' && (
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
                  )}
                </button>
              ))
            )}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full px-6 text-center">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center mb-4">
                <MessageSquare className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">Start Building</h3>
              <p className="text-sm text-gray-500">
                Describe what you want to create
              </p>
            </div>
          ) : (
            <div>
              {messages.map(msg => (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  isUser={msg.role === 'user'}
                />
              ))}
              {isGenerating && (
                <div className="flex gap-3 py-4 px-4 bg-[#0d0d0d]">
                  <div className="w-7 h-7 rounded-md bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                    <Loader2 className="w-4 h-4 text-white animate-spin" />
                  </div>
                  <div className="flex-1">
                    <span className="text-xs text-gray-400">Melus AI</span>
                    <p className="text-sm text-gray-500 mt-1">{currentPhase || 'Thinking...'}</p>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="p-3 border-t border-[#222]">
          <div className="flex items-end gap-2">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={projectId ? "Ask me to make changes..." : "Describe your app..."}
                className="w-full bg-[#1a1a1a] border border-[#333] rounded-xl px-4 py-3 pr-12 text-sm text-white placeholder-gray-500 resize-none outline-none focus:border-cyan-500/50 transition-colors"
                rows={1}
                style={{ minHeight: '48px', maxHeight: '120px' }}
                data-testid="chat-input"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isGenerating}
                className="absolute bottom-2 right-2 p-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                data-testid="send-btn"
              >
                {isGenerating ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ArrowRight className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Model Selector */}
          <div className="mt-2">
            <ModelSelector
              selectedModel={selectedModel}
              onSelect={setSelectedModel}
              isPremiumUser={user?.unlimited_credits || user?.subscription === 'pro'}
            />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Header */}
        <header className="h-12 bg-[#111] border-b border-[#222] flex items-center justify-between px-3">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 hover:bg-[#222] rounded-lg transition-colors"
              data-testid="toggle-sidebar"
            >
              {sidebarOpen ? <PanelLeftClose className="w-4 h-4 text-gray-400" /> : <PanelLeft className="w-4 h-4 text-gray-400" />}
            </button>

            <div className="h-4 w-px bg-[#333]" />

            <span className="text-sm text-gray-300">{projectName}</span>
          </div>

          <div className="flex items-center gap-2">
            {/* View Toggle */}
            <div className="flex items-center gap-0.5 bg-[#1a1a1a] rounded-lg p-0.5">
              <button
                onClick={() => setRightPanel('code')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
                  rightPanel === 'code' ? 'bg-[#333] text-white' : 'text-gray-500 hover:text-gray-300'
                }`}
                data-testid="code-view"
              >
                <Code className="w-4 h-4" />
                Code
              </button>
              <button
                onClick={() => setRightPanel('preview')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
                  rightPanel === 'preview' ? 'bg-[#333] text-white' : 'text-gray-500 hover:text-gray-300'
                }`}
                data-testid="preview-view"
              >
                <Eye className="w-4 h-4" />
                Preview
              </button>
            </div>

            <div className="h-4 w-px bg-[#333]" />

            {/* Actions */}
            <button
              onClick={handleDownload}
              className="p-2 hover:bg-[#222] rounded-lg transition-colors"
              title="Download"
              data-testid="download-btn"
            >
              <Download className="w-4 h-4 text-gray-400" />
            </button>

            <button
              className="p-2 hover:bg-[#222] rounded-lg transition-colors"
              title="Share"
            >
              <Share2 className="w-4 h-4 text-gray-400" />
            </button>

            <button
              className="flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
              data-testid="deploy-btn"
            >
              <Rocket className="w-4 h-4" />
              Deploy
            </button>

            <div className="h-4 w-px bg-[#333]" />

            {/* Credits */}
            <button
              onClick={() => navigate('/pricing')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1a1a1a] hover:bg-[#222] rounded-lg transition-colors"
              data-testid="credits-display"
            >
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-gray-300">{displayCredits()}</span>
            </button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white text-sm font-medium">
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48 bg-[#1e1e1e] border-[#333]">
                <DropdownMenuItem onClick={() => navigate('/pricing')} className="cursor-pointer text-gray-300 hover:text-white">
                  <Zap className="mr-2 h-4 w-4 text-yellow-400" />
                  Upgrade
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer text-gray-300 hover:text-white">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-[#333]" />
                <DropdownMenuItem
                  onClick={() => {
                    localStorage.removeItem('session_token');
                    navigate('/');
                  }}
                  className="cursor-pointer text-red-400 hover:text-red-300"
                >
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Main Panel */}
        <div className="flex-1 flex overflow-hidden">
          {rightPanel === 'code' ? (
            <>
              {/* File Explorer */}
              <div className="w-56 bg-[#111] border-r border-[#222] flex flex-col">
                <div className="h-8 flex items-center px-3 text-xs text-gray-500 uppercase font-medium border-b border-[#222]">
                  Explorer
                </div>
                <div className="flex-1 overflow-y-auto py-1">
                  {hasFiles ? renderTree(fileTree) : (
                    <div className="px-3 py-4 text-sm text-gray-500 text-center">
                      No files yet
                    </div>
                  )}
                </div>
              </div>

              {/* Code Editor */}
              <div className="flex-1 flex flex-col bg-[#1e1e1e]">
                {selectedFile ? (
                  <>
                    {/* Editor Tab */}
                    <div className="h-9 bg-[#252525] flex items-center border-b border-[#1e1e1e]">
                      <div className="flex items-center gap-2 px-4 h-full bg-[#1e1e1e] border-t-2 border-cyan-500 text-sm text-white">
                        {(() => {
                          const { icon: Icon, color } = getFileIcon(selectedFile);
                          return <Icon className={`w-4 h-4 ${color}`} />;
                        })()}
                        <span>{selectedFile.split('/').pop()}</span>
                        <button className="p-0.5 hover:bg-[#333] rounded">
                          <X className="w-3 h-3 text-gray-500" />
                        </button>
                      </div>
                    </div>

                    {/* Code Content */}
                    <div className="flex-1 overflow-auto">
                      <pre className="p-4 text-sm font-mono text-gray-300 leading-relaxed">
                        <code>{files[selectedFile]}</code>
                      </pre>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                    {hasFiles ? 'Select a file to view' : 'Generate a project first'}
                  </div>
                )}
              </div>
            </>
          ) : (
            /* Preview Panel */
            <div className="flex-1 flex flex-col bg-[#0a0a0a]">
              {/* Preview Header */}
              <div className="h-10 bg-white flex items-center justify-between px-3 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-400" />
                    <div className="w-3 h-3 rounded-full bg-yellow-400" />
                    <div className="w-3 h-3 rounded-full bg-green-400" />
                  </div>
                  <div className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-500">
                    preview.melus.ai/{projectId?.slice(0, 8) || 'new'}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <DeviceSelector device={previewDevice} onChange={setPreviewDevice} />
                  <button
                    onClick={() => {
                      const iframe = document.getElementById('preview-iframe');
                      if (iframe) iframe.src = iframe.src;
                    }}
                    className="p-1.5 hover:bg-gray-100 rounded"
                    title="Refresh"
                  >
                    <RefreshCw className="w-4 h-4 text-gray-400" />
                  </button>
                  <button
                    onClick={() => projectId && window.open(`${API_BASE}/api/pipeline/preview/${projectId}`, '_blank')}
                    className="p-1.5 hover:bg-gray-100 rounded"
                    title="Open in new tab"
                  >
                    <ExternalLink className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Preview Content */}
              <div className="flex-1 flex items-center justify-center p-4 bg-gray-100">
                <div
                  className={`bg-white rounded-lg shadow-xl overflow-hidden transition-all ${
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
                      title="Preview"
                      sandbox="allow-scripts allow-same-origin"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <div className="text-center">
                        <Eye className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                        <p className="text-sm">Generate a project to see the preview</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Terminal */}
        {terminalOpen && (
          <div className="h-36 bg-[#1e1e1e] border-t border-[#333]">
            <div className="h-7 bg-[#252525] flex items-center justify-between px-3 border-b border-[#333]">
              <span className="text-xs text-gray-400">Terminal</span>
              <button onClick={() => setTerminalOpen(false)} className="p-0.5 hover:bg-[#333] rounded">
                <X className="w-3 h-3 text-gray-500" />
              </button>
            </div>
            <div className="p-3 font-mono text-xs text-gray-300 overflow-y-auto h-[calc(100%-28px)]">
              {terminalLogs.map((line, i) => (
                <div key={i} className={line.includes('✓') ? 'text-green-400' : line.includes('Error') ? 'text-red-400' : ''}>
                  {line}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Bottom Bar */}
        <div className="h-6 bg-[#111] border-t border-[#222] flex items-center justify-between px-3 text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setTerminalOpen(!terminalOpen)}
              className={`flex items-center gap-1.5 hover:text-gray-300 transition-colors ${terminalOpen ? 'text-cyan-400' : ''}`}
            >
              <Terminal className="w-3.5 h-3.5" />
              Terminal
            </button>
            <span>Mode: {agentMode.toUpperCase()}</span>
          </div>
          <div className="flex items-center gap-4">
            <span>{hasFiles ? `${Object.keys(files).length} files` : 'No files'}</span>
            <span>UTF-8</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuilderPage;
