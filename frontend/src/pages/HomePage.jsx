import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Home,
  Send,
  Zap,
  Sparkles,
  Clock,
  Rocket,
  MoreHorizontal,
  User,
  LogOut,
  Receipt,
  Shield,
  Loader2,
  Store,
  Paperclip,
  Mic,
  MicOff,
  Settings,
  ChevronDown,
  ChevronUp,
  Brain,
  Cpu,
  Wand2,
  X,
  Check,
  Volume2
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

// Matrix background effect
const MatrixBackground = () => (
  <div className="absolute inset-0 overflow-hidden opacity-5 pointer-events-none">
    <div className="matrix-rain" style={{
      backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20'%3E%3Ctext x='0' y='15' fill='%2300ff00' font-family='monospace' font-size='12'%3E01%3C/text%3E%3C/svg%3E")`,
      backgroundRepeat: 'repeat',
      animation: 'matrix 20s linear infinite',
      width: '100%',
      height: '200%'
    }} />
  </div>
);

// AI Model options
const AI_MODELS = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', icon: '🤖', description: 'Modelo rápido y eficiente' },
  { id: 'claude-opus', name: 'Claude 4.5 Opus', provider: 'Anthropic', icon: '🧠', description: 'Máxima calidad y razonamiento' },
  { id: 'claude-sonnet', name: 'Claude 4.5 Sonnet', provider: 'Anthropic', icon: '✨', description: 'Balance entre velocidad y calidad' },
  { id: 'gemini-pro', name: 'Gemini 3 Pro', provider: 'Google', icon: '💎', description: 'Multimodal avanzado' },
];

// Agent modes
const AGENT_MODES = [
  { id: 'e1', name: 'E1', description: 'Estándar - Generación básica', cost: 1 },
  { id: 'e2', name: 'E2', description: 'Avanzado - Múltiples agentes', cost: 2 },
];

