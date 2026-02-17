import React, { useState } from 'react';
import { Bot, User, Edit2, RefreshCw, Check, X } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { messagesAPI } from '../api/client';
import { toast } from '../hooks/use-toast';

const ChatMessage = ({ message, onMessageUpdated }) => {
  const isUser = message.role === 'user';
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [isRegenerating, setIsRegenerating] = useState(false);
  
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
  
  return (
    <div className={`group flex gap-4 p-6 ${
      isUser ? 'bg-transparent' : 'bg-gray-50'
    }`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-purple-600 text-white'
      }`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      
      <div className="flex-1 space-y-2">
        <div className="flex items-center justify-between">
          <div className="font-semibold text-sm text-gray-900">
            {isUser ? 'Tú' : 'Assistant Melus'}
            {message.edited && (
              <span className="ml-2 text-xs text-gray-500 font-normal">(editado)</span>
            )}
          </div>
          
          {/* Action buttons - shown on hover */}
          <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2">
            {isUser && !isEditing && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing(true)}
                className="h-8 px-2"
              >
                <Edit2 size={14} />
              </Button>
            )}
            
            {!isUser && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRegenerate}
                disabled={isRegenerating}
                className="h-8 px-2"
              >
                <RefreshCw size={14} className={isRegenerating ? 'animate-spin' : ''} />
              </Button>
            )}
          </div>
        </div>
        
        {isEditing ? (
          <div className="space-y-2">
            <Textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="min-h-[100px]"
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleEdit}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Check size={14} className="mr-1" />
                Guardar
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setIsEditing(false);
                  setEditContent(message.content);
                }}
              >
                <X size={14} className="mr-1" />
                Cancelar
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-gray-800 whitespace-pre-wrap leading-relaxed">
            {message.content}
          </div>
        )}
        
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>
            {new Date(message.timestamp).toLocaleTimeString('es-ES', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </span>
          {message.model && !isUser && (
            <span className="text-purple-600 font-medium">
              {message.model}
            </span>
          )}
          {message.tokens_used > 0 && !isUser && (
            <span className="text-gray-400">
              {message.tokens_used} tokens
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
