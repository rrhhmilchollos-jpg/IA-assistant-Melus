import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Search,
  Heart,
  Download,
  ArrowLeft,
  Loader2,
  Layout,
  ShoppingCart,
  BarChart3,
  User,
  FileText,
  Cloud,
  Smartphone,
  Gamepad2,
  Wrench,
  Box,
  X,
  Plus,
  ExternalLink,
  Sparkles,
  Zap,
  Code2,
  Shield,
  Eye,
  MessageSquare,
  Bot,
  Palette,
  Database,
  Globe,
  Cpu,
  Briefcase,
  Star,
  ChevronRight,
  Check,
  Lock
} from 'lucide-react';
import { Toaster, toast } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Native agents and services - similar to Vercel marketplace
const NATIVE_AGENTS = [
  {
    id: 'game',
    name: 'Game Developer',
    category: 'development',
    description: 'Crea juegos completos con canvas, física y loops de juego',
    icon: Gamepad2,
    cost: 200,
    capabilities: ['Canvas', 'Física', 'Animaciones', 'Sprites'],
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'mobile',
    name: 'Mobile App',
    category: 'development',
    description: 'Aplicaciones móviles PWA con diseño responsive y touch',
    icon: Smartphone,
    cost: 250,
    capabilities: ['PWA', 'Responsive', 'Touch', 'Offline'],
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'ecommerce',
    name: 'E-commerce',
    category: 'development',
    description: 'Tiendas online con carrito, productos y checkout',
    icon: ShoppingCart,
    cost: 300,
    capabilities: ['Carrito', 'Productos', 'Checkout', 'Inventario'],
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'dashboard',
    name: 'Dashboard Admin',
    category: 'development',
    description: 'Paneles de administración con gráficos y métricas',
    icon: BarChart3,
    cost: 250,
    capabilities: ['Gráficos', 'Tablas', 'Analytics', 'Dark Mode'],
    color: 'from-orange-500 to-amber-500'
  },
  {
    id: 'saas',
    name: 'SaaS App',
    category: 'development',
    description: 'Aplicaciones SaaS con auth, suscripciones y más',
    icon: Cloud,
    cost: 350,
    capabilities: ['Auth', 'Suscripciones', 'API', 'Multi-tenant'],
    color: 'from-indigo-500 to-purple-500'
  },
  {
    id: 'ai_app',
    name: 'AI Application',
    category: 'ai',
    description: 'Apps con integración de LLM y chatbots inteligentes',
    icon: Bot,
    cost: 300,
    capabilities: ['Chat LLM', 'Embeddings', 'Prompts', 'Streaming'],
    color: 'from-cyan-500 to-blue-500'
  },
  {
    id: 'portfolio',
    name: 'Portfolio Creator',
    category: 'development',
    description: 'Portfolios personales con animaciones y galerías',
    icon: User,
    cost: 150,
    capabilities: ['Animaciones', 'Galería', 'Contacto', 'SEO'],
    color: 'from-pink-500 to-rose-500'
  },
  {
    id: 'api',
    name: 'API Builder',
    category: 'backend',
    description: 'Diseño y documentación de APIs RESTful',
    icon: Code2,
    cost: 200,
    capabilities: ['REST', 'GraphQL', 'Swagger', 'Auth JWT'],
    color: 'from-slate-500 to-gray-500'
  }
];

// Service categories
const SERVICE_CATEGORIES = [
  { id: 'all', name: 'Todos', icon: Globe },
  { id: 'development', name: 'Desarrollo', icon: Code2 },
  { id: 'ai', name: 'IA & ML', icon: Bot },
  { id: 'backend', name: 'Backend', icon: Database },
  { id: 'design', name: 'Diseño', icon: Palette },
  { id: 'security', name: 'Seguridad', icon: Shield },
];

// Featured/upcoming services
const COMING_SOON_SERVICES = [
  { name: 'Code Review AI', description: 'Revisión automática de código', icon: Eye },
  { name: 'Security Scanner', description: 'Análisis de vulnerabilidades', icon: Shield },
  { name: 'Auto Testing', description: 'Tests E2E automatizados', icon: Check },
  { name: 'DB Designer', description: 'Diseño visual de bases de datos', icon: Database },
];

