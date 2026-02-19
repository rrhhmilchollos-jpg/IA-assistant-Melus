import React, { useState, useEffect } from 'react';
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
  Loader2
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

const HomePage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recentTasks, setRecentTasks] = useState([]);
  const [activeTab, setActiveTab] = useState('recent');
  const [deployedApps, setDeployedApps] = useState([]);
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);

  // Suggestions - Simple ideas
  const suggestions = [
    { id: 'store', label: 'Tienda online', prompt: 'Crea una tienda online de ropa con carrito de compras' },
    { id: 'landing', label: 'Landing page', prompt: 'Crea una landing page para mi negocio de consultoría' },
    { id: 'dashboard', label: 'Dashboard', prompt: 'Crea un dashboard de administración con gráficos' },
    { id: 'blog', label: 'Blog', prompt: 'Crea un blog moderno con sistema de comentarios' },
    { id: 'portfolio', label: 'Portfolio', prompt: 'Crea un portfolio profesional para desarrollador' },
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
        setDeployedApps(data.apps || []);
      }
    } catch (error) {
      console.error('Failed to load deployed apps:', error);
    }
  };

  const handleSubmit = () => {
    if (!prompt.trim() || isLoading) return;
    
    // Navigate to workspace with the prompt directly without setting loading state
    // since we're navigating away immediately
    navigate(`/workspace?prompt=${encodeURIComponent(prompt)}`);
  };

  const handleSuggestionClick = (suggestion) => {
    setPrompt(suggestion.prompt);
  };

  const handleTaskClick = (task) => {
    navigate(`/workspace?workspace=${task.workspace_id}`);
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

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white relative" data-testid="home-page">
      <MatrixBackground />
      
      {/* Header */}
      <header className="relative z-10 border-b border-gray-800/50 bg-[#0a0a12]/80 backdrop-blur-sm">
        <div className="flex items-center justify-between h-14 px-4">
          {/* Left - Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Sparkles size={20} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Melus AI</h1>
              <p className="text-xs text-gray-500">Constructor Universal de Apps</p>
            </div>
          </div>

          {/* Right - Credits and User */}
          <div className="flex items-center gap-3">
            {/* Credits */}
            <button
              onClick={() => setIsCreditModalOpen(true)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full hover:opacity-80 transition-colors ${
                user?.unlimited_credits || user?.is_owner 
                  ? 'bg-gradient-to-r from-yellow-500/30 to-orange-500/30 border border-yellow-500/50' 
                  : 'bg-purple-500/20 border border-purple-500/30'
              }`}
              data-testid="credits-display"
            >
              <Zap size={14} className={user?.unlimited_credits ? 'text-yellow-400' : 'text-purple-400'} />
              <span className={`font-bold text-sm ${user?.unlimited_credits ? 'text-yellow-400' : 'text-purple-400'}`}>
                {user?.unlimited_credits || user?.is_owner 
                  ? '∞ ILIMITADO' 
                  : user?.credits?.toLocaleString() || 0}
              </span>
              {(user?.unlimited_credits || user?.is_owner) && (
                <span className="text-xs text-yellow-500">👑</span>
              )}
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
      <main className="relative z-10 max-w-3xl mx-auto px-4 pt-20 pb-8">
        {/* Main Title */}
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-4 text-white">
          ¿Qué quieres crear?
        </h1>
        <p className="text-center text-gray-400 mb-10">
          Describe tu idea y los agentes de IA la construirán automáticamente
        </p>

        {/* Input Box - Simple */}
        <div className="relative mb-8">
          <div className="bg-[#1a1a2e]/80 backdrop-blur-sm border border-gray-700/50 rounded-2xl p-4 focus-within:border-purple-500/50 transition-colors">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ejemplo: Crea una tienda online de productos artesanales..."
              className="w-full bg-transparent text-white placeholder-gray-500 resize-none outline-none text-lg min-h-[120px]"
              data-testid="main-prompt-input"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            
            {/* Send Button */}
            <div className="flex justify-end mt-4 pt-4 border-t border-gray-700/50">
              <button
                onClick={handleSubmit}
                disabled={!prompt.trim() || isLoading}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-medium hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                data-testid="submit-btn"
              >
                {isLoading ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    <span>Creando...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={20} />
                    <span>Crear App</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Suggestions */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
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
              Mis proyectos
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
              Desplegadas
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
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Proyecto</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Última vez</th>
                  <th className="px-4 py-3 text-right"></th>
                </tr>
              </thead>
              <tbody>
                {activeTab === 'recent' ? (
                  recentTasks.length > 0 ? (
                    recentTasks.map((task) => (
                      <tr 
                        key={task.workspace_id}
                        className="border-b border-gray-700/30 hover:bg-white/5 cursor-pointer transition-colors"
                        onClick={() => handleTaskClick(task)}
                        data-testid={`task-row-${task.workspace_id}`}
                      >
                        <td className="px-4 py-4">
                          <div className="text-white font-medium">{task.name}</div>
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
                      <td colSpan={3} className="px-4 py-12 text-center text-gray-500">
                        <Sparkles size={32} className="mx-auto mb-3 opacity-30" />
                        <p>No tienes proyectos aún</p>
                        <p className="text-sm mt-1">Describe tu idea arriba para comenzar</p>
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
                      <td colSpan={3} className="px-4 py-12 text-center text-gray-500">
                        <Rocket size={32} className="mx-auto mb-3 opacity-30" />
                        <p>No hay apps desplegadas</p>
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
