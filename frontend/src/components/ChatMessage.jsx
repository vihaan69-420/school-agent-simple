import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { User, Bot, Copy, Check } from 'lucide-react';
import { useChatStore } from '../store/chatStore';

const TypewriterText = ({ text, delay = 50, onComplete }) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, delay);

      return () => clearTimeout(timeout);
    } else if (onComplete) {
      onComplete();
    }
  }, [currentIndex, text, delay, onComplete]);

  return displayText;
};

const ChatMessage = ({ message, isTyping = false }) => {
  const { isDarkMode } = useChatStore();
  const [copied, setCopied] = useState(false);
  const [isTypingComplete, setIsTypingComplete] = useState(!isTyping);

  const isUser = message.role === 'user';

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const MarkdownComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      
      if (!inline && match) {
        return (
          <div className="relative group">
            <button
              onClick={() => copyToClipboard(String(children).replace(/\n$/, ''))}
              className="absolute top-2 right-2 p-2 bg-gray-700 hover:bg-gray-600 rounded text-white opacity-0 group-hover:opacity-100 transition-opacity"
              aria-label="Copy code"
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
            </button>
            <SyntaxHighlighter
              style={isDarkMode ? oneDark : oneLight}
              language={match[1]}
              PreTag="div"
              className="rounded-lg !bg-gray-100 dark:!bg-gray-800"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          </div>
        );
      }
      
      return (
        <code 
          className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-sm font-mono text-gray-800 dark:text-gray-200" 
          {...props}
        >
          {children}
        </code>
      );
    },
    pre({ children }) {
      return <div className="my-4">{children}</div>;
    },
    blockquote({ children }) {
      return (
        <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 my-4 italic text-gray-700 dark:text-gray-300">
          {children}
        </blockquote>
      );
    },
    h1({ children }) {
      return <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">{children}</h1>;
    },
    h2({ children }) {
      return <h2 className="text-xl font-bold mb-3 text-gray-900 dark:text-gray-100">{children}</h2>;
    },
    h3({ children }) {
      return <h3 className="text-lg font-bold mb-2 text-gray-900 dark:text-gray-100">{children}</h3>;
    },
    p({ children }) {
      return <p className="mb-4 text-gray-800 dark:text-gray-200 leading-relaxed">{children}</p>;
    },
    ul({ children }) {
      return <ul className="list-disc pl-6 mb-4 text-gray-800 dark:text-gray-200">{children}</ul>;
    },
    ol({ children }) {
      return <ol className="list-decimal pl-6 mb-4 text-gray-800 dark:text-gray-200">{children}</ol>;
    },
    li({ children }) {
      return <li className="mb-1">{children}</li>;
    },
    a({ href, children }) {
      return (
        <a 
          href={href}
          className="text-blue-600 dark:text-blue-400 hover:underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          {children}
        </a>
      );
    },
    strong({ children }) {
      return <strong className="font-bold text-gray-900 dark:text-gray-100">{children}</strong>;
    },
    em({ children }) {
      return <em className="italic text-gray-800 dark:text-gray-200">{children}</em>;
    },
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}
    >
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : 'bg-gradient-to-br from-purple-500 to-pink-500 text-white'
          }`}>
            {isUser ? <User size={18} /> : <Bot size={18} />}
          </div>
        </div>

        {/* Message content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block px-4 py-3 rounded-2xl max-w-full ${
            isUser
              ? 'bg-blue-500 text-white rounded-br-md'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md'
          }`}>
            {isUser ? (
              <p className="text-sm leading-relaxed">{message.content}</p>
            ) : (
              <div className="text-sm leading-relaxed">
                {isTyping && !isTypingComplete ? (
                  <TypewriterText 
                    text={message.content}
                    delay={30}
                    onComplete={() => setIsTypingComplete(true)}
                  />
                ) : (
                  <ReactMarkdown components={MarkdownComponents}>
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>
            )}
          </div>
          
          {/* Timestamp */}
          <div className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${
            isUser ? 'text-right' : 'text-left'
          }`}>
            {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : ''}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;