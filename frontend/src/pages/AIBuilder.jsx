import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Send, Loader2, Plus, ChevronLeft, Code2, Eye, Download,
  FileCode, FolderTree, Sparkles, Bot, User, Copy, Check,
  Play, Settings, Layers, Smartphone, Monitor, RefreshCw
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Message Component
const ChatMessage = ({ message, isUser }) => {
  const [copied, setCopied] = useState(false);

  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-gradient-to-br from-cyan-500 to-blue-600' 
          : 'bg-gradient-to-br from-purple-500 to-pink-600'
      }`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>
      
      <div className={`max-w-[80%] ${isUser ? 'text-right' : ''}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser 
            ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white' 
            : 'bg-gray-800 text-gray-100'
        }`}>
          {message.type === 'code' ? (
            <div className="relative">
              <pre className="text-sm overflow-x-auto bg-gray-900 rounded-lg p-3 text-left">
                <code>{message.content}</code>
              </pre>
              <button 
                onClick={() => copyCode(message.content)}
                className="absolute top-2 right-2 p-1 bg-gray-700 rounded hover:bg-gray-600"
              >
                {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          ) : (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          )}
        </div>
        
        {message.files && message.files.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.files.map((file, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-gray-400 bg-gray-800/50 rounded-lg px-3 py-2">
                <FileCode className="w-4 h-4 text-cyan-400" />
                <span>{file.path}</span>
              </div>
            ))}
          </div>
        )}
        
        <span className="text-xs text-gray-500 mt-1 block">
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};

// File Tree Component
const FileTree = ({ files, onSelectFile, selectedFile }) => {
  const getFileIcon = (path) => {
    if (path.endsWith('.jsx') || path.endsWith('.js')) return '⚛️';
    if (path.endsWith('.css')) return '🎨';
    if (path.endsWith('.html')) return '📄';
    if (path.endsWith('.json')) return '📋';
    if (path.endsWith('.py')) return '🐍';
    return '📁';
  };

  return (
    <div className="space-y-1">
      {files.map((file, i) => (
        <button
          key={i}
          onClick={() => onSelectFile(file)}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm transition-colors ${
            selectedFile?.path === file.path
              ? 'bg-cyan-500/20 text-cyan-400'
              : 'hover:bg-gray-800 text-gray-300'
          }`}
        >
          <span>{getFileIcon(file.path)}</span>
          <span className="truncate">{file.path}</span>
        </button>
      ))}
    </div>
  );
};

// Code Preview Component
const CodePreview = ({ file }) => {
  if (!file) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <Code2 className="w-12 h-12 mb-2 opacity-50" />
        <p>Selecciona un archivo para ver el código</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <span className="text-sm font-medium text-white">{file.path}</span>
        <button className="p-1 hover:bg-gray-700 rounded">
          <Copy className="w-4 h-4" />
        </button>
      </div>
      <pre className="flex-1 overflow-auto p-4 text-sm text-gray-300 bg-gray-900">
        <code>{file.content}</code>
      </pre>
    </div>
  );
};

