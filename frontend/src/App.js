import { useState, useEffect } from "react";
import "@/App.css";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";
import { getMockConversations, createMockMessage, getMockAIResponse } from "./mock/mockData";
import { Toaster } from "./components/ui/sonner";
import { toast } from "./hooks/use-toast";

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load mock conversations on mount
    const mockConvs = getMockConversations();
    setConversations(mockConvs);
    if (mockConvs.length > 0) {
      setCurrentConversationId(mockConvs[0].id);
    }
  }, []);

  const handleNewConversation = () => {
    const newConversation = {
      id: `conv-${Date.now()}`,
      title: 'Nueva Conversación',
      timestamp: new Date(),
      messages: []
    };
    
    setConversations([newConversation, ...conversations]);
    setCurrentConversationId(newConversation.id);
    
    toast({
      title: "Nueva conversación creada",
      description: "Comienza a chatear con Assistant Melus"
    });
  };

  const handleSelectConversation = (conversationId) => {
    setCurrentConversationId(conversationId);
  };

  const handleDeleteConversation = (conversationId) => {
    const filteredConversations = conversations.filter(c => c.id !== conversationId);
    setConversations(filteredConversations);
    
    if (currentConversationId === conversationId) {
      setCurrentConversationId(filteredConversations.length > 0 ? filteredConversations[0].id : null);
    }
    
    toast({
      title: "Conversación eliminada",
      description: "La conversación ha sido eliminada correctamente"
    });
  };

  const handleSendMessage = async (messageContent) => {
    if (!currentConversationId) return;

    // Add user message
    const userMessage = createMockMessage('user', messageContent);
    
    setConversations(conversations.map(conv => {
      if (conv.id === currentConversationId) {
        const updatedConv = {
          ...conv,
          messages: [...conv.messages, userMessage],
          timestamp: new Date()
        };
        
        // Update title if it's a new conversation
        if (conv.messages.length === 0) {
          updatedConv.title = messageContent.substring(0, 50) + (messageContent.length > 50 ? '...' : '');
        }
        
        return updatedConv;
      }
      return conv;
    }));

    // Simulate AI response
    setIsLoading(true);
    
    setTimeout(() => {
      const aiResponse = getMockAIResponse(messageContent);
      const aiMessage = createMockMessage('assistant', aiResponse);
      
      setConversations(conversations.map(conv => {
        if (conv.id === currentConversationId) {
          return {
            ...conv,
            messages: [...conv.messages, userMessage, aiMessage]
          };
        }
        return conv;
      }));
      
      setIsLoading(false);
    }, 1500);
  };

  const currentConversation = conversations.find(c => c.id === currentConversationId);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
      />
      <ChatArea
        conversation={currentConversation}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
      <Toaster />
    </div>
  );
}

export default App;
