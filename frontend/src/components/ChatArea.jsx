import React, { useEffect, useRef, useState, useImperativeHandle, forwardRef } from 'react';
import ChatMessage from './ChatMessage';
import { Loader2, MessageSquare } from 'lucide-react';
import { conversationsAPI } from '../api/client';

const ChatArea = forwardRef(function ChatArea({ conversationId, isLoading }, ref) {
  const messagesEndRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);

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

  const addTempMessage = (content) => {
    const tempUserMessage = {
      message_id: `temp-${Date.now()}`,
      role: 'user',
      content: content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMessage]);
  };

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    loadMessages,
    addTempMessage
  }));

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleMessageUpdated = () => {
    loadMessages();
  };

  if (!conversationId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0d0d1a] text-gray-400">
        <div className="text-center space-y-4">
          <div className="w-20 h-20 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto">
            <MessageSquare size={40} className="text-gray-600" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-200">Assistant Melus</h2>
          <p className="text-gray-500 max-w-md">
            Selecciona una conversación o crea una nueva para comenzar a trabajar con el agente
          </p>
        </div>
      </div>
    );
  }

  if (loadingMessages) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0d0d1a]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0d0d1a]" data-testid="chat-area">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <div className="w-16 h-16 bg-gray-800 rounded-xl flex items-center justify-center mb-4">
              <MessageSquare size={32} className="text-gray-600" />
            </div>
            <p className="text-gray-500">Envía un mensaje para comenzar</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage 
                key={message.message_id} 
                message={message}
                onMessageUpdated={handleMessageUpdated}
              />
            ))}
          </>
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="px-6 py-4">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-purple-600 flex items-center justify-center">
                  <Loader2 size={14} className="text-white animate-spin" />
                </div>
                <div className="flex-1">
                  <div className="text-gray-200 font-medium text-sm mb-2">Assistant Melus</div>
                  <div className="flex items-center gap-2 text-gray-400 text-sm">
                    <span>Processing next step...</span>
                    <div className="flex gap-1">
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
});

export default ChatArea;
