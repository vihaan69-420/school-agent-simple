import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ArrowRight, Sparkles } from 'lucide-react';

const PerplexitySearchInput = ({ onSearch, isLoading = false, className = "" }) => {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query.trim());
      setQuery('');
      inputRef.current?.blur();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`w-full max-w-4xl mx-auto ${className}`}
    >
      {/* Search Container */}
      <div className="relative">
        <motion.div
          className={`
            relative overflow-hidden rounded-2xl bg-white/90 backdrop-blur-md 
            border transition-all duration-300 ease-out shadow-lg
            ${isFocused 
              ? 'border-blue-400 shadow-2xl shadow-blue-500/25 bg-white' 
              : 'border-gray-200 hover:border-gray-300 hover:shadow-xl'
            }
          `}
          whileHover={{ scale: 1.01 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
          {/* Animated Background Gradient */}
          <AnimatePresence>
            {isFocused && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-gradient-to-r from-blue-50 via-purple-50 to-pink-50"
                transition={{ duration: 0.3 }}
              />
            )}
          </AnimatePresence>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="relative">
            <div className="flex items-center px-6 py-4">
              {/* Search Icon */}
              <motion.div
                animate={{ 
                  scale: isFocused ? 1.1 : 1,
                  color: isFocused ? '#3B82F6' : '#6B7280'
                }}
                transition={{ duration: 0.2 }}
                className="mr-4 flex-shrink-0"
              >
                <Search className="w-6 h-6" />
              </motion.div>

              {/* Text Input */}
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                onKeyPress={handleKeyPress}
                placeholder="Ask anything..."
                disabled={isLoading}
                className={`
                  flex-1 text-lg bg-transparent outline-none resize-none
                  placeholder-gray-500 text-gray-900 font-medium
                  transition-all duration-200
                  ${isLoading ? 'cursor-not-allowed opacity-70' : ''}
                `}
                autoComplete="off"
                spellCheck="false"
              />

              {/* Submit Button */}
              <AnimatePresence>
                {(query.trim() || isLoading) && (
                  <motion.button
                    initial={{ opacity: 0, scale: 0.8, x: 10 }}
                    animate={{ opacity: 1, scale: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.8, x: 10 }}
                    transition={{ duration: 0.2 }}
                    type="submit"
                    disabled={!query.trim() || isLoading}
                    className={`
                      ml-4 flex-shrink-0 p-2 rounded-xl transition-all duration-200
                      ${query.trim() && !isLoading
                        ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg hover:shadow-xl' 
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }
                    `}
                  >
                    {isLoading ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        <Sparkles className="w-5 h-5" />
                      </motion.div>
                    ) : (
                      <ArrowRight className="w-5 h-5" />
                    )}
                  </motion.button>
                )}
              </AnimatePresence>
            </div>
          </form>

          {/* Focus Ring */}
          <AnimatePresence>
            {isFocused && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="absolute inset-0 rounded-2xl ring-2 ring-blue-400 ring-opacity-50 pointer-events-none"
                transition={{ duration: 0.2 }}
              />
            )}
          </AnimatePresence>
        </motion.div>

        {/* Subtle Hint Text */}
        <AnimatePresence>
          {!isFocused && !query && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ delay: 0.5, duration: 0.3 }}
              className="text-center mt-4"
            >
              <p className="text-sm text-gray-500 font-medium">
                Press <kbd className="px-2 py-1 text-xs bg-gray-100 rounded border">Enter</kbd> to search
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Optional: Floating Suggestions */}
      <AnimatePresence>
        {isFocused && !query && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ delay: 0.1, duration: 0.3 }}
            className="mt-4 p-4 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200 shadow-lg"
          >
            <p className="text-sm text-gray-600 mb-3 font-medium">Try asking:</p>
            <div className="space-y-2">
              {[
                "What's the weather like today?",
                "Explain quantum computing in simple terms",
                "Help me plan a vacation to Japan"
              ].map((suggestion, index) => (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 + 0.2 }}
                  onClick={() => {
                    setQuery(suggestion);
                    inputRef.current?.focus();
                  }}
                  className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                >
                  {suggestion}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default PerplexitySearchInput;