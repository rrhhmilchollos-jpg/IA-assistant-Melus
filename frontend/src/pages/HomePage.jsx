import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Send,
  Zap,
  Clock,
  LogOut,
  Shield,
  Loader2,
  Paperclip,
  Mic,
  MicOff,
  X,
  Plus,
  ChevronLeft,
  Menu,
  Settings,
  FolderOpen,
  Sparkles,
  ArrowRight,
  Bot
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import CreditModal from '../components/CreditModal';
import { Toaster, toast } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Agent modes
const AGENT_MODES = [
  { id: 'e1', name: 'E1', description: 'Standard agent' },
  { id: 'e1.5', name: 'E1.5', description: 'Enhanced agent' },
  { id: 'e2', name: 'E2', description: 'Advanced multi-agent' },
];

const HomePage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recentProjects, setRecentProjects] = useState([]);
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [agentMode, setAgentMode] = useState('e1');
  const [isRecording, setIsRecording] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);
  
  // Pipeline state
  const [currentProject, setCurrentProject] = useState(null);
  const [projectStatus, setProjectStatus] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Refs
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    loadRecentProjects();
    
    // Cleanup polling on unmount
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [prompt]);

  const loadRecentProjects = async () => {
    const token = localStorage.getItem('session_token');
    try {
      // Load from new pipeline API
      const response = await fetch(`${API_BASE}/api/pipeline/projects`, {
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        const data = await response.json();
        setRecentProjects(data || []);
      }
    } catch (error) {
      console.error('Failed to load recent projects:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Poll for project status
  const pollProjectStatus = (projectId) => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
    
    pollIntervalRef.current = setInterval(async () => {
      const token = localStorage.getItem('session_token');
      try {
        const response = await fetch(`${API_BASE}/api/pipeline/projects/${projectId}/status`, {
          headers: { 'X-Session-Token': token }
        });
        if (response.ok) {
          const status = await response.json();
          setProjectStatus(status);
          
          // Stop polling when complete or failed
          if (status.phase === 'completed' || status.phase === 'failed') {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
            setIsGenerating(false);
            loadRecentProjects();
            
            if (status.phase === 'completed') {
              toast.success('Project generated successfully!');
              // Navigate to workspace with project
              navigate(`/workspace?project=${projectId}`);
            } else {
              toast.error('Project generation failed');
            }
          }
        }
      } catch (error) {
        console.error('Status poll error:', error);
      }
    }, 2000); // Poll every 2 seconds
  };

  const handleSubmit = async () => {
    if (!prompt.trim() || isLoading || isGenerating) return;
    
    setIsLoading(true);
    setIsGenerating(true);
    setProjectStatus({ phase: 'planning', status: 'Starting...' });
    
    const token = localStorage.getItem('session_token');
    
    try {
      // Create project via pipeline API
      const response = await fetch(`${API_BASE}/api/pipeline/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          prompt: prompt,
          mode: agentMode
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentProject(data.project_id);
        toast.info('Building your project...');
        
        // Start polling for status
        pollProjectStatus(data.project_id);
      } else {
        throw new Error('Failed to create project');
      }
    } catch (error) {
      console.error('Submit error:', error);
      toast.error('Failed to start project generation');
      setIsGenerating(false);
      setProjectStatus(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // File attachment
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      setAttachedFiles(prev => [...prev, ...files]);
      toast.success(`${files.length} file(s) attached`);
    }
  };

  const removeFile = (index) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast.info('Recording... Speak now');
    } catch (error) {
      toast.error('Could not access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      toast.info('Processing audio...');
    }
  };

  const transcribeAudio = async (audioBlob) => {
    const token = localStorage.getItem('session_token');
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await fetch(`${API_BASE}/api/voice/transcribe`, {
        method: 'POST',
        headers: { 'X-Session-Token': token },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        if (data.text) {
          setPrompt(prev => prev + (prev ? ' ' : '') + data.text);
          toast.success('Audio transcribed');
        }
      }
    } catch (error) {
      toast.error('Transcription error');
    }
  };

  const openProject = (project) => {
    navigate(`/workspace?project=${project.id}`);
  };

  const displayCredits = () => {
    if (user?.unlimited_credits || user?.is_owner) {
      return '∞';
    }
    return user?.credits || 0;
  };

  // Quick suggestions
  const suggestions = [
    'Build a todo app with React',
    'Create an e-commerce landing page',
    'Make a portfolio website',
    'Build a chat application'
  ];

  return (
    <div className="min-h-screen bg-[#f8f9fa] text-gray-800 flex">
      <Toaster />
      
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 flex flex-col overflow-hidden`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-100">
          <button
            onClick={() => {
              setPrompt('');
              setAttachedFiles([]);
            }}
            className="w-full flex items-center gap-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-gray-700"
            data-testid="new-chat-btn"
          >
            <Plus size={18} />
            <span className="font-medium">New Chat</span>
          </button>
          
          {/* Orchestrator Button */}
          <button
            onClick={() => navigate('/orchestrator')}
            className="w-full flex items-center gap-2 px-4 py-2.5 mt-2 bg-gradient-to-r from-cyan-50 to-blue-50 hover:from-cyan-100 hover:to-blue-100 border border-cyan-200 rounded-lg transition-colors text-cyan-700"
            data-testid="orchestrator-btn"
          >
            <Bot size={18} />
            <span className="font-medium">Orchestrator</span>
          </button>
        </div>
        
        {/* Projects List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            <div className="text-xs text-gray-400 uppercase px-3 py-2 font-medium">
              Recent Projects
            </div>
            
            {recentProjects.length === 0 ? (
              <div className="px-3 py-8 text-center text-gray-400 text-sm">
                No projects yet.<br/>Start by describing what you want to build.
              </div>
            ) : (
              <div className="space-y-1">
                {recentProjects.map((project) => (
                  <button
                    key={project.workspace_id}
                    onClick={() => openProject(project)}
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors group"
                    data-testid={`project-${project.workspace_id}`}
                  >
                    <div className="flex items-center gap-2">
                      <FolderOpen size={14} className="text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-600 truncate flex-1">
                        {project.name || project.prompt?.slice(0, 30) || 'Untitled'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5 pl-6">
                      {new Date(project.updated_at || project.created_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Sidebar Footer - User */}
        <div className="p-3 border-t border-gray-100">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                data-testid="user-menu-sidebar"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white font-bold text-sm">
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium text-gray-700 truncate">
                    {user?.name || 'User'}
                  </div>
                  <div className="text-xs text-gray-400 truncate">
                    {user?.email}
                  </div>
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56 bg-white border-gray-200 text-gray-700">
              <DropdownMenuItem onClick={() => setIsCreditModalOpen(true)} className="cursor-pointer">
                <Zap className="mr-2 h-4 w-4 text-yellow-500" />
                Credits: {displayCredits()}
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="mr-2 h-4 w-4 text-gray-400" />
                Settings
              </DropdownMenuItem>
              {user?.is_admin && (
                <DropdownMenuItem onClick={() => navigate('/admin')} className="cursor-pointer">
                  <Shield className="mr-2 h-4 w-4 text-orange-500" />
                  Admin Panel
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator className="bg-gray-100" />
              <DropdownMenuItem onClick={handleLogout} className="text-red-500 cursor-pointer">
                <LogOut className="mr-2 h-4 w-4" />
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            {/* Toggle Sidebar */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500"
              data-testid="toggle-sidebar"
            >
              {sidebarOpen ? <ChevronLeft size={20} /> : <Menu size={20} />}
            </button>
            
            {/* Logo */}
            <div className="flex items-center gap-2">
              <span className="text-xl font-light tracking-tight text-gray-800">
                melus<span className="font-normal">AI</span>
              </span>
            </div>
          </div>
          
          {/* Agent Mode Selector */}
          <div className="flex items-center gap-1 bg-gray-100 rounded-full p-1">
            {AGENT_MODES.map(mode => (
              <button
                key={mode.id}
                onClick={() => setAgentMode(mode.id)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                  agentMode === mode.id
                    ? 'bg-white text-gray-800 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                data-testid={`mode-${mode.id}`}
                title={mode.description}
              >
                {mode.name}
              </button>
            ))}
          </div>
          
          {/* Right side - Credits */}
          <button
            onClick={() => setIsCreditModalOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
            data-testid="credits-btn"
          >
            <Zap size={16} className="text-yellow-500" />
            <span className="text-sm font-medium text-gray-700">{displayCredits()}</span>
          </button>
        </header>
        
        {/* Chat Area */}
        <div className="flex-1 flex flex-col items-center justify-center px-4 py-8">
          {/* Welcome Message */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-100 to-blue-100 flex items-center justify-center">
              <Sparkles size={32} className="text-cyan-500" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-800 mb-2">
              What do you want to build?
            </h1>
            <p className="text-gray-500">
              Describe your app and let AI agents build it for you
            </p>
          </div>
          
          {/* Input Container */}
          <div className="w-full max-w-2xl">
            {/* Attached Files */}
            {attachedFiles.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {attachedFiles.map((file, index) => (
                  <div 
                    key={index} 
                    className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg text-sm"
                  >
                    <span className="text-gray-600 truncate max-w-[150px]">{file.name}</span>
                    <button 
                      onClick={() => removeFile(index)} 
                      className="text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {/* Main Input */}
            <div className="relative bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm focus-within:border-gray-300 focus-within:shadow-md transition-all">
              <textarea
                ref={textareaRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe what you want to build..."
                className="w-full bg-transparent text-gray-800 placeholder-gray-400 resize-none outline-none p-4 pr-28 min-h-[56px] max-h-[200px]"
                data-testid="main-input"
                rows={1}
              />
              
              {/* Input Actions */}
              <div className="absolute bottom-3 right-3 flex items-center gap-1">
                {/* File Attachment */}
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  multiple
                  className="hidden"
                  accept="image/*,.pdf,.doc,.docx,.txt"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  data-testid="attach-btn"
                  title="Attach files"
                >
                  <Paperclip size={18} />
                </button>
                
                {/* Voice Input */}
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`p-2 rounded-lg transition-colors ${
                    isRecording 
                      ? 'bg-red-100 text-red-500' 
                      : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                  }`}
                  data-testid="voice-btn"
                  title={isRecording ? 'Stop recording' : 'Voice input'}
                >
                  {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
                </button>
                
                {/* Submit */}
                <button
                  onClick={handleSubmit}
                  disabled={!prompt.trim() || isLoading}
                  className="p-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  data-testid="submit-btn"
                >
                  {isLoading ? (
                    <Loader2 size={18} className="animate-spin" />
                  ) : (
                    <ArrowRight size={18} />
                  )}
                </button>
              </div>
            </div>
            
            {/* Quick Suggestions */}
            <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(suggestion)}
                  className="px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 rounded-full text-sm text-gray-600 hover:text-gray-800 hover:border-gray-300 transition-all"
                  data-testid={`suggestion-${index}`}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <footer className="py-3 text-center text-xs text-gray-400">
          Powered by AI agents • <span className="text-gray-500 font-medium">{agentMode.toUpperCase()}</span> mode selected
        </footer>
      </main>
      
      {/* Credit Modal */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
    </div>
  );
};

export default HomePage;
