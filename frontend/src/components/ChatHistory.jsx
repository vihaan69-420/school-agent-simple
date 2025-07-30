import React, { useState } from 'react';
import { 
  MessageSquare, Trash2, Star, StarOff, Archive, 
  MoreVertical, Edit3, FolderPlus, ChevronRight,
  Clock, Search
} from 'lucide-react';

const ChatHistory = ({ 
  sessions, 
  folders, 
  activeSessionId, 
  onSelectSession, 
  onDeleteSession,
  onUpdateSession,
  onCreateFolder 
}) => {
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [editingTitle, setEditingTitle] = useState(null);
  const [showFolderDialog, setShowFolderDialog] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  // Group sessions by date
  const groupSessionsByDate = (sessions) => {
    const groups = {
      today: [],
      yesterday: [],
      lastWeek: [],
      lastMonth: [],
      older: []
    };

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterdayStart = new Date(todayStart);
    yesterdayStart.setDate(yesterdayStart.getDate() - 1);
    const weekAgo = new Date(todayStart);
    weekAgo.setDate(weekAgo.getDate() - 7);
    const monthAgo = new Date(todayStart);
    monthAgo.setMonth(monthAgo.getMonth() - 1);

    sessions.forEach(session => {
      const sessionDate = new Date(session.updated_at || session.created_at);
      
      if (sessionDate >= todayStart) {
        groups.today.push(session);
      } else if (sessionDate >= yesterdayStart) {
        groups.yesterday.push(session);
      } else if (sessionDate >= weekAgo) {
        groups.lastWeek.push(session);
      } else if (sessionDate >= monthAgo) {
        groups.lastMonth.push(session);
      } else {
        groups.older.push(session);
      }
    });

    return groups;
  };

  const toggleFolder = (folderId) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const handleTitleEdit = (sessionId, newTitle) => {
    onUpdateSession(sessionId, { title: newTitle });
    setEditingTitle(null);
  };

  const handleCreateFolder = () => {
    if (newFolderName.trim()) {
      onCreateFolder(newFolderName.trim());
      setNewFolderName('');
      setShowFolderDialog(false);
    }
  };

  const formatRelativeTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const SessionItem = ({ session }) => {
    const [showMenu, setShowMenu] = useState(false);
    const isActive = session.id === activeSessionId;
    const isEditing = editingTitle === session.id;

    return (
      <div
        className={`group relative flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 ${
          isActive 
            ? 'bg-purple-100 dark:bg-purple-900/20 text-purple-900 dark:text-purple-200' 
            : 'hover:bg-gray-100 dark:hover:bg-gray-700'
        }`}
        onClick={() => !isEditing && onSelectSession(session.id)}
      >
        <MessageSquare className="w-4 h-4 flex-shrink-0 text-gray-500 dark:text-gray-400" />
        
        {isEditing ? (
          <input
            type="text"
            value={session.title}
            onChange={(e) => onUpdateSession(session.id, { title: e.target.value })}
            onBlur={() => setEditingTitle(null)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                setEditingTitle(null);
              }
              if (e.key === 'Escape') {
                setEditingTitle(null);
              }
            }}
            onClick={(e) => e.stopPropagation()}
            className="flex-1 bg-white dark:bg-gray-800 px-2 py-1 rounded border border-purple-500 focus:outline-none"
            autoFocus
          />
        ) : (
          <div className="flex-1 overflow-hidden">
            <div className="truncate text-sm font-medium">
              {session.title}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {session.message_count || 0} messages • {formatRelativeTime(session.updated_at)}
            </div>
          </div>
        )}
        
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {session.is_starred && (
            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
          )}
          
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              <MoreVertical className="w-4 h-4" />
            </button>
            
            {showMenu && (
              <div className="absolute right-0 top-8 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingTitle(session.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                >
                  <Edit3 className="w-4 h-4" />
                  Rename
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onUpdateSession(session.id, { is_starred: !session.is_starred });
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                >
                  {session.is_starred ? <StarOff className="w-4 h-4" /> : <Star className="w-4 h-4" />}
                  {session.is_starred ? 'Unstar' : 'Star'}
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onUpdateSession(session.id, { is_archived: true });
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                >
                  <Archive className="w-4 h-4" />
                  Archive
                </button>
                
                <div className="border-t border-gray-200 dark:border-gray-700 my-1" />
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const groupedSessions = groupSessionsByDate(sessions);

  return (
    <div className="px-4 pb-4">
      {/* Folders */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
            Folders
          </h3>
          <button
            onClick={() => setShowFolderDialog(true)}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <FolderPlus className="w-4 h-4 text-gray-500" />
          </button>
        </div>
        
        {folders.map(folder => (
          <div key={folder.id} className="mb-1">
            <button
              onClick={() => toggleFolder(folder.id)}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-left"
            >
              <ChevronRight 
                className={`w-4 h-4 transition-transform ${
                  expandedFolders.has(folder.id) ? 'rotate-90' : ''
                }`}
              />
              <span className="text-2xl leading-none">{folder.icon}</span>
              <span className="flex-1 text-sm font-medium">{folder.name}</span>
              <span className="text-xs text-gray-500">{folder.count || 0}</span>
            </button>
            
            {expandedFolders.has(folder.id) && (
              <div className="ml-8 mt-1">
                {/* Folder sessions would go here */}
                <div className="text-xs text-gray-500 dark:text-gray-400 py-2">
                  No chats in this folder
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Date Groups */}
      <div className="space-y-4">
        {groupedSessions.today.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
              Today
            </h3>
            <div className="space-y-1">
              {groupedSessions.today.map(session => (
                <SessionItem key={session.id} session={session} />
              ))}
            </div>
          </div>
        )}

        {groupedSessions.yesterday.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
              Yesterday
            </h3>
            <div className="space-y-1">
              {groupedSessions.yesterday.map(session => (
                <SessionItem key={session.id} session={session} />
              ))}
            </div>
          </div>
        )}

        {groupedSessions.lastWeek.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
              Last 7 days
            </h3>
            <div className="space-y-1">
              {groupedSessions.lastWeek.map(session => (
                <SessionItem key={session.id} session={session} />
              ))}
            </div>
          </div>
        )}

        {groupedSessions.lastMonth.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
              Last 30 days
            </h3>
            <div className="space-y-1">
              {groupedSessions.lastMonth.map(session => (
                <SessionItem key={session.id} session={session} />
              ))}
            </div>
          </div>
        )}

        {groupedSessions.older.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
              Older
            </h3>
            <div className="space-y-1">
              {groupedSessions.older.map(session => (
                <SessionItem key={session.id} session={session} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Create Folder Dialog */}
      {showFolderDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">Create New Folder</h3>
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="Folder name"
              className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-4"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateFolder();
                if (e.key === 'Escape') setShowFolderDialog(false);
              }}
            />
            <div className="flex gap-2">
              <button
                onClick={handleCreateFolder}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Create
              </button>
              <button
                onClick={() => setShowFolderDialog(false)}
                className="flex-1 px-4 py-2 bg-gray-300 dark:bg-gray-600 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistory;