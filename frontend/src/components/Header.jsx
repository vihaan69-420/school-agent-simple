import React from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon, Settings, User, MessageSquare } from 'lucide-react';
import { useChatStore } from '../store/chatStore';

const Header = () => {
  const { 
    isDarkMode, 
    toggleTheme, 
    getCurrentSession 
  } = useChatStore();
  
  const currentSession = getCurrentSession();

  return (
    <motion.header 
      className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-md dark:bg-gray-900/80 dark:border-gray-800"
      initial={{ y: -50 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <div className="flex items-center justify-between px-4 py-2 lg:px-6">
        {/* Left section */}
        <div className="flex items-center space-x-3">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center space-x-2"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <MessageSquare size={18} className="text-white" />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              VihaanGPT
            </h1>
          </motion.div>
        </div>

        {/* Center section - Chat title */}
        <div className="flex-1 text-center px-4">
          <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
            {currentSession?.title || 'New Chat'}
          </h2>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle theme"
          >
            {isDarkMode ? (
              <Sun size={20} className="text-yellow-500" />
            ) : (
              <Moon size={20} className="text-gray-600" />
            )}
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Settings"
          >
            <Settings size={20} className="text-gray-600 dark:text-gray-400" />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Profile"
          >
            <User size={20} className="text-gray-600 dark:text-gray-400" />
          </motion.button>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;