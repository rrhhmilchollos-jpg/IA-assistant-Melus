import React, { useState } from 'react';
import { Send, Paperclip, Save, Sparkles, Mic, Square, Zap } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import ModelSelector from './ModelSelector';

const PromptBox = ({ 
  onSendMessage, 
  disabled, 
  selectedModel, 
  onModelChange,
  isAgentRunning = false 
}) => {
  const [message, setMessage] = useState('');
  const [budget, setBudget] = useState(10000);
  const [usedBudget, setUsedBudget] = useState(0);

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
    <div className="bg-[#0d0d1a] border-t border-gray-800" data-testid="prompt-box">
      <div className="max-w-4xl mx-auto p-4">
        {/* Status Indicator */}
        {isAgentRunning && (
          <div className="flex items-center gap-2 mb-3 text-green-400" data-testid="agent-status">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm font-medium">Agent is running...</span>
          </div>
        )}

        {/* Main Input Container */}
        <div className="bg-[#1a1a2e] rounded-xl border border-gray-700 overflow-hidden">
          {/* Message Input */}
          <div className="relative">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Agent"
              className="min-h-[60px] bg-transparent border-0 text-white placeholder-gray-500 resize-none focus:ring-0 focus-visible:ring-0 text-base px-4 py-3"
              disabled={disabled}
              data-testid="message-input"
            />
          </div>

          {/* Action Bar */}
          <div className="flex items-center justify-between px-3 py-2 border-t border-gray-700/50">
            {/* Left Actions */}
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg h-8 px-2"
                data-testid="attach-button"
              >
                <Paperclip size={16} />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg h-8 px-3"
                data-testid="save-button"
              >
                <Save size={16} className="mr-1.5" />
                <span className="text-xs">Save</span>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg h-8 px-3"
                data-testid="summarize-button"
              >
                <Sparkles size={16} className="mr-1.5" />
                <span className="text-xs">Summarize</span>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg h-8 px-3"
                data-testid="ultra-button"
              >
                <Zap size={16} className="mr-1.5" />
                <span className="text-xs">Ultra</span>
              </Button>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                disabled={disabled}
                className="text-gray-400 hover:text-white hover:bg-gray-700 rounded-full h-8 w-8 p-0"
                data-testid="mic-button"
              >
                <Mic size={16} />
              </Button>
              
              {disabled ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-red-600 hover:bg-red-700 text-white rounded-full h-8 w-8 p-0"
                  data-testid="stop-button"
                >
                  <Square size={14} />
                </Button>
              ) : (
                <Button 
                  type="submit" 
                  onClick={handleSubmit}
                  disabled={!message.trim() || disabled}
                  className="bg-purple-600 hover:bg-purple-700 text-white rounded-full h-8 w-8 p-0"
                  data-testid="send-button"
                >
                  <Send size={14} />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Budget Display */}
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <span className="text-gray-400">Budget:</span>
            <span className="text-white font-mono">
              {usedBudget.toLocaleString()} / {budget.toLocaleString()}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Sparkles size={12} className="text-purple-500" />
            <span>Powered by {selectedModel || 'gpt-4o'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptBox;
