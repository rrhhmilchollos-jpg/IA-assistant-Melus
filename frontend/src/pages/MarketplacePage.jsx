import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Search,
  Heart,
  Download,
  Star,
  Filter,
  Grid,
  List,
  Plus,
  ArrowLeft,
  Loader2,
  Layout,
  ShoppingCart,
  BarChart,
  User,
  FileText,
  Cloud,
  Smartphone,
  Gamepad,
  Tool,
  Box,
  X
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_ICONS = {
  landing: Layout,
  ecommerce: ShoppingCart,
  dashboard: BarChart,
  portfolio: User,
  blog: FileText,
  saas: Cloud,
  mobile: Smartphone,
  game: Gamepad,
  tool: Tool,
  other: Box
};

const MarketplacePage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [sortBy, setSortBy] = useState('popular');
  const [viewMode, setViewMode] = useState('grid');
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [userWorkspaces, setUserWorkspaces] = useState([]);
  const [publishLoading, setPublishLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  useEffect(() => {
    loadCategories();
    loadTemplates();
  }, [selectedCategory, sortBy]);

  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/marketplace/categories`);
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        sort: sortBy,
        ...(selectedCategory && { category: selectedCategory }),
        ...(searchQuery && { search: searchQuery })
      });
      
      const response = await fetch(`${API_BASE}/api/marketplace/templates?${params}`);
      const data = await response.json();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadTemplates();
  };

  const handleUseTemplate = async (templateId) => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/marketplace/templates/${templateId}/use`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        navigate(`/workspace?workspace=${data.workspace_id}`);
      } else {
        alert(data.detail || 'Error al usar template');
      }
    } catch (error) {
      console.error('Error using template:', error);
    }
  };

  const handleLikeTemplate = async (templateId) => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/marketplace/templates/${templateId}/like`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        loadTemplates();
      }
    } catch (error) {
      console.error('Error liking template:', error);
    }
  };

  const loadUserWorkspaces = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/workspace/recent`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await response.json();
      setUserWorkspaces(data.workspaces?.filter(w => Object.keys(w.files || {}).length > 0) || []);
    } catch (error) {
      console.error('Error loading workspaces:', error);
    }
  };

  const handlePublishTemplate = async (workspace, formData) => {
    const token = localStorage.getItem('session_token');
    setPublishLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/marketplace/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          workspace_id: workspace.workspace_id,
          name: formData.name,
          description: formData.description,
          category: formData.category,
          tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
          is_free: true
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setShowPublishModal(false);
        loadTemplates();
        alert('Template publicado exitosamente!');
      } else {
        alert(data.detail || 'Error al publicar');
      }
    } catch (error) {
      console.error('Error publishing:', error);
    } finally {
      setPublishLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-white">
      {/* Header */}
      <header className="border-b border-gray-800 sticky top-0 bg-[#0d1117]/95 backdrop-blur z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/home')} className="text-gray-400 hover:text-white">
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-xl font-bold">Marketplace</h1>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                loadUserWorkspaces();
                setShowPublishModal(true);
              }}
              className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center gap-2 hover:opacity-90"
            >
              <Plus size={18} />
              Publicar Template
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar templates..."
                className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none"
              />
            </div>
          </form>
          
          <div className="flex gap-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
            >
              <option value="popular">Más populares</option>
              <option value="newest">Más recientes</option>
              <option value="name">Por nombre</option>
            </select>
            
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="p-2 bg-gray-800 border border-gray-700 rounded-lg"
            >
              {viewMode === 'grid' ? <List size={20} /> : <Grid size={20} />}
            </button>
          </div>
        </div>

        {/* Categories */}
        <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-4 py-2 rounded-full whitespace-nowrap ${
              !selectedCategory 
                ? 'bg-cyan-500 text-white' 
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Todos
          </button>
          {categories.map((cat) => {
            const Icon = CATEGORY_ICONS[cat.id] || Box;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-4 py-2 rounded-full whitespace-nowrap flex items-center gap-2 ${
                  selectedCategory === cat.id 
                    ? 'bg-cyan-500 text-white' 
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <Icon size={16} />
                {cat.name}
              </button>
            );
          })}
        </div>

        {/* Templates Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={32} className="animate-spin text-cyan-500" />
          </div>
        ) : templates.length === 0 ? (
          <div className="text-center py-20">
            <Box size={48} className="mx-auto mb-4 text-gray-600" />
            <h3 className="text-xl font-medium text-gray-400">No hay templates</h3>
            <p className="text-gray-500 mt-2">Sé el primero en publicar un template</p>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
          }>
            {templates.map((template) => (
              <div
                key={template.template_id}
                className={`bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden hover:border-gray-600 transition-colors ${
                  viewMode === 'list' ? 'flex' : ''
                }`}
              >
                {/* Preview Image */}
                <div className={`bg-gradient-to-br from-purple-600/20 to-cyan-600/20 ${
                  viewMode === 'list' ? 'w-48 h-32' : 'h-40'
                } flex items-center justify-center`}>
                  {CATEGORY_ICONS[template.category] ? (
                    React.createElement(CATEGORY_ICONS[template.category], { size: 48, className: 'text-gray-500' })
                  ) : (
                    <Box size={48} className="text-gray-500" />
                  )}
                </div>
                
                {/* Content */}
                <div className="p-4 flex-1">
                  <h3 className="font-semibold text-lg mb-1">{template.name}</h3>
                  <p className="text-gray-400 text-sm line-clamp-2 mb-3">{template.description}</p>
                  
                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-3">
                    {template.tags?.slice(0, 3).map((tag, i) => (
                      <span key={i} className="px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-300">
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  {/* Stats */}
                  <div className="flex items-center gap-4 text-sm text-gray-400 mb-3">
                    <span className="flex items-center gap-1">
                      <Download size={14} />
                      {template.downloads || 0}
                    </span>
                    <span className="flex items-center gap-1">
                      <Heart size={14} />
                      {template.likes || 0}
                    </span>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleUseTemplate(template.template_id)}
                      className="flex-1 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg text-sm font-medium hover:opacity-90"
                    >
                      Usar Template
                    </button>
                    <button
                      onClick={() => handleLikeTemplate(template.template_id)}
                      className="p-2 bg-gray-700 rounded-lg hover:bg-gray-600"
                    >
                      <Heart size={18} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Publish Modal */}
      {showPublishModal && (
        <PublishModal
          workspaces={userWorkspaces}
          categories={categories}
          onClose={() => setShowPublishModal(false)}
          onPublish={handlePublishTemplate}
          loading={publishLoading}
        />
      )}
    </div>
  );
};

