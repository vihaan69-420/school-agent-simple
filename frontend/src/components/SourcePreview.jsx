import React, { useState, useEffect } from 'react';
import { X, ExternalLink, Loader2, AlertCircle } from 'lucide-react';

const SourcePreview = ({ url, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    fetchPreview();
  }, [url]);

  const fetchPreview = async () => {
    try {
      setLoading(true);
      // In a real app, this would fetch a preview from your backend
      // For now, we'll just show basic URL info
      const domain = new URL(url).hostname;
      
      setPreview({
        title: `Preview of ${domain}`,
        description: 'Click the link below to view the full page',
        image: null,
        favicon: `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
      });
    } catch (err) {
      setError('Failed to load preview');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Source Preview
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
            </div>
          ) : error ? (
            <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
              <span className="text-red-900 dark:text-red-200">{error}</span>
            </div>
          ) : preview ? (
            <div className="space-y-4">
              {/* Favicon and URL */}
              <div className="flex items-center gap-3">
                {preview.favicon && (
                  <img 
                    src={preview.favicon} 
                    alt="Site favicon" 
                    className="w-8 h-8 rounded"
                    onError={(e) => e.target.style.display = 'none'}
                  />
                )}
                <div className="flex-1">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {new URL(url).hostname}
                  </div>
                  <div className="text-xs text-gray-400 dark:text-gray-500 truncate">
                    {url}
                  </div>
                </div>
              </div>

              {/* Preview content */}
              <div className="space-y-2">
                <h4 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {preview.title}
                </h4>
                <p className="text-gray-600 dark:text-gray-400">
                  {preview.description}
                </p>
              </div>

              {/* Preview image if available */}
              {preview.image && (
                <img 
                  src={preview.image} 
                  alt="Page preview" 
                  className="w-full rounded-lg"
                />
              )}

              {/* Open link button */}
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                Open in new tab
              </a>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default SourcePreview;