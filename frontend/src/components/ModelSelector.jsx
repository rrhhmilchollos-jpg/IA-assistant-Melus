import React, { useState, useEffect } from 'react';
import { Settings, Cpu, Zap, Sparkles, ChevronDown, Check, X } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Model icons by provider
const ProviderIcons = {
  openai: '🤖',
  anthropic: '🧠',
  gemini: '✨'
};

// Mode icons
const ModeIcons = {
  e1: '⚡',
  'e1.5': '⚖️',
  e2: '🎯',
  pro: '👑',
  prototype: '🚀',
  mobile: '📱'
};

const ModelSelector = ({ token, onModelChange, onModeChange }) => {
  const [models, setModels] = useState([]);
  const [modes, setModes] = useState([]);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [selectedMode, setSelectedMode] = useState('e1');
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('modes'); // 'modes' or 'models'
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchModels();
    fetchModes();
  }, [token]);

  const fetchModels = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/brain/models`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await res.json();
      setModels(data.models || []);
    } catch (err) {
      console.error('Error fetching models:', err);
    }
  };

  const fetchModes = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/brain/modes`, {
        headers: { 'X-Session-Token': token }
      });
      const data = await res.json();
      setModes(data.modes || []);
    } catch (err) {
      console.error('Error fetching modes:', err);
    }
  };

  const selectModel = async (modelKey) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/brain/set-model?model_key=${modelKey}`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      const data = await res.json();
      if (data.success) {
        setSelectedModel(modelKey);
        onModelChange?.(modelKey, data);
      }
    } catch (err) {
      console.error('Error setting model:', err);
    }
    setLoading(false);
  };

  const selectMode = async (modeKey) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/brain/set-mode?mode=${modeKey}`, {
        method: 'POST',
        headers: { 'X-Session-Token': token }
      });
      const data = await res.json();
      if (data.success) {
        setSelectedMode(modeKey);
        onModeChange?.(modeKey, data);
        // Update selected model to mode's default
        const mode = modes.find(m => m.id === modeKey);
        if (mode) {
          setSelectedModel(mode.default_model);
        }
      }
    } catch (err) {
      console.error('Error setting mode:', err);
    }
    setLoading(false);
  };

  const selectedModeInfo = modes.find(m => m.id === selectedMode);
  const selectedModelInfo = models.find(m => m.id === selectedModel);

  return (
    <div className="relative">
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-700 transition-all"
      >
        <span className="text-lg">{ModeIcons[selectedMode] || '⚡'}</span>
        <div className="text-left">
          <div className="text-sm font-medium text-white">
            {selectedModeInfo?.name || 'E-1'}
          </div>
          <div className="text-xs text-gray-400">
            {selectedModelInfo?.name || 'GPT-4o'}
          </div>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl z-50 overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-700">
            <button
              onClick={() => setActiveTab('modes')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === 'modes'
                  ? 'text-cyan-400 border-b-2 border-cyan-400 bg-gray-800/50'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Zap className="w-4 h-4 inline mr-2" />
              Modos
            </button>
            <button
              onClick={() => setActiveTab('models')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === 'models'
                  ? 'text-cyan-400 border-b-2 border-cyan-400 bg-gray-800/50'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Cpu className="w-4 h-4 inline mr-2" />
              Modelos
            </button>
          </div>

          {/* Content */}
          <div className="max-h-96 overflow-y-auto">
            {activeTab === 'modes' ? (
              <div className="p-2">
                {modes.map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => selectMode(mode.id)}
                    disabled={loading}
                    className={`w-full text-left p-3 rounded-lg mb-1 transition-all ${
                      selectedMode === mode.id
                        ? 'bg-cyan-500/20 border border-cyan-500/50'
                        : 'hover:bg-gray-800 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{ModeIcons[mode.id] || '⚡'}</span>
                        <div>
                          <div className="font-medium text-white">{mode.name}</div>
                          <div className="text-xs text-gray-400">{mode.description}</div>
                        </div>
                      </div>
                      {selectedMode === mode.id && (
                        <Check className="w-5 h-5 text-cyan-400" />
                      )}
                    </div>
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-300">
                        {mode.default_model}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        mode.focus === 'fullstack' ? 'bg-purple-500/20 text-purple-300' :
                        mode.focus === 'frontend' ? 'bg-blue-500/20 text-blue-300' :
                        'bg-green-500/20 text-green-300'
                      }`}>
                        {mode.focus}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        mode.speed === 'fast' ? 'bg-yellow-500/20 text-yellow-300' :
                        mode.speed === 'thorough' ? 'bg-red-500/20 text-red-300' :
                        'bg-gray-500/20 text-gray-300'
                      }`}>
                        {mode.speed}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-2">
                {/* Group by provider */}
                {['openai', 'anthropic', 'gemini'].map(provider => {
                  const providerModels = models.filter(m => m.provider === provider);
                  if (providerModels.length === 0) return null;
                  
                  return (
                    <div key={provider} className="mb-4">
                      <div className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                        <span>{ProviderIcons[provider]}</span>
                        {provider}
                      </div>
                      {providerModels.map((model) => (
                        <button
                          key={model.id}
                          onClick={() => selectModel(model.id)}
                          disabled={loading}
                          className={`w-full text-left p-3 rounded-lg mb-1 transition-all ${
                            selectedModel === model.id
                              ? 'bg-cyan-500/20 border border-cyan-500/50'
                              : 'hover:bg-gray-800 border border-transparent'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-white">{model.name}</span>
                                {model.is_pro && (
                                  <span className="text-xs px-1.5 py-0.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded font-medium">
                                    PRO
                                  </span>
                                )}
                                {model.is_fast && (
                                  <span className="text-xs px-1.5 py-0.5 bg-green-500/20 text-green-300 rounded">
                                    Fast
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-gray-400 mt-0.5">{model.description}</div>
                            </div>
                            {selectedModel === model.id && (
                              <Check className="w-5 h-5 text-cyan-400" />
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Close button */}
          <div className="p-2 border-t border-gray-700">
            <button
              onClick={() => setIsOpen(false)}
              className="w-full py-2 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
