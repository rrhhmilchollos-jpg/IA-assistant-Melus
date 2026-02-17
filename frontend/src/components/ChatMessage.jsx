import React, { useState } from 'react';
import { Bot, User, Edit2, RefreshCw, Check, X, Copy, RotateCcw, ChevronRight, Terminal, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { messagesAPI, advancedAPI } from '../api/client';
import { toast } from '../hooks/use-toast';

const ChatMessage = ({ message, onMessageUpdated }) => {
  const isUser = message.role === 'user';
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isRollingBack, setIsRollingBack] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);
  
  const handleEdit = async () => {
    if (!editContent.trim()) return;
    
    try {
      await messagesAPI.edit(message.message_id, editContent);
      setIsEditing(false);
      onMessageUpdated();
      toast({
        title: "Mensaje editado",
        description: "El mensaje ha sido actualizado correctamente"
      });
    } catch (error) {
      console.error('Failed to edit message:', error);
      toast({
        title: "Error",
        description: "No se pudo editar el mensaje",
        variant: "destructive"
      });
    }
  };
  
  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      await messagesAPI.regenerate(message.message_id);
      onMessageUpdated();
      toast({
        title: "Respuesta regenerada",
        description: "Se ha generado una nueva respuesta"
      });
    } catch (error) {
      console.error('Failed to regenerate:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "No se pudo regenerar la respuesta",
        variant: "destructive"
      });
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleRollback = async () => {
    setIsRollingBack(true);
    try {
      const result = await advancedAPI.rollback(message.message_id);
      toast({
        title: "Rollback completado",
        description: `Se eliminaron ${result.messages_deleted} mensajes posteriores`
      });
      onMessageUpdated();
    } catch (error) {
      console.error('Failed to rollback:', error);
      toast({
        title: "Error",
        description: "No se pudo realizar el rollback",
        variant: "destructive"
      });
    } finally {
      setIsRollingBack(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast({
      title: "Copiado",
      description: "Contenido copiado al portapapeles"
    });
  };

  // Check if content looks like a command/code block
  const isCodeBlock = message.content.includes('```') ||
                      message.content.startsWith('$') || 
                      message.content.startsWith('sudo') ||
                      message.content.includes('cd /app') ||
                      message.content.includes('npm ') ||
                      message.content.includes('pip ');

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  // Render code blocks with syntax highlighting style
  const renderContent = (content) => {
    if (!content.includes('```')) {
      return <span className="whitespace-pre-wrap">{content}</span>;
    }

    const parts = content.split(/(```[\s\S]*?```)/g);
    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        const match = part.match(/```(\w+)?\n?([\s\S]*?)```/);
        if (match) {
          const lang = match[1] || 'code';
          const code = match[2];
          return (
            <div key={index} className="my-3 rounded-lg overflow-hidden bg-[#1a3a2a] border border-green-900/50">
              <div className="flex items-center justify-between px-3 py-1.5 bg-green-900/30 text-xs text-green-400">
                <span className="flex items-center gap-2">
                  <Terminal size={12} />
                  {lang.toUpperCase()}
                </span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(code);
                    toast({ title: "Código copiado" });
                  }}
                  className="hover:text-white"
                >
                  <Copy size={12} />
                </button>
              </div>
              <pre className="p-3 text-sm font-mono text-green-300 overflow-x-auto">
                {code}
              </pre>
            </div>
          );
        }
      }
      return <span key={index} className="whitespace-pre-wrap">{part}</span>;
    });
  };
  
  return (
    <div className={`group px-6 py-4 hover:bg-gray-900/30 transition-colors`} data-testid={`message-${message.message_id}`}>
      <div className="max-w-4xl mx-auto">
        {/* Message Header with Icon */}
        <div className="flex items-start gap-3">
          {/* Status Icon */}
          <div className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center mt-0.5 ${
            isUser 
              ? 'bg-blue-600' 
              : 'bg-purple-600'
          }`}>
            {isUser ? (
              <User size={14} className="text-white" />
            ) : (
              <Bot size={14} className="text-white" />
            )}
          </div>

          <div className="flex-1 min-w-0">
            {/* Message Title */}
            <div className="flex items-center gap-2 mb-2">
              <span className="text-gray-200 font-medium text-sm">
                {isUser ? 'You' : 'Assistant Melus'}
              </span>
              {message.edited && (
                <span className="text-xs text-gray-500">(edited)</span>
              )}
            </div>

            {/* Message Content */}
            {isEditing ? (
              <div className="space-y-2">
                <Textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="min-h-[100px] bg-gray-800 border-gray-700 text-white"
                />
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={handleEdit}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Check size={14} className="mr-1" />
                    Save
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setIsEditing(false);
                      setEditContent(message.content);
                    }}
                    className="border-gray-600 text-gray-300 hover:bg-gray-700"
                  >
                    <X size={14} className="mr-1" />
                    Cancel
                  </Button>
                </div>
              </div>
            ) : isCodeBlock && !isUser ? (
              /* Code Block Style */
              <div 
                className="bg-[#1a3a2a] border border-green-900/50 rounded-lg overflow-hidden cursor-pointer hover:bg-[#1f4533] transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                <div className="flex items-center justify-between px-4 py-2">
                  <div className="flex items-center gap-2 text-green-400 font-mono text-sm">
                    <Check size={14} className="text-green-500" />
                    <Terminal size={14} />
                    <span className="truncate">{message.content.substring(0, 60)}...</span>
                  </div>
                  <ChevronRight 
                    size={18} 
                    className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                  />
                </div>
                {isExpanded && (
                  <div className="px-4 py-3 border-t border-green-900/30 bg-[#0d1f15]">
                    <div className="text-green-300 text-sm">
                      {renderContent(message.content)}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* Regular Text */
              <div className="text-gray-300 leading-relaxed text-sm">
                {renderContent(message.content)}
              </div>
            )}

            {/* Message Footer */}
            <div className="flex items-center justify-between mt-3">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>{formatTime(message.timestamp)}</span>
                {message.model && !isUser && (
                  <span className="text-purple-400 font-medium">
                    {message.model}
                  </span>
                )}
                {message.tokens_used > 0 && !isUser && (
                  <span>{message.tokens_used} tokens</span>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {!isUser && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleRollback}
                      disabled={isRollingBack}
                      className="text-gray-400 hover:text-white hover:bg-gray-700 h-7 px-2 text-xs"
                    >
                      {isRollingBack ? (
                        <Loader2 size={12} className="animate-spin mr-1" />
                      ) : (
                        <RotateCcw size={12} className="mr-1" />
                      )}
                      Rollback
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCopy}
                      className="text-gray-400 hover:text-white hover:bg-gray-700 h-7 px-2 text-xs"
                    >
                      {copied ? (
                        <Check size={12} className="text-green-400 mr-1" />
                      ) : (
                        <Copy size={12} className="mr-1" />
                      )}
                      Copy
                    </Button>
                  </>
                )}
                {isUser && !isEditing && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                    className="text-gray-400 hover:text-white hover:bg-gray-700 h-7 px-2"
                  >
                    <Edit2 size={12} />
                  </Button>
                )}
                {!isUser && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleRegenerate}
                    disabled={isRegenerating}
                    className="text-gray-400 hover:text-white hover:bg-gray-700 h-7 px-2"
                  >
                    <RefreshCw size={12} className={isRegenerating ? 'animate-spin' : ''} />
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
