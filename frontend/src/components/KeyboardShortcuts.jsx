import React, { useState, useEffect } from 'react';
import { Command, X } from 'lucide-react';

const KeyboardShortcuts = ({ isOpen, onClose }) => {
  const shortcuts = [
    { keys: ['⌘', 'K'], description: 'Open command palette' },
    { keys: ['⌘', '/'], description: 'New chat' },
    { keys: ['⌘', 'Shift', 'E'], description: 'Export chat' },
    { keys: ['⌘', 'Shift', 'D'], description: 'Toggle dark mode' },
    { keys: ['⌘', 'B'], description: 'Toggle sidebar' },
    { keys: ['⌘', 'Enter'], description: 'Send message' },
    { keys: ['Shift', 'Enter'], description: 'New line in message' },
    { keys: ['Esc'], description: 'Close modals/Cancel edit' },
    { keys: ['⌘', 'C'], description: 'Copy message' },
    { keys: ['⌘', 'R'], description: 'Regenerate response' },
    { keys: ['⌘', 'S'], description: 'Save chat (auto-saved)' },
    { keys: ['⌘', 'F'], description: 'Search in chat' },
  ];

  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  const formatKey = (key) => {
    if (key === '⌘' && !isMac) return 'Ctrl';
    return key;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Command className="w-6 h-6" />
            Keyboard Shortcuts
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Shortcuts List */}
        <div className="p-6 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-900"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {shortcut.description}
                </span>
                <div className="flex items-center gap-1">
                  {shortcut.keys.map((key, i) => (
                    <React.Fragment key={i}>
                      <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 dark:text-gray-200 bg-gray-200 dark:bg-gray-700 rounded">
                        {formatKey(key)}
                      </kbd>
                      {i < shortcut.keys.length - 1 && (
                        <span className="text-gray-500 dark:text-gray-400">+</span>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <p className="text-sm text-purple-900 dark:text-purple-200">
              <strong>Pro tip:</strong> Press <kbd className="px-2 py-1 text-xs font-semibold bg-purple-200 dark:bg-purple-800 rounded">?</kbd> anywhere to show this help dialog.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KeyboardShortcuts;