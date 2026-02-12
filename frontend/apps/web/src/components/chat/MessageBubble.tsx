import React from 'react';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 px-4 animate-in`}>
      <div className="flex flex-col max-w-[75%]">
        {/* Message bubble with glassmorphism */}
        <div
          className={`rounded-2xl px-5 py-3 backdrop-blur-md ${
            isUser
              ? 'bg-gradient-to-br from-blue-500/90 to-blue-600/90 text-white shadow-lg rounded-br-sm'
              : 'bg-white/70 text-gray-800 border border-gray-200/50 shadow-md rounded-bl-sm'
          }`}
          style={{
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)'
          }}
        >
          <div className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">
            {message.content}
          </div>
        </div>
        {/* Timestamp */}
        <div
          className={`text-xs mt-1.5 px-2 ${
            isUser ? 'text-right text-gray-400' : 'text-left text-gray-400'
          }`}
        >
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </div>
  );
}
