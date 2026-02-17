import React, { useState, useRef } from 'react';
import { Send, Paperclip, Save, Sparkles, Mic, Square, Zap, X, FileText, Image, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { attachmentsAPI, conversationsAPI, voiceAPI } from '../api/client';
import { toast } from '../hooks/use-toast';

const PromptBox = ({ 
  onSendMessage, 
  disabled, 
  selectedModel, 
  onModelChange,
  isAgentRunning = false,
  conversationId,
  onSummarized,
  onSaved
}) => {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [ultraMode, setUltraMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [budget] = useState(10000);
  const [usedBudget] = useState(0);
  
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim(), attachments);
      setMessage('');
      setAttachments([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setIsUploading(true);
    
    for (const file of files) {
      try {
        // Read file as base64
        const reader = new FileReader();
        reader.onload = async () => {
          try {
            const result = await attachmentsAPI.upload(reader.result, file.name, file.type, conversationId);
            setAttachments(prev => [...prev, {
              id: result.attachment_id,
              name: file.name,
              type: file.type,
              size: result.file_size
            }]);
            toast({
              title: "Archivo adjuntado",
              description: file.name
            });
          } catch (error) {
            console.error('Upload error:', error);
            toast({
              title: "Error al subir archivo",
              description: error.response?.data?.detail || "No se pudo subir el archivo",
              variant: "destructive"
            });
          }
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error('File read error:', error);
      }
    }
    
    setIsUploading(false);
    e.target.value = '';
  };

  const removeAttachment = (id) => {
    setAttachments(prev => prev.filter(a => a.id !== id));
  };

  const handleSave = async () => {
    if (!conversationId) {
      toast({
        title: "Error",
        description: "Selecciona una conversación primero",
        variant: "destructive"
      });
      return;
    }

    try {
      const result = await conversationsAPI.save(conversationId);
      toast({
        title: result.saved ? "Guardado" : "Removido de guardados",
        description: result.saved ? "Conversación guardada" : "Conversación removida"
      });
      onSaved && onSaved(result.saved);
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: "Error",
        description: "No se pudo guardar",
        variant: "destructive"
      });
    }
  };

  const handleSummarize = async () => {
    if (!conversationId) {
      toast({
        title: "Error",
        description: "Selecciona una conversación primero",
        variant: "destructive"
      });
      return;
    }

    setIsSummarizing(true);
    try {
      const result = await conversationsAPI.summarize(conversationId);
      toast({
        title: "Resumen generado",
        description: `Usados ${result.tokens_used} créditos`
      });
      onSummarized && onSummarized(result.summary);
    } catch (error) {
      console.error('Summarize error:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "No se pudo generar el resumen",
        variant: "destructive"
      });
    } finally {
      setIsSummarizing(false);
    }
  };

  const handleUltraToggle = async () => {
    if (!conversationId) {
      toast({
        title: "Error",
        description: "Selecciona una conversación primero",
        variant: "destructive"
      });
      return;
    }

    try {
      const newState = !ultraMode;
      setUltraMode(newState);
      toast({
        title: newState ? "Ultra Mode Activado" : "Ultra Mode Desactivado",
        description: newState ? "Usando modelo de mayor rendimiento" : "Usando modelo estándar"
      });
    } catch (error) {
      console.error('Ultra toggle error:', error);
      toast({
        title: "Error",
        description: "No se pudo cambiar el modo",
        variant: "destructive"
      });
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.onloadend = async () => {
          try {
            setIsTranscribing(true);
            const result = await voiceAPI.transcribe(reader.result, 'es');
            if (result.text) {
              setMessage(prev => prev + (prev ? ' ' : '') + result.text);
              toast({
                title: "Transcripción completada",
                description: `Créditos usados: ${result.credits_used}`
              });
            }
          } catch (error) {
            console.error('Transcription error:', error);
            toast({
              title: "Error de transcripción",
              description: error.response?.data?.detail || "No se pudo transcribir el audio",
              variant: "destructive"
            });
          } finally {
            setIsTranscribing(false);
          }
        };
        reader.readAsDataURL(audioBlob);
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      
      toast({
        title: "Grabando...",
        description: "Haz clic de nuevo para detener"
      });
    } catch (error) {
      console.error('Recording error:', error);
      toast({
        title: "Error",
        description: "No se pudo acceder al micrófono",
        variant: "destructive"
      });
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="bg-[#0d0d1a] border-t border-gray-800" data-testid="prompt-box">
      <div className="max-w-4xl mx-auto p-4">
        {/* Status Indicator */}
        {isAgentRunning && (
          <div className="flex items-center gap-2 mb-3 text-green-400" data-testid="agent-status">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm font-medium">Agent is running...</span>
          </div>
        )}

        {/* Attachments Preview */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {attachments.map((att) => (
              <div 
                key={att.id}
                className="flex items-center gap-2 bg-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
              >
                {att.type.startsWith('image/') ? (
                  <Image size={14} className="text-blue-400" />
                ) : (
                  <FileText size={14} className="text-purple-400" />
                )}
                <span className="max-w-[150px] truncate">{att.name}</span>
                <button
                  onClick={() => removeAttachment(att.id)}
                  className="text-gray-500 hover:text-white"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Main Input Container */}
        <div className="bg-[#1a1a2e] rounded-xl border border-gray-700 overflow-hidden">
          {/* Message Input */}
          <div className="relative">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Agent"
              className="min-h-[60px] bg-transparent border-0 text-white placeholder-gray-500 resize-none focus:ring-0 focus-visible:ring-0 text-base px-4 py-3"
              disabled={disabled}
              data-testid="message-input"
            />
          </div>

          {/* Action Bar */}
          <div className="flex items-center justify-between px-3 py-2 border-t border-gray-700/50">
            {/* Left Actions */}
            <div className="flex items-center gap-1">
              {/* File Input (hidden) */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                className="hidden"
                multiple
                accept=".png,.jpg,.jpeg,.gif,.webp,.pdf,.txt,.md,.py,.js,.json,.csv"
              />
              
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled || isUploading}
                onClick={() => fileInputRef.current?.click()}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg h-8 px-2"
                data-testid="attach-button"
              >
                {isUploading ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Paperclip size={16} />
                )}
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled || !conversationId}
                onClick={handleSave}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg h-8 px-3"
                data-testid="save-button"
              >
                <Save size={16} className="mr-1.5" />
                <span className="text-xs">Save</span>
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled || isSummarizing || !conversationId}
                onClick={handleSummarize}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg h-8 px-3"
                data-testid="summarize-button"
              >
                {isSummarizing ? (
                  <Loader2 size={16} className="animate-spin mr-1.5" />
                ) : (
                  <Sparkles size={16} className="mr-1.5" />
                )}
                <span className="text-xs">Summarize</span>
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled || !conversationId}
                onClick={handleUltraToggle}
                className={`rounded-lg h-8 px-3 ${
                  ultraMode 
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                data-testid="ultra-button"
              >
                <Zap size={16} className="mr-1.5" />
                <span className="text-xs">Ultra</span>
              </Button>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled}
                onClick={handleMicClick}
                className={`rounded-full h-8 w-8 p-0 ${
                  isRecording 
                    ? 'bg-red-600 text-white hover:bg-red-700 animate-pulse' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                data-testid="mic-button"
              >
                <Mic size={16} />
              </Button>
              
              {disabled ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-red-600 hover:bg-red-700 text-white rounded-full h-8 w-8 p-0"
                  data-testid="stop-button"
                >
                  <Square size={14} />
                </Button>
              ) : (
                <Button 
                  type="submit" 
                  onClick={handleSubmit}
                  disabled={!message.trim() || disabled}
                  className="bg-purple-600 hover:bg-purple-700 text-white rounded-full h-8 w-8 p-0"
                  data-testid="send-button"
                >
                  <Send size={14} />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Budget Display */}
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <span className="text-gray-400">Budget:</span>
            <span className="text-white font-mono">
              {usedBudget.toLocaleString()} / {budget.toLocaleString()}
            </span>
            {ultraMode && (
              <span className="bg-yellow-600 text-white px-2 py-0.5 rounded text-[10px] font-medium">
                ULTRA
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Sparkles size={12} className="text-purple-500" />
            <span>Powered by {selectedModel || 'gpt-4o'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptBox;
