"use client";

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import MessageBubble from './MessageBubble';
import InputBox from './InputBox';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    setLoading(true);
    setError(null);

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/chat/message`,
        {
          message: content,
          conversation_id: conversationId,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const { response: assistantResponse, conversation_id } = response.data;

      if (!conversationId) {
        setConversationId(conversation_id);
      }

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: assistantResponse,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error('Error sending message:', err);
      setError(
        err.response?.data?.detail || 'Failed to send message. Please try again.'
      );

      const errorMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    const actionMessages: { [key: string]: string } = {
      'add': 'Add a new task',
      'view': 'Show me all my tasks',
      'complete': 'Show me my pending tasks',
      'stats': 'How many tasks do I have?'
    };

    sendMessage(actionMessages[action]);
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-md shadow-md border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-md">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Todo Assistant</h1>
              <p className="text-sm text-gray-500 font-medium">AI-powered task management</p>
            </div>
          </div>
          <button
            onClick={startNewConversation}
            className="px-5 py-2.5 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all shadow-sm hover:shadow-md transform hover:-translate-y-0.5"
          >
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </span>
          </button>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto py-6">
          {messages.length === 0 ? (
            <div className="text-center py-16 px-4">
              <div className="text-5xl mb-6">✅</div>
              <h2 className="text-3xl font-bold text-gray-900 mb-3">
                Welcome to Todo Assistant!
              </h2>
              <p className="text-gray-600 text-lg mb-10 max-w-2xl mx-auto">
                I can help you manage your tasks with natural language. Just tell me what you need!
              </p>

              {/* Example Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto text-left mb-8">
                <div className="bg-white p-5 rounded-2xl border-2 border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all cursor-pointer group">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 mb-1">Add tasks</div>
                      <div className="text-sm text-gray-600">"Add a task to buy groceries tomorrow"</div>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl border-2 border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all cursor-pointer group">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 mb-1">View tasks</div>
                      <div className="text-sm text-gray-600">"Show me all my pending tasks"</div>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl border-2 border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all cursor-pointer group">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                      <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 mb-1">Complete tasks</div>
                      <div className="text-sm text-gray-600">"Mark task 5 as completed"</div>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl border-2 border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all cursor-pointer group">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center group-hover:bg-orange-200 transition-colors">
                      <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 mb-1">Get statistics</div>
                      <div className="text-sm text-gray-600">"How many tasks do I have?"</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {loading && (
                <div className="flex justify-start mb-6 px-4">
                  <div className="bg-white rounded-2xl rounded-bl-sm px-5 py-4 shadow-md border border-gray-200">
                    <div className="flex space-x-2">
                      <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Quick Action Buttons */}
      {messages.length > 0 && (
        <div className="bg-white/80 backdrop-blur-md border-t border-gray-200/50 px-6 py-4">
          <div className="max-w-6xl mx-auto">
            <div className="flex flex-wrap gap-3 justify-center">
              <button
                onClick={() => handleQuickAction('add')}
                disabled={loading}
                className="filter-button"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add Task
                </span>
              </button>

              <button
                onClick={() => handleQuickAction('view')}
                disabled={loading}
                className="filter-button"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  View Tasks
                </span>
              </button>

              <button
                onClick={() => handleQuickAction('complete')}
                disabled={loading}
                className="filter-button"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Complete Task
                </span>
              </button>

              <button
                onClick={() => handleQuickAction('stats')}
                disabled={loading}
                className="filter-button"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Statistics
                </span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="max-w-6xl mx-auto px-6 py-3">
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-5 py-3 rounded-lg shadow-sm">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="max-w-6xl mx-auto w-full">
        <InputBox onSend={sendMessage} disabled={loading} />
      </div>
    </div>
  );
}
