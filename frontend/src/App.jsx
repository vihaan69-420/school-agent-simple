import React, { useState, useRef, useEffect } from 'react';
import { 
  Moon, Sun, User, Bot, Globe, Loader2, 
  Copy, Check, MessageSquare, X, Menu, Search,
  Mic, Download, RefreshCw,
  Edit3, Plus, GraduationCap, Command, ArrowUp, Code, Globe2
} from 'lucide-react';
import ModelSelector from './components/ModelSelector';
import ChatHistory from './components/ChatHistory';
import SourcePreview from './components/SourcePreview';
import ArtifactsPanel from './components/ArtifactsPanel';
import VoiceInput from './components/VoiceInput';
import DynamicSuggestions from './components/DynamicSuggestions';
import './App.css';
import API_URL from './config';

function App() {
  // Core states
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}`);
  const [selectedModel, setSelectedModel] = useState('general');
  const [models, setModels] = useState([]);
  
  // UI states
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  const [showTypingIndicator, setShowTypingIndicator] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [showSourcePreview, setShowSourcePreview] = useState(null);
  
  // Chat history states
  const [sessions, setSessions] = useState([]);
  const [folders, setFolders] = useState([]);
  const [activeFolder, setActiveFolder] = useState(null);
  
  // Voice states
  const [isListening, setIsListening] = useState(false);
  
  // Edit states
  const [editingMessageIndex, setEditingMessageIndex] = useState(null);
  const [editingSessionId, setEditingSessionId] = useState(null);
  
  // Advanced features
  const [commandMode, setCommandMode] = useState(false);
  const [artifacts, setArtifacts] = useState([]);
  const [streamingMessage, setStreamingMessage] = useState('');
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize
  useEffect(() => {
    fetchModels();
    fetchSessions();
    fetchFolders();
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // API calls
  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_URL}/api/models`);
      const data = await response.json();
      setModels(data.models || []);
      setSelectedModel(data.default || 'general');
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchSessions = async () => {
    try {
      const response = await fetch(`${API_URL}/api/sessions`);
      const data = await response.json();
      if (data.success) {
        setSessions(data.data.sessions || []);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const fetchFolders = async () => {
    try {
      const response = await fetch(`${API_URL}/api/folders`);
      const data = await response.json();
      if (data.success) {
        setFolders(data.data.folders || []);
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/api/sessions/${sessionId}`);
      const data = await response.json();
      if (data.success) {
        setMessages(data.data.messages || []);
        setSessionId(sessionId);
        setSelectedModel(data.data.model || 'general');
      }
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm('Delete this chat?')) return;
    
    try {
      const response = await fetch(`${API_URL}/api/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchSessions();
        if (sessionId === sessionId) {
          newChat();
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const updateSession = async (sessionId, updates) => {
    try {
      await fetch(`${API_URL}/api/sessions/${sessionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      fetchSessions();
    } catch (error) {
      console.error('Error updating session:', error);
    }
  };

  const searchSessions = async (query) => {
    if (!query.trim()) {
      fetchSessions();
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/api/sessions/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      if (data.success) {
        setSessions(data.data.results || []);
      }
    } catch (error) {
      console.error('Error searching sessions:', error);
    }
  };

  // UI helpers
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const newChat = () => {
    setSessionId(`session_${Date.now()}`);
    setMessages([]);
    setArtifacts([]);
    setStreamingMessage('');
    // Show greeting for Everest model
    if (selectedModel === 'everest') {
      showEverestGreeting();
    }
  };
  
  const showEverestGreeting = () => {
    const greetingMessage = {
      role: 'assistant',
      content: 'Welcome to Everest Academy Assistant! 🎓\n\nI can help you with:\n\n**General Questions** about Everest Academy:\n- Admissions process\n- Tuition and fees\n- School programs\n- Contact information\n- Campus facilities\n\n**Grade-Specific Resources** (Currently available for Grade 9):\n- Study materials\n- Subject resources\n- Academic guidance\n\nWhat would you like to know? You can ask a general question or specify a grade level.',
      timestamp: new Date().toISOString(),
      model: 'Everest Academy Assistant'
    };
    setMessages([greetingMessage]);
  };
  
  const handleModelChange = (newModel) => {
    setSelectedModel(newModel);
    // If switching to Everest model on a new chat, show greeting
    if (newModel === 'everest' && messages.length === 0) {
      showEverestGreeting();
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    localStorage.setItem('darkMode', (!isDarkMode).toString());
  };

  // Message handling
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
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          session_id: sessionId,
          model: selectedModel
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
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
        
        // Extract artifacts (code blocks, tables, etc.)
        extractArtifacts(data.message);
        
        // Refresh sessions list
        fetchSessions();
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: `I encountered an error: ${error.message}. Please make sure the backend is running on port 8000.`,
        timestamp: new Date().toISOString(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setShowTypingIndicator(false);
    }
  };

  const regenerateResponse = async (messageIndex) => {
    if (messageIndex <= 0 || messages[messageIndex - 1]?.role !== 'user') return;
    
    const userMessage = messages[messageIndex - 1];
    const newMessages = messages.slice(0, messageIndex);
    setMessages(newMessages);
    
    // Resubmit the message
    setInputMessage(userMessage.content);
    setTimeout(() => {
      document.querySelector('form').dispatchEvent(new Event('submit', { bubbles: true }));
    }, 100);
  };

  const editMessage = async (index, newContent) => {
    const updatedMessages = [...messages];
    updatedMessages[index].content = newContent;
    setMessages(updatedMessages);
    setEditingMessageIndex(null);
    
    // If editing a user message, regenerate response
    if (messages[index].role === 'user' && index < messages.length - 1) {
      regenerateResponse(index + 1);
    }
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const exportChat = () => {
    const exportData = {
      sessionId,
      model: selectedModel,
      messages,
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_${sessionId}_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
  };


  const extractArtifacts = (content) => {
    // Extract code blocks
    const codeBlockRegex = /```(\w+)?\n([\s\S]+?)```/g;
    const codeBlocks = [];
    let match;
    
    while ((match = codeBlockRegex.exec(content)) !== null) {
      codeBlocks.push({
        id: `artifact_${Date.now()}_${codeBlocks.length}`,
        type: 'code',
        language: match[1] || 'plaintext',
        content: match[2].trim(),
        timestamp: new Date().toISOString()
      });
    }
    
    if (codeBlocks.length > 0) {
      setArtifacts(prev => [...prev, ...codeBlocks]);
      setShowArtifacts(true);
    }
  };

  // Voice handling
  const handleVoiceInput = (transcript) => {
    setInputMessage(prev => prev + ' ' + transcript);
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestionText) => {
    setInputMessage(suggestionText);
    inputRef.current?.focus();
  };


  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Cmd/Ctrl + K for command mode
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandMode(true);
      }
      
      // Cmd/Ctrl + / for new chat
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        newChat();
      }
      
      // Cmd/Ctrl + Shift + E for export
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'E') {
        e.preventDefault();
        exportChat();
      }
      
      // Escape to close modals
      if (e.key === 'Escape') {
        setCommandMode(false);
        setShowArtifacts(false);
        setEditingMessageIndex(null);
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Message formatting with advanced features
  const formatMessage = (content) => {
    // This would be more sophisticated in production
    return content
      .split('\n')
      .map((line, i) => {
        // Handle images with markdown syntax ![alt](src)
        const imageMatch = line.match(/!\[([^\]]*)\]\(([^\)]+)\)/);
        if (imageMatch) {
          const [, alt, src] = imageMatch;
          return (
            <img 
              key={i} 
              src={src} 
              alt={alt} 
              className="max-w-full h-auto rounded-lg my-2" 
              style={{ maxHeight: '400px' }}
            />
          );
        }
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
        
        // Regular paragraphs with link detection
        if (line.trim()) {
          // Parse line for links and return React elements
          const parseLineWithLinks = (text, key) => {
            const parts = [];
            let lastIndex = 0;
            
            // Regex to match markdown links and plain URLs
            const combinedRegex = /\[([^\]]+)\]\(([^)]+)\)|(https?:\/\/[^\s]+)/g;
            let match;
            
            while ((match = combinedRegex.exec(text)) !== null) {
              // Add text before the match
              if (match.index > lastIndex) {
                parts.push(text.substring(lastIndex, match.index));
              }
              
              if (match[0].startsWith('[')) {
                // Markdown link
                const linkText = match[1];
                const url = match[2];
                parts.push(
                  <a
                    key={`link-${key}-${match.index}`}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    {linkText}
                  </a>
                );
              } else {
                // Plain URL
                const url = match[0];
                parts.push(
                  <a
                    key={`link-${key}-${match.index}`}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    {url}
                  </a>
                );
              }
              
              lastIndex = match.index + match[0].length;
            }
            
            // Add remaining text
            if (lastIndex < text.length) {
              parts.push(text.substring(lastIndex));
            }
            
            return parts;
          };
          
          return (
            <p key={i} className="mb-2">
              {parseLineWithLinks(line, i)}
            </p>
          );
        }
        
        return <br key={i} />;
      });
  };

  
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Enhanced Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-40 flex transition-all duration-300 ${
        sidebarOpen ? 'w-80' : 'w-0'
      }`}>
        <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          {/* Sidebar Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <GraduationCap className="w-6 h-6 text-blue-900" />
              AcademiaAI
            </h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* New Chat Button */}
          <div className="p-4">
            <button
              onClick={newChat}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-900 to-yellow-600 text-white rounded-xl hover:from-blue-800 hover:to-yellow-500 transition-all duration-200 transform hover:scale-105"
            >
              <Plus className="w-5 h-5" />
              New Chat
            </button>
          </div>
          
          {/* Search Bar */}
          <div className="px-4 pb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search chats..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  searchSessions(e.target.value);
                }}
                className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-900"
              />
            </div>
          </div>
          
          {/* Folders and Chat History */}
          <div className="flex-1 overflow-y-auto">
            <ChatHistory
              sessions={sessions}
              folders={folders}
              activeSessionId={sessionId}
              onSelectSession={loadSession}
              onDeleteSession={deleteSession}
              onUpdateSession={updateSession}
              onCreateFolder={(name) => {
                // Create folder API call
              }}
            />
          </div>
          
          {/* Sidebar Footer */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
            <button 
              onClick={() => setCommandMode(true)}
              className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <Command className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <span className="text-gray-700 dark:text-gray-300">Keyboard Shortcuts</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${
        sidebarOpen ? 'ml-80' : 'ml-0'
      }`}>
        {/* Enhanced Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Menu className="w-5 h-5" />
                </button>
              )}
              
              
              {/* Session Title */}
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {sessions.find(s => s.id === sessionId)?.title || 'New Chat'}
                </h3>
                <button
                  onClick={() => {
                    const currentSession = sessions.find(s => s.id === sessionId);
                    if (currentSession) {
                      const newTitle = prompt('Edit chat title:', currentSession.title);
                      if (newTitle && newTitle !== currentSession.title) {
                        updateSession(sessionId, { title: newTitle });
                      }
                    }
                  }}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Edit3 className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Export */}
              <button
                onClick={exportChat}
                className="p-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              
              {/* Dark Mode */}
              <button
                onClick={toggleDarkMode}
                className="p-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {isDarkMode ? (
                  <Sun className="w-5 h-5 text-yellow-500" />
                ) : (
                  <Moon className="w-5 h-5 text-gray-600" />
                )}
              </button>
            </div>
          </div>
        </header>

        {/* Messages Area with Artifacts */}
        <div className="flex-1 flex overflow-hidden">
          {/* Messages */}
          <div className={`flex-1 overflow-y-auto ${showArtifacts ? 'mr-96' : ''}`}>
            <div className="max-w-4xl mx-auto py-8 px-4">
              {messages.length === 0 ? (
                <div className="text-center py-16">
                  <div className="mb-6">
                    <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-900 to-yellow-600 rounded-2xl flex items-center justify-center animate-pulse">
                      <GraduationCap className="w-10 h-10 text-white" />
                    </div>
                  </div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    Welcome to AcademiaAI
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-12">
                    Your intelligent academic companion for learning, research, and educational excellence.
                  </p>
                  
                  {/* Dynamic Suggestions */}
                  <DynamicSuggestions 
                    selectedModel={selectedModel}
                    onSuggestionClick={handleSuggestionClick}
                  />
                  
                  {/* Quick Actions */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto mt-12">
                    <button 
                      onClick={() => setInputMessage("Help me write code")}
                      className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-purple-500 transition-colors text-left"
                    >
                      <Code className="w-6 h-6 text-purple-600 mb-2" />
                      <h3 className="font-semibold text-gray-900 dark:text-white">Write Code</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Generate, debug, or explain code</p>
                    </button>
                    
                    <button 
                      onClick={() => setInputMessage("Analyze this website: ")}
                      className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-purple-500 transition-colors text-left"
                    >
                      <Globe2 className="w-6 h-6 text-purple-600 mb-2" />
                      <h3 className="font-semibold text-gray-900 dark:text-white">Analyze Web</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Research any website or URL</p>
                    </button>
                    
                    <button 
                      onClick={() => {
                        handleModelChange('everest');
                        setInputMessage("");
                      }}
                      className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-purple-500 transition-colors text-left"
                    >
                      <GraduationCap className="w-6 h-6 text-purple-600 mb-2" />
                      <h3 className="font-semibold text-gray-900 dark:text-white">Everest Info</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Ask about Everest Academy</p>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`group flex gap-4 ${
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
                        {editingMessageIndex === index ? (
                          <div className="w-full">
                            <textarea
                              value={messages[index].content}
                              onChange={(e) => {
                                const updated = [...messages];
                                updated[index].content = e.target.value;
                                setMessages(updated);
                              }}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                  e.preventDefault();
                                  editMessage(index, messages[index].content);
                                }
                              }}
                              className="w-full p-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-900"
                              rows={4}
                              autoFocus
                            />
                            <div className="flex gap-2 mt-2">
                              <button
                                onClick={() => editMessage(index, messages[index].content)}
                                className="px-3 py-1 bg-blue-900 text-white rounded-lg hover:bg-blue-800"
                              >
                                Save
                              </button>
                              <button
                                onClick={() => setEditingMessageIndex(null)}
                                className="px-3 py-1 bg-gray-300 dark:bg-gray-600 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className={`rounded-2xl px-4 py-3 ${
                              message.role === 'user'
                                ? 'bg-gradient-to-r from-blue-900 to-yellow-600 text-white'
                                : message.error
                                ? 'bg-red-50 dark:bg-red-900/20 text-red-900 dark:text-red-200 border border-red-200 dark:border-red-800'
                                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                            }`}>
                              <div className="prose prose-sm dark:prose-invert max-w-none">
                                {formatMessage(message.content)}
                              </div>
                              
                              {/* Sources with preview */}
                              {message.sources && message.sources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                                  <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                                    Sources:
                                  </p>
                                  <div className="flex flex-wrap gap-2">
                                    {message.sources.map((source, i) => (
                                      <button
                                        key={i}
                                        onClick={() => setShowSourcePreview(source)}
                                        className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg text-xs hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                      >
                                        <Globe className="w-3 h-3" />
                                        {(() => {
                                          try {
                                            return new URL(source).hostname;
                                          } catch (e) {
                                            // Handle invalid URLs (like base64 images or plain text)
                                            if (source.startsWith('data:')) {
                                              return 'Image';
                                            }
                                            return source.length > 30 ? source.substring(0, 30) + '...' : source;
                                          }
                                        })()}
                                      </button>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {/* Message Actions */}
                            <div className="flex items-center gap-2 mt-1 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
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
                              
                              <div className="flex items-center gap-1 ml-2">
                                {/* Copy */}
                                <button
                                  onClick={() => copyToClipboard(message.content, index)}
                                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                                >
                                  {copiedIndex === index ? (
                                    <Check className="w-4 h-4 text-green-600" />
                                  ) : (
                                    <Copy className="w-4 h-4 text-gray-500" />
                                  )}
                                </button>
                                
                                {/* Edit */}
                                <button
                                  onClick={() => setEditingMessageIndex(index)}
                                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                                >
                                  <Edit3 className="w-4 h-4 text-gray-500" />
                                </button>
                                
                                {/* Regenerate (for assistant messages) */}
                                {message.role === 'assistant' && index === messages.length - 1 && (
                                  <button
                                    onClick={() => regenerateResponse(index)}
                                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                                  >
                                    <RefreshCw className="w-4 h-4 text-gray-500" />
                                  </button>
                                )}
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                      
                      {message.role === 'user' && (
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
                            <User className="w-5 h-5 text-white" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {/* Typing Indicator */}
                  {showTypingIndicator && (
                    <div className="flex gap-4 justify-start animate-in fade-in duration-300">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                          <Bot className="w-5 h-5 text-white animate-pulse" />
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {models.find(m => m.id === selectedModel)?.name || 'AI'} is thinking...
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Streaming Message Preview */}
                  {streamingMessage && (
                    <div className="flex gap-4 justify-start">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                          <Bot className="w-5 h-5 text-white" />
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 max-w-2xl">
                        <div className="prose prose-sm dark:prose-invert">
                          {formatMessage(streamingMessage)}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
          
          {/* Artifacts Panel */}
          {showArtifacts && (
            <ArtifactsPanel
              artifacts={artifacts}
              onClose={() => setShowArtifacts(false)}
              onRemove={(id) => setArtifacts(prev => prev.filter(a => a.id !== id))}
            />
          )}
        </div>

        {/* Enhanced Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-4">
          {/* Dynamic Suggestions for active conversations */}
          {messages.length > 0 && (
            <div className="mb-4">
              <DynamicSuggestions 
                selectedModel={selectedModel}
                onSuggestionClick={handleSuggestionClick}
              />
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="relative">
              
              <div className="flex items-end gap-3">
                {/* Model Selector */}
                <ModelSelector
                  selectedModel={selectedModel}
                  onModelChange={handleModelChange}
                  models={models}
                />
                
                {/* Input field with voice */}
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e);
                      }
                    }}
                    placeholder={`Message ${models.find(m => m.id === selectedModel)?.name || 'AI Assistant'}...`}
                    className="w-full px-4 py-3 pr-12 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-transparent transition-all duration-200 resize-none"
                    rows={1}
                    style={{
                      minHeight: '48px',
                      maxHeight: '200px'
                    }}
                    disabled={isLoading}
                  />
                  
                  {/* Voice input button */}
                  <VoiceInput
                    onTranscript={handleVoiceInput}
                    isListening={isListening}
                    setIsListening={setIsListening}
                    className="absolute right-2 bottom-2"
                  />
                </div>
                
                {/* Send button */}
                <button
                  type="submit"
                  disabled={isLoading || !inputMessage.trim()}
                  className="p-3 bg-gradient-to-r from-blue-900 to-yellow-600 text-white rounded-xl hover:from-blue-800 hover:to-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 active:scale-95"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <ArrowUp className="w-5 h-5" />
                  )}
                </button>
              </div>
              
              {/* Character count */}
              {inputMessage.length > 0 && (
                <div className="absolute -top-6 right-0 text-xs text-gray-500 dark:text-gray-400">
                  {inputMessage.length} / 4000
                </div>
              )}
            </div>
          </form>
          
          {/* Input hints */}
          <div className="max-w-4xl mx-auto mt-2 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <Command className="w-3 h-3" />K for commands
              </span>
              <span className="flex items-center gap-1">
                <Command className="w-3 h-3" />/ for new chat
              </span>
              <span>Shift+Enter for new line</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1">
                <Mic className="w-3 h-3" />
                Voice input
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Keyboard Shortcuts Modal */}
      {commandMode && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setCommandMode(false)}>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-200" onClick={(e) => e.stopPropagation()}>
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Keyboard Shortcuts</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">⌘</kbd>
                    <span className="text-gray-500 dark:text-gray-400">+</span>
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">K</kbd>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Open command palette</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">⌘</kbd>
                    <span className="text-gray-500 dark:text-gray-400">+</span>
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">/</kbd>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">New chat</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">⌘</kbd>
                    <span className="text-gray-500 dark:text-gray-400">+</span>
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">⇧</kbd>
                    <span className="text-gray-500 dark:text-gray-400">+</span>
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">E</kbd>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Export chat</span>
                </div>
                <div className="flex items-center justify-between">
                  <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">Escape</kbd>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Close modals</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">Shift</kbd>
                    <span className="text-gray-500 dark:text-gray-400">+</span>
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600">Enter</kbd>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">New line</span>
                </div>
              </div>
              <button 
                onClick={() => setCommandMode(false)}
                className="mt-6 w-full px-4 py-2 bg-gradient-to-r from-blue-900 to-yellow-600 text-white rounded-lg hover:from-blue-800 hover:to-yellow-500 transition-all"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Source Preview Modal */}
      {showSourcePreview && (
        <SourcePreview
          url={showSourcePreview}
          onClose={() => setShowSourcePreview(null)}
        />
      )}

      {/* Keyboard Shortcuts Modal */}
      {/* <KeyboardShortcuts isOpen={false} onClose={() => {}} /> */}
    </div>
  );
}

export default App;