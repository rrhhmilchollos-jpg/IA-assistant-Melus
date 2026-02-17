import React, { useState, useEffect } from 'react';
import { Send, Paperclip, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import ModelSelector from './ModelSelector';

const PromptBox = ({ onSendMessage, disabled, selectedModel, onModelChange }) => {
  const [message, setMessage] = useState('');
  const [rows, setRows] = useState(2);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      setRows(2);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
    // Auto-expand textarea
    const lineCount = e.target.value.split('\n').length;
    setRows(Math.min(Math.max(lineCount, 2), 10));
  };

  return (
    <div className="bg-white border-t border-gray-200">
      <div className="max-w-4xl mx-auto p-4">
        {/* Model and Options Bar */}
        <div className="flex items-center gap-3 mb-3">
          <div className="flex-1">
            <ModelSelector 
              value={selectedModel} 
              onChange={onModelChange}
              disabled={disabled}
            />
          </div>
          <Button
            variant="outline"
            size="sm"
            disabled={disabled}
            className="border-gray-300"
          >
            <Paperclip size={16} className="mr-2" />
            Adjuntar
          </Button>
        </div>

        {/* Message Input */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="relative">
            <Textarea
              value={message}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu mensaje aquí... (Shift + Enter para nueva línea)"
              className="min-h-[80px] pr-12 text-base resize-none border-2 border-gray-200 focus:border-purple-400"
              disabled={disabled}
              rows={rows}
            />
            <Button 
              type="submit" 
              disabled={!message.trim() || disabled}
              className="absolute right-2 bottom-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg h-10 w-10 p-0"
            >
              <Send size={18} />
            </Button>
          </div>
        </form>

        {/* Info Text */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <Sparkles size={12} className="text-purple-500" />
            <span>
              Potenciado por {selectedModel || 'GPT-4o'}
            </span>
          </div>
          <span>
            {message.length} caracteres
          </span>
        </div>
      </div>
    </div>
  );
};

export default PromptBox;