const HomePage = () => {
  const navigate = useNavigate();
  const { user, logout, updateCredits } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recentTasks, setRecentTasks] = useState([]);
  const [activeTab, setActiveTab] = useState('recent');
  const [deployedApps, setDeployedApps] = useState([]);
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
  
  // New state for controls
  const [selectedModel, setSelectedModel] = useState(AI_MODELS[0]);
  const [agentMode, setAgentMode] = useState('e1');
  const [ultraMode, setUltraMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  
  // Refs
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Suggestions - Simple ideas
  const suggestions = [
    { id: 'meltbot', label: 'MeltBot', prompt: 'Crea un chatbot inteligente con interfaz moderna' },
    { id: 'ideas', label: 'Registrador de ideas', prompt: 'Crea una app para guardar y organizar ideas con categorías' },
    { id: 'bakery', label: 'Delicias horneadas', prompt: 'Crea una tienda online de panadería con carrito' },
    { id: 'surprise', label: 'Sorpréndeme', prompt: 'Crea algo creativo e innovador que me sorprenda' },
  ];

  useEffect(() => {
    loadRecentTasks();
    loadDeployedApps();
  }, []);

  const loadRecentTasks = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/workspace/recent`, {
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        const data = await response.json();
        setRecentTasks(data.workspaces || []);
      }
    } catch (error) {
      console.error('Failed to load recent tasks:', error);
    }
  };

  const loadDeployedApps = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/workspace/deployed`, {
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        const data = await response.json();
        setDeployedApps(data.workspaces || []);
      }
    } catch (error) {
      console.error('Failed to load deployed apps:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSuggestionClick = (suggestion) => {
    setPrompt(suggestion.prompt);
  };

  const handleSubmit = () => {
    if (!prompt.trim() || isLoading) return;
    
    // Build query params with all settings
    const params = new URLSearchParams({
      prompt: prompt,
      model: selectedModel.id,
      mode: agentMode,
      ultra: ultraMode.toString()
    });
    
    navigate(`/workspace?${params.toString()}`);
  };

  // File attachment handler
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      setAttachedFiles(prev => [...prev, ...files]);
      toast.success(`${files.length} archivo(s) adjuntado(s)`);
    }
  };

  const removeFile = (index) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Voice recording handler
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
      toast.info('Grabando... Habla ahora');
    } catch (error) {
      console.error('Error accessing microphone:', error);
      toast.error('No se pudo acceder al micrófono');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      toast.info('Procesando audio...');
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
          toast.success('Audio transcrito');
        }
      } else {
        toast.error('Error al transcribir audio');
      }
    } catch (error) {
      console.error('Transcription error:', error);
      toast.error('Error de transcripción');
    }
  };

  // Credits display
  const displayCredits = () => {
    if (user?.unlimited_credits || user?.is_owner) {
      return '∞ ILIMITADO';
    }
    return user?.credits || 0;
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-white relative overflow-hidden">
      <MatrixBackground />
      <Toaster />
      
      {/* Header */}
      <header className="relative z-20 border-b border-gray-800/50 bg-[#0d1117]/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Sparkles size={18} className="text-white" />
            </div>
            <div>
              <span className="font-bold text-lg">Melus AI</span>
              <span className="text-xs text-gray-500 ml-2">Constructor Universal de Apps</span>
            </div>
          </div>
          
          {/* Right Side */}
          <div className="flex items-center gap-3">
            {/* Credits */}
            <button 
              onClick={() => setIsCreditModalOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-full text-sm"
            >
              <Zap size={14} className="text-yellow-400" />
              <span className="text-yellow-400 font-medium">{displayCredits()}</span>
            </button>
            
            {/* User Avatar */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button 
                  className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-sm hover:ring-2 hover:ring-purple-500/50 transition-all"
                  data-testid="user-menu"
                >
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 bg-[#1a1a2e] border-gray-700 text-gray-200">
                <div className="px-3 py-2 border-b border-gray-700">
                  <div className="font-medium">{user?.name || 'Usuario'}</div>
                  <div className="text-xs text-gray-400">{user?.email}</div>
                </div>
                <DropdownMenuItem onClick={() => setIsCreditModalOpen(true)} className="cursor-pointer">
                  <Zap className="mr-2 h-4 w-4 text-yellow-400" />
                  Créditos
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/marketplace')} className="cursor-pointer">
                  <Store className="mr-2 h-4 w-4 text-cyan-400" />
                  Marketplace
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer">
                  <Receipt className="mr-2 h-4 w-4" />
                  Historial
                </DropdownMenuItem>
                {user?.is_admin && (
                  <DropdownMenuItem onClick={() => navigate('/admin')} className="cursor-pointer">
                    <Shield className="mr-2 h-4 w-4 text-yellow-400" />
                    Admin
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator className="bg-gray-700" />
                <DropdownMenuItem onClick={handleLogout} className="text-red-400 cursor-pointer">
                  <LogOut className="mr-2 h-4 w-4" />
                  Cerrar Sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-4 pt-12 pb-8">
        {/* Agent Mode Selector - E1/E2 */}
        <div className="flex items-center justify-center gap-3 mb-8">
          {AGENT_MODES.map(mode => (
            <button
              key={mode.id}
              onClick={() => setAgentMode(mode.id)}
              data-testid={`agent-mode-${mode.id}`}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                agentMode === mode.id
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/30'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
              title={mode.description}
            >
              {mode.name}
              {mode.id === 'e2' && <span className="ml-1 text-xs opacity-70">Avanzado</span>}
            </button>
          ))}
          
          {/* Ultra Mode Toggle */}
          <button
            onClick={() => {
              setUltraMode(!ultraMode);
              toast.info(ultraMode ? 'Ultra Mode desactivado' : 'Ultra Mode activado - 2x créditos, máxima calidad');
            }}
            data-testid="ultra-mode-toggle"
            className={`px-4 py-2 rounded-full font-medium transition-all flex items-center gap-2 ${
              ultraMode
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/30'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <Zap size={16} className={ultraMode ? 'text-yellow-300' : ''} />
            Ultra
          </button>
        </div>

        {/* Main Title */}
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-4 text-white">
          ¿Qué quieres crear?
        </h1>
        <p className="text-center text-gray-400 mb-8">
          Describe tu idea y los agentes de IA la construirán automáticamente
        </p>

        {/* Input Box - Enhanced */}
        <div className="relative mb-6">
          <div className="bg-[#1a1a2e]/80 backdrop-blur-sm border border-gray-700/50 rounded-2xl overflow-hidden focus-within:border-purple-500/50 transition-colors">
            {/* Top toolbar */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700/30">
              {/* AI Model Selector */}
              <div className="relative">
                <button
                  onClick={() => setShowModelDropdown(!showModelDropdown)}
                  data-testid="model-selector-btn"
                  className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                >
                  <Brain size={16} className="text-purple-400" />
                  <span>{selectedModel.name}</span>
                  <ChevronDown size={14} className={`transition-transform ${showModelDropdown ? 'rotate-180' : ''}`} />
                </button>
                
                {showModelDropdown && (
                  <div className="absolute top-full left-0 mt-2 w-72 bg-[#1a1a2e] border border-gray-700 rounded-xl shadow-xl z-50 overflow-hidden">
                    {AI_MODELS.map(model => (
                      <button
                        key={model.id}
                        onClick={() => {
                          setSelectedModel(model);
                          setShowModelDropdown(false);
                          toast.success(`Modelo cambiado a ${model.name}`);
                        }}
                        className={`w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-800 transition-colors text-left ${
                          selectedModel.id === model.id ? 'bg-purple-500/20' : ''
                        }`}
                      >
                        <span className="text-2xl">{model.icon}</span>
                        <div className="flex-1">
                          <div className="font-medium text-white">{model.name}</div>
                          <div className="text-xs text-gray-400">{model.description}</div>
                        </div>
                        {selectedModel.id === model.id && (
                          <Check size={16} className="text-purple-400" />
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Settings button */}
              <button
                onClick={() => {
                  setShowSettings(!showSettings);
                  toast.info(showSettings ? 'Configuración cerrada' : 'Configuración abierta');
                }}
                data-testid="settings-btn"
                className={`p-2 rounded-lg transition-colors ${
                  showSettings ? 'bg-purple-500/20 text-purple-400' : 'hover:bg-gray-800 text-gray-400'
                }`}
              >
                <Settings size={18} />
              </button>
            </div>
            
            {/* Settings Panel */}
            {showSettings && (
              <div className="px-4 py-3 bg-gray-800/50 border-b border-gray-700/30">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <label className="text-gray-400 block mb-1">Temperatura</label>
                    <input type="range" min="0" max="100" defaultValue="70" className="w-full" />
                  </div>
                  <div>
                    <label className="text-gray-400 block mb-1">Max Tokens</label>
                    <input type="number" defaultValue="4096" className="w-full bg-gray-700 rounded px-2 py-1 text-white" />
                  </div>
                  <div className="col-span-2">
                    <label className="flex items-center gap-2 text-gray-400 cursor-pointer">
                      <input type="checkbox" className="rounded" defaultChecked />
                      <span>Incluir código de ejemplo</span>
                    </label>
                  </div>
                </div>
              </div>
            )}
            
            {/* Attached files preview */}
            {attachedFiles.length > 0 && (
              <div className="px-4 py-2 flex flex-wrap gap-2 border-b border-gray-700/30">
                {attachedFiles.map((file, index) => (
                  <div key={index} className="flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-full text-sm">
                    <span className="truncate max-w-[150px]">{file.name}</span>
                    <button onClick={() => removeFile(index)} className="text-gray-400 hover:text-red-400">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {/* Text input */}
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe lo que quieres crear..."
              className="w-full bg-transparent text-white placeholder-gray-500 resize-none outline-none text-lg p-4 min-h-[120px]"
              data-testid="main-prompt-input"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            
            {/* Bottom toolbar */}
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-700/30">
              {/* Left side - Attachment & Voice */}
              <div className="flex items-center gap-2">
                {/* File attachment */}
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
                  data-testid="file-attach-btn"
                  className="p-2 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
                  title="Adjuntar archivo"
                >
                  <Paperclip size={20} />
                </button>
                
                {/* Voice input */}
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  data-testid="mic-btn"
                  className={`p-2 rounded-lg transition-colors ${
                    isRecording 
                      ? 'bg-red-500/20 text-red-400 animate-pulse' 
                      : 'hover:bg-gray-800 text-gray-400 hover:text-white'
                  }`}
                  title={isRecording ? 'Detener grabación' : 'Grabar audio'}
                >
                  {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
                </button>
                
                {/* Expand/Collapse */}
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  data-testid="expand-collapse-btn"
                  className="p-2 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
                  title={isExpanded ? 'Colapsar' : 'Expandir'}
                >
                  {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>
              
              {/* Right side - Submit */}
              <button
                onClick={handleSubmit}
                disabled={!prompt.trim() || isLoading}
                className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-medium hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                data-testid="submit-btn"
              >
                {isLoading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    <span>Creando...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    <span>Crear App</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Quick Action - New button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={() => {
              setPrompt('');
              setAttachedFiles([]);
              toast.info('Nuevo proyecto');
            }}
            className="px-4 py-2 bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 rounded-full text-sm hover:bg-cyan-500/30 transition-colors flex items-center gap-2"
          >
            <Wand2 size={16} />
            Nuevo
          </button>
        </div>

        {/* Suggestions */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-10">
          {suggestions.map(suggestion => (
            <button
              key={suggestion.id}
              onClick={() => handleSuggestionClick(suggestion)}
              className="px-4 py-2 bg-[#1a1a2e]/60 border border-gray-700/50 rounded-full text-sm text-gray-300 hover:bg-purple-500/20 hover:border-purple-500/30 hover:text-white transition-all"
              data-testid={`suggestion-${suggestion.id}`}
            >
              {suggestion.label}
            </button>
          ))}
        </div>

        {/* Recent Projects Section */}
        {isExpanded && (
          <div className="bg-[#1a1a2e]/60 backdrop-blur-sm border border-gray-700/50 rounded-2xl overflow-hidden">
            {/* Tabs */}
            <div className="flex items-center gap-1 px-4 pt-4 border-b border-gray-700/50">
              <button
                onClick={() => setActiveTab('recent')}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative ${
                  activeTab === 'recent' ? 'text-white' : 'text-gray-400 hover:text-gray-300'
                }`}
                data-testid="tab-recent"
              >
                <Clock size={16} />
                Tareas recientes
                {activeTab === 'recent' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500" />
                )}
              </button>
              <span className="text-gray-600">|</span>
              <button
                onClick={() => setActiveTab('deployed')}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative ${
                  activeTab === 'deployed' ? 'text-white' : 'text-gray-400 hover:text-gray-300'
                }`}
                data-testid="tab-deployed"
              >
                <Rocket size={16} />
                Aplicaciones desplegadas
                {activeTab === 'deployed' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500" />
                )}
              </button>
            </div>
            
            {/* Content */}
            <div className="p-4">
              {activeTab === 'recent' ? (
                recentTasks.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Clock size={32} className="mx-auto mb-2 opacity-50" />
                    <p>No hay tareas recientes</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <table className="w-full">
                      <thead>
                        <tr className="text-left text-xs text-gray-500 uppercase">
                          <th className="pb-2 font-medium">Proyecto</th>
                          <th className="pb-2 font-medium text-right">Última vez</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentTasks.slice(0, 5).map((task) => (
                          <tr 
                            key={task.workspace_id}
                            onClick={() => navigate(`/workspace?workspace=${task.workspace_id}`)}
                            className="cursor-pointer hover:bg-gray-800/50 transition-colors"
                          >
                            <td className="py-2">
                              <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500" />
                                <span className="text-gray-200">{task.name || 'Sin nombre'}</span>
                              </div>
                            </td>
                            <td className="py-2 text-right text-sm text-gray-400">
                              {new Date(task.updated_at || task.created_at).toLocaleDateString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )
              ) : (
                deployedApps.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Rocket size={32} className="mx-auto mb-2 opacity-50" />
                    <p>No hay aplicaciones desplegadas</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {deployedApps.slice(0, 5).map((app) => (
                      <div 
                        key={app.workspace_id}
                        onClick={() => window.open(app.deploy_url, '_blank')}
                        className="flex items-center justify-between p-3 bg-gray-800/30 rounded-lg cursor-pointer hover:bg-gray-800/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded bg-green-500/20 flex items-center justify-center">
                            <Rocket size={16} className="text-green-400" />
                          </div>
                          <div>
                            <div className="text-gray-200">{app.name}</div>
                            <div className="text-xs text-gray-500">{app.deploy_url}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              )}
            </div>
          </div>
        )}
      </main>

      {/* Credit Modal */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
      
      {/* Click outside to close dropdowns */}
      {showModelDropdown && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowModelDropdown(false)}
        />
      )}
    </div>
  );
};

export default HomePage;
