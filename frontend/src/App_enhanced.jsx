import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, Moon, Sun, Sparkles, User, Bot, Link, 
  Globe, Loader2, AlertCircle, Copy, Check,
  MessageSquare, X, Menu, Settings, Github
} from 'lucide-react';
import ModelSelector from './components/ModelSelector';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [selectedModel, setSelectedModel] = useState('general');
  const [models, setModels] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  const [showTypingIndicator, setShowTypingIndicator] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    fetchModels();
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/models');
      const data = await response.json();
      setModels(data.models);
      setSelectedModel(data.default);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setShowTypingIndicator(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          session_id: sessionId,
          model: selectedModel
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        const assistantMessage = {
          role: 'assistant',
          content: data.message,
          timestamp: new Date().toISOString(),
          model: data.model,
          sources: data.sources,
          metadata: data.metadata
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setShowTypingIndicator(false);
    }
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    localStorage.setItem('darkMode', (!isDarkMode).toString());
  };

  const clearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .split('\n')
      .map((line, i) => {
        // Headers
        if (line.startsWith('### ')) {
          return <h3 key={i} className="text-lg font-semibold mt-4 mb-2">{line.substring(4)}</h3>;
        }
        if (line.startsWith('## ')) {
          return <h2 key={i} className="text-xl font-semibold mt-4 mb-2">{line.substring(3)}</h2>;
        }
        if (line.startsWith('# ')) {
          return <h1 key={i} className="text-2xl font-bold mt-4 mb-2">{line.substring(2)}</h1>;
        }
        
        // Lists
        if (line.match(/^\d+\./)) {
          return <li key={i} className="ml-6 list-decimal">{line.substring(line.indexOf('.') + 1).trim()}</li>;
        }
        if (line.startsWith('- ') || line.startsWith('* ')) {
          return <li key={i} className="ml-6 list-disc">{line.substring(2)}</li>;
        }
        
        // Code blocks
        if (line.startsWith('```')) {
          return null; // Handle multi-line code blocks separately
        }
        
        // Links
        const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        if (line.match(linkRegex)) {
          const parts = line.split(linkRegex);
          return (
            <p key={i} className="mb-2">
              {parts.map((part, j) => {
                if (j % 3 === 1) {
                  return (
                    <a
                      key={j}
                      href={parts[j + 1]}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1"
                    >
                      {part}
                      <Link className="w-3 h-3" />
                    </a>
                  );
                }
                if (j % 3 === 2) return null;
                return part;
              })}
            </p>
          );
        }
        
        // Regular paragraphs
        if (line.trim()) {
          return <p key={i} className="mb-2">{line}</p>;
        }
        
        return <br key={i} />;
      });
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-purple-600" />
              VihaanGPT
            </h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 p-4 space-y-4">
            <button
              onClick={clearChat}
              className="w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <MessageSquare className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <span className="text-gray-700 dark:text-gray-300">New Chat</span>
            </button>
            
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                Chat History
              </h3>
              <p className="text-sm text-gray-400 dark:text-gray-500">
                Coming soon...
              </p>
            </div>
          </div>
          
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <Github className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <span className="text-gray-700 dark:text-gray-300">GitHub</span>
            </a>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Menu className="w-5 h-5" />
              </button>
              
              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                models={models}
              />
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={toggleDarkMode}
                className="p-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="Toggle dark mode"
              >
                {isDarkMode ? (
                  <Sun className="w-5 h-5 text-yellow-500" />
                ) : (
                  <Moon className="w-5 h-5 text-gray-600" />
                )}
              </button>
              
              <button
                className="p-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="Settings"
              >
                <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto py-8 px-4">
            {messages.length === 0 ? (
              <div className="text-center py-16">
                <div className="mb-6">
                  <div className="w-20 h-20 mx-auto bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                </div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  Welcome to VihaanGPT
                </h1>
                <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                  Choose a model above and start chatting. I can help with general questions, 
                  Everest Academy inquiries, or research any website for you.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-4 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    } animate-in fade-in slide-in-from-bottom-2 duration-300`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                          <Bot className="w-5 h-5 text-white" />
                        </div>
                      </div>
                    )}
                    
                    <div className={`flex flex-col max-w-2xl ${
                      message.role === 'user' ? 'items-end' : 'items-start'
                    }`}>
                      <div className={`rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : message.error
                          ? 'bg-red-50 dark:bg-red-900/20 text-red-900 dark:text-red-200 border border-red-200 dark:border-red-800'
                          : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                      }`}>
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                          {formatMessage(message.content)}
                        </div>
                        
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                            <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                              Sources:
                            </p>
                            <div className="space-y-1">
                              {message.sources.map((source, i) => (
                                <a
                                  key={i}
                                  href={source}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                                >
                                  <Globe className="w-3 h-3" />
                                  {new URL(source).hostname}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-2 mt-1 px-1">
                        {message.model && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {message.model}
                          </span>
                        )}
                        {message.metadata?.processing_time && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            • {message.metadata.processing_time.toFixed(2)}s
                          </span>
                        )}
                        {message.role === 'assistant' && (
                          <button
                            onClick={() => copyToClipboard(message.content, index)}
                            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                            aria-label="Copy message"
                          >
                            {copiedIndex === index ? (
                              <Check className="w-3 h-3 text-green-600" />
                            ) : (
                              <Copy className="w-3 h-3 text-gray-500" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {message.role === 'user' && (
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-lg bg-gray-600 flex items-center justify-center">
                          <User className="w-5 h-5 text-white" />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                
                {showTypingIndicator && (
                  <div className="flex gap-4 justify-start animate-in fade-in duration-300">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <Bot className="w-5 h-5 text-white" />
                      </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-4">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={`Ask ${models.find(m => m.id === selectedModel)?.name || 'AI'} anything...`}
                className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 active:scale-95 flex items-center gap-2"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;