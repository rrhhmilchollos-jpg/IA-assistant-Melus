import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Code, ChevronDown, ChevronRight, Terminal } from 'lucide-react';
import { Button } from './ui/button';
import { advancedAPI } from '../api/client';
import { toast } from '../hooks/use-toast';

const CodeViewer = ({ conversationId, isOpen, onClose }) => {
  const [codeBlocks, setCodeBlocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedBlocks, setExpandedBlocks] = useState({});
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    if (isOpen && conversationId) {
      loadCode();
    }
  }, [isOpen, conversationId]);

  const loadCode = async () => {
    setLoading(true);
    try {
      const result = await advancedAPI.getCode(conversationId);
      setCodeBlocks(result.code_blocks);
      // Expand all by default
      const expanded = {};
      result.code_blocks.forEach((_, i) => expanded[i] = true);
      setExpandedBlocks(expanded);
    } catch (error) {
      console.error('Failed to load code:', error);
      toast({
        title: "Error",
        description: "No se pudo cargar el código",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleBlock = (index) => {
    setExpandedBlocks(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const copyCode = async (code, index) => {
    await navigator.clipboard.writeText(code);
    setCopiedId(index);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getLanguageColor = (lang) => {
    const colors = {
      javascript: 'bg-yellow-500',
      python: 'bg-blue-500',
      bash: 'bg-green-500',
      html: 'bg-orange-500',
      css: 'bg-pink-500',
      json: 'bg-purple-500',
      text: 'bg-gray-500'
    };
    return colors[lang.toLowerCase()] || 'bg-gray-500';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#1a1a2e] rounded-xl border border-gray-700 w-full max-w-4xl max-h-[80vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-600 flex items-center justify-center">
              <Code size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Code Viewer</h2>
              <p className="text-sm text-gray-400">{codeBlocks.length} bloques de código</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-full h-8 w-8 p-0"
          >
            <X size={18} />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-400">Cargando código...</div>
            </div>
          ) : codeBlocks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Terminal size={48} className="text-gray-600 mb-4" />
              <h3 className="text-lg text-gray-300 mb-2">No hay código aún</h3>
              <p className="text-gray-500">Los bloques de código aparecerán aquí cuando el agente genere código</p>
            </div>
          ) : (
            codeBlocks.map((block, index) => (
              <div 
                key={index}
                className="bg-[#0d0d1a] rounded-lg border border-gray-800 overflow-hidden"
              >
                {/* Block Header */}
                <div 
                  className="flex items-center justify-between px-4 py-2 bg-gray-800/50 cursor-pointer hover:bg-gray-800 transition-colors"
                  onClick={() => toggleBlock(index)}
                >
                  <div className="flex items-center gap-3">
                    {expandedBlocks[index] ? (
                      <ChevronDown size={16} className="text-gray-400" />
                    ) : (
                      <ChevronRight size={16} className="text-gray-400" />
                    )}
                    <span className={`w-2 h-2 rounded-full ${getLanguageColor(block.language)}`} />
                    <span className="text-sm text-gray-300 font-medium">
                      {block.language.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(block.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      copyCode(block.code, index);
                    }}
                    className="text-gray-400 hover:text-white hover:bg-gray-700 h-7 px-2"
                  >
                    {copiedId === index ? (
                      <Check size={14} className="text-green-400" />
                    ) : (
                      <Copy size={14} />
                    )}
                  </Button>
                </div>

                {/* Code Content */}
                {expandedBlocks[index] && (
                  <div className="p-4 overflow-x-auto">
                    <pre className="text-sm font-mono text-green-300 whitespace-pre-wrap">
                      {block.code}
                    </pre>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeViewer;
