import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';

const ChatInput = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t bg-white p-4">
      <div className="max-w-4xl mx-auto flex gap-3 items-end">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu mensaje aquí..."
          className="flex-1 min-h-[60px] max-h-[200px] resize-none"
          disabled={disabled}
        />
        <Button 
          type="submit" 
          disabled={!message.trim() || disabled}
          className="h-[60px] px-6 bg-purple-600 hover:bg-purple-700"
        >
          <Send size={20} />
        </Button>
      </div>
    </form>
  );
};

export default ChatInput;