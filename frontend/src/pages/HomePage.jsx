import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Send,
  Zap,
  Clock,
  Rocket,
  LogOut,
  Shield,
  Loader2,
  Paperclip,
  Mic,
  MicOff,
  X,
  Plus,
  ChevronLeft,
  ChevronRight,
  Settings,
  User,
  CreditCard,
  FolderOpen,
  Trash2,
  ExternalLink,
  Menu
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

// Agent modes - E1 and E2 like Emergent
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
  
  // Refs
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    loadRecentProjects();
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
      const response = await fetch(`${API_BASE}/api/workspace/recent`, {
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        const data = await response.json();
        setRecentProjects(data.workspaces || []);
      }
    } catch (error) {
      console.error('Failed to load recent projects:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleSubmit = () => {
    if (!prompt.trim() || isLoading) return;
    
    const params = new URLSearchParams({
      prompt: prompt,
      mode: agentMode
    });
    
    navigate(`/workspace?${params.toString()}`);
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
    navigate(`/workspace?workspace=${project.workspace_id}`);
  };

  const displayCredits = () => {
    if (user?.unlimited_credits || user?.is_owner) {
      return '∞';
    }
    return user?.credits || 0;
  };

  return (
    <div className="min-h-screen bg-black text-white flex">
      <Toaster />
      
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 border-r border-gray-800 flex flex-col overflow-hidden`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-800">
          <button
            onClick={() => {
              setPrompt('');
              setAttachedFiles([]);
            }}
            className="w-full flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-lg transition-colors"
            data-testid="new-chat-btn"
          >
            <Plus size={18} />
            <span className="font-medium">New Chat</span>
          </button>
        </div>
        
        {/* Projects List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            <div className="text-xs text-gray-500 uppercase px-3 py-2 font-medium">
              Recent Projects
            </div>
            
            {recentProjects.length === 0 ? (
              <div className="px-3 py-8 text-center text-gray-600 text-sm">
                No projects yet.<br/>Start by describing what you want to build.
              </div>
            ) : (
              <div className="space-y-1">
                {recentProjects.map((project) => (
                  <button
                    key={project.workspace_id}
                    onClick={() => openProject(project)}
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-900 transition-colors group"
                    data-testid={`project-${project.workspace_id}`}
                  >
                    <div className="flex items-center gap-2">
                      <FolderOpen size={14} className="text-gray-500 flex-shrink-0" />
                      <span className="text-sm text-gray-300 truncate flex-1">
                        {project.name || project.prompt?.slice(0, 30) || 'Untitled'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600 mt-0.5 pl-6">
                      {new Date(project.updated_at || project.created_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Sidebar Footer - User */}
        <div className="p-3 border-t border-gray-800">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-900 transition-colors"
                data-testid="user-menu-sidebar"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white font-bold text-sm">
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium text-gray-200 truncate">
                    {user?.name || 'User'}
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    {user?.email}
                  </div>
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56 bg-gray-900 border-gray-700 text-gray-200">
              <DropdownMenuItem onClick={() => setIsCreditModalOpen(true)} className="cursor-pointer">
                <Zap className="mr-2 h-4 w-4 text-yellow-400" />
                Credits: {displayCredits()}
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              {user?.is_admin && (
                <DropdownMenuItem onClick={() => navigate('/admin')} className="cursor-pointer">
                  <Shield className="mr-2 h-4 w-4 text-yellow-400" />
                  Admin Panel
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator className="bg-gray-700" />
              <DropdownMenuItem onClick={handleLogout} className="text-red-400 cursor-pointer">
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
        <header className="h-14 border-b border-gray-800 flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            {/* Toggle Sidebar */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-900 rounded-lg transition-colors"
              data-testid="toggle-sidebar"
            >
              {sidebarOpen ? <ChevronLeft size={20} /> : <Menu size={20} />}
            </button>
            
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-black border border-gray-700 flex items-center justify-center">
                <span className="text-lg font-bold text-white">e</span>
              </div>
              <span className="font-semibold text-gray-200">Melus AI</span>
            </div>
          </div>
          
          {/* Agent Mode Selector */}
          <div className="flex items-center gap-1 bg-gray-900 rounded-lg p-1">
            {AGENT_MODES.map(mode => (
              <button
                key={mode.id}
                onClick={() => setAgentMode(mode.id)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                  agentMode === mode.id
                    ? 'bg-white text-black'
                    : 'text-gray-400 hover:text-white'
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
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-900 hover:bg-gray-800 rounded-lg transition-colors"
            data-testid="credits-btn"
          >
            <Zap size={16} className="text-yellow-400" />
            <span className="text-sm font-medium">{displayCredits()}</span>
          </button>
        </header>
        
        {/* Chat Area */}
        <div className="flex-1 flex flex-col items-center justify-center px-4 py-8">
          {/* Welcome Message */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-semibold text-white mb-2">
              What do you want to build?
            </h1>
            <p className="text-gray-500">
              Describe your app and let AI agents build it for you
            </p>
          </div>
          
          {/* Input Container */}
          <div className="w-full max-w-3xl">
            {/* Attached Files */}
            {attachedFiles.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {attachedFiles.map((file, index) => (
                  <div 
                    key={index} 
                    className="flex items-center gap-2 px-3 py-1.5 bg-gray-900 border border-gray-700 rounded-lg text-sm"
                  >
                    <span className="text-gray-300 truncate max-w-[150px]">{file.name}</span>
                    <button 
                      onClick={() => removeFile(index)} 
                      className="text-gray-500 hover:text-red-400 transition-colors"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {/* Main Input */}
            <div className="relative bg-gray-900 border border-gray-700 rounded-2xl overflow-hidden focus-within:border-gray-600 transition-colors">
              <textarea
                ref={textareaRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe what you want to build..."
                className="w-full bg-transparent text-white placeholder-gray-500 resize-none outline-none p-4 pr-24 min-h-[56px] max-h-[200px]"
                data-testid="main-input"
                rows={1}
              />
              
              {/* Input Actions */}
              <div className="absolute bottom-3 right-3 flex items-center gap-2">
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
                  className="p-2 text-gray-500 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
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
                      ? 'bg-red-500/20 text-red-400' 
                      : 'text-gray-500 hover:text-white hover:bg-gray-800'
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
                  className="p-2 bg-white text-black rounded-lg hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  data-testid="submit-btn"
                >
                  {isLoading ? (
                    <Loader2 size={18} className="animate-spin" />
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </div>
            </div>
            
            {/* Quick Suggestions */}
            <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
              {[
                'Build a todo app',
                'Create an e-commerce site',
                'Make a portfolio website',
                'Build a chat application'
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(suggestion)}
                  className="px-4 py-2 bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-gray-700 rounded-full text-sm text-gray-400 hover:text-white transition-all"
                  data-testid={`suggestion-${index}`}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <footer className="py-3 text-center text-xs text-gray-600">
          Powered by AI agents • <span className="text-gray-500">{agentMode.toUpperCase()}</span> mode selected
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
