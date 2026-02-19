import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Home,
  ChevronDown,
  Paperclip,
  Mic,
  Zap,
  Send,
  Settings,
  Sparkles,
  Clock,
  Rocket,
  MoreHorizontal,
  Plus,
  User,
  LogOut,
  Receipt,
  Shield
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import CreditModal from '../components/CreditModal';
import { Toaster } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Matrix background effect component
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

const HomePage = () => {
  const navigate = useNavigate();
  const { user, logout, updateCredits } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [selectedProject, setSelectedProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [ultraMode, setUltraMode] = useState(false);
  const [activeTab, setActiveTab] = useState('recent'); // 'recent' | 'deployed'
  const [recentTasks, setRecentTasks] = useState([]);
  const [deployedApps, setDeployedApps] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);

  const suggestions = [
    { id: 'meltbot', label: 'MeltBot', isNew: true, color: 'text-red-400' },
    { id: 'idea', label: 'Idea Logger', color: 'text-cyan-400' },
    { id: 'baking', label: 'Baking Bliss', color: 'text-yellow-400' },
    { id: 'surprise', label: 'Sorpréndeme', color: 'text-purple-400' }
  ];

  const models = [
    { id: 'gpt-4o', name: 'GPT-4o', icon: '🧠' },
    { id: 'claude-4.5-opus', name: 'Claude 4.5 Opus', icon: '🎭' },
    { id: 'claude-4.5-sonnet', name: 'Claude 4.5 Sonnet', icon: '🎵' },
    { id: 'gemini-3-pro', name: 'Gemini 3 Pro', icon: '💎' }
  ];

  useEffect(() => {
    loadProjects();
    loadRecentTasks();
    loadDeployedApps();
  }, []);

  const loadProjects = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/workspace/list`, {
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        const data = await response.json();
        setProjects(data.workspaces || []);
        if (data.workspaces?.length > 0 && !selectedProject) {
          setSelectedProject(data.workspaces[0]);
        }
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

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
      // Mock data for demo
      setRecentTasks([
        { workspace_id: 'EMT-8ac70B', name: 'protect-staging-1', description: 'Fork 1 de <analysis>**original_problem_statement**: The user wants to build a comprehensive, enterprise-grade,...', updated_at: new Date(Date.now() - 18*60*60*1000).toISOString() },
        { workspace_id: 'EMT-1c2aa2', name: 'mano-protect-preview', description: 'Fork 1 de <analysis>**original_problem_statement**: The user wants to build a...', updated_at: new Date(Date.now() - 18*60*60*1000).toISOString() }
      ]);
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
        setDeployedApps(data.apps || []);
      }
    } catch (error) {
      console.error('Failed to load deployed apps:', error);
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) return;
    
    setIsLoading(true);
    const token = localStorage.getItem('session_token');
    
    try {
      // Create new workspace and start generation
      const response = await fetch(`${API_BASE}/api/agents/v2/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          description: prompt,
          name: prompt.substring(0, 50),
          ultra_mode: ultraMode,
          model: selectedModel
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        updateCredits(data.credits_remaining);
        // Navigate to the workspace/generator view
        navigate(`/generator?workspace=${data.workspace_id}`);
      } else {
        throw new Error(data.detail || 'Error al generar');
      }
    } catch (error) {
      console.error('Generation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    if (suggestion.id === 'surprise') {
      const ideas = [
        'Construye una app de gestión de tareas con drag and drop',
        'Crea un dashboard de analytics con gráficos interactivos',
        'Genera un e-commerce de productos artesanales',
        'Desarrolla una plataforma de cursos online'
      ];
      setPrompt(ideas[Math.floor(Math.random() * ideas.length)]);
    } else {
      setPrompt(`Construyeme una app ${suggestion.label}`);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const formatTimeAgo = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
    if (diffHours < 1) return 'Hace menos de 1 hora';
    if (diffHours < 24) return `Hace ${diffHours} hrs`;
    const diffDays = Math.floor(diffHours / 24);
    return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;
  };

  const currentModel = models.find(m => m.id === selectedModel) || models[0];

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white relative" data-testid="home-page">
      <MatrixBackground />
      
      {/* Header */}
      <header className="relative z-10 border-b border-gray-800/50 bg-[#0a0a12]/80 backdrop-blur-sm">
        <div className="flex items-center justify-between h-14 px-4">
          {/* Left - Home */}
          <button 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 px-3 py-2 text-gray-300 hover:bg-white/5 rounded-lg transition-colors"
            data-testid="home-button"
          >
            <Home size={18} />
            <span className="text-sm font-medium">Home</span>
          </button>

          {/* Right - Credits and User */}
          <div className="flex items-center gap-3">
            {/* Credits */}
            <button
              onClick={() => setIsCreditModalOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-red-500/20 border border-red-500/30 rounded-full hover:bg-red-500/30 transition-colors"
              data-testid="credits-display"
            >
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-red-400 font-bold text-sm">
                {user?.credits?.toLocaleString() || 0}
              </span>
            </button>

            {/* Buy Credits */}
            <button
              onClick={() => setIsCreditModalOpen(true)}
              className="px-4 py-1.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full text-sm font-medium hover:from-purple-600 hover:to-pink-600 transition-all"
              data-testid="buy-credits-btn"
            >
              <Zap size={14} className="inline mr-1" />
              Comprar
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
                  {user?.is_admin && (
                    <span className="inline-block mt-1 px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded">Admin</span>
                  )}
                </div>
                <DropdownMenuItem onClick={() => setIsCreditModalOpen(true)} className="cursor-pointer">
                  <Zap className="mr-2 h-4 w-4 text-yellow-400" />
                  Comprar Créditos
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
      <main className="relative z-10 max-w-4xl mx-auto px-4 pt-16 pb-8">
        {/* Project Selector */}
        <div className="flex justify-center mb-6">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 border border-cyan-500/30 rounded-full text-cyan-400 hover:bg-cyan-500/30 transition-colors">
                <div className="w-2 h-2 bg-cyan-400 rounded-full" />
                <span className="text-sm font-medium">{selectedProject?.name || "Nuevo Proyecto"}</span>
                <ChevronDown size={16} />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 bg-[#1a1a2e] border-gray-700 text-gray-200">
              <DropdownMenuItem 
                onClick={() => setSelectedProject(null)}
                className="cursor-pointer"
              >
                <Plus className="mr-2 h-4 w-4 text-green-400" />
                Nuevo Proyecto
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-700" />
              {projects.map(project => (
                <DropdownMenuItem 
                  key={project.workspace_id}
                  onClick={() => setSelectedProject(project)}
                  className="cursor-pointer"
                >
                  <div className={`w-2 h-2 rounded-full mr-2 ${project.workspace_id === selectedProject?.workspace_id ? 'bg-cyan-400' : 'bg-gray-500'}`} />
                  {project.name}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Main Title */}
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-10 text-white">
          ¿Qué construirás hoy?
        </h1>

        {/* Input Box */}
        <div className="relative mb-6">
          <div className="bg-[#1a1a2e]/80 backdrop-blur-sm border border-gray-700/50 rounded-2xl p-4 focus-within:border-purple-500/50 transition-colors">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Construyeme una app SaaS..."
              className="w-full bg-transparent text-white placeholder-gray-500 resize-none outline-none text-lg min-h-[100px]"
              data-testid="main-prompt-input"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            
            {/* Input Controls */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-700/50">
              <div className="flex items-center gap-2">
                {/* Attachment */}
                <button 
                  className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                  data-testid="attach-btn"
                >
                  <Paperclip size={20} />
                </button>
                
                {/* Voice */}
                <button 
                  className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                  data-testid="voice-btn"
                >
                  <Mic size={20} />
                </button>

                {/* Tier Selector - E1 */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-500/20 text-cyan-400 rounded-full text-sm hover:bg-cyan-500/30 transition-colors">
                      <Zap size={14} />
                      <span>E1</span>
                      <ChevronDown size={14} />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#1a1a2e] border-gray-700">
                    <DropdownMenuItem className="text-cyan-400">
                      <Zap className="mr-2 h-4 w-4" />E1 - Standard
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-purple-400">
                      <Zap className="mr-2 h-4 w-4" />E2 - Advanced
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/* Ultra Toggle */}
                <button 
                  onClick={() => setUltraMode(!ultraMode)}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-sm transition-all ${
                    ultraMode 
                      ? 'bg-yellow-500/30 text-yellow-400 border border-yellow-500/50' 
                      : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700'
                  }`}
                  data-testid="ultra-toggle"
                >
                  <Sparkles size={14} />
                  <span>Ultra</span>
                  <div className={`w-8 h-4 rounded-full relative transition-colors ${ultraMode ? 'bg-yellow-500' : 'bg-gray-600'}`}>
                    <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${ultraMode ? 'left-4' : 'left-0.5'}`} />
                  </div>
                </button>

                {/* Model Selector */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/20 text-purple-400 rounded-full text-sm hover:bg-purple-500/30 transition-colors">
                      <span>{currentModel.icon}</span>
                      <span>{currentModel.name}</span>
                      <ChevronDown size={14} />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-[#1a1a2e] border-gray-700">
                    {models.map(model => (
                      <DropdownMenuItem 
                        key={model.id}
                        onClick={() => setSelectedModel(model.id)}
                        className={`cursor-pointer ${model.id === selectedModel ? 'text-purple-400' : 'text-gray-300'}`}
                      >
                        <span className="mr-2">{model.icon}</span>
                        {model.name}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                  <Settings size={20} />
                </button>
                <button className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                  <ChevronDown size={20} />
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!prompt.trim() || isLoading}
                  className="p-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl text-white hover:from-orange-600 hover:to-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  data-testid="submit-btn"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Send size={20} />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Suggestions */}
        <div className="flex items-center justify-center gap-3 mb-8">
          {suggestions.map(suggestion => (
            <button
              key={suggestion.id}
              onClick={() => handleSuggestionClick(suggestion)}
              className={`flex items-center gap-2 px-4 py-2 bg-[#1a1a2e]/60 border border-gray-700/50 rounded-full text-sm hover:bg-white/5 hover:border-gray-600 transition-all ${suggestion.color}`}
              data-testid={`suggestion-${suggestion.id}`}
            >
              {suggestion.isNew && (
                <span className="px-1.5 py-0.5 bg-red-500 text-white text-xs rounded">New</span>
              )}
              <Sparkles size={14} />
              <span>{suggestion.label}</span>
            </button>
          ))}
          <button className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
            <Settings size={18} />
          </button>
        </div>

        {/* Tasks Section */}
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
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500" />
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
              Apps desplegadas
              {activeTab === 'deployed' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500" />
              )}
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700/50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-cyan-400 uppercase">Tarea</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-yellow-400 uppercase">Última modificación</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase"></th>
                </tr>
              </thead>
              <tbody>
                {activeTab === 'recent' ? (
                  recentTasks.length > 0 ? (
                    recentTasks.map((task) => (
                      <tr 
                        key={task.workspace_id}
                        className="border-b border-gray-700/30 hover:bg-white/5 cursor-pointer transition-colors"
                        onClick={() => navigate(`/generator?workspace=${task.workspace_id}`)}
                        data-testid={`task-row-${task.workspace_id}`}
                      >
                        <td className="px-4 py-4 text-sm text-gray-400 font-mono">{task.workspace_id}</td>
                        <td className="px-4 py-4">
                          <div className="text-cyan-400 font-medium">{task.name}</div>
                          <div className="text-xs text-gray-500 mt-1 line-clamp-1">
                            {task.description}
                          </div>
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-400">
                          {formatTimeAgo(task.updated_at)}
                        </td>
                        <td className="px-4 py-4 text-right">
                          <button className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                            <MoreHorizontal size={18} />
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                        No hay tareas recientes
                      </td>
                    </tr>
                  )
                ) : (
                  deployedApps.length > 0 ? (
                    deployedApps.map((app) => (
                      <tr 
                        key={app.workspace_id}
                        className="border-b border-gray-700/30 hover:bg-white/5 cursor-pointer transition-colors"
                        onClick={() => window.open(app.url, '_blank')}
                      >
                        <td className="px-4 py-4 text-sm text-gray-400 font-mono">{app.workspace_id}</td>
                        <td className="px-4 py-4">
                          <div className="text-green-400 font-medium">{app.name}</div>
                          <div className="text-xs text-gray-500 mt-1">{app.url}</div>
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-400">
                          {formatTimeAgo(app.deployed_at)}
                        </td>
                        <td className="px-4 py-4 text-right">
                          <button className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                            <MoreHorizontal size={18} />
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                        No hay apps desplegadas
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Credit Modal */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
      <Toaster />
    </div>
  );
};

export default HomePage;
