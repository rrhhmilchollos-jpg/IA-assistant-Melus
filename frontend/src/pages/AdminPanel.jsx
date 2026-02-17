import React, { useState, useEffect } from 'react';
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
  CheckCircle
} from 'lucide-react';

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

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }
    loadDashboardData();
  }, [user, navigate]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [dashboard, health, chart] = await Promise.all([
        adminAPI.getDashboard(),
        adminAPI.getSystemHealth(),
        adminAPI.getRevenueChart(30)
      ]);
      setDashboardData(dashboard);
      setSystemHealth(health);
      setRevenueChart(chart.data || []);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0d0d1a] flex items-center justify-center">
        <div className="flex items-center gap-3 text-purple-400">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Cargando panel de administración...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d0d1a] text-white" data-testid="admin-panel">
      {/* Header */}
      <header className="bg-[#1a1a2e] border-b border-purple-500/20 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-white">Panel de Administración</h1>
            <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
              Admin
            </span>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Volver al Dashboard
          </button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-[#1a1a2e] border-r border-purple-500/20 min-h-[calc(100vh-73px)]">
          <nav className="p-4 space-y-2">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: Activity },
              { id: 'users', label: 'Usuarios', icon: Users },
              { id: 'transactions', label: 'Transacciones', icon: CreditCard },
              { id: 'revenue', label: 'Ingresos', icon: TrendingUp },
              { id: 'system', label: 'Sistema', icon: Server },
              { id: 'settings', label: 'Configuración', icon: Settings },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  activeTab === item.id
                    ? 'bg-purple-500/20 text-purple-400'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
                data-testid={`admin-tab-${item.id}`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
                {activeTab === item.id && <ChevronRight className="w-4 h-4 ml-auto" />}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeTab === 'dashboard' && dashboardData && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Dashboard</h2>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Total Usuarios"
                  value={dashboardData.users?.total || 0}
                  icon={Users}
                  color="purple"
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
                />
              </div>

              {/* Agent Usage */}
              <div className="bg-[#1a1a2e] rounded-xl p-6 border border-purple-500/20">
                <h3 className="text-lg font-semibold mb-4">Uso de Agentes</h3>
                <div className="space-y-3">
                  {(dashboardData.agent_usage || []).map((agent, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-[#0d0d1a] rounded-lg">
                      <div className="flex items-center gap-3">
                        <Cpu className="w-5 h-5 text-purple-400" />
                        <span className="capitalize">{agent.agent_type}</span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-gray-400">{agent.actions} acciones</span>
                        <span className="text-purple-400 font-medium">{agent.credits_used} créditos</span>
                      </div>
                    </div>
                  ))}
                  {(!dashboardData.agent_usage || dashboardData.agent_usage.length === 0) && (
                    <p className="text-gray-500 text-center py-4">No hay datos de uso de agentes</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Usuarios</h2>
                <button
                  onClick={loadUsers}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Actualizar
                </button>
              </div>

              <div className="bg-[#1a1a2e] rounded-xl border border-purple-500/20 overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#0d0d1a]">
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
                      <tr key={u.user_id} className="border-t border-purple-500/10 hover:bg-white/5">
                        <td className="px-4 py-3 text-sm">{u.email}</td>
                        <td className="px-4 py-3 text-sm">{u.name}</td>
                        <td className="px-4 py-3 text-sm text-purple-400">{u.credits}</td>
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
                            <span className="text-gray-500">-</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <button
                            onClick={() => handleUpdateUser(u.user_id, { credits: u.credits + 1000 })}
                            className="text-purple-400 hover:text-purple-300 text-xs"
                          >
                            +1000 créditos
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

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

              <div className="bg-[#1a1a2e] rounded-xl border border-purple-500/20 overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#0d0d1a]">
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
                      <tr key={txn.transaction_id} className="border-t border-purple-500/10 hover:bg-white/5">
                        <td className="px-4 py-3 text-sm font-mono text-gray-400">{txn.transaction_id?.slice(0, 12)}...</td>
                        <td className="px-4 py-3 text-sm">{txn.user_email}</td>
                        <td className="px-4 py-3 text-sm text-green-400">${txn.amount?.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm text-purple-400">{txn.credits}</td>
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

          {activeTab === 'system' && systemHealth && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Estado del Sistema</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-[#1a1a2e] rounded-xl p-6 border border-purple-500/20">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Database className="w-5 h-5 text-purple-400" />
                    MongoDB
                  </h3>
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

                <div className="bg-[#1a1a2e] rounded-xl p-6 border border-purple-500/20">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Server className="w-5 h-5 text-purple-400" />
                    API
                  </h3>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-green-400">Operacional</span>
                  </div>
                </div>
              </div>

              <div className="bg-[#1a1a2e] rounded-xl p-6 border border-purple-500/20">
                <h3 className="text-lg font-semibold mb-4">Métricas</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-[#0d0d1a] rounded-lg">
                    <p className="text-gray-400 text-sm">Sesiones Activas</p>
                    <p className="text-2xl font-bold text-white">{systemHealth.metrics?.active_sessions || 0}</p>
                  </div>
                  <div className="p-4 bg-[#0d0d1a] rounded-lg">
                    <p className="text-gray-400 text-sm">Proyectos en Progreso</p>
                    <p className="text-2xl font-bold text-white">{systemHealth.metrics?.pending_projects || 0}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'revenue' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Análisis de Ingresos</h2>
              
              <div className="bg-[#1a1a2e] rounded-xl p-6 border border-purple-500/20">
                <h3 className="text-lg font-semibold mb-4">Ingresos Últimos 30 Días</h3>
                <div className="h-64 flex items-end justify-between gap-1">
                  {revenueChart.map((day, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center gap-2">
                      <div
                        className="w-full bg-purple-500/50 rounded-t hover:bg-purple-500 transition-colors"
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

          {activeTab === 'settings' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Configuración</h2>
              
              <div className="bg-[#1a1a2e] rounded-xl p-6 border border-purple-500/20">
                <h3 className="text-lg font-semibold mb-4">Costos de Agentes (Créditos)</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {[
                    { key: 'orchestrator', label: 'Orquestador', value: 50 },
                    { key: 'design', label: 'Diseño', value: 100 },
                    { key: 'frontend', label: 'Frontend', value: 150 },
                    { key: 'backend', label: 'Backend', value: 150 },
                    { key: 'database', label: 'Base de Datos', value: 100 },
                    { key: 'deploy', label: 'Despliegue', value: 200 },
                  ].map(agent => (
                    <div key={agent.key} className="p-4 bg-[#0d0d1a] rounded-lg">
                      <p className="text-gray-400 text-sm mb-2">{agent.label}</p>
                      <input
                        type="number"
                        defaultValue={agent.value}
                        className="w-full bg-transparent border border-purple-500/30 rounded px-3 py-2 text-white focus:border-purple-500 outline-none"
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

// Stat Card Component
const StatCard = ({ title, value, icon: Icon, color }) => {
  const colorClasses = {
    purple: 'bg-purple-500/20 text-purple-400',
    green: 'bg-green-500/20 text-green-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
    blue: 'bg-blue-500/20 text-blue-400',
  };

  return (
    <div className="bg-[#1a1a2e] rounded-xl p-6 border border-purple-500/20">
      <div className="flex items-center justify-between mb-4">
        <span className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </span>
      </div>
      <p className="text-gray-400 text-sm">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
};

export default AdminPanel;