// Main AI Builder Component
const AIBuilder = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'text',
      content: '¡Hola! Soy el AI Builder de MelusAI. Describe la aplicación que quieres crear y la construiré para ti. Por ejemplo:\n\n• "Crea una app de tareas con categorías"\n• "Haz un dashboard de ventas con gráficos"\n• "Construye un blog con autenticación"',
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [projectName, setProjectName] = useState('Mi Proyecto');
  const [previewKey, setPreviewKey] = useState(Date.now());
  const messagesEndRef = useRef(null);
  const token = localStorage.getItem('session_token');

  // Generate Preview HTML from files
  const generatePreviewHTML = () => {
    if (generatedFiles.length === 0) return '';
    
    // Find index.html or create one
    const indexFile = generatedFiles.find(f => f.path === 'index.html' || f.path.endsWith('index.html'));
    if (indexFile) {
      return indexFile.content;
    }
    
    // Find JSX/JS and CSS files
    const jsxFiles = generatedFiles.filter(f => f.path.endsWith('.jsx') || f.path.endsWith('.js'));
    const cssFiles = generatedFiles.filter(f => f.path.endsWith('.css'));
    
    // Build preview HTML
    let html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${projectName}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
      ${cssFiles.map(f => f.content).join('\n')}
    </style>
</head>
<body class="bg-gray-100">
    <div id="root"></div>
`;
    
    // Add each script
    jsxFiles.forEach(file => {
      html += `<script type="text/babel">\n${file.content}\n</script>\n`;
    });
    
    // Add render call
    html += `
    <script type="text/babel">
        if (typeof App !== 'undefined') {
            ReactDOM.createRoot(document.getElementById('root')).render(<App />);
        }
    </script>
</body>
</html>`;
    
    return html;
  };
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeTab, setActiveTab] = useState('chat'); // chat, files, preview
  const [projectName, setProjectName] = useState('Mi Proyecto');
  const messagesEndRef = useRef(null);
  const token = localStorage.getItem('session_token');

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message
  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'text',
      content: input.trim(),
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Add thinking message
      const thinkingId = Date.now().toString() + '_thinking';
      setMessages(prev => [...prev, {
        id: thinkingId,
        type: 'text',
        content: '🤔 Analizando tu solicitud y generando código...',
        isUser: false,
        timestamp: new Date()
      }]);

      // Call the pipeline API
      const response = await fetch(`${API_BASE}/api/agents-v3/pipeline/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({ 
          prompt: input.trim(),
          project_name: projectName
        })
      });

      const data = await response.json();

      // Poll for results
      let attempts = 0;
      const maxAttempts = 30;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const statusRes = await fetch(`${API_BASE}/api/agents-v3/status`, {
          headers: { 'X-Session-Token': token }
        });
        const statusData = await statusRes.json();
        
        if (!statusData.current_project) {
          // Pipeline completed
          break;
        }
        attempts++;
      }

      // Get tasks to find generated code
      const tasksRes = await fetch(`${API_BASE}/api/agents-v3/tasks`, {
        headers: { 'X-Session-Token': token }
      });
      const tasksData = await tasksRes.json();

      // Find developer task output
      const devTask = tasksData.completed.find(t => t.agent_type === 'developer');
      const files = devTask?.output_data?.files || [];

      // Remove thinking message and add response
      setMessages(prev => prev.filter(m => m.id !== thinkingId));

      if (files.length > 0) {
        setGeneratedFiles(files);
        setSelectedFile(files[0]);

        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          type: 'text',
          content: `✨ ¡Proyecto generado exitosamente!\n\nHe creado ${files.length} archivos para tu aplicación. Puedes ver el código en la pestaña "Archivos" o continuar agregando funcionalidades.\n\n¿Qué más te gustaría añadir?`,
          isUser: false,
          timestamp: new Date(),
          files: files
        }]);
      } else {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          type: 'text',
          content: '¡Entendido! He procesado tu solicitud. ¿Podrías darme más detalles sobre las funcionalidades específicas que necesitas?',
          isUser: false,
          timestamp: new Date()
        }]);
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'text',
        content: '❌ Hubo un error procesando tu solicitud. Por favor intenta de nuevo.',
        isUser: false,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Download project
  const downloadProject = () => {
    if (generatedFiles.length === 0) return;
    
    const content = generatedFiles.map(f => `// ${f.path}\n${f.content}`).join('\n\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName.replace(/\s+/g, '_')}.txt`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-md">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/home')}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-gray-400" />
            </button>
            
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="font-semibold text-white">AI Builder</h1>
                <p className="text-xs text-gray-400">Construye apps con IA</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white w-40"
              placeholder="Nombre del proyecto"
            />
            
            {generatedFiles.length > 0 && (
              <button
                onClick={downloadProject}
                className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/20 text-cyan-400 rounded-lg text-sm hover:bg-cyan-500/30"
              >
                <Download className="w-4 h-4" />
                Descargar
              </button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-t border-gray-800">
          {[
            { id: 'chat', label: 'Chat', icon: Bot },
            { id: 'files', label: 'Archivos', icon: FolderTree, count: generatedFiles.length },
            { id: 'preview', label: 'Vista Previa', icon: Eye }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-cyan-400 border-b-2 border-cyan-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
              {tab.count > 0 && (
                <span className="px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 rounded text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map(message => (
                <ChatMessage key={message.id} message={message} isUser={message.isUser} />
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-800 p-4">
              <div className="flex gap-3">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder="Describe lo que quieres crear... Ej: 'Crea una app de notas con etiquetas y búsqueda'"
                  className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 resize-none"
                  rows={2}
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !input.trim()}
                  className={`px-4 rounded-xl flex items-center justify-center transition-all ${
                    isLoading || !input.trim()
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:opacity-90'
                  }`}
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
              
              {/* Quick prompts */}
              <div className="flex flex-wrap gap-2 mt-3">
                {[
                  'Añade autenticación de usuarios',
                  'Agrega una base de datos',
                  'Crea un formulario de contacto',
                  'Añade un dashboard'
                ].map(prompt => (
                  <button
                    key={prompt}
                    onClick={() => setInput(prompt)}
                    className="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded-full text-xs transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'files' && (
          <div className="flex-1 flex">
            {/* File Tree */}
            <div className="w-64 border-r border-gray-800 p-4 overflow-y-auto">
              <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <FolderTree className="w-4 h-4" />
                Archivos del Proyecto
              </h3>
              {generatedFiles.length > 0 ? (
                <FileTree 
                  files={generatedFiles} 
                  onSelectFile={setSelectedFile}
                  selectedFile={selectedFile}
                />
              ) : (
                <p className="text-sm text-gray-500">No hay archivos generados aún</p>
              )}
            </div>

            {/* Code View */}
            <div className="flex-1 bg-gray-900">
              <CodePreview file={selectedFile} />
            </div>
          </div>
        )}

        {activeTab === 'preview' && (
          <div className="flex-1 flex flex-col bg-gray-900">
            {/* Preview Header */}
            <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <span className="text-sm text-gray-400 ml-2">Live Preview</span>
              </div>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setPreviewKey(Date.now())}
                  className="p-1.5 hover:bg-gray-700 rounded"
                  title="Refresh"
                >
                  <RefreshCw className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>
            
            {/* Preview Content */}
            {generatedFiles.length > 0 ? (
              <div className="flex-1 bg-white">
                <iframe
                  key={previewKey}
                  srcDoc={generatePreviewHTML()}
                  className="w-full h-full border-0"
                  title="Live Preview"
                  sandbox="allow-scripts"
                />
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center max-w-md">
                  <div className="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Monitor className="w-8 h-8 text-gray-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">Vista Previa</h3>
                  <p className="text-gray-400">
                    Genera un proyecto primero para ver la vista previa en vivo
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIBuilder;
