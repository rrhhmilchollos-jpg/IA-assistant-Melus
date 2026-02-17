import React, { useState, useEffect } from 'react';
import { X, ExternalLink, RefreshCw, Clock, MessageSquare, Zap, Bookmark, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { advancedAPI } from '../api/client';
import { toast } from '../hooks/use-toast';

const PreviewPanel = ({ conversationId, isOpen, onClose }) => {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [redeploying, setRedeploying] = useState(false);

  useEffect(() => {
    if (isOpen && conversationId) {
      loadPreview();
    }
  }, [isOpen, conversationId]);

  const loadPreview = async () => {
    setLoading(true);
    try {
      const result = await advancedAPI.getPreview(conversationId);
      setPreview(result);
    } catch (error) {
      console.error('Failed to load preview:', error);
      toast({
        title: "Error",
        description: "No se pudo cargar la información",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRedeploy = async () => {
    setRedeploying(true);
    try {
      await advancedAPI.redeploy(conversationId);
      toast({
        title: "Redeploy iniciado",
        description: "Los cambios se están aplicando"
      });
    } catch (error) {
      console.error('Redeploy error:', error);
      toast({
        title: "Error",
        description: "No se pudo iniciar el redeploy",
        variant: "destructive"
      });
    } finally {
      setRedeploying(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#1a1a2e] rounded-xl border border-gray-700 w-full max-w-2xl shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
              <ExternalLink size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Preview</h2>
              <p className="text-sm text-gray-400">Información del proyecto</p>
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
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
            </div>
          ) : preview ? (
            <div className="space-y-6">
              {/* Project Title */}
              <div className="text-center">
                <h3 className="text-2xl font-bold text-white mb-2">{preview.title}</h3>
                <div className="flex items-center justify-center gap-2">
                  {preview.ultra_mode && (
                    <span className="bg-yellow-600 text-white px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1">
                      <Zap size={12} />
                      Ultra
                    </span>
                  )}
                  {preview.saved && (
                    <span className="bg-purple-600 text-white px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1">
                      <Bookmark size={12} />
                      Saved
                    </span>
                  )}
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#0d0d1a] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 text-gray-400 mb-2">
                    <MessageSquare size={16} />
                    <span className="text-sm">Mensajes</span>
                  </div>
                  <div className="text-2xl font-bold text-white">{preview.message_count}</div>
                </div>
                
                <div className="bg-[#0d0d1a] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 text-gray-400 mb-2">
                    <Zap size={16} />
                    <span className="text-sm">Modelo</span>
                  </div>
                  <div className="text-lg font-bold text-purple-400">{preview.model}</div>
                </div>

                <div className="bg-[#0d0d1a] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 text-gray-400 mb-2">
                    <Clock size={16} />
                    <span className="text-sm">Creado</span>
                  </div>
                  <div className="text-sm text-white">{formatDate(preview.created_at)}</div>
                </div>
                
                <div className="bg-[#0d0d1a] rounded-lg p-4 border border-gray-800">
                  <div className="flex items-center gap-2 text-gray-400 mb-2">
                    <RefreshCw size={16} />
                    <span className="text-sm">Última actividad</span>
                  </div>
                  <div className="text-sm text-white">{formatDate(preview.last_activity)}</div>
                </div>
              </div>

              {/* Summary */}
              {preview.summary && (
                <div className="bg-[#0d0d1a] rounded-lg p-4 border border-gray-800">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Resumen</h4>
                  <p className="text-gray-300 text-sm whitespace-pre-wrap">{preview.summary}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <Button
                  onClick={handleRedeploy}
                  disabled={redeploying}
                  className="flex-1 bg-yellow-600 hover:bg-yellow-700 text-white"
                >
                  {redeploying ? (
                    <Loader2 size={16} className="animate-spin mr-2" />
                  ) : (
                    <RefreshCw size={16} className="mr-2" />
                  )}
                  Redeploy
                </Button>
                <Button
                  variant="outline"
                  onClick={onClose}
                  className="flex-1 border-gray-600 text-gray-300 hover:bg-gray-800"
                >
                  Cerrar
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              No se encontró información del proyecto
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PreviewPanel;
