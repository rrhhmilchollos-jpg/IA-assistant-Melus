import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlusCircle, MessageSquare, Trash2, Sparkles, Zap, CreditCard, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { useAuth } from '../context/AuthContext';
import CreditModal from './CreditModal';

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
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);

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
          className="w-full bg-white text-gray-900 hover:bg-gray-100 font-medium mb-4"
        >
          <PlusCircle size={18} className="mr-2" />
          Nueva Conversación
        </Button>

        {/* Credits Display */}
        <div 
          className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-750 transition-colors"
          onClick={() => setIsCreditModalOpen(true)}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-400">Créditos</span>
            <CreditCard size={16} className="text-gray-400" />
          </div>
          <div className="flex items-center gap-2">
            <Zap size={18} className="text-yellow-500" />
            <span className="font-bold text-lg">{userCredits?.toLocaleString() || 0}</span>
          </div>
          <p className="text-xs text-gray-500 mt-1">Click para comprar más</p>
        </div>
      </div>

      {/* Conversations List */}
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-2">
          {conversations.map((conversation) => (
            <div
              key={conversation.conversation_id}
              className={`group relative p-3 rounded-lg cursor-pointer transition-all ${
                currentConversationId === conversation.conversation_id
                  ? 'bg-gray-800 border border-gray-700'
                  : 'hover:bg-gray-800'
              }`}
              onClick={() => onSelectConversation(conversation.conversation_id)}
            >
              <div className="flex items-start gap-3">
                <MessageSquare size={16} className="mt-1 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">
                    {conversation.title}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(conversation.updated_at).toLocaleDateString('es-ES', {
                      day: 'numeric',
                      month: 'short'
                    })}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conversation.conversation_id);
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
      <div className="p-4 border-t border-gray-800">
        {user && (
          <div className="mb-3">
            <div className="flex items-center gap-3 mb-2">
              {user.picture && (
                <img 
                  src={user.picture} 
                  alt={user.name}
                  className="w-8 h-8 rounded-full"
                />
              )}
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{user.name}</div>
                <div className="text-xs text-gray-400 truncate">{user.email}</div>
              </div>
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          className="w-full justify-start text-gray-300 hover:text-white hover:bg-gray-800"
          onClick={handleLogout}
        >
          <LogOut size={16} className="mr-2" />
          Cerrar Sesión
        </Button>
        <p className="text-xs text-gray-400 mt-3">Assistant Melus v1.0</p>
      </div>
      
      {/* Credit Modal */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
    </div>
  );
};

export default Sidebar;