const MarketplacePage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('agents'); // 'agents' | 'templates'
  const [showAgentModal, setShowAgentModal] = useState(null);
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [userWorkspaces, setUserWorkspaces] = useState([]);

  // Only admin/owner can access marketplace
  useEffect(() => {
    if (user && !user.is_admin && !user.is_owner) {
      toast.error('Acceso restringido - Solo administradores');
      navigate('/home');
    }
  }, [user, navigate]);

  useEffect(() => {
    if (activeTab === 'templates') {
      loadTemplates();
    }
  }, [activeTab, searchQuery]);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        sort: 'popular',
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

  const filteredAgents = NATIVE_AGENTS.filter(agent => {
    const matchesSearch = !searchQuery || 
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || agent.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleUseAgent = (agent) => {
    // Navigate to home with pre-filled prompt
    const prompt = `Crea una aplicación de tipo ${agent.name}: `;
    navigate(`/home?agent=${agent.id}&prompt=${encodeURIComponent(prompt)}`);
    toast.success(`Agente ${agent.name} seleccionado`);
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
        toast.success('Template aplicado');
        navigate(`/workspace?workspace=${data.workspace_id}`);
      } else {
        toast.error(data.detail || 'Error al usar template');
      }
    } catch (error) {
      toast.error('Error de conexión');
    }
  };

  const handlePurchaseTemplate = async (template) => {
    const token = localStorage.getItem('session_token');
    
    // Confirm purchase
    if (!window.confirm(`¿Comprar "${template.name}" por ${template.price} créditos?`)) {
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE}/api/marketplace/templates/${template.template_id}/purchase`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        if (data.already_purchased) {
          toast.info(data.message);
        } else {
          toast.success(`¡Template comprado! Te quedan ${data.credits_remaining?.toFixed(2)} créditos`);
        }
        // Now use the template
        handleUseTemplate(template.template_id);
      } else {
        toast.error(data.detail || 'Error al comprar template');
      }
    } catch (error) {
      toast.error('Error de conexión');
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

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <Toaster />
      
      {/* Header */}
      <header className="border-b border-gray-800/50 sticky top-0 bg-[#0a0a0a]/95 backdrop-blur-xl z-20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/home')} 
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              data-testid="back-btn"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-xl font-semibold">Marketplace</h1>
              <p className="text-sm text-gray-500">Agentes y servicios nativos</p>
            </div>
          </div>
          
          <button
            onClick={() => {
              loadUserWorkspaces();
              setShowPublishModal(true);
            }}
            className="px-4 py-2 bg-white text-black rounded-lg font-medium hover:bg-gray-100 transition-colors flex items-center gap-2"
            data-testid="publish-template-btn"
          >
            <Plus size={18} />
            Publicar Template
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Intro Section */}
        <div className="mb-10">
          <h2 className="text-3xl font-bold mb-3">Agentes y Servicios Nativos</h2>
          <p className="text-gray-400 max-w-2xl">
            Una colección de agentes especializados que puedes agregar fácilmente a tu proyecto. 
            Cada agente está optimizado para un tipo específico de aplicación.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-8 border-b border-gray-800">
          <button
            onClick={() => setActiveTab('agents')}
            className={`px-4 py-3 font-medium transition-colors relative ${
              activeTab === 'agents' ? 'text-white' : 'text-gray-500 hover:text-gray-300'
            }`}
            data-testid="tab-agents"
          >
            Agentes Especializados
            {activeTab === 'agents' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-white" />
            )}
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-4 py-3 font-medium transition-colors relative ${
              activeTab === 'templates' ? 'text-white' : 'text-gray-500 hover:text-gray-300'
            }`}
            data-testid="tab-templates"
          >
            Templates de la Comunidad
            {activeTab === 'templates' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-white" />
            )}
          </button>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative max-w-md">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Buscar agentes y servicios..."
              className="w-full pl-11 pr-4 py-3 bg-[#111] border border-gray-800 rounded-xl focus:border-gray-600 focus:ring-0 outline-none placeholder-gray-600"
              data-testid="search-input"
            />
          </div>
        </div>

        {activeTab === 'agents' ? (
          <>
            {/* Category Filter */}
            <div className="flex gap-2 overflow-x-auto pb-4 mb-8 scrollbar-hide">
              {SERVICE_CATEGORIES.map((cat) => {
                const Icon = cat.icon;
                return (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`px-4 py-2 rounded-full whitespace-nowrap flex items-center gap-2 transition-all ${
                      selectedCategory === cat.id 
                        ? 'bg-white text-black font-medium' 
                        : 'bg-[#111] text-gray-400 hover:bg-gray-800 border border-gray-800'
                    }`}
                    data-testid={`category-${cat.id}`}
                  >
                    <Icon size={16} />
                    {cat.name}
                  </button>
                );
              })}
            </div>

            {/* Agents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-12">
              {filteredAgents.map((agent) => {
                const Icon = agent.icon;
                return (
                  <div
                    key={agent.id}
                    className="bg-[#111] border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-700 transition-all group"
                    data-testid={`agent-card-${agent.id}`}
                  >
                    {/* Gradient Header */}
                    <div className={`h-2 bg-gradient-to-r ${agent.color}`} />
                    
                    <div className="p-5">
                      {/* Icon & Name */}
                      <div className="flex items-start gap-4 mb-4">
                        <div className={`p-3 rounded-xl bg-gradient-to-br ${agent.color} bg-opacity-10`}>
                          <Icon size={24} className="text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-white mb-1">{agent.name}</h3>
                          <span className="text-xs text-gray-500 uppercase tracking-wider">
                            {agent.category}
                          </span>
                        </div>
                      </div>
                      
                      {/* Description */}
                      <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                        {agent.description}
                      </p>
                      
                      {/* Capabilities */}
                      <div className="flex flex-wrap gap-1.5 mb-4">
                        {agent.capabilities.slice(0, 3).map((cap, i) => (
                          <span 
                            key={i} 
                            className="px-2 py-0.5 bg-gray-800/50 rounded text-xs text-gray-400"
                          >
                            {cap}
                          </span>
                        ))}
                      </div>
                      
                      {/* Footer */}
                      <div className="flex items-center justify-between pt-3 border-t border-gray-800/50">
                        <div className="flex items-center gap-1 text-yellow-500">
                          <Zap size={14} />
                          <span className="text-sm font-medium">{agent.cost}</span>
                          <span className="text-xs text-gray-500">créditos</span>
                        </div>
                        <button
                          onClick={() => handleUseAgent(agent)}
                          className="px-4 py-1.5 bg-white text-black rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors flex items-center gap-1.5"
                          data-testid={`use-agent-${agent.id}`}
                        >
                          Usar
                          <ChevronRight size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Coming Soon Section */}
            <div className="mb-12">
              <div className="flex items-center gap-2 mb-6">
                <Sparkles size={20} className="text-purple-400" />
                <h3 className="text-lg font-semibold">Próximamente</h3>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {COMING_SOON_SERVICES.map((service, i) => {
                  const Icon = service.icon;
                  return (
                    <div 
                      key={i}
                      className="p-4 bg-[#111] border border-gray-800 border-dashed rounded-xl opacity-60"
                    >
                      <Icon size={24} className="text-gray-500 mb-3" />
                      <h4 className="font-medium text-gray-400 mb-1">{service.name}</h4>
                      <p className="text-xs text-gray-600">{service.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Request Agent */}
            <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-2xl p-6 flex items-center justify-between">
              <div>
                <h3 className="font-semibold mb-1">¿No encuentras el agente que necesitas?</h3>
                <p className="text-sm text-gray-400">Solicita una integración y la evaluaremos.</p>
              </div>
              <button className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition-colors">
                Solicitar Agente
              </button>
            </div>
          </>
        ) : (
          /* Templates Tab */
          <div>
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 size={32} className="animate-spin text-gray-500" />
              </div>
            ) : templates.length === 0 ? (
              <div className="text-center py-20">
                <Box size={48} className="mx-auto mb-4 text-gray-700" />
                <h3 className="text-xl font-medium text-gray-400 mb-2">No hay templates</h3>
                <p className="text-gray-600 mb-6">Sé el primero en publicar un template</p>
                <button
                  onClick={() => {
                    loadUserWorkspaces();
                    setShowPublishModal(true);
                  }}
                  className="px-6 py-2.5 bg-white text-black rounded-lg font-medium"
                >
                  Publicar Template
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {templates.map((template) => (
                  <div
                    key={template.template_id}
                    className="bg-[#111] border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-700 transition-colors"
                    data-testid={`template-card-${template.template_id}`}
                  >
                    {/* Preview */}
                    <div className="h-40 bg-gradient-to-br from-purple-600/20 to-cyan-600/20 flex items-center justify-center relative">
                      <Layout size={48} className="text-gray-600" />
                      {/* Price badge */}
                      {!template.is_free && template.price > 0 && (
                        <div className="absolute top-3 right-3 px-2 py-1 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full text-xs font-bold text-black">
                          {template.price} créditos
                        </div>
                      )}
                      {template.is_free && (
                        <div className="absolute top-3 right-3 px-2 py-1 bg-green-500/20 border border-green-500/40 rounded-full text-xs font-medium text-green-400">
                          Gratis
                        </div>
                      )}
                    </div>
                    
                    {/* Content */}
                    <div className="p-5">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold">{template.name}</h3>
                        <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">
                          {template.category}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 line-clamp-2 mb-4">{template.description}</p>
                      
                      {/* Stats */}
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                        <span className="flex items-center gap-1">
                          <Download size={14} />
                          {template.downloads || 0}
                        </span>
                        <span className="flex items-center gap-1">
                          <Heart size={14} />
                          {template.likes || 0}
                        </span>
                        {template.purchases > 0 && (
                          <span className="flex items-center gap-1 text-amber-500">
                            <Star size={14} />
                            {template.purchases} ventas
                          </span>
                        )}
                      </div>
                      
                      {template.is_free ? (
                        <button
                          onClick={() => handleUseTemplate(template.template_id)}
                          className="w-full py-2.5 bg-white text-black rounded-lg font-medium hover:bg-gray-100 transition-colors"
                          data-testid={`use-template-${template.template_id}`}
                        >
                          Usar Template
                        </button>
                      ) : (
                        <button
                          onClick={() => handlePurchaseTemplate(template)}
                          className="w-full py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-black rounded-lg font-medium hover:from-amber-600 hover:to-orange-600 transition-colors flex items-center justify-center gap-2"
                          data-testid={`buy-template-${template.template_id}`}
                        >
                          <Zap size={16} />
                          Comprar por {template.price} créditos
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Publish Modal */}
      {showPublishModal && (
        <PublishTemplateModal
          workspaces={userWorkspaces}
          onClose={() => setShowPublishModal(false)}
          onSuccess={() => {
            setShowPublishModal(false);
            setActiveTab('templates');
            loadTemplates();
            toast.success('Template publicado exitosamente');
          }}
        />
      )}
    </div>
  );
};

// Publish Template Modal Component
const PublishTemplateModal = ({ workspaces, onClose, onSuccess }) => {
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'other',
    tags: '',
    is_free: true,
    price: 50
  });

  const categories = [
    { id: 'landing', name: 'Landing Pages' },
    { id: 'ecommerce', name: 'E-commerce' },
    { id: 'dashboard', name: 'Dashboards' },
    { id: 'portfolio', name: 'Portfolios' },
    { id: 'blog', name: 'Blogs' },
    { id: 'saas', name: 'SaaS Apps' },
    { id: 'tool', name: 'Herramientas' },
    { id: 'other', name: 'Otro' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedWorkspace || !formData.name) return;
    
    setLoading(true);
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/marketplace/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          workspace_id: selectedWorkspace.workspace_id,
          name: formData.name,
          description: formData.description,
          category: formData.category,
          tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
          is_free: formData.is_free,
          price: formData.is_free ? 0 : formData.price
        })
      });
      
      if (response.ok) {
        onSuccess();
      } else {
        const data = await response.json();
        toast.error(data.detail || 'Error al publicar');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#0f0f0f] border border-gray-800 rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-800">
          <h3 className="text-xl font-semibold">Publicar Template</h3>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="p-6">
          {!selectedWorkspace ? (
            <div className="space-y-3">
              <p className="text-gray-400 mb-4">Selecciona un proyecto para publicar:</p>
              {workspaces.length === 0 ? (
                <div className="text-center py-12">
                  <Box size={40} className="mx-auto mb-3 text-gray-700" />
                  <p className="text-gray-500">No tienes proyectos con código</p>
                </div>
              ) : (
                workspaces.map((ws) => (
                  <button
                    key={ws.workspace_id}
                    onClick={() => {
                      setSelectedWorkspace(ws);
                      setFormData(f => ({ ...f, name: ws.name }));
                    }}
                    className="w-full p-4 bg-[#111] border border-gray-800 rounded-xl text-left hover:border-gray-700 transition-colors"
                  >
                    <p className="font-medium">{ws.name}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {Object.keys(ws.files || {}).length} archivos
                    </p>
                  </button>
                ))
              )}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Nombre del Template</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                  className="w-full px-4 py-3 bg-[#111] border border-gray-800 rounded-xl focus:border-gray-600 outline-none"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Descripción</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))}
                  className="w-full px-4 py-3 bg-[#111] border border-gray-800 rounded-xl focus:border-gray-600 outline-none h-24 resize-none"
                  placeholder="Describe tu template..."
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Categoría</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData(f => ({ ...f, category: e.target.value }))}
                  className="w-full px-4 py-3 bg-[#111] border border-gray-800 rounded-xl focus:border-gray-600 outline-none"
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
                  className="w-full px-4 py-3 bg-[#111] border border-gray-800 rounded-xl focus:border-gray-600 outline-none"
                />
              </div>
              
              {/* Pricing Section */}
              <div className="border-t border-gray-800 pt-5">
                <label className="block text-sm text-gray-400 mb-3">Precio del Template</label>
                <div className="flex gap-3 mb-3">
                  <button
                    type="button"
                    onClick={() => setFormData(f => ({ ...f, is_free: true }))}
                    className={`flex-1 py-3 rounded-xl transition-colors flex items-center justify-center gap-2 ${
                      formData.is_free 
                        ? 'bg-green-500/20 border border-green-500/40 text-green-400' 
                        : 'bg-[#111] border border-gray-800 text-gray-400 hover:border-gray-700'
                    }`}
                  >
                    <Check size={18} />
                    Gratis
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData(f => ({ ...f, is_free: false }))}
                    className={`flex-1 py-3 rounded-xl transition-colors flex items-center justify-center gap-2 ${
                      !formData.is_free 
                        ? 'bg-amber-500/20 border border-amber-500/40 text-amber-400' 
                        : 'bg-[#111] border border-gray-800 text-gray-400 hover:border-gray-700'
                    }`}
                  >
                    <Zap size={18} />
                    De pago
                  </button>
                </div>
                
                {!formData.is_free && (
                  <div className="flex items-center gap-3">
                    <input
                      type="number"
                      value={formData.price}
                      onChange={(e) => setFormData(f => ({ ...f, price: Math.max(10, parseInt(e.target.value) || 0) }))}
                      min="10"
                      step="10"
                      className="flex-1 px-4 py-3 bg-[#111] border border-gray-800 rounded-xl focus:border-gray-600 outline-none"
                    />
                    <span className="text-gray-400">créditos</span>
                  </div>
                )}
                
                {!formData.is_free && (
                  <p className="text-xs text-gray-500 mt-2">
                    Recibirás el 80% ({(formData.price * 0.8).toFixed(0)} créditos) por cada venta
                  </p>
                )}
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setSelectedWorkspace(null)}
                  className="flex-1 py-3 bg-gray-800 rounded-xl hover:bg-gray-700 transition-colors"
                >
                  Atrás
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-3 bg-white text-black rounded-xl font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? <Loader2 size={18} className="animate-spin" /> : 'Publicar'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketplacePage;
