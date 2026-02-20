import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Brain,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Settings,
  Database,
  Star,
  Download,
  AlertTriangle,
  RefreshCw,
  ChevronLeft,
  Activity,
  Zap,
  Clock,
  FileCode,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { Toaster, toast } from '../components/ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const LearningDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    const token = localStorage.getItem('session_token');
    
    try {
      const [statsRes, settingsRes] = await Promise.all([
        fetch(`${API_BASE}/api/learning/stats`, {
          headers: { 'X-Session-Token': token }
        }),
        fetch(`${API_BASE}/api/learning/settings`, {
          headers: { 'X-Session-Token': token }
        })
      ]);
      
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }
      
      if (settingsRes.ok) {
        const data = await settingsRes.json();
        setSettings(data.settings || {});
      }
    } catch (error) {
      toast.error('Error loading learning data');
    } finally {
      setLoading(false);
    }
  };

  const runOptimization = async () => {
    setOptimizing(true);
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/learning/optimize/run`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      
      if (response.ok) {
        toast.success('Optimization started');
        setTimeout(loadData, 2000);
      } else {
        toast.error('Optimization failed');
      }
    } catch (error) {
      toast.error('Error running optimization');
    } finally {
      setOptimizing(false);
    }
  };

  const updateSetting = async (key, value) => {
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/learning/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({ key, value })
      });
      
      if (response.ok) {
        setSettings(prev => ({ ...prev, [key]: value }));
        toast.success('Setting updated');
      }
    } catch (error) {
      toast.error('Error updating setting');
    }
  };

  const MetricCard = ({ title, value, icon: Icon, trend, color = 'cyan' }) => (
    <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-800 mt-1">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {trend && (
            <div className={`flex items-center gap-1 mt-1 text-sm ${
              trend === 'improving' ? 'text-green-500' : 
              trend === 'declining' ? 'text-red-500' : 'text-gray-400'
            }`}>
              {trend === 'improving' ? <TrendingUp size={14} /> : 
               trend === 'declining' ? <TrendingDown size={14} /> : null}
              <span className="capitalize">{trend}</span>
            </div>
          )}
        </div>
        <div className={`w-10 h-10 rounded-lg bg-${color}-100 flex items-center justify-center`}>
          <Icon size={20} className={`text-${color}-500`} />
        </div>
      </div>
    </div>
  );

  const ToggleSetting = ({ label, description, settingKey }) => (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div>
        <p className="text-sm font-medium text-gray-700">{label}</p>
        <p className="text-xs text-gray-400">{description}</p>
      </div>
      <button
        onClick={() => updateSetting(settingKey, !settings[settingKey])}
        className={`w-12 h-6 rounded-full transition-colors relative ${
          settings[settingKey] ? 'bg-cyan-500' : 'bg-gray-300'
        }`}
      >
        <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
          settings[settingKey] ? 'left-7' : 'left-1'
        }`} />
      </button>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center gap-3 text-gray-500">
          <RefreshCw className="animate-spin" size={24} />
          <span>Loading learning data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster />
      
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/home')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500"
              data-testid="back-btn"
            >
              <ChevronLeft size={20} />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                <Brain size={22} className="text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-800">Learning System</h1>
                <p className="text-xs text-gray-400">Continuous improvement engine</p>
              </div>
            </div>
          </div>
          
          <button
            onClick={runOptimization}
            disabled={optimizing}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors disabled:opacity-50"
            data-testid="optimize-btn"
          >
            <RefreshCw size={16} className={optimizing ? 'animate-spin' : ''} />
            {optimizing ? 'Optimizing...' : 'Run Optimization'}
          </button>
        </div>
        
        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'memory', label: 'Memory', icon: Database },
              { id: 'metrics', label: 'Metrics', icon: Activity },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'text-cyan-600 border-cyan-500'
                    : 'text-gray-500 border-transparent hover:text-gray-700'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>
      
      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                title="Memory Entries"
                value={stats?.memory?.total_entries || 0}
                icon={Database}
                color="cyan"
              />
              <MetricCard
                title="Total Feedback"
                value={stats?.feedback?.total_feedbacks || 0}
                icon={Star}
                color="yellow"
              />
              <MetricCard
                title="Projects Today"
                value={stats?.metrics?.projects_today || 0}
                icon={FileCode}
                color="green"
              />
              <MetricCard
                title="Total Metrics"
                value={stats?.metrics?.total_metrics || 0}
                icon={Activity}
                color="purple"
              />
            </div>
            
            {/* Learning Status */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Memory by Type */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Database size={18} className="text-cyan-500" />
                  Memory Distribution
                </h3>
                {Object.keys(stats?.memory?.by_type || {}).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(stats.memory.by_type).map(([type, data]) => (
                      <div key={type} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-full ${
                            type === 'prompt' ? 'bg-blue-500' :
                            type === 'code' ? 'bg-green-500' :
                            type === 'error' ? 'bg-red-500' :
                            type === 'solution' ? 'bg-purple-500' : 'bg-gray-400'
                          }`} />
                          <span className="text-sm text-gray-600 capitalize">{type}</span>
                        </div>
                        <div className="text-right">
                          <span className="text-sm font-medium text-gray-800">{data.count}</span>
                          <span className="text-xs text-gray-400 ml-2">
                            avg: {(data.avg_quality * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 text-center py-8">
                    No memory entries yet. Generate projects to build knowledge.
                  </p>
                )}
              </div>
              
              {/* Feedback Summary */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Star size={18} className="text-yellow-500" />
                  Feedback Summary
                </h3>
                {Object.keys(stats?.feedback?.feedback_by_type || {}).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(stats.feedback.feedback_by_type).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">
                          {type.replace(/_/g, ' ')}
                        </span>
                        <span className="text-sm font-medium text-gray-800">{count}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 text-center py-8">
                    No feedback recorded yet.
                  </p>
                )}
              </div>
            </div>
            
            {/* Prompt Performance */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Zap size={18} className="text-orange-500" />
                Prompt Performance
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                {['planner', 'generator', 'validator'].map(promptType => {
                  const data = stats?.prompts?.[promptType] || {};
                  return (
                    <div key={promptType} className="border border-gray-100 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 capitalize">{promptType}</span>
                        {data.trend && (
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            data.trend === 'improving' ? 'bg-green-100 text-green-600' :
                            data.trend === 'declining' ? 'bg-red-100 text-red-600' :
                            'bg-gray-100 text-gray-600'
                          }`}>
                            {data.trend}
                          </span>
                        )}
                      </div>
                      {data.status === 'no_data' ? (
                        <p className="text-xs text-gray-400">No data yet</p>
                      ) : (
                        <div className="text-xs text-gray-500">
                          <div>Quality: {((data.current_version?.avg_quality || 0) * 100).toFixed(0)}%</div>
                          <div>Usage: {data.total_usage || 0} times</div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'memory' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Vector Memory Store</h3>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-500 mb-4">
                    The memory stores embeddings of successful prompts, generated code, 
                    errors, and solutions to improve future generations.
                  </p>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-600">Total Entries</span>
                      <span className="text-sm font-medium">{stats?.memory?.total_entries || 0}</span>
                    </div>
                    {Object.entries(stats?.memory?.by_type || {}).map(([type, data]) => (
                      <div key={type} className="flex items-center justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600 capitalize">{type}</span>
                        <div>
                          <span className="text-sm font-medium">{data.count}</span>
                          <span className="text-xs text-gray-400 ml-2">
                            ({(data.avg_quality * 100).toFixed(0)}% quality)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">How Memory Works</h4>
                  <ul className="space-y-2 text-sm text-gray-500">
                    <li className="flex items-start gap-2">
                      <CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Stores successful prompts and their project types</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Saves high-quality generated code as examples</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Records errors to avoid in future generations</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Tracks user iterations as improvement patterns</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'metrics' && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {stats?.metrics?.week_stats && Object.entries(stats.metrics.week_stats).map(([key, data]) => (
                <div key={key} className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-400 uppercase mb-1">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p className="text-xl font-semibold text-gray-800">
                    {data.avg?.toFixed(2) || 0}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span>Min: {data.min?.toFixed(2) || 0}</span>
                    <span>Max: {data.max?.toFixed(2) || 0}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {data.count} samples (7 days)
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'settings' && (
          <div className="max-w-2xl">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Settings size={18} className="text-gray-500" />
                Learning Settings
              </h3>
              
              <div className="space-y-1">
                <ToggleSetting
                  label="Auto Learn"
                  description="Automatically learn from project generations"
                  settingKey="auto_learn"
                />
                <ToggleSetting
                  label="Auto Optimize Prompts"
                  description="Automatically improve prompts based on performance"
                  settingKey="auto_optimize_prompts"
                />
                <ToggleSetting
                  label="Cleanup Low Quality"
                  description="Automatically remove low-quality memory entries"
                  settingKey="cleanup_low_quality"
                />
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-100">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Thresholds</h4>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-600">
                      Minimum Quality Threshold: {(settings.min_quality_threshold * 100).toFixed(0)}%
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={(settings.min_quality_threshold || 0.6) * 100}
                      onChange={(e) => updateSetting('min_quality_threshold', e.target.value / 100)}
                      className="w-full mt-1"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default LearningDashboard;
