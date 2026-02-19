import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminAPI } from '../api/client';
import { 
  Users, 
  CreditCard, 
  TrendingUp, 
  Server, 
  Settings, 
  RefreshCw,
  ChevronRight,
  DollarSign,
  Activity,
  Database,
  Cpu,
  AlertCircle,
  CheckCircle,
  Box,
  Code,
  Rocket,
  Terminal,
  Eye,
  EyeOff,
  GripVertical,
  BarChart3,
  PieChart,
  Calendar,
  Zap,
  ArrowUp,
  ArrowDown,
  Clock,
  FileCode,
  Bot,
  Layers
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const AdminPanel = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [revenueChart, setRevenueChart] = useState([]);
  
  // New metrics state
  const [projectsMetrics, setProjectsMetrics] = useState(null);
  const [sandboxMetrics, setSandboxMetrics] = useState(null);
  const [creditsMetrics, setCreditsMetrics] = useState(null);
  
  // Widget visibility state (saved to localStorage)
  const [widgetVisibility, setWidgetVisibility] = useState(() => {
    const saved = localStorage.getItem('admin_widgets');
    return saved ? JSON.parse(saved) : {
      stats: true,
      agents: true,
      projects: true,
      credits: true,
      sandbox: true,
      recentActivity: true
    };
  });

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }
    loadAllData();
  }, [user, navigate]);

  useEffect(() => {
    localStorage.setItem('admin_widgets', JSON.stringify(widgetVisibility));
  }, [widgetVisibility]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('session_token');
      
      // Load standard data
      const [dashboard, health, chart] = await Promise.all([
        adminAPI.getDashboard(),
        adminAPI.getSystemHealth(),
        adminAPI.getRevenueChart(30)
      ]);
      setDashboardData(dashboard);
      setSystemHealth(health);
      setRevenueChart(chart.data || []);
      
      // Load new metrics
      const [projectsRes, sandboxRes, creditsRes] = await Promise.all([
        fetch(`${API_BASE}/api/admin/metrics/projects`, { headers: { 'X-Session-Token': token } }).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/admin/metrics/sandbox`, { headers: { 'X-Session-Token': token } }).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/admin/metrics/credits`, { headers: { 'X-Session-Token': token } }).then(r => r.json()).catch(() => null)
      ]);
      
      setProjectsMetrics(projectsRes);
      setSandboxMetrics(sandboxRes);
      setCreditsMetrics(creditsRes);
      
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await adminAPI.getUsers(100, 0);
      setUsers(response.users || []);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const loadTransactions = async () => {
    try {
      const response = await adminAPI.getTransactions(100, 0);
      setTransactions(response.transactions || []);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'users') loadUsers();
    if (activeTab === 'transactions') loadTransactions();
  }, [activeTab]);

  const handleUpdateUser = async (userId, updates) => {
    try {
      await adminAPI.updateUser(userId, updates);
      loadUsers();
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const toggleWidget = (widgetId) => {
    setWidgetVisibility(prev => ({
      ...prev,
      [widgetId]: !prev[widgetId]
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="flex items-center gap-3 text-purple-400">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Cargando panel de administración...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white" data-testid="admin-panel">
      {/* Header */}
      <header className="bg-[#111] border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold">Panel de Administración</h1>
            <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded font-medium">
              Admin
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={loadAllData}
              className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Actualizar
            </button>
            <button
              onClick={() => navigate('/home')}
              className="px-4 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Volver al Home
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-[#111] border-r border-gray-800 min-h-[calc(100vh-73px)]">
          <nav className="p-4 space-y-1">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: Activity },
              { id: 'users', label: 'Usuarios', icon: Users },
              { id: 'transactions', label: 'Transacciones', icon: CreditCard },
              { id: 'projects', label: 'Proyectos', icon: FileCode },
              { id: 'agents', label: 'Agentes', icon: Bot },
              { id: 'sandbox', label: 'Sandbox', icon: Terminal },
              { id: 'revenue', label: 'Ingresos', icon: TrendingUp },
              { id: 'system', label: 'Sistema', icon: Server },
              { id: 'settings', label: 'Configuración', icon: Settings },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                  activeTab === item.id
                    ? 'bg-purple-500/20 text-purple-400'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
                data-testid={`admin-tab-${item.id}`}
              >
                <item.icon className="w-5 h-5" />
                <span className="text-sm">{item.label}</span>
                {activeTab === item.id && <ChevronRight className="w-4 h-4 ml-auto" />}
              </button>
            ))}
          </nav>
          
          {/* Widget Controls */}
          {activeTab === 'dashboard' && (
            <div className="px-4 py-3 border-t border-gray-800">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Widgets</p>
              <div className="space-y-2">
                {Object.entries(widgetVisibility).map(([key, visible]) => (
                  <button
                    key={key}
                    onClick={() => toggleWidget(key)}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-gray-800/50 hover:bg-gray-800 text-sm"
                  >
                    <span className="capitalize text-gray-300">{key}</span>
                    {visible ? (
                      <Eye className="w-4 h-4 text-green-400" />
                    ) : (
                      <EyeOff className="w-4 h-4 text-gray-500" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          {/* DASHBOARD TAB */}
          {activeTab === 'dashboard' && dashboardData && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Dashboard</h2>
                <span className="text-sm text-gray-500">
                  Última actualización: {new Date().toLocaleTimeString()}
                </span>
              </div>
              
              {/* Stats Grid */}
              {widgetVisibility.stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <StatCard
                    title="Total Usuarios"
                    value={dashboardData.users?.total || 0}
                    icon={Users}
                    color="purple"
                    trend={dashboardData.users?.growth}
                  />
                  <StatCard
                    title="Usuarios Activos (24h)"
                    value={dashboardData.users?.active_24h || 0}
                    icon={Activity}
                    color="green"
                  />
                  <StatCard
                    title="Ingresos Totales"
                    value={`$${(dashboardData.revenue?.total || 0).toFixed(2)}`}
                    icon={DollarSign}
                    color="yellow"
                  />
                  <StatCard
                    title="Ingresos Hoy"
                    value={`$${(dashboardData.revenue?.today || 0).toFixed(2)}`}
                    icon={TrendingUp}
                    color="blue"
                    trend={dashboardData.revenue?.today_growth}
                  />
                </div>
              )}

              {/* Projects & Sandbox Row */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Projects Metrics */}
                {widgetVisibility.projects && (
                  <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                    <div className="flex items-center gap-2 mb-4">
                      <FileCode className="w-5 h-5 text-cyan-400" />
                      <h3 className="text-lg font-semibold">Proyectos Generados</h3>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-[#0a0a0a] rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-white">{projectsMetrics?.total || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Total</p>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-green-400">{projectsMetrics?.today || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Hoy</p>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-blue-400">{projectsMetrics?.this_week || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Esta Semana</p>
                      </div>
                    </div>
                    {/* Project types breakdown */}
                    <div className="mt-4 space-y-2">
                      {(projectsMetrics?.by_type || []).slice(0, 5).map((type, i) => (
                        <div key={i} className="flex items-center justify-between text-sm">
                          <span className="text-gray-400 capitalize">{type.type}</span>
                          <span className="text-white font-medium">{type.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Sandbox Metrics */}
                {widgetVisibility.sandbox && (
                  <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                    <div className="flex items-center gap-2 mb-4">
                      <Terminal className="w-5 h-5 text-purple-400" />
                      <h3 className="text-lg font-semibold">Ejecuciones Sandbox</h3>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-[#0a0a0a] rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-white">{sandboxMetrics?.total || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Total</p>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-green-400">{sandboxMetrics?.successful || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Exitosos</p>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-red-400">{sandboxMetrics?.failed || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Fallidos</p>
                      </div>
                    </div>
                    {/* By method */}
                    <div className="mt-4 space-y-2">
                      {['node', 'codesandbox', 'docker'].map(method => (
                        <div key={method} className="flex items-center justify-between text-sm">
                          <span className="text-gray-400 capitalize">{method}</span>
                          <span className="text-white font-medium">
                            {sandboxMetrics?.by_method?.[method] || 0}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Credits Chart */}
              {widgetVisibility.credits && creditsMetrics && (
                <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-yellow-400" />
                      <h3 className="text-lg font-semibold">Consumo de Créditos (7 días)</h3>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-400">
                        Total: <span className="text-yellow-400 font-medium">{creditsMetrics.total_consumed?.toFixed(0) || 0}</span>
                      </span>
                      <span className="text-gray-400">
                        Promedio/día: <span className="text-white font-medium">{creditsMetrics.daily_average?.toFixed(0) || 0}</span>
                      </span>
                    </div>
                  </div>
                  <div className="h-40 flex items-end gap-2">
                    {(creditsMetrics.daily || []).map((day, i) => (
                      <div key={i} className="flex-1 flex flex-col items-center gap-1">
                        <div 
                          className="w-full bg-gradient-to-t from-yellow-500/50 to-yellow-400/20 rounded-t hover:from-yellow-500 hover:to-yellow-400/50 transition-colors"
                          style={{ 
                            height: `${Math.max(4, (day.credits / Math.max(...creditsMetrics.daily.map(d => d.credits || 1))) * 120)}px` 
                          }}
                          title={`${day.date}: ${day.credits.toFixed(0)} créditos`}
                        />
                        <span className="text-xs text-gray-600">{day.day}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Agent Usage */}
              {widgetVisibility.agents && (
                <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                  <div className="flex items-center gap-2 mb-4">
                    <Bot className="w-5 h-5 text-cyan-400" />
                    <h3 className="text-lg font-semibold">Uso de Agentes</h3>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {(dashboardData.agent_usage || []).map((agent, index) => (
                      <div key={index} className="p-4 bg-[#0a0a0a] rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Cpu className="w-4 h-4 text-purple-400" />
                          <span className="text-sm font-medium capitalize">{agent.agent_type}</span>
                        </div>
                        <p className="text-2xl font-bold text-white">{agent.actions}</p>
                        <p className="text-xs text-gray-500">{agent.credits_used} créditos</p>
                      </div>
                    ))}
                    {(!dashboardData.agent_usage || dashboardData.agent_usage.length === 0) && (
                      <p className="col-span-4 text-gray-500 text-center py-8">No hay datos de uso de agentes</p>
                    )}
                  </div>
                </div>
              )}

              {/* Recent Activity */}
              {widgetVisibility.recentActivity && (
                <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold">Actividad Reciente</h3>
                  </div>
                  <div className="space-y-3">
                    {(dashboardData.recent_activity || []).slice(0, 10).map((activity, i) => (
                      <div key={i} className="flex items-center gap-4 p-3 bg-[#0a0a0a] rounded-lg">
                        <div className={`p-2 rounded-lg ${
                          activity.type === 'project' ? 'bg-cyan-500/20 text-cyan-400' :
                          activity.type === 'payment' ? 'bg-green-500/20 text-green-400' :
                          activity.type === 'user' ? 'bg-purple-500/20 text-purple-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {activity.type === 'project' ? <FileCode className="w-4 h-4" /> :
                           activity.type === 'payment' ? <DollarSign className="w-4 h-4" /> :
                           activity.type === 'user' ? <Users className="w-4 h-4" /> :
                           <Activity className="w-4 h-4" />}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-white">{activity.description}</p>
                          <p className="text-xs text-gray-500">{activity.user}</p>
                        </div>
                        <span className="text-xs text-gray-500">{activity.time}</span>
                      </div>
                    ))}
                    {(!dashboardData.recent_activity || dashboardData.recent_activity.length === 0) && (
                      <p className="text-gray-500 text-center py-8">No hay actividad reciente</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* USERS TAB */}
          {activeTab === 'users' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Usuarios ({users.length})</h2>
                <button
                  onClick={loadUsers}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Actualizar
                </button>
              </div>

              <div className="bg-[#111] rounded-xl border border-gray-800 overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#0a0a0a]">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Email</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Nombre</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Créditos</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Plan</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Admin</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(u => (
                      <tr key={u.user_id} className="border-t border-gray-800 hover:bg-gray-900/50">
                        <td className="px-4 py-3 text-sm">{u.email}</td>
                        <td className="px-4 py-3 text-sm">{u.name}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className="text-yellow-400 font-medium">{u.credits?.toFixed(2)}</span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded text-xs ${
                            u.subscription_tier === 'enterprise' ? 'bg-yellow-500/20 text-yellow-400' :
                            u.subscription_tier === 'pro' ? 'bg-purple-500/20 text-purple-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {u.subscription_tier || 'free'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {u.is_admin ? (
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          ) : (
                            <span className="text-gray-600">-</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleUpdateUser(u.user_id, { credits: (u.credits || 0) + 1000 })}
                              className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs hover:bg-green-500/30"
                            >
                              +1000
                            </button>
                            <button
                              onClick={() => handleUpdateUser(u.user_id, { is_admin: !u.is_admin })}
                              className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs hover:bg-purple-500/30"
                            >
                              {u.is_admin ? 'Quitar Admin' : 'Hacer Admin'}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TRANSACTIONS TAB */}
          {activeTab === 'transactions' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Transacciones</h2>
                <button
                  onClick={loadTransactions}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Actualizar
                </button>
              </div>

              <div className="bg-[#111] rounded-xl border border-gray-800 overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#0a0a0a]">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">ID</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Usuario</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Monto</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Créditos</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Estado</th>
                      <th className="px-4 py-3 text-left text-sm text-gray-400">Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map(txn => (
                      <tr key={txn.transaction_id} className="border-t border-gray-800 hover:bg-gray-900/50">
                        <td className="px-4 py-3 text-sm font-mono text-gray-500">{txn.transaction_id?.slice(0, 12)}...</td>
                        <td className="px-4 py-3 text-sm">{txn.user_email}</td>
                        <td className="px-4 py-3 text-sm text-green-400 font-medium">${txn.amount?.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm text-yellow-400">{txn.credits}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded text-xs ${
                            txn.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                            txn.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-red-500/20 text-red-400'
                          }`}>
                            {txn.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-400">
                          {new Date(txn.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* PROJECTS TAB */}
          {activeTab === 'projects' && (
            <ProjectsTab />
          )}

          {/* AGENTS TAB */}
          {activeTab === 'agents' && (
            <AgentsTab />
          )}

          {/* SANDBOX TAB */}
          {activeTab === 'sandbox' && (
            <SandboxTab />
          )}

          {/* SYSTEM TAB */}
          {activeTab === 'system' && systemHealth && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Estado del Sistema</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                  <div className="flex items-center gap-3 mb-4">
                    <Database className="w-6 h-6 text-purple-400" />
                    <h3 className="text-lg font-semibold">MongoDB</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    {systemHealth.services?.mongodb === 'healthy' ? (
                      <>
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <span className="text-green-400">Saludable</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-5 h-5 text-red-400" />
                        <span className="text-red-400">{systemHealth.services?.mongodb}</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                  <div className="flex items-center gap-3 mb-4">
                    <Server className="w-6 h-6 text-blue-400" />
                    <h3 className="text-lg font-semibold">API</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-green-400">Operacional</span>
                  </div>
                </div>

                <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                  <div className="flex items-center gap-3 mb-4">
                    <Terminal className="w-6 h-6 text-cyan-400" />
                    <h3 className="text-lg font-semibold">Sandbox</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-green-400">Activo (Node.js)</span>
                  </div>
                </div>
              </div>

              <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold mb-4">Métricas del Sistema</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-[#0a0a0a] rounded-lg">
                    <p className="text-gray-400 text-sm">Sesiones Activas</p>
                    <p className="text-2xl font-bold text-white">{systemHealth.metrics?.active_sessions || 0}</p>
                  </div>
                  <div className="p-4 bg-[#0a0a0a] rounded-lg">
                    <p className="text-gray-400 text-sm">Proyectos en Progreso</p>
                    <p className="text-2xl font-bold text-white">{systemHealth.metrics?.pending_projects || 0}</p>
                  </div>
                  <div className="p-4 bg-[#0a0a0a] rounded-lg">
                    <p className="text-gray-400 text-sm">WebSocket Connections</p>
                    <p className="text-2xl font-bold text-white">{systemHealth.metrics?.websocket_connections || 0}</p>
                  </div>
                  <div className="p-4 bg-[#0a0a0a] rounded-lg">
                    <p className="text-gray-400 text-sm">API Latency</p>
                    <p className="text-2xl font-bold text-white">{systemHealth.metrics?.api_latency || '<50'}ms</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* REVENUE TAB */}
          {activeTab === 'revenue' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Análisis de Ingresos</h2>
              
              <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold mb-4">Ingresos Últimos 30 Días</h3>
                <div className="h-64 flex items-end justify-between gap-1">
                  {revenueChart.map((day, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center gap-2">
                      <div
                        className="w-full bg-gradient-to-t from-green-500/50 to-green-400/20 rounded-t hover:from-green-500 hover:to-green-400/50 transition-colors cursor-pointer"
                        style={{
                          height: `${Math.max(4, (day.revenue / Math.max(...revenueChart.map(d => d.revenue || 1))) * 200)}px`
                        }}
                        title={`${day.date}: $${day.revenue?.toFixed(2)}`}
                      />
                    </div>
                  ))}
                </div>
                {revenueChart.length === 0 && (
                  <p className="text-gray-500 text-center py-8">No hay datos de ingresos</p>
                )}
              </div>
            </div>
          )}

          {/* SETTINGS TAB */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Configuración</h2>
              
              <div className="bg-[#111] rounded-xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold mb-4">Costos de Agentes (Créditos)</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {[
                    { key: 'orchestrator', label: 'Orquestador', value: 50 },
                    { key: 'classifier', label: 'Clasificador', value: 25 },
                    { key: 'design', label: 'Diseño', value: 100 },
                    { key: 'frontend', label: 'Frontend', value: 150 },
                    { key: 'backend', label: 'Backend', value: 150 },
                    { key: 'database', label: 'Base de Datos', value: 100 },
                    { key: 'integrator', label: 'Integrador', value: 75 },
                    { key: 'testing', label: 'Testing', value: 50 },
                    { key: 'deploy', label: 'Despliegue', value: 200 },
                  ].map(agent => (
                    <div key={agent.key} className="p-4 bg-[#0a0a0a] rounded-lg">
                      <p className="text-gray-400 text-sm mb-2">{agent.label}</p>
                      <input
                        type="number"
                        defaultValue={agent.value}
                        className="w-full bg-transparent border border-gray-700 rounded px-3 py-2 text-white focus:border-purple-500 outline-none"
                      />
                    </div>
                  ))}
                </div>
                <button className="mt-4 px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
                  Guardar Cambios
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

// Stat Card Component with Trend
const StatCard = ({ title, value, icon: Icon, color, trend }) => {
  const colorClasses = {
    purple: 'bg-purple-500/20 text-purple-400',
    green: 'bg-green-500/20 text-green-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
    blue: 'bg-blue-500/20 text-blue-400',
    cyan: 'bg-cyan-500/20 text-cyan-400',
  };

  return (
    <div className="bg-[#111] rounded-xl p-5 border border-gray-800">
      <div className="flex items-center justify-between mb-3">
        <span className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </span>
        {trend !== undefined && (
          <span className={`flex items-center text-xs ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend >= 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <p className="text-gray-400 text-sm">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
};

// Projects Tab Component
const ProjectsTab = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/admin/projects?limit=50`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Proyectos Generados</h2>
        <button
          onClick={loadProjects}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Actualizar
        </button>
      </div>

      <div className="bg-[#111] rounded-xl border border-gray-800 overflow-hidden">
        <table className="w-full">
          <thead className="bg-[#0a0a0a]">
            <tr>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Proyecto</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Usuario</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Tipo</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Archivos</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Créditos</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {projects.map(p => (
              <tr key={p.workspace_id} className="border-t border-gray-800 hover:bg-gray-900/50">
                <td className="px-4 py-3 text-sm font-medium">{p.name}</td>
                <td className="px-4 py-3 text-sm text-gray-400">{p.user_email}</td>
                <td className="px-4 py-3 text-sm">
                  <span className="px-2 py-1 bg-cyan-500/20 text-cyan-400 rounded text-xs">
                    {p.project_type || 'custom'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">{p.file_count || 0}</td>
                <td className="px-4 py-3 text-sm text-yellow-400">{p.credits_used || 0}</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(p.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Agents Tab Component
const AgentsTab = () => {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/agents/v2/expert-agents`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Failed to load agents:', error);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Expert Agents</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map(agent => (
          <div key={agent.id} className="bg-[#111] rounded-xl p-5 border border-gray-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Bot className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h3 className="font-semibold">{agent.name}</h3>
                <span className="text-xs text-gray-500">{agent.category}</span>
              </div>
            </div>
            <p className="text-sm text-gray-400 mb-3">{agent.description}</p>
            <div className="flex items-center justify-between">
              <span className="text-yellow-400 font-medium">{agent.cost} créditos</span>
              <div className="flex gap-1">
                {(agent.capabilities || []).slice(0, 2).map((cap, i) => (
                  <span key={i} className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-400">
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Sandbox Tab Component
const SandboxTab = () => {
  const [executions, setExecutions] = useState([]);
  const [methods, setMethods] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const [execRes, methodsRes] = await Promise.all([
        fetch(`${API_BASE}/api/sandbox/executions?limit=50`, { headers: { 'X-Session-Token': token } }).then(r => r.json()),
        fetch(`${API_BASE}/api/sandbox/methods`).then(r => r.json())
      ]);
      setExecutions(execRes.executions || []);
      setMethods(methodsRes);
    } catch (error) {
      console.error('Failed to load sandbox data:', error);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Sandbox Execution</h2>
      
      {/* Methods Status */}
      {methods && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(methods.methods || {}).map(([key, method]) => (
            <div key={key} className="bg-[#111] rounded-xl p-5 border border-gray-800">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold capitalize">{key}</h3>
                <span className={`px-2 py-1 rounded text-xs ${
                  method.available ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                }`}>
                  {method.available ? 'Activo' : 'No disponible'}
                </span>
              </div>
              <p className="text-sm text-gray-400">{method.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Recent Executions */}
      <div className="bg-[#111] rounded-xl border border-gray-800 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-800">
          <h3 className="font-semibold">Ejecuciones Recientes</h3>
        </div>
        <table className="w-full">
          <thead className="bg-[#0a0a0a]">
            <tr>
              <th className="px-4 py-3 text-left text-sm text-gray-400">ID</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Tipo</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Estado</th>
              <th className="px-4 py-3 text-left text-sm text-gray-400">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {executions.map(exec => (
              <tr key={exec.execution_id} className="border-t border-gray-800 hover:bg-gray-900/50">
                <td className="px-4 py-3 text-sm font-mono text-gray-500">{exec.execution_id}</td>
                <td className="px-4 py-3 text-sm">
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
                    {exec.type}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${
                    exec.exit_code === 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {exec.exit_code === 0 ? 'Éxito' : 'Error'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(exec.executed_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminPanel;
