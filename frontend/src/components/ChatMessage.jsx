import React from 'react';
import { Bot, User } from 'lucide-react';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex gap-4 p-6 ${
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
        <div className="font-semibold text-sm text-gray-900">
          {isUser ? 'Tú' : 'Assistant Melus'}
        </div>
        <div className="text-gray-800 whitespace-pre-wrap leading-relaxed">
          {message.content}
        </div>
        <div className="text-xs text-gray-500">
          {message.timestamp.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;