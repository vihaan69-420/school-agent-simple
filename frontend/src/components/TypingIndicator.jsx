import React from 'react';
import { motion } from 'framer-motion';

const TypingIndicator = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex w-full mb-4 justify-start"
    >
      <div className="message-bubble rounded-2xl px-4 py-3 bg-gray-100 border border-gray-200 shadow-sm">
        <div className="flex items-center mb-1">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          <span className="text-xs font-medium text-gray-600">Qwen v2.5-Max</span>
        </div>
        <div className="flex items-center space-x-1">
          <div className="flex space-x-1">
            <motion.div
              className="w-2 h-2 bg-gray-400 rounded-full"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0 }}
            />
            <motion.div
              className="w-2 h-2 bg-gray-400 rounded-full"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }}
            />
            <motion.div
              className="w-2 h-2 bg-gray-400 rounded-full"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0.4 }}
            />
          </div>
          <span className="text-xs text-gray-500 ml-2">Thinking...</span>
        </div>
      </div>
    </motion.div>
  );
};

export default TypingIndicator;