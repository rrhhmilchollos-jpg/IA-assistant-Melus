import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { Loader2 } from 'lucide-react';

const ChatArea = ({ conversation, onSendMessage, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  if (!conversation) {
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

  return (
    <div className="flex-1 flex flex-col h-screen">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          {conversation.messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
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
      <ChatInput onSendMessage={onSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatArea;