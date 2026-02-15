import React, { useState, KeyboardEvent } from 'react';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function InputBox({ onSend, disabled = false }: InputBoxProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white/80 backdrop-blur-md px-6 py-4 shadow-lg">
      <div className="flex items-center gap-3 max-w-5xl mx-auto">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (e.g., 'Add a task to buy groceries')"
          disabled={disabled}
          rows={1}
          className="flex-1 glass-input"
          style={{ minHeight: '48px', maxHeight: '120px', marginBottom: 0 }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="glass-button flex-shrink-0"
          style={{ height: '48px', width: 'auto', padding: '0 1.5rem' }}
        >
          <span className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            Send
          </span>
        </button>
      </div>
      <div className="mt-2 text-xs text-gray-400 text-center max-w-5xl mx-auto">
        Press Enter to send • Shift+Enter for new line
      </div>
    </div>
  );
}
