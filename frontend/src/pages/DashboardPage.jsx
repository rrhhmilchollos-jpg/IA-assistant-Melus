import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Plus,
  FolderOpen,
  Trash2,
  MoreHorizontal,
  Clock,
  Check,
  AlertCircle,
  Loader2,
  Search,
  Filter,
  Grid,
  List,
  Sparkles,
  ChevronLeft,
  ExternalLink,
  Download,
  Copy,
  Zap,
  Settings,
  LogOut,
  User,
  Code,
  Eye,
  Play
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

// Project Card Component
const ProjectCard = ({ project, onOpen, onDelete, viewMode }) => {
  const navigate = useNavigate();
  const [isDeleting, setIsDeleting] = useState(false);

  const getStatusColor = (status, phase) => {
    if (phase === 'completed') return 'bg-green-500';
    if (phase === 'error') return 'bg-red-500';
    if (status?.includes('Processing') || status?.includes('Generating')) return 'bg-blue-500';
    return 'bg-yellow-500';
  };

  const getStatusText = (status, phase) => {
    if (phase === 'completed') return 'Ready';
    if (phase === 'error') return 'Error';
    if (status?.includes('Processing')) return 'Building...';
    return phase || 'Draft';
  };

  const handleDelete = async (e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this project?')) return;
    
    setIsDeleting(true);
    try {
      const token = localStorage.getItem('session_token');
      await fetch(`${API_BASE}/api/pipeline/projects/${project.id}`, {
        method: 'DELETE',
        headers: { 'X-Session-Token': token }
      });
      onDelete(project.id);
      toast.success('Project deleted');
    } catch (error) {
      toast.error('Failed to delete project');
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  if (viewMode === 'list') {
    return (
      <div
        onClick={() => onOpen(project.id)}
        className="group flex items-center gap-4 p-4 bg-[#111] border border-[#222] rounded-xl hover:border-[#333] cursor-pointer transition-all"
      >
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center flex-shrink-0">
          <FolderOpen className="w-5 h-5 text-cyan-400" />
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-medium truncate">
            {project.plan?.project_name || project.prompt?.slice(0, 40) || 'Untitled Project'}
          </h3>
          <p className="text-xs text-gray-500 truncate">
            {project.prompt?.slice(0, 80)}...
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${getStatusColor(project.status, project.phase)}`} />
            <span className="text-xs text-gray-500">{getStatusText(project.status, project.phase)}</span>
          </div>
          
          <span className="text-xs text-gray-600">{project.files_count || 0} files</span>
          
          <span className="text-xs text-gray-600">{formatDate(project.created_at)}</span>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                onClick={(e) => e.stopPropagation()}
                className="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-[#222] rounded transition-all"
              >
                <MoreHorizontal className="w-4 h-4 text-gray-400" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-[#1e1e1e] border-[#333]">
              <DropdownMenuItem onClick={() => onOpen(project.id)} className="cursor-pointer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Open
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Download className="mr-2 h-4 w-4" />
                Download
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-[#333]" />
              <DropdownMenuItem onClick={handleDelete} className="cursor-pointer text-red-400">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    );
  }

  return (
    <div
      onClick={() => onOpen(project.id)}
      className="group relative bg-[#111] border border-[#222] rounded-xl overflow-hidden hover:border-[#333] cursor-pointer transition-all"
    >
      {/* Preview Thumbnail */}
      <div className="aspect-video bg-[#0a0a0a] flex items-center justify-center relative">
        {project.preview_url ? (
          <iframe
            src={project.preview_url}
            className="w-full h-full border-0 pointer-events-none"
            title="Preview"
          />
        ) : (
          <div className="flex flex-col items-center text-gray-600">
            <Code className="w-8 h-8 mb-2" />
            <span className="text-xs">No preview</span>
          </div>
        )}
        
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center gap-3 transition-opacity">
          <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
            <Eye className="w-5 h-5 text-white" />
          </button>
          <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
            <Code className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>
      
      {/* Info */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="text-white font-medium truncate flex-1">
            {project.plan?.project_name || project.prompt?.slice(0, 30) || 'Untitled'}
          </h3>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                onClick={(e) => e.stopPropagation()}
                className="p-1 hover:bg-[#222] rounded transition-colors"
              >
                <MoreHorizontal className="w-4 h-4 text-gray-400" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-[#1e1e1e] border-[#333]">
              <DropdownMenuItem onClick={() => onOpen(project.id)} className="cursor-pointer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Open
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Download className="mr-2 h-4 w-4" />
                Download
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-[#333]" />
              <DropdownMenuItem onClick={handleDelete} className="cursor-pointer text-red-400">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        <p className="text-xs text-gray-500 line-clamp-2 mb-3">
          {project.prompt?.slice(0, 80)}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${getStatusColor(project.status, project.phase)}`} />
            <span className="text-xs text-gray-500">{getStatusText(project.status, project.phase)}</span>
          </div>
          
          <span className="text-xs text-gray-600">{formatDate(project.created_at)}</span>
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Page
const DashboardPage = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [filter, setFilter] = useState('all');

  // Load projects
  useEffect(() => {
    if (isAuthenticated) {
      loadProjects();
    }
  }, [isAuthenticated]);

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
      setLoading(false);
    }
  };

  const handleOpenProject = (projectId) => {
    navigate(`/builder?project=${projectId}`);
  };

  const handleDeleteProject = (projectId) => {
    setProjects(prev => prev.filter(p => p.id !== projectId));
  };

  const handleCreateNew = () => {
    navigate('/builder');
  };

  // Filter projects
  const filteredProjects = projects.filter(p => {
    const matchesSearch = !searchQuery || 
      p.prompt?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.plan?.project_name?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = filter === 'all' ||
      (filter === 'completed' && p.phase === 'completed') ||
      (filter === 'building' && p.phase !== 'completed' && p.phase !== 'error') ||
      (filter === 'error' && p.phase === 'error');
    
    return matchesSearch && matchesFilter;
  });

  const displayCredits = () => {
    if (user?.unlimited_credits || user?.is_owner) return '∞';
    return user?.credits?.toFixed?.(1) || 0;
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Toaster />

      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-[#222]">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-semibold text-white">Melus AI</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Credits */}
            <button
              onClick={() => navigate('/pricing')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1a1a1a] hover:bg-[#222] rounded-lg transition-colors"
            >
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-white">{displayCredits()} credits</span>
            </button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 p-1.5 hover:bg-[#222] rounded-lg transition-colors">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white text-sm font-medium">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 bg-[#1e1e1e] border-[#333]">
                <div className="px-3 py-2 border-b border-[#333]">
                  <p className="text-sm font-medium text-white">{user?.name || 'User'}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <DropdownMenuItem onClick={() => navigate('/pricing')} className="cursor-pointer text-gray-300">
                  <Zap className="mr-2 h-4 w-4 text-yellow-400" />
                  Upgrade Plan
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer text-gray-300">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-[#333]" />
                <DropdownMenuItem
                  onClick={() => {
                    logout();
                    navigate('/');
                  }}
                  className="cursor-pointer text-red-400"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Your Projects</h1>
            <p className="text-gray-500">
              {projects.length} {projects.length === 1 ? 'project' : 'projects'}
            </p>
          </div>
          
          <button
            onClick={handleCreateNew}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Project
          </button>
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-64 pl-10 pr-4 py-2 bg-[#111] border border-[#222] rounded-lg text-white placeholder-gray-500 outline-none focus:border-[#333] transition-colors"
              />
            </div>
            
            {/* Filter */}
            <div className="flex items-center gap-1 bg-[#111] border border-[#222] rounded-lg p-0.5">
              {['all', 'completed', 'building', 'error'].map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 rounded-md text-sm capitalize transition-colors ${
                    filter === f
                      ? 'bg-[#222] text-white'
                      : 'text-gray-500 hover:text-gray-300'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
          
          {/* View Toggle */}
          <div className="flex items-center gap-1 bg-[#111] border border-[#222] rounded-lg p-0.5">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'grid' ? 'bg-[#222] text-white' : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'list' ? 'bg-[#222] text-white' : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Projects Grid/List */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 rounded-2xl bg-[#111] flex items-center justify-center mb-4">
              <FolderOpen className="w-8 h-8 text-gray-600" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">
              {searchQuery ? 'No projects found' : 'No projects yet'}
            </h3>
            <p className="text-gray-500 mb-6 max-w-md">
              {searchQuery
                ? 'Try adjusting your search or filters'
                : 'Start building something amazing with AI'}
            </p>
            {!searchQuery && (
              <button
                onClick={handleCreateNew}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create First Project
              </button>
            )}
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' 
            : 'flex flex-col gap-2'
          }>
            {filteredProjects.map(project => (
              <ProjectCard
                key={project.id}
                project={project}
                onOpen={handleOpenProject}
                onDelete={handleDeleteProject}
                viewMode={viewMode}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardPage;
