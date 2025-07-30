import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import ChatPanel from './components/ChatPanel';
import ChatInput from './components/ChatInput';
import { useChatStore } from './store/chatStore';
import './index.css';

function App() {
  const { 
    isDarkMode, 
    currentSessionId, 
    createNewSession, 
    addMessage, 
    setIsLoading, 
    getCurrentSession
  } = useChatStore();

  // Initialize first session if none exists
  useEffect(() => {
    if (!currentSessionId) {
      createNewSession();
    }
  }, [currentSessionId, createNewSession]);

  // Apply dark mode class to document
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleSendMessage = async (message) => {
    if (!message.trim() || !currentSessionId) return;

    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    addMessage(currentSessionId, userMessage);
    setIsLoading(true);

    try {
      const currentSession = getCurrentSession();
      const allMessages = [...(currentSession?.messages || []), userMessage];
      
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: allMessages,
          session_id: currentSessionId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      if (data.success) {
        const assistantMessage = {
          role: 'assistant',
          content: data.message,
          timestamp: new Date().toISOString()
        };
        addMessage(currentSessionId, assistantMessage);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
      addMessage(currentSessionId, errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`h-screen bg-white dark:bg-gray-900 transition-colors duration-300`}>
      <Header />
      
      <motion.div 
        className="flex flex-col overflow-hidden" 
        style={{ height: 'calc(100vh - 60px)' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <ChatPanel />
        <ChatInput onSendMessage={handleSendMessage} />
      </motion.div>
    </div>
  );
}

export default App;