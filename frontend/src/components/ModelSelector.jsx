import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Zap, GraduationCap, Globe, Check } from 'lucide-react';

const ModelSelector = ({ selectedModel, onModelChange, models = [] }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getIcon = (iconName) => {
    switch (iconName) {
      case '⚡':
        return <Zap className="w-4 h-4" />;
      case '🎓':
        return <GraduationCap className="w-4 h-4" />;
      case '🌐':
        return <Globe className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const currentModel = models.find(m => m.id === selectedModel) || models[0] || {
    id: 'general',
    name: 'Loading...',
    icon: '⚡',
    color: '#3B82F6',
    description: 'Loading models...'
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-750 transition-all duration-200 shadow-sm hover:shadow-md"
        style={{ borderColor: isOpen ? currentModel.color : undefined }}
      >
        <div className="flex items-center gap-2">
          <div style={{ color: currentModel.color }}>
            {getIcon(currentModel.icon)}
          </div>
          <span className="font-medium text-gray-900 dark:text-gray-100">
            {currentModel.name}
          </span>
        </div>
        <ChevronDown 
          className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>

      {isOpen && (
        <div className="absolute z-50 bottom-full mb-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-in fade-in slide-in-from-bottom-1 duration-200">
          <div className="p-2">
            {models.map((model) => (
              <button
                key={model.id}
                onClick={() => {
                  onModelChange(model.id);
                  setIsOpen(false);
                }}
                className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
                  selectedModel === model.id
                    ? 'bg-gray-100 dark:bg-gray-700'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-750'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div 
                    className="mt-0.5 p-2 rounded-lg"
                    style={{ 
                      backgroundColor: `${model.color}20`,
                      color: model.color 
                    }}
                  >
                    {getIcon(model.icon)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                        {model.name}
                      </h3>
                      {selectedModel === model.id && (
                        <Check className="w-4 h-4" style={{ color: model.color }} />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                      {model.description}
                    </p>
                    {model.features && (
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {model.features.web_scraping && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                            Web Scraping
                          </span>
                        )}
                        {model.features.knowledge_base && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                            Knowledge Base
                          </span>
                        )}
                        {model.features.citations && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
                            Citations
                          </span>
                        )}
                        {model.features.streaming && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200">
                            Streaming
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;