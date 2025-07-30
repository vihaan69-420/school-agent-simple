import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Brain, Zap } from 'lucide-react';
import PerplexitySearchInput from './PerplexitySearchInput';

const LandingPage = ({ onSearch, isLoading }) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 px-4">
      {/* Hero Section */}
      <div className="w-full max-w-6xl mx-auto text-center">
        {/* Animated Logo/Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="mb-8"
        >
          <div className="flex items-center justify-center space-x-3 mb-4">
            <motion.div
              animate={{ 
                rotate: [0, 360],
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                rotate: { duration: 8, repeat: Infinity, ease: "linear" },
                scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
              }}
              className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-lg"
            >
              <Sparkles className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Qwen Assistant
            </h1>
          </div>
          
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed"
          >
            Your intelligent AI companion powered by{' '}
            <span className="font-semibold text-blue-600">Qwen v2.5-Max</span> and{' '}
            <span className="font-semibold text-purple-600">LangChain</span>
          </motion.p>
        </motion.div>

        {/* Feature Pills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="flex flex-wrap justify-center gap-4 mb-12"
        >
          {[
            { icon: Brain, text: "Advanced AI", color: "blue" },
            { icon: Zap, text: "Lightning Fast", color: "yellow" },
            { icon: Sparkles, text: "Creative Responses", color: "purple" }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7 + index * 0.1, duration: 0.4 }}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full bg-white/70 backdrop-blur-sm border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300`}
            >
              <feature.icon className={`w-4 h-4 text-${feature.color}-500`} />
              <span className="text-sm font-medium text-gray-700">{feature.text}</span>
            </motion.div>
          ))}
        </motion.div>

        {/* Search Input */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="mb-16"
        >
          <PerplexitySearchInput 
            onSearch={onSearch} 
            isLoading={isLoading}
            className="px-4"
          />
        </motion.div>

        {/* Stats/Info Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
        >
          {[
            { 
              title: "Multi-turn Memory", 
              description: "Remembers context throughout your conversation",
              gradient: "from-blue-500 to-cyan-500"
            },
            { 
              title: "Real-time Responses", 
              description: "Get instant answers powered by advanced AI",
              gradient: "from-purple-500 to-pink-500"
            },
            { 
              title: "Natural Language", 
              description: "Chat naturally, no special commands needed",
              gradient: "from-green-500 to-emerald-500"
            }
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.4 + index * 0.1, duration: 0.5 }}
              className="text-center p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <div className={`w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-r ${stat.gradient} flex items-center justify-center shadow-lg`}>
                <div className="w-6 h-6 bg-white rounded-full"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">{stat.title}</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{stat.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8, duration: 0.6 }}
          className="mt-16 text-center"
        >
          <p className="text-sm text-gray-500">
            Powered by Qwen v2.5-Max • Built with React & LangChain
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingPage;