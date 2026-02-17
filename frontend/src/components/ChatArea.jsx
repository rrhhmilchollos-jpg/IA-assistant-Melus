import React, { useEffect, useRef, useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { Loader2 } from 'lucide-react';
import { conversationsAPI } from '../api/client';

const ChatArea = ({ conversationId, onSendMessage, isLoading }) => {
  const messagesEndRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);

  useEffect(() => {
    if (conversationId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    if (!conversationId) return;
    
    setLoadingMessages(true);
    try {
      const msgs = await conversationsAPI.getMessages(conversationId);
      setMessages(msgs);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoadingMessages(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (content) => {
    if (!conversationId || isLoading) return;

    // Optimistically add user message to UI
    const tempUserMessage = {
      message_id: `temp-${Date.now()}`,
      role: 'user',
      content: content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      await onSendMessage(content);
      // Reload messages to get the real messages from server
      await loadMessages();
    } catch (error) {
      // Remove temp message on error
      setMessages(prev => prev.filter(m => m.message_id !== tempUserMessage.message_id));
    }
  };
  
  const handleMessageUpdated = () => {
    // Reload messages when a message is edited or regenerated
    loadMessages();
  };

  if (!conversationId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-white text-gray-500">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
            <span className="text-3xl">💬</span>
          </div>
          <h2 className="text-2xl font-semibold text-gray-800">Assistant Melus</h2>
          <p className="text-gray-600">Selecciona una conversación o crea una nueva para comenzar</p>
        </div>
      </div>
    );
  }

  if (loadingMessages) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-screen">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          {messages.map((message) => (
            <ChatMessage 
              key={message.message_id} 
              message={message}
              onMessageUpdated={handleMessageUpdated}
            />
          ))}
          
          {isLoading && (
            <div className="flex gap-4 p-6 bg-gray-50">
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-purple-600 text-white">
                <Loader2 size={18} className="animate-spin" />
              </div>
              <div className="flex-1 space-y-2">
                <div className="font-semibold text-sm text-gray-900">Assistant Melus</div>
                <div className="text-gray-600">Pensando...</div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatArea;