const PublishModal = ({ workspaces, categories, onClose, onPublish, loading }) => {
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'other',
    tags: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedWorkspace && formData.name) {
      onPublish(selectedWorkspace, formData);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-[#1a1f26] border border-gray-700 rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-white">Publicar Template</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {!selectedWorkspace ? (
          <div className="space-y-3">
            <p className="text-gray-400 mb-4">Selecciona un proyecto para publicar:</p>
            {workspaces.length === 0 ? (
              <p className="text-center py-8 text-gray-500">No tienes proyectos con código</p>
            ) : (
              workspaces.map((ws) => (
                <button
                  key={ws.workspace_id}
                  onClick={() => {
                    setSelectedWorkspace(ws);
                    setFormData(f => ({ ...f, name: ws.name }));
                  }}
                  className="w-full p-4 bg-gray-800 rounded-lg text-left hover:bg-gray-700"
                >
                  <p className="font-medium">{ws.name}</p>
                  <p className="text-sm text-gray-400">{Object.keys(ws.files || {}).length} archivos</p>
                </button>
              ))
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Nombre del Template</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Descripción</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none h-24 resize-none"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Categoría</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(f => ({ ...f, category: e.target.value }))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Tags (separados por coma)</label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData(f => ({ ...f, tags: e.target.value }))}
                placeholder="react, tailwind, landing"
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-cyan-500 outline-none"
              />
            </div>
            
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => setSelectedWorkspace(null)}
                className="flex-1 py-2 bg-gray-700 rounded-lg hover:bg-gray-600"
              >
                Atrás
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : 'Publicar'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default MarketplacePage;
