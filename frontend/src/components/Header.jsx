import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Home, Plus, Zap, Code, Eye, RotateCcw, 
  User, LogOut, Settings, Receipt, Loader2,
  X, Shield, Wand2
} from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import CreditModal from './CreditModal';
import TransactionHistory from './TransactionHistory';
import CodeViewer from './CodeViewer';
import PreviewPanel from './PreviewPanel';
import { conversationsAPI } from '../api/client';
import { toast } from '../hooks/use-toast';

const Header = ({ 
  conversations = [], 
  currentConversationId, 
  onSelectConversation,
  onNewConversation,
  onCloseConversation
}) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
  const [isTransactionHistoryOpen, setIsTransactionHistoryOpen] = useState(false);
  const [isCodeViewerOpen, setIsCodeViewerOpen] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [isRedeploying, setIsRedeploying] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleRedeploy = async () => {
    if (!currentConversationId) {
      toast({
        title: "Error",
        description: "Selecciona una conversación primero",
        variant: "destructive"
      });
      return;
    }

    setIsRedeploying(true);
    try {
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
      setIsRedeploying(false);
    }
  };

  // Get active tabs (last 5 conversations)
  const activeTabs = conversations.slice(0, 5);

  return (
    <>
      <header className="bg-[#1a1a2e] border-b border-gray-800" data-testid="main-header">
        <div className="flex items-center justify-between h-14 px-4">
          {/* Left side - Logo and Tabs */}
          <div className="flex items-center gap-1">
            {/* Home Button */}
            <button 
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 px-3 py-2 text-gray-300 hover:bg-gray-800 rounded-lg transition-colors"
              data-testid="home-button"
            >
              <Home size={18} />
              <span className="text-sm font-medium">Home</span>
            </button>

            {/* Generator Button */}
            <button 
              onClick={() => navigate('/generator')}
              className="flex items-center gap-2 px-3 py-2 text-purple-400 hover:bg-purple-500/20 rounded-lg transition-colors"
              data-testid="generator-button"
            >
              <Wand2 size={18} />
              <span className="text-sm font-medium">Generar App</span>
            </button>

            {/* Project Tabs */}
            <div className="flex items-center ml-2">
              {activeTabs.map((conv, index) => (
                <div 
                  key={conv.conversation_id}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm cursor-pointer transition-colors ${
                    conv.conversation_id === currentConversationId
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                  }`}
                  onClick={() => onSelectConversation(conv.conversation_id)}
                  data-testid={`tab-${index}`}
                >
                  <div className={`w-2 h-2 rounded-full ${
                    conv.conversation_id === currentConversationId 
                      ? 'bg-green-500' 
                      : 'bg-gray-600'
                  }`} />
                  <span className="max-w-[120px] truncate">
                    {conv.title || 'Sin título'}
                  </span>
                  {conv.conversation_id === currentConversationId && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onCloseConversation && onCloseConversation(conv.conversation_id);
                      }}
                      className="ml-1 p-0.5 hover:bg-gray-600 rounded"
                    >
                      <X size={12} />
                    </button>
                  )}
                </div>
              ))}

              {/* New Tab Button */}
              <button 
                onClick={onNewConversation}
                className="flex items-center justify-center w-8 h-8 text-gray-400 hover:bg-gray-800 hover:text-white rounded-lg transition-colors ml-1"
                data-testid="new-tab-button"
              >
                <Plus size={18} />
              </button>
            </div>
          </div>

          {/* Right side - Credits and Actions */}
          <div className="flex items-center gap-3">
            {/* Credits Display */}
            <button
              onClick={() => setIsCreditModalOpen(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border border-yellow-500/30 rounded-full px-4 py-1.5 hover:from-yellow-500/30 hover:to-yellow-600/30 transition-all"
              data-testid="credits-button"
            >
              <Zap size={16} className="text-yellow-400" />
              <span className="text-yellow-400 font-bold">
                {user?.credits?.toLocaleString() || 0}
              </span>
            </button>

            {/* Buy Credits Button */}
            <Button
              onClick={() => setIsCreditModalOpen(true)}
              className="bg-green-600 hover:bg-green-700 text-white rounded-full px-4 py-1.5 h-auto text-sm font-medium"
              data-testid="buy-credits-button"
            >
              Comprar créditos
            </Button>

            {/* Action Buttons */}
            <div className="flex items-center gap-1 ml-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCodeViewerOpen(true)}
                disabled={!currentConversationId}
                className="text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg"
                data-testid="code-button"
              >
                <Code size={16} className="mr-2" />
                Code
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsPreviewOpen(true)}
                disabled={!currentConversationId}
                className="text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg"
                data-testid="preview-button"
              >
                <Eye size={16} className="mr-2" />
                Preview
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRedeploy}
                disabled={isRedeploying || !currentConversationId}
                className="bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg"
                data-testid="redeploy-button"
              >
                {isRedeploying ? (
                  <Loader2 size={16} className="mr-2 animate-spin" />
                ) : (
                  <RotateCcw size={16} className="mr-2" />
                )}
                Redeploy
              </Button>
            </div>

            {/* Admin Button (only for admins) */}
            {user?.is_admin && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/admin')}
                className="text-yellow-400 hover:text-yellow-300 hover:bg-yellow-500/20 rounded-lg"
                data-testid="admin-button"
              >
                <Shield size={16} className="mr-2" />
                Admin
              </Button>
            )}

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center justify-center w-9 h-9 rounded-full bg-purple-600 text-white font-bold text-sm hover:bg-purple-700 transition-colors ml-2">
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 bg-[#1a1a2e] border-gray-700 text-gray-200">
                <div className="px-3 py-2 border-b border-gray-700">
                  <div className="font-medium">{user?.name || 'Usuario'}</div>
                  <div className="text-xs text-gray-400">{user?.email || ''}</div>
                  {user?.is_admin && (
                    <span className="inline-block mt-1 px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded">
                      Admin
                    </span>
                  )}
                </div>
                <DropdownMenuItem 
                  onClick={() => setIsCreditModalOpen(true)}
                  className="text-gray-200 focus:bg-gray-700 focus:text-white cursor-pointer"
                >
                  <Zap className="mr-2 h-4 w-4 text-yellow-400" />
                  Comprar Créditos
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => setIsTransactionHistoryOpen(true)}
                  className="text-gray-200 focus:bg-gray-700 focus:text-white cursor-pointer"
                >
                  <Receipt className="mr-2 h-4 w-4" />
                  Historial de Compras
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => navigate('/generator')}
                  className="text-gray-200 focus:bg-gray-700 focus:text-white cursor-pointer"
                >
                  <Wand2 className="mr-2 h-4 w-4 text-purple-400" />
                  Generador de Apps
                </DropdownMenuItem>
                {user?.is_admin && (
                  <DropdownMenuItem 
                    onClick={() => navigate('/admin')}
                    className="text-yellow-400 focus:bg-gray-700 focus:text-yellow-300 cursor-pointer"
                  >
                    <Shield className="mr-2 h-4 w-4" />
                    Panel de Admin
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator className="bg-gray-700" />
                <DropdownMenuItem className="text-gray-200 focus:bg-gray-700 focus:text-white cursor-pointer">
                  <Settings className="mr-2 h-4 w-4" />
                  Configuración
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={handleLogout} 
                  className="text-red-400 focus:bg-gray-700 focus:text-red-300 cursor-pointer"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Cerrar Sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Modals */}
      <CreditModal 
        isOpen={isCreditModalOpen} 
        onClose={() => setIsCreditModalOpen(false)} 
      />
      <TransactionHistory
        isOpen={isTransactionHistoryOpen}
        onClose={() => setIsTransactionHistoryOpen(false)}
      />
      <CodeViewer
        conversationId={currentConversationId}
        isOpen={isCodeViewerOpen}
        onClose={() => setIsCodeViewerOpen(false)}
      />
      <PreviewPanel
        conversationId={currentConversationId}
        isOpen={isPreviewOpen}
        onClose={() => setIsPreviewOpen(false)}
      />
    </>
  );
};

export default Header;
