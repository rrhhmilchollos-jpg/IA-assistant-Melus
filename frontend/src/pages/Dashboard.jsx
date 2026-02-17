import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import ChatArea from '../components/ChatArea';
import PromptBox from '../components/PromptBox';
import { conversationsAPI } from '../api/client';
import { toast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/sonner';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, updateCredits } = useAuth();
  const chatAreaRef = useRef(null);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');

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
  };

  const handleCloseConversation = async (conversationId) => {
    try {
      await conversationsAPI.delete(conversationId);
      const filteredConvs = conversations.filter(c => c.conversation_id !== conversationId);
      setConversations(filteredConvs);
      
      if (currentConversationId === conversationId) {
        setCurrentConversationId(filteredConvs.length > 0 ? filteredConvs[0].conversation_id : null);
      }
      
      toast({
        title: "Conversación cerrada",
        description: "La conversación ha sido eliminada"
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
    
    // Optimistically add user message to UI
    if (chatAreaRef.current) {
      chatAreaRef.current.addTempMessage(content);
    }
    
    try {
      const response = await conversationsAPI.sendMessage(currentConversationId, content);
      updateCredits(response.credits_remaining);
      
      // Reload messages in ChatArea to show the AI response
      if (chatAreaRef.current) {
        await chatAreaRef.current.loadMessages();
      }
      
      await loadConversations();
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Reload messages to remove optimistic update
      if (chatAreaRef.current) {
        await chatAreaRef.current.loadMessages();
      }
      
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
    <div className="flex flex-col h-screen bg-[#0d0d1a]" data-testid="dashboard-page">
      <Header 
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onCloseConversation={handleCloseConversation}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatArea
          ref={chatAreaRef}
          conversationId={currentConversationId}
          isLoading={isSending}
        />
        
        <PromptBox
          onSendMessage={handleSendMessage}
          disabled={isSending}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          isAgentRunning={isSending}
        />
      </div>

      <Toaster />
    </div>
  );
};

export default Dashboard;
