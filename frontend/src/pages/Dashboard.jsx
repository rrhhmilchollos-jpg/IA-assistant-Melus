import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/Sidebar';
import ChatArea from '../components/ChatArea';
import { conversationsAPI } from '../api/client';
import { toast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/sonner';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, updateCredits } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);

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
      const newConv = await conversationsAPI.create();
      setConversations([newConv, ...conversations]);
      setCurrentConversationId(newConv.conversation_id);
      
      toast({
        title: "Nueva conversación creada",
        description: "Comienza a chatear con Assistant Melus"
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

  const handleSendMessage = async (content) => {
    if (!currentConversationId || isSending) return;

    setIsSending(true);
    
    try {
      const response = await conversationsAPI.sendMessage(currentConversationId, content);
      
      // Update credits
      updateCredits(response.credits_remaining);
      
      // Reload conversations to update timestamps and titles
      await loadConversations();
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      if (error.response?.status === 402) {
        toast({
          title: "Créditos insuficientes",
          description: "Necesitas comprar más créditos para continuar",
          variant: "destructive",
          action: {
            label: "Comprar Créditos",
            onClick: () => navigate('/pricing')
          }
        });
      } else {
        toast({
          title: "Error",
          description: "No se pudo enviar el mensaje",
          variant: "destructive"
        });
      }
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        userCredits={user?.credits || 0}
      />
      <ChatArea
        conversationId={currentConversationId}
        onSendMessage={handleSendMessage}
        isLoading={isSending}
      />
      <Toaster />
    </div>
  );
};

export default Dashboard;