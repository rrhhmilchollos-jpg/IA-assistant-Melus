import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Bot, Brain, Code2, TestTube, Zap, DollarSign,
  Play, Pause, RefreshCw, CheckCircle, XCircle, Clock,
  MessageSquare, ChevronRight, Loader2, Send, ArrowLeft
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Agent icons mapping
const agentIcons = {
  planner: Brain,
  researcher: Bot,
  developer: Code2,
  qa: TestTube,
  optimizer: Zap,
  cost_controller: DollarSign
};

// Agent colors
const agentColors = {
  planner: 'from-purple-500 to-purple-700',
  researcher: 'from-blue-500 to-blue-700',
  developer: 'from-green-500 to-green-700',
  qa: 'from-yellow-500 to-yellow-700',
  optimizer: 'from-orange-500 to-orange-700',
  cost_controller: 'from-red-500 to-red-700'
};

// Status badge component
const StatusBadge = ({ status }) => {
  const styles = {
    idle: 'bg-gray-600 text-gray-200',
    working: 'bg-cyan-500 text-white animate-pulse',
    completed: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    waiting: 'bg-yellow-500 text-black'
  };

  const icons = {
    idle: Clock,
    working: Loader2,
    completed: CheckCircle,
    error: XCircle,
    waiting: Clock
  };

  const Icon = icons[status] || Clock;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${styles[status] || styles.idle}`}>
      <Icon className={`w-3 h-3 ${status === 'working' ? 'animate-spin' : ''}`} />
      {status}
    </span>
  );
};

// Agent Card Component
const AgentCard = ({ agent, isActive }) => {
  const Icon = agentIcons[agent.agent_type] || Bot;
  const colorClass = agentColors[agent.agent_type] || 'from-gray-500 to-gray-700';

  return (
    <div className={`relative p-4 rounded-xl border transition-all duration-300 ${
      isActive 
        ? 'bg-gray-800/80 border-cyan-500/50 shadow-lg shadow-cyan-500/20' 
        : 'bg-gray-900/50 border-gray-800 hover:border-gray-700'
    }`}>
      {/* Active indicator */}
      {isActive && (
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full animate-ping" />
      )}
      
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClass} flex items-center justify-center flex-shrink-0`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-semibold text-white truncate">{agent.name}</h3>
            <StatusBadge status={agent.status} />
          </div>
          
          <p className="text-xs text-gray-400 mt-1 line-clamp-2">
            {agent.description}
          </p>
          
          {agent.current_task && (
            <div className="mt-2 p-2 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-cyan-400 font-medium">Current Task:</p>
              <p className="text-xs text-gray-300 truncate">{agent.current_task.description}</p>
            </div>
          )}
          
          <div className="mt-2 text-xs text-gray-500">
            Tasks completed: {agent.tasks_completed}
          </div>
        </div>
      </div>
    </div>
  );
};

