import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import ChatArea from '../components/ChatArea';
import PromptBox from '../components/PromptBox';
import ProjectsTable from '../components/ProjectsTable';
import { conversationsAPI } from '../api/client';
import { toast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/sonner';
import { Button } from '../components/ui/button';
import { PlusCircle, LayoutGrid, MessageSquare } from 'lucide-react';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../components/ui/tabs';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, updateCredits } = useAuth();
  const chatAreaRef = useRef(null);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [view, setView] = useState('workspace'); // 'workspace' or 'chat'

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const convs = await conversationsAPI.getAll();
      setConversations(convs);
      if (convs.length > 0 && !currentConversationId) {
        setCurrentConversationId(convs[0].conversation_id);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
      if (error.response?.status === 401) {
        navigate('/login');
      }
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await conversationsAPI.create('Nueva Conversación', selectedModel);
      setConversations([newConv, ...conversations]);
      setCurrentConversationId(newConv.conversation_id);
      setView('chat');
      
      toast({
        title: "Nueva conversación creada",
        description: `Usando modelo ${selectedModel}`
      });
    } catch (error) {
      console.error('Failed to create conversation:', error);
      toast({
        title: "Error",
        description: "No se pudo crear la conversación",
        variant: "destructive"
      });
    }
  };

  const handleSelectConversation = (conversationId) => {
    setCurrentConversationId(conversationId);
    setView('chat');
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await conversationsAPI.delete(conversationId);
      const filteredConvs = conversations.filter(c => c.conversation_id !== conversationId);
      setConversations(filteredConvs);
      
      if (currentConversationId === conversationId) {
        setCurrentConversationId(filteredConvs.length > 0 ? filteredConvs[0].conversation_id : null);
      }
      
      toast({
        title: "Conversación eliminada",
        description: "La conversación ha sido eliminada correctamente"
      });
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      toast({
        title: "Error",
        description: "No se pudo eliminar la conversación",
        variant: "destructive"
      });
    }
  };

  const handleForkConversation = async (conversationId) => {
    try {
      await conversationsAPI.fork(conversationId);
      await loadConversations();
      toast({
        title: "Conversación bifurcada",
        description: "Se ha creado una copia de la conversación"
      });
    } catch (error) {
      console.error('Failed to fork:', error);
      toast({
        title: "Error",
        description: "No se pudo bifurcar la conversación",
        variant: "destructive"
      });
    }
  };

  const handleExportConversation = async (conversationId) => {
    try {
      await conversationsAPI.exportConversation(conversationId);
      toast({
        title: "Conversación exportada",
        description: "El archivo se ha descargado correctamente"
      });
    } catch (error) {
      console.error('Failed to export:', error);
      toast({
        title: "Error",
        description: "No se pudo exportar la conversación",
        variant: "destructive"
      });
    }
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId || isSending) return;

    setIsSending(true);
    
    try {
      const response = await conversationsAPI.sendMessage(currentConversationId, content);
      updateCredits(response.credits_remaining);
      await loadConversations();
    } catch (error) {
      console.error('Failed to send message:', error);
      
      if (error.response?.status === 402) {
        toast({
          title: "Créditos insuficientes",
          description: "Necesitas comprar más créditos para continuar",
          variant: "destructive"
        });
      } else {
        toast({
          title: "Error",
          description: error.response?.data?.detail || "No se pudo enviar el mensaje",
          variant: "destructive"
        });
      }
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      
      <div className="flex-1 overflow-hidden">
        <Tabs value={view} onValueChange={setView} className="h-full flex flex-col">
          {/* Tab Navigation */}
          <div className="bg-white border-b border-gray-200 px-6">
            <div className="max-w-7xl mx-auto">
              <TabsList className="bg-transparent border-0">
                <TabsTrigger value="workspace" className="data-[state=active]:border-b-2 data-[state=active]:border-purple-600">
                  <LayoutGrid size={16} className="mr-2" />
                  Workspace
                </TabsTrigger>
                <TabsTrigger value="chat" className="data-[state=active]:border-b-2 data-[state=active]:border-purple-600">
                  <MessageSquare size={16} className="mr-2" />
                  Chat
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          {/* Workspace View */}
          <TabsContent value="workspace" className="flex-1 overflow-auto m-0" data-testid="workspace-tab">
            <div className="max-w-7xl mx-auto p-6">
              {/* Action Bar */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900" data-testid="conversations-title">Tus Conversaciones</h2>
                  <p className="text-gray-600 mt-1" data-testid="conversations-count">
                    {conversations.length} conversaciones totales
                  </p>
                </div>
                <Button
                  onClick={handleNewConversation}
                  className="bg-purple-600 hover:bg-purple-700"
                  data-testid="new-conversation-button"
                >
                  <PlusCircle size={18} className="mr-2" />
                  Nueva Conversación
                </Button>
              </div>

              {/* Projects Table */}
              <ProjectsTable
                conversations={conversations}
                currentConversationId={currentConversationId}
                onSelectConversation={handleSelectConversation}
                onDeleteConversation={handleDeleteConversation}
                onForkConversation={handleForkConversation}
                onExportConversation={handleExportConversation}
              />
            </div>
          </TabsContent>

          {/* Chat View */}
          <TabsContent value="chat" className="flex-1 flex flex-col m-0" data-testid="chat-tab">
            {currentConversationId ? (
              <>
                <div className="flex-1 overflow-hidden">
                  <ChatArea
                    conversationId={currentConversationId}
                    onSendMessage={handleSendMessage}
                    isLoading={isSending}
                  />
                </div>
                <PromptBox
                  onSendMessage={handleSendMessage}
                  disabled={isSending}
                  selectedModel={selectedModel}
                  onModelChange={setSelectedModel}
                />
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    No hay conversación seleccionada
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Selecciona una conversación del workspace o crea una nueva
                  </p>
                  <Button
                    onClick={handleNewConversation}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <PlusCircle size={18} className="mr-2" />
                    Nueva Conversación
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      <Toaster />
    </div>
  );
};

export default Dashboard;
