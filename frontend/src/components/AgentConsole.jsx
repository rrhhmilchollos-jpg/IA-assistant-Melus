import React, { useState, useEffect, useRef } from 'react';
import { agentsAPI, projectsAPI } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  Play, 
  Square, 
  Cpu, 
  Palette, 
  Code, 
  Server, 
  Database, 
  Cloud,
  CheckCircle,
  Clock,
  AlertCircle,
  Download,
  Copy,
  ChevronDown,
  ChevronRight,
  Zap
} from 'lucide-react';

const AGENT_ICONS = {
  orchestrator: Cpu,
  design: Palette,
  frontend: Code,
  backend: Server,
  database: Database,
  deploy: Cloud
};

const AGENT_COLORS = {
  orchestrator: 'purple',
  design: 'pink',
  frontend: 'blue',
  backend: 'green',
  database: 'orange',
  deploy: 'cyan'
};

const AgentConsole = ({ onProjectCreated }) => {
  const { user, updateCredits } = useAuth();
  const [appDescription, setAppDescription] = useState('');
  const [appName, setAppName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [agentLogs, setAgentLogs] = useState([]);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [project, setProject] = useState(null);
  const [expandedAgents, setExpandedAgents] = useState({});
  const [agentCosts, setAgentCosts] = useState({});
  const logsEndRef = useRef(null);

  useEffect(() => {
    loadAgentCosts();
  }, []);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [agentLogs]);

  const loadAgentCosts = async () => {
    try {
      const response = await agentsAPI.getCosts();
      setAgentCosts(response.costs || {});
    } catch (error) {
      console.error('Failed to load agent costs:', error);
    }
  };

  const addLog = (agent, message, type = 'info', data = null) => {
    setAgentLogs(prev => [...prev, {
      id: Date.now(),
      agent,
      message,
      type,
      data,
      timestamp: new Date().toISOString()
    }]);
  };

  const handleGenerateApp = async () => {
    if (!appDescription.trim()) return;

    const projectName = appName.trim() || 'Mi Aplicación';
    
    setIsGenerating(true);
    setAgentLogs([]);
    setProject(null);

    const totalEstimated = Object.values(agentCosts).reduce((a, b) => a + b, 0);
    
    addLog('system', `Iniciando generación de "${projectName}"...`, 'info');
    addLog('system', `Créditos estimados: ${totalEstimated}`, 'info');

    try {
      // Step 1: Orchestrator
      setCurrentAgent('orchestrator');
      addLog('orchestrator', 'Analizando requisitos del proyecto...', 'working');
      
      const analysis = await agentsAPI.analyze(appDescription);
      addLog('orchestrator', 'Análisis completado', 'success', analysis.analysis);
      updateCredits(analysis.credits_remaining);

      // Step 2: Design Agent
      setCurrentAgent('design');
      addLog('design', 'Diseñando UI/UX y wireframes...', 'working');
      
      const designResult = await agentsAPI.execute('design', 
        `Diseña la UI/UX para: ${appDescription}`,
        { analysis: analysis.analysis }
      );
      addLog('design', 'Diseño completado', 'success', designResult.result?.result);
      updateCredits(designResult.credits_remaining);

      // Step 3: Database Agent
      setCurrentAgent('database');
      addLog('database', 'Diseñando esquema de base de datos...', 'working');
      
      const dbResult = await agentsAPI.execute('database',
        `Diseña la base de datos para: ${appDescription}`,
        { analysis: analysis.analysis, design: designResult.result?.result }
      );
      addLog('database', 'Base de datos diseñada', 'success', dbResult.result?.result);
      updateCredits(dbResult.credits_remaining);

      // Step 4: Backend Agent
      setCurrentAgent('backend');
      addLog('backend', 'Generando código backend...', 'working');
      
      const backendResult = await agentsAPI.execute('backend',
        `Genera el backend para: ${appDescription}`,
        { analysis: analysis.analysis, database: dbResult.result?.result }
      );
      addLog('backend', 'Backend generado', 'success', backendResult.result?.result);
      updateCredits(backendResult.credits_remaining);

      // Step 5: Frontend Agent
      setCurrentAgent('frontend');
      addLog('frontend', 'Generando código frontend...', 'working');
      
      const frontendResult = await agentsAPI.execute('frontend',
        `Genera el frontend para: ${appDescription}`,
        { 
          analysis: analysis.analysis, 
          design: designResult.result?.result,
          backend: backendResult.result?.result 
        }
      );
      addLog('frontend', 'Frontend generado', 'success', frontendResult.result?.result);
      updateCredits(frontendResult.credits_remaining);

      // Step 6: Deploy Agent
      setCurrentAgent('deploy');
      addLog('deploy', 'Configurando despliegue...', 'working');
      
      const deployResult = await agentsAPI.execute('deploy',
        `Configura el despliegue para: ${appDescription}`,
        { backend: backendResult.result?.result, frontend: frontendResult.result?.result }
      );
      addLog('deploy', 'Configuración de despliegue lista', 'success', deployResult.result?.result);
      updateCredits(deployResult.credits_remaining);

      // Create project with all results
      const newProject = await projectsAPI.create(appName, appDescription);
      setProject({
        ...newProject,
        results: {
          analysis: analysis.analysis,
          design: designResult.result?.result,
          database: dbResult.result?.result,
          backend: backendResult.result?.result,
          frontend: frontendResult.result?.result,
          deploy: deployResult.result?.result
        }
      });

      addLog('system', `¡Proyecto "${appName}" generado exitosamente!`, 'success');
      
      if (onProjectCreated) {
        onProjectCreated(newProject);
      }

    } catch (error) {
      console.error('Generation failed:', error);
      addLog('system', `Error: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setIsGenerating(false);
      setCurrentAgent(null);
    }
  };

  const toggleAgentExpanded = (logId) => {
    setExpandedAgents(prev => ({
      ...prev,
      [logId]: !prev[logId]
    }));
  };

  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
  };

  const getStatusIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'working': return <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-400" />;
      default: return <Zap className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <div className="bg-[#0d0d1a] min-h-screen text-white" data-testid="agent-console">
      {/* Input Section */}
      <div className="p-6 border-b border-purple-500/20">
        <h2 className="text-xl font-bold mb-4">Generador de Aplicaciones IA</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Nombre de la aplicación</label>
            <input
              type="text"
              value={appName}
              onChange={(e) => setAppName(e.target.value)}
              placeholder="Mi Aplicación"
              className="w-full bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-purple-500 outline-none"
              disabled={isGenerating}
              data-testid="app-name-input"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">Describe tu aplicación</label>
            <textarea
              value={appDescription}
              onChange={(e) => setAppDescription(e.target.value)}
              placeholder="Describe la aplicación que quieres crear en lenguaje natural. Por ejemplo: 'Una aplicación de gestión de tareas con autenticación de usuarios, donde los usuarios pueden crear, editar y eliminar tareas, marcarlas como completadas y organizarlas por categorías.'"
              className="w-full h-32 bg-[#1a1a2e] border border-purple-500/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-purple-500 outline-none resize-none"
              disabled={isGenerating}
              data-testid="app-description-input"
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Créditos disponibles: <span className="text-purple-400 font-medium">{user?.credits || 0}</span>
              <span className="mx-2">|</span>
              Estimado: <span className="text-yellow-400">{Object.values(agentCosts).reduce((a, b) => a + b, 0)} créditos</span>
            </div>
            
            <button
              onClick={handleGenerateApp}
              disabled={isGenerating || !appDescription.trim()}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                isGenerating
                  ? 'bg-red-500/20 text-red-400 cursor-not-allowed'
                  : 'bg-purple-500 text-white hover:bg-purple-600'
              }`}
              data-testid="generate-app-btn"
            >
              {isGenerating ? (
                <>
                  <Square className="w-5 h-5" />
                  Generando...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Generar Aplicación
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Agent Status Bar */}
      <div className="px-6 py-4 border-b border-purple-500/20 bg-[#1a1a2e]/50">
        <div className="flex items-center gap-4">
          {Object.entries(AGENT_ICONS).map(([agent, Icon]) => (
            <div
              key={agent}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
                currentAgent === agent
                  ? 'bg-purple-500/30 ring-2 ring-purple-500'
                  : agentLogs.some(l => l.agent === agent && l.type === 'success')
                  ? 'bg-green-500/20'
                  : 'bg-white/5'
              }`}
            >
              <Icon className={`w-4 h-4 ${
                currentAgent === agent ? 'text-purple-400 animate-pulse' : 'text-gray-400'
              }`} />
              <span className="text-xs capitalize">{agent}</span>
              {agentLogs.some(l => l.agent === agent && l.type === 'success') && (
                <CheckCircle className="w-3 h-3 text-green-400" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Console Output */}
      <div className="p-6">
        <div className="bg-[#0a0a12] rounded-xl border border-purple-500/20 overflow-hidden">
          <div className="px-4 py-2 bg-[#1a1a2e] border-b border-purple-500/20 flex items-center justify-between">
            <span className="text-sm text-gray-400">Consola de Agentes</span>
            {agentLogs.length > 0 && (
              <span className="text-xs text-purple-400">{agentLogs.length} eventos</span>
            )}
          </div>
          
          <div className="h-96 overflow-y-auto p-4 font-mono text-sm space-y-2">
            {agentLogs.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                Describe tu aplicación y haz clic en "Generar" para comenzar
              </div>
            ) : (
              agentLogs.map(log => {
                const Icon = AGENT_ICONS[log.agent] || Zap;
                const hasData = log.data && typeof log.data === 'object';
                const isExpanded = expandedAgents[log.id];

                return (
                  <div key={log.id} className="group">
                    <div
                      className={`flex items-start gap-3 p-2 rounded ${
                        log.type === 'error' ? 'bg-red-500/10' :
                        log.type === 'success' ? 'bg-green-500/10' :
                        log.type === 'working' ? 'bg-yellow-500/10' :
                        'bg-white/5'
                      }`}
                    >
                      {getStatusIcon(log.type)}
                      <Icon className={`w-4 h-4 mt-0.5 ${
                        log.agent === 'system' ? 'text-purple-400' : 'text-gray-400'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-purple-400 capitalize">[{log.agent}]</span>
                          <span className={`${
                            log.type === 'error' ? 'text-red-400' :
                            log.type === 'success' ? 'text-green-400' :
                            'text-gray-300'
                          }`}>
                            {log.message}
                          </span>
                        </div>
                        
                        {hasData && (
                          <button
                            onClick={() => toggleAgentExpanded(log.id)}
                            className="flex items-center gap-1 mt-1 text-xs text-gray-500 hover:text-gray-300"
                          >
                            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                            Ver detalles
                          </button>
                        )}
                        
                        {hasData && isExpanded && (
                          <div className="mt-2 p-3 bg-[#0d0d1a] rounded border border-purple-500/20 overflow-x-auto">
                            <pre className="text-xs text-gray-400 whitespace-pre-wrap">
                              {JSON.stringify(log.data, null, 2)}
                            </pre>
                            <button
                              onClick={() => copyCode(JSON.stringify(log.data, null, 2))}
                              className="mt-2 flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300"
                            >
                              <Copy className="w-3 h-3" />
                              Copiar
                            </button>
                          </div>
                        )}
                      </div>
                      <span className="text-xs text-gray-600">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
            <div ref={logsEndRef} />
          </div>
        </div>

        {/* Generated Project Summary */}
        {project && (
          <div className="mt-6 bg-[#1a1a2e] rounded-xl border border-green-500/30 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-green-400 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Proyecto Generado: {project.name}
              </h3>
              <button
                onClick={() => {/* Download logic */}}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
              >
                <Download className="w-4 h-4" />
                Descargar Código
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(project.results || {}).map(([agent, result]) => (
                <div key={agent} className="p-4 bg-[#0d0d1a] rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    {React.createElement(AGENT_ICONS[agent] || Cpu, { className: 'w-4 h-4 text-purple-400' })}
                    <span className="text-sm font-medium capitalize">{agent}</span>
                  </div>
                  <p className="text-xs text-gray-400 truncate">
                    {result?.files?.length || 0} archivos generados
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentConsole;
