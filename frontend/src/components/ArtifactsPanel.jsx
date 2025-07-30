import React, { useState } from 'react';
import { X, Copy, Download, Code, FileText, Maximize2, Check } from 'lucide-react';

const ArtifactsPanel = ({ artifacts, onClose, onRemove }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [copiedId, setCopiedId] = useState(null);

  const copyToClipboard = (content, id) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const downloadArtifact = (artifact) => {
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `artifact_${artifact.language || 'text'}_${Date.now()}.${artifact.language || 'txt'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getLanguageColor = (language) => {
    const colors = {
      javascript: 'text-yellow-600',
      python: 'text-blue-600',
      html: 'text-orange-600',
      css: 'text-pink-600',
      json: 'text-green-600',
      sql: 'text-purple-600',
      default: 'text-gray-600'
    };
    return colors[language] || colors.default;
  };

  if (artifacts.length === 0) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Code className="w-5 h-5" />
          Artifacts ({artifacts.length})
        </h3>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {artifacts.map((artifact, index) => (
          <button
            key={artifact.id}
            onClick={() => setActiveTab(index)}
            className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === index
                ? 'text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <span className={`${getLanguageColor(artifact.language)}`}>
              {artifact.language || 'Text'}
            </span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {artifacts[activeTab] && (
          <div className="h-full flex flex-col">
            {/* Toolbar */}
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {artifacts[activeTab].language || 'Plain Text'}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => copyToClipboard(artifacts[activeTab].content, artifacts[activeTab].id)}
                  className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                  title="Copy"
                >
                  {copiedId === artifacts[activeTab].id ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={() => downloadArtifact(artifacts[activeTab])}
                  className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                  title="Download"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    // Open in fullscreen/modal
                    console.log('Maximize artifact');
                  }}
                  className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                  title="Maximize"
                >
                  <Maximize2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onRemove(artifacts[activeTab].id)}
                  className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                  title="Remove"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Code Display */}
            <div className="flex-1 overflow-auto p-4 bg-gray-900 dark:bg-gray-950">
              <pre className="text-sm text-gray-100 font-mono">
                <code>{artifacts[activeTab].content}</code>
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArtifactsPanel;