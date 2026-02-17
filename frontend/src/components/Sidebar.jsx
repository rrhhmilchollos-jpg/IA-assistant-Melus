import React from 'react';
import { useNavigate } from 'react-router-dom';
import { PlusCircle, MessageSquare, Trash2, Sparkles, Zap, CreditCard, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { useAuth } from '../context/AuthContext';

const Sidebar = ({ 
  conversations, 
  currentConversationId, 
  onSelectConversation, 
  onNewConversation,
  onDeleteConversation,
  userCredits
}) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };
  return (
    <div className="w-80 bg-gray-900 text-white flex flex-col h-screen">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
            <Sparkles size={20} />
          </div>
          <h1 className="text-xl font-bold">Assistant Melus</h1>
        </div>
        
        <Button 
          onClick={onNewConversation}
          className="w-full bg-white text-gray-900 hover:bg-gray-100 font-medium"
        >
          <PlusCircle size={18} className="mr-2" />
          Nueva Conversación
        </Button>
      </div>

      {/* Conversations List */}
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-2">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`group relative p-3 rounded-lg cursor-pointer transition-all ${
                currentConversationId === conversation.id
                  ? 'bg-gray-800 border border-gray-700'
                  : 'hover:bg-gray-800'
              }`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="flex items-start gap-3">
                <MessageSquare size={16} className="mt-1 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">
                    {conversation.title}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {conversation.timestamp.toLocaleDateString('es-ES', {
                      day: 'numeric',
                      month: 'short'
                    })}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conversation.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-600 rounded"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800 text-xs text-gray-400">
        <p>Assistant Melus v1.0</p>
        <p className="mt-1">Tu asistente de IA personal</p>
      </div>
    </div>
  );
};

export default Sidebar;