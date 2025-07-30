import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Paperclip, Image, Code, FileText } from 'lucide-react';
import { useChatStore } from '../store/chatStore';

const ChatInput = ({ onSendMessage }) => {
  const { inputValue, setInputValue, isLoading } = useChatStore();
  const textareaRef = useRef(null);
  const [rows, setRows] = useState(1);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const lineHeight = 20;
      const maxRows = 5;
      const newRows = Math.min(Math.max(Math.ceil(textarea.scrollHeight / lineHeight), 1), maxRows);
      setRows(newRows);
      textarea.style.height = `${newRows * lineHeight}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
      setRows(1);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <motion.div 
      className="sticky bottom-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t border-gray-200 dark:border-gray-800 p-3"
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <div className="max-w-4xl mx-auto">
        {/* Tool Icons Row */}
        <div className="flex items-center space-x-2 mb-2 px-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
            aria-label="Text chat (active)"
          >
            <FileText size={18} />
          </motion.button>
          
          <button
            className="p-2 rounded-lg text-gray-400 dark:text-gray-600 cursor-not-allowed opacity-50"
            disabled
            aria-label="Image upload (disabled)"
          >
            <Image size={18} />
          </button>
          
          <button
            className="p-2 rounded-lg text-gray-400 dark:text-gray-600 cursor-not-allowed opacity-50"
            disabled
            aria-label="File upload (disabled)"
          >
            <Paperclip size={18} />
          </button>
          
          <button
            className="p-2 rounded-lg text-gray-400 dark:text-gray-600 cursor-not-allowed opacity-50"
            disabled
            aria-label="Code tools (disabled)"
          >
            <Code size={18} />
          </button>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-end space-x-3 bg-gray-100 dark:bg-gray-800 rounded-2xl p-3 shadow-lg">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Message VihaanGPT..."
                className="w-full bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 resize-none focus:outline-none text-sm leading-5"
                rows={rows}
                style={{ minHeight: '20px', maxHeight: '100px' }}
                disabled={isLoading}
              />
            </div>
            
            <motion.button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              whileHover={{ scale: inputValue.trim() && !isLoading ? 1.05 : 1 }}
              whileTap={{ scale: inputValue.trim() && !isLoading ? 0.95 : 1 }}
              className={`p-2 rounded-xl transition-all duration-200 ${
                inputValue.trim() && !isLoading
                  ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              }`}
              aria-label="Send message"
            >
              {isLoading ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                />
              ) : (
                <Send size={18} />
              )}
            </motion.button>
          </div>
        </form>

      </div>
    </motion.div>
  );
};

export default ChatInput;