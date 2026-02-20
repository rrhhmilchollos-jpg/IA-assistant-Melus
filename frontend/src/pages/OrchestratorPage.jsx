import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  ChevronLeft,
  Zap,
  Play,
  Pause,
  RotateCcw,
  Plus,
  Settings,
  Activity,
  Cpu,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  DollarSign,
  Users,
  Layers,
  Target,
  Bot,
  Code,
  FileText,
  Search,
  Brain,
  Shield,
  Gauge,
  Workflow,
  MoreHorizontal,
  ChevronRight,
  RefreshCw,
  File,
  Folder,
  Eye,
  Download,
  X,
  Loader2
} from 'lucide-react';
import { Toaster, toast } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Agent role icons mapping
const agentIcons = {
  planner: Target,
  research: Search,
  reasoning: Brain,
  content: FileText,
  code: Code,
  automation: Workflow,
  qa: CheckCircle,
  security: Shield,
  optimization: Gauge,
  cost_control: DollarSign
};

// Agent role colors
const agentColors = {
  planner: 'from-blue-500 to-cyan-500',
  research: 'from-purple-500 to-pink-500',
  reasoning: 'from-amber-500 to-orange-500',
  content: 'from-emerald-500 to-teal-500',
  code: 'from-yellow-500 to-amber-500',
  automation: 'from-indigo-500 to-purple-500',
  qa: 'from-green-500 to-emerald-500',
  security: 'from-red-500 to-rose-500',
  optimization: 'from-cyan-500 to-blue-500',
  cost_control: 'from-gray-500 to-slate-500'
};

const OrchestratorPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [objectives, setObjectives] = useState([]);
  const [agents, setAgents] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [autoMode, setAutoMode] = useState(true);
  const [selectedTab, setSelectedTab] = useState('overview');
  
  // New objective modal
  const [showNewObjective, setShowNewObjective] = useState(false);
  const [newObjective, setNewObjective] = useState({
    title: '',
    description: '',
    type: 'code',
    priority: 5,
    auto_mode: true
  });

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const [statsRes, objectivesRes, agentsRes, activityRes] = await Promise.all([
        fetch(`${API_BASE}/api/orchestrator/stats`, { headers: { 'X-Session-Token': token } }),
        fetch(`${API_BASE}/api/orchestrator/objectives`, { headers: { 'X-Session-Token': token } }),
        fetch(`${API_BASE}/api/orchestrator/agents`, { headers: { 'X-Session-Token': token } }),
        fetch(`${API_BASE}/api/orchestrator/activity`, { headers: { 'X-Session-Token': token } })
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (objectivesRes.ok) setObjectives(await objectivesRes.json());
      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (activityRes.ok) setActivity(await activityRes.json());
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const createObjective = async () => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/orchestrator/objectives`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify(newObjective)
      });

      if (response.ok) {
        toast.success('Objective created');
        setShowNewObjective(false);
        setNewObjective({ title: '', description: '', type: 'code', priority: 5, auto_mode: true });
        loadDashboardData();
      }
    } catch (error) {
      toast.error('Failed to create objective');
    }
  };

  const startObjective = async (objectiveId) => {
    const token = localStorage.getItem('session_token');
    try {
      const response = await fetch(`${API_BASE}/api/orchestrator/objectives/${objectiveId}/start`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      if (response.ok) {
        toast.success('Objective started');
        loadDashboardData();
      }
    } catch (error) {
      toast.error('Failed to start objective');
    }
  };

  const toggleAgent = async (agentId) => {
    const token = localStorage.getItem('session_token');
    try {
      await fetch(`${API_BASE}/api/orchestrator/agents/${agentId}/toggle`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      loadDashboardData();
    } catch (error) {
      toast.error('Failed to toggle agent');
    }
  };

  const StatCard = ({ icon: Icon, label, value, subvalue, color = 'cyan' }) => (
    <div className="bg-white rounded-xl p-5 border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <div className={`w-10 h-10 rounded-lg bg-${color}-100 flex items-center justify-center`}>
          <Icon size={20} className={`text-${color}-600`} />
        </div>
        <span className="text-xs text-gray-400 font-medium uppercase">{label}</span>
      </div>
      <div className="text-2xl font-bold text-gray-800">{value}</div>
      {subvalue && <div className="text-sm text-gray-500 mt-1">{subvalue}</div>}
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f8f9fa] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      <Toaster />
      
      {/* Header */}
      <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/home')}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            <ChevronLeft size={20} />
          </button>
          <span className="text-lg font-light text-gray-800">
            melus<span className="font-normal">AI</span>
          </span>
          <div className="h-5 w-px bg-gray-200" />
          <span className="text-sm text-gray-600">Orchestrator</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Auto Mode Toggle */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
            <span className="text-sm text-gray-600">Auto Mode</span>
            <button
              onClick={() => setAutoMode(!autoMode)}
              className={`w-10 h-5 rounded-full transition-colors ${autoMode ? 'bg-cyan-500' : 'bg-gray-300'}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full shadow transition-transform ${autoMode ? 'translate-x-5' : 'translate-x-0.5'}`} />
            </button>
          </div>

          <button
            onClick={() => setShowNewObjective(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-lg text-sm font-medium"
          >
            <Plus size={16} />
            New Objective
          </button>

          <button
            onClick={loadDashboardData}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 px-6">
        <div className="flex gap-1">
          {['overview', 'objectives', 'agents', 'activity'].map(tab => (
            <button
              key={tab}
              onClick={() => setSelectedTab(tab)}
              className={`px-4 py-3 text-sm font-medium capitalize border-b-2 transition-colors ${
                selectedTab === tab
                  ? 'text-gray-800 border-gray-800'
                  : 'text-gray-500 border-transparent hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6 max-w-7xl mx-auto">
        {selectedTab === 'overview' && stats && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4">
              <StatCard
                icon={Target}
                label="Objectives"
                value={stats.objectives.total}
                subvalue={`${stats.objectives.active} active`}
              />
              <StatCard
                icon={Layers}
                label="Tasks"
                value={stats.tasks.total}
                subvalue={`${stats.tasks.completed} completed`}
              />
              <StatCard
                icon={Bot}
                label="Agents"
                value={stats.agents.active}
                subvalue={`of ${stats.agents.total} total`}
              />
              <StatCard
                icon={DollarSign}
                label="Cost"
                value={`$${stats.cost.total.toFixed(2)}`}
                subvalue="total spent"
              />
            </div>

            {/* Agents Grid */}
            <div>
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Active Agents</h2>
              <div className="grid grid-cols-5 gap-3">
                {agents.map(agent => {
                  const Icon = agentIcons[agent.role] || Bot;
                  const gradient = agentColors[agent.role] || 'from-gray-500 to-gray-600';
                  
                  return (
                    <div
                      key={agent.id}
                      className={`bg-white rounded-xl p-4 border border-gray-200 ${
                        agent.status === 'inactive' ? 'opacity-50' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center`}>
                          <Icon size={20} className="text-white" />
                        </div>
                        <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-500' : 'bg-gray-300'}`} />
                      </div>
                      <div className="text-sm font-medium text-gray-800 truncate">{agent.name}</div>
                      <div className="text-xs text-gray-500 capitalize">{agent.role}</div>
                      <div className="mt-2 flex items-center justify-between text-xs">
                        <span className="text-gray-400">{agent.tasks_completed} tasks</span>
                        <span className="text-green-600">{agent.success_rate}%</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Recent Activity */}
            <div>
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h2>
              <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
                {activity.slice(0, 5).map((item, i) => (
                  <div key={i} className="px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        item.type === 'objective' ? 'bg-cyan-100' : 'bg-gray-100'
                      }`}>
                        {item.type === 'objective' ? (
                          <Target size={16} className="text-cyan-600" />
                        ) : (
                          <Activity size={16} className="text-gray-600" />
                        )}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-800">{item.title}</div>
                        <div className="text-xs text-gray-500 capitalize">{item.action}</div>
                      </div>
                    </div>
                    <span className="text-xs text-gray-400">
                      {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'objectives' && (
          <div className="space-y-4">
            {objectives.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <Target size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-800 mb-2">No objectives yet</h3>
                <p className="text-gray-500 mb-4">Create your first objective to get started</p>
                <button
                  onClick={() => setShowNewObjective(true)}
                  className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium"
                >
                  Create Objective
                </button>
              </div>
            ) : (
              objectives.map(obj => (
                <div key={obj.id} className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${
                          obj.status === 'completed' ? 'bg-green-100 text-green-700' :
                          obj.status === 'in_progress' ? 'bg-cyan-100 text-cyan-700' :
                          obj.status === 'failed' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {obj.status.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-400 capitalize">{obj.type}</span>
                        <span className="text-xs text-gray-400">Priority: {obj.priority}</span>
                      </div>
                      <h3 className="text-base font-medium text-gray-800">{obj.title}</h3>
                      <p className="text-sm text-gray-500 mt-1">{obj.description}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {obj.status === 'pending' && (
                        <button
                          onClick={() => startObjective(obj.id)}
                          className="p-2 text-cyan-600 hover:bg-cyan-50 rounded-lg"
                        >
                          <Play size={18} />
                        </button>
                      )}
                      {obj.status === 'in_progress' && (
                        <button className="p-2 text-amber-600 hover:bg-amber-50 rounded-lg">
                          <Pause size={18} />
                        </button>
                      )}
                      <button className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg">
                        <MoreHorizontal size={18} />
                      </button>
                    </div>
                  </div>
                  {obj.quality_score && (
                    <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-4">
                      <span className="text-xs text-gray-500">Quality: {(obj.quality_score * 100).toFixed(0)}%</span>
                      <span className="text-xs text-gray-500">Cost: ${obj.cost_used?.toFixed(2) || '0.00'}</span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {selectedTab === 'agents' && (
          <div className="grid grid-cols-2 gap-4">
            {agents.map(agent => {
              const Icon = agentIcons[agent.role] || Bot;
              const gradient = agentColors[agent.role] || 'from-gray-500 to-gray-600';
              
              return (
                <div key={agent.id} className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center`}>
                        <Icon size={24} className="text-white" />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-800">{agent.name}</h3>
                        <p className="text-sm text-gray-500 capitalize">{agent.role.replace('_', ' ')}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => toggleAgent(agent.id)}
                      className={`px-3 py-1 rounded-lg text-sm font-medium ${
                        agent.status === 'active'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-500'
                      }`}
                    >
                      {agent.status === 'active' ? 'Active' : 'Inactive'}
                    </button>
                  </div>
                  <div className="mt-4 grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-800">{agent.tasks_completed}</div>
                      <div className="text-xs text-gray-500">Tasks</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-green-600">{agent.success_rate}%</div>
                      <div className="text-xs text-gray-500">Success</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-800">{agent.reputation_score}</div>
                      <div className="text-xs text-gray-500">Reputation</div>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="text-xs text-gray-400">Model: <span className="text-gray-600">{agent.model}</span></div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {selectedTab === 'activity' && (
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {activity.map((item, i) => (
              <div key={i} className="px-5 py-4 flex items-center justify-between hover:bg-gray-50">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    item.type === 'objective' ? 'bg-cyan-100' : 'bg-gray-100'
                  }`}>
                    {item.type === 'objective' ? (
                      <Target size={18} className="text-cyan-600" />
                    ) : (
                      <Activity size={18} className="text-gray-600" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium text-gray-800">{item.title}</div>
                    <div className="text-sm text-gray-500">
                      <span className="capitalize">{item.action}</span>
                      {item.agent && <span> • {item.agent}</span>}
                    </div>
                  </div>
                </div>
                <span className="text-sm text-gray-400">
                  {item.timestamp ? new Date(item.timestamp).toLocaleString() : ''}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* New Objective Modal */}
      {showNewObjective && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">New Objective</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Title</label>
                <input
                  type="text"
                  value={newObjective.title}
                  onChange={(e) => setNewObjective({ ...newObjective, title: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg"
                  placeholder="Build a REST API"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-600 mb-1">Description</label>
                <textarea
                  value={newObjective.description}
                  onChange={(e) => setNewObjective({ ...newObjective, description: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg resize-none"
                  rows={3}
                  placeholder="Create a REST API with authentication..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Type</label>
                  <select
                    value={newObjective.type}
                    onChange={(e) => setNewObjective({ ...newObjective, type: e.target.value })}
                    className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg"
                  >
                    <option value="code">Code</option>
                    <option value="content">Content</option>
                    <option value="automation">Automation</option>
                    <option value="research">Research</option>
                    <option value="mixed">Mixed</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Priority (1-10)</label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={newObjective.priority}
                    onChange={(e) => setNewObjective({ ...newObjective, priority: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg"
                  />
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={newObjective.auto_mode}
                  onChange={(e) => setNewObjective({ ...newObjective, auto_mode: e.target.checked })}
                  className="rounded"
                />
                <label className="text-sm text-gray-600">Auto mode (automatic execution)</label>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowNewObjective(false)}
                className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={createObjective}
                disabled={!newObjective.title || !newObjective.description}
                className="flex-1 px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-lg disabled:opacity-50"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrchestratorPage;
