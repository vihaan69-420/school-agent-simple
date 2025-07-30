import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, MessageSquare, Edit2, Trash2, X, Check } from 'lucide-react';
import { useChatStore } from '../store/chatStore';

const Sidebar = () => {
  const { 
    sessions, 
    currentSessionId, 
    sidebarOpen, 
    setSidebarOpen,
    createNewSession,
    switchSession,
    deleteSession,
    renameSession 
  } = useChatStore();
  
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  const handleNewChat = () => {
    createNewSession();
  };

  const handleRename = (sessionId, currentTitle) => {
    setEditingSessionId(sessionId);
    setEditingTitle(currentTitle);
  };

  const handleSaveRename = () => {
    if (editingTitle.trim()) {
      renameSession(editingSessionId, editingTitle.trim());
    }
    setEditingSessionId(null);
    setEditingTitle('');
  };

  const handleCancelRename = () => {
    setEditingSessionId(null);
    setEditingTitle('');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (hours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={{ x: -320 }}
        animate={{ x: sidebarOpen ? 0 : -320 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="fixed top-0 left-0 z-50 w-80 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 lg:relative lg:translate-x-0 lg:block"
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-800">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Chat History
              </h2>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors lg:hidden"
                aria-label="Close sidebar"
              >
                <X size={20} className="text-gray-600 dark:text-gray-400" />
              </button>
            </div>
          </div>

          {/* New Chat Button */}
          <div className="p-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleNewChat}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
            >
              <Plus size={20} />
              <span className="font-medium">New Chat</span>
            </motion.button>
          </div>

          {/* Chat Sessions */}
          <div className="flex-1 overflow-y-auto px-4 pb-4">
            <div className="space-y-2">
              {sessions.map((session) => (
                <motion.div
                  key={session.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.02 }}
                  className={`group relative p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                    currentSessionId === session.id
                      ? 'bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-200 dark:border-blue-700'
                      : 'bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                  onClick={() => switchSession(session.id)}
                >
                  <div className="flex items-start space-x-3">
                    <div className="mt-1">
                      <MessageSquare size={16} className="text-gray-500 dark:text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      {editingSessionId === session.id ? (
                        <div className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={editingTitle}
                            onChange={(e) => setEditingTitle(e.target.value)}
                            className="flex-1 px-2 py-1 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                            onKeyPress={(e) => e.key === 'Enter' && handleSaveRename()}
                            autoFocus
                          />
                          <button
                            onClick={handleSaveRename}
                            className="p-1 text-green-600 hover:text-green-700"
                          >
                            <Check size={14} />
                          </button>
                          <button
                            onClick={handleCancelRename}
                            className="p-1 text-gray-600 hover:text-gray-700"
                          >
                            <X size={14} />
                          </button>
                        </div>
                      ) : (
                        <>
                          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                            {session.title}
                          </h3>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {formatDate(session.updatedAt)}
                          </p>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Action buttons */}
                  {editingSessionId !== session.id && (
                    <div className="absolute top-2 right-2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRename(session.id, session.title);
                        }}
                        className="p-1 text-gray-500 hover:text-blue-600 dark:hover:text-blue-400"
                        aria-label="Rename chat"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.id);
                        }}
                        className="p-1 text-gray-500 hover:text-red-600 dark:hover:text-red-400"
                        aria-label="Delete chat"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
            
            {sessions.length === 0 && (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
                <p className="text-sm">No chat sessions yet</p>
                <p className="text-xs mt-1">Start a new conversation to begin</p>
              </div>
            )}
          </div>
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;