// Message Component
const MessageItem = ({ message }) => {
  const fromColor = agentColors[message.from_agent] || 'from-gray-500 to-gray-700';
  
  return (
    <div className="flex items-start gap-3 p-3 bg-gray-800/30 rounded-lg">
      <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${fromColor} flex items-center justify-center flex-shrink-0`}>
        <MessageSquare className="w-4 h-4 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 text-xs">
          <span className="font-medium text-white capitalize">{message.from_agent}</span>
          <ChevronRight className="w-3 h-3 text-gray-500" />
          <span className="text-gray-400 capitalize">{message.to_agent || 'All'}</span>
          <span className="text-gray-600 ml-auto">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-sm text-gray-300 mt-1">{message.content}</p>
      </div>
    </div>
  );
};

// Main Dashboard Component
const AgentDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [agents, setAgents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState({ pending: [], completed: [] });
  const [prompt, setPrompt] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const token = localStorage.getItem('session_token');

  // Fetch agent status
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agents-v3/status`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await response.json();
      setAgents(Object.values(data.agents));
      setCurrentProject(data.current_project);
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  // Fetch messages
  const fetchMessages = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agents-v3/messages?limit=20`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await response.json();
      setMessages(data.messages);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agents-v3/tasks`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      console.error('Error fetching tasks:', err);
    }
  };

  // Start pipeline
  const startPipeline = async () => {
    if (!prompt.trim()) return;
    
    setIsRunning(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/agents-v3/pipeline/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({ prompt: prompt.trim() })
      });
      
      const data = await response.json();
      setCurrentProject(data.project_id);
      
      // Start polling for updates
      const pollInterval = setInterval(async () => {
        await fetchStatus();
        await fetchMessages();
        await fetchTasks();
        
        // Check if pipeline is complete
        const statusRes = await fetch(`${API_BASE}/api/agents-v3/status`, {
          headers: { 'X-Session-Token': token }
        });
        const statusData = await statusRes.json();
        
        if (!statusData.current_project) {
          clearInterval(pollInterval);
          setIsRunning(false);
        }
      }, 2000);
      
    } catch (err) {
      setError(err.message);
      setIsRunning(false);
    }
  };

  // Initial fetch and polling
  useEffect(() => {
    fetchStatus();
    fetchMessages();
    fetchTasks();
    
    const interval = setInterval(() => {
      fetchStatus();
      if (isRunning) {
        fetchMessages();
        fetchTasks();
      }
    }, 3000);
    
    return () => clearInterval(interval);
  }, [isRunning]);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/home')}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-xl font-bold">Multi-Agent Dashboard</h1>
              <p className="text-sm text-gray-400">Watch AI agents build your app in real-time</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {currentProject && (
              <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded-full text-sm">
                Project: {currentProject}
              </span>
            )}
            <button 
              onClick={fetchStatus}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Prompt Input */}
        <div className="mb-6 p-4 bg-gray-900/50 border border-gray-800 rounded-xl">
          <div className="flex gap-3">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your app idea... e.g., 'Build a todo app with user authentication and categories'"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 resize-none"
              rows={2}
              disabled={isRunning}
            />
            <button
              onClick={startPipeline}
              disabled={isRunning || !prompt.trim()}
              className={`px-6 py-3 rounded-xl font-medium flex items-center gap-2 transition-all ${
                isRunning 
                  ? 'bg-gray-700 text-gray-400 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:opacity-90'
              }`}
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start Build
                </>
              )}
            </button>
          </div>
          
          {error && (
            <p className="mt-2 text-red-400 text-sm">{error}</p>
          )}
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Agents Grid */}
          <div className="lg:col-span-2">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Bot className="w-5 h-5 text-cyan-400" />
              AI Agents
            </h2>
            <div className="grid sm:grid-cols-2 gap-4">
              {agents.map((agent) => (
                <AgentCard 
                  key={agent.agent_type} 
                  agent={agent} 
                  isActive={agent.status === 'working'}
                />
              ))}
            </div>

            {/* Tasks Section */}
            <div className="mt-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                Recent Tasks ({tasks.completed.length})
              </h2>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {tasks.completed.slice(-5).reverse().map((task) => (
                  <div key={task.id} className="flex items-center gap-3 p-3 bg-gray-900/50 rounded-lg">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white truncate">{task.description}</p>
                      <p className="text-xs text-gray-500 capitalize">{task.agent_type}</p>
                    </div>
                    <StatusBadge status={task.status} />
                  </div>
                ))}
                {tasks.completed.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">No tasks completed yet</p>
                )}
              </div>
            </div>
          </div>

          {/* Messages Panel */}
          <div className="lg:col-span-1">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-purple-400" />
              Agent Communication
            </h2>
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 h-[500px] flex flex-col">
              <div className="flex-1 overflow-y-auto space-y-3">
                {messages.length > 0 ? (
                  messages.map((msg) => (
                    <MessageItem key={msg.id} message={msg} />
                  ))
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-gray-500">
                    <MessageSquare className="w-12 h-12 mb-2 opacity-50" />
                    <p className="text-sm">No messages yet</p>
                    <p className="text-xs">Start a build to see agents communicate</p>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentDashboard;
