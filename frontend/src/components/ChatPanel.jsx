import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Sparkles } from 'lucide-react';
import ChatMessage from './ChatMessage';
import { useChatStore } from '../store/chatStore';

const EmptyState = () => {
  return (
    <motion.div 
      className="flex-1 flex items-center justify-center p-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="text-center max-w-md">
        <motion.div
          animate={{ 
            rotate: 360,
            scale: [1, 1.1, 1]
          }}
          transition={{ 
            rotate: { duration: 20, repeat: Infinity, ease: "linear" },
            scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
          }}
          className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg"
        >
          <Sparkles size={28} className="text-white" />
        </motion.div>
        
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3">
          Welcome to VihaanGPT
        </h2>
        
        <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
          Your intelligent AI assistant powered by Qwen v2.5-Max. Ask questions about Everest Academy Manila or anything else you'd like to know.
        </p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          <motion.div 
            whileHover={{ scale: 1.02 }}
            className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center space-x-2 mb-2">
              <MessageSquare size={16} className="text-blue-500" />
              <span className="font-medium text-gray-900 dark:text-gray-100">Ask about Everest Academy</span>
            </div>
            <p className="text-gray-600 dark:text-gray-400">Get information about tuition, programs, admissions, and more</p>
          </motion.div>
          
          <motion.div 
            whileHover={{ scale: 1.02 }}
            className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center space-x-2 mb-2">
              <Sparkles size={16} className="text-purple-500" />
              <span className="font-medium text-gray-900 dark:text-gray-100">General Questions</span>
            </div>
            <p className="text-gray-600 dark:text-gray-400">Ask about anything - coding, science, history, and more</p>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

const ChatPanel = () => {
  const { getCurrentSession, isLoading } = useChatStore();
  const messagesEndRef = useRef(null);
  const currentSession = getCurrentSession();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages, isLoading]);

  if (!currentSession || currentSession.messages.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto p-4 space-y-6">
        <AnimatePresence mode="wait">
          {currentSession.messages.map((message, index) => (
            <ChatMessage
              key={message.id || index}
              message={message}
              isTyping={
                index === currentSession.messages.length - 1 && 
                message.role === 'assistant' && 
                isLoading
              }
            />
          ))}
        </AnimatePresence>
        
        {/* Loading indicator for when AI is typing */}
        {isLoading && currentSession.messages[currentSession.messages.length - 1]?.role === 'user' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start mb-6"
          >
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <Sparkles size={18} />
                </motion.div>
              </div>
              <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex space-x-1">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                    className="w-2 h-2 bg-gray-400 rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    className="w-2 h-2 bg-gray-400 rounded-full"
                  />
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                    className="w-2 h-2 bg-gray-400 rounded-full"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatPanel;