#!/usr/bin/env python3
"""
Enhanced chat management system with history, folders, and advanced features
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
import logging
import sqlite3
import time
from database import DatabaseManager

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages chat sessions, history, and folders"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._init_chat_tables()
    
    def _init_chat_tables(self):
        """Initialize chat-related tables"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Chat sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        model TEXT DEFAULT 'general',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        folder_id TEXT,
                        is_starred BOOLEAN DEFAULT 0,
                        is_archived BOOLEAN DEFAULT 0,
                        summary TEXT,
                        tags TEXT,
                        message_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Chat folders table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_folders (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        color TEXT DEFAULT '#6B7280',
                        icon TEXT DEFAULT '📁',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        parent_id TEXT,
                        sort_order INTEGER DEFAULT 0
                    )
                ''')
                
                # Chat metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_metadata (
                        session_id TEXT PRIMARY KEY,
                        total_tokens INTEGER DEFAULT 0,
                        model_switches TEXT,
                        shared_link TEXT,
                        is_public BOOLEAN DEFAULT 0,
                        view_count INTEGER DEFAULT 0,
                        FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_updated ON chat_sessions(updated_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_folder ON chat_sessions(folder_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_starred ON chat_sessions(is_starred)')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize chat tables: {e}")
    
    def create_session(self, session_id: str, title: str = "New Chat", model: str = "general") -> Dict:
        """Create a new chat session"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                now_iso = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO chat_sessions (id, title, model, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, title, model, now_iso, now_iso))
                
                # Also create metadata entry
                cursor.execute('''
                    INSERT INTO chat_metadata (session_id)
                    VALUES (?)
                ''', (session_id,))
                
                conn.commit()
                
                return {
                    'id': session_id,
                    'title': title,
                    'model': model,
                    'created_at': now_iso,
                    'updated_at': now_iso,
                    'message_count': 0
                }
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a specific chat session"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.*, m.total_tokens, m.view_count
                    FROM chat_sessions s
                    LEFT JOIN chat_metadata m ON s.id = m.session_id
                    WHERE s.id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'title': row[1],
                        'model': row[2],
                        'created_at': row[3],
                        'updated_at': row[4],
                        'folder_id': row[5],
                        'is_starred': bool(row[6]),
                        'is_archived': bool(row[7]),
                        'summary': row[8],
                        'tags': json.loads(row[9]) if row[9] else [],
                        'message_count': row[10],
                        'total_tokens': row[11] if len(row) > 11 else 0,
                        'view_count': row[12] if len(row) > 12 else 0
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def get_all_sessions(self, include_archived: bool = False) -> List[Dict]:
        """Get all chat sessions"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT s.*, m.total_tokens, 
                           (SELECT COUNT(*) FROM conversations WHERE session_id = s.id) as actual_count
                    FROM chat_sessions s
                    LEFT JOIN chat_metadata m ON s.id = m.session_id
                '''
                
                if not include_archived:
                    query += ' WHERE s.is_archived = 0'
                
                query += ' ORDER BY s.updated_at DESC'
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    sessions.append({
                        'id': row[0],
                        'title': row[1],
                        'model': row[2],
                        'created_at': row[3],
                        'updated_at': row[4],
                        'folder_id': row[5],
                        'is_starred': bool(row[6]),
                        'is_archived': bool(row[7]),
                        'summary': row[8],
                        'tags': json.loads(row[9]) if row[9] else [],
                        'message_count': row[12] if len(row) > 12 else row[10],
                        'total_tokens': row[11] if len(row) > 11 else 0
                    })
                
                return sessions
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            return []
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session properties"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query
                updates = []
                params = []
                
                allowed_fields = ['title', 'model', 'folder_id', 'is_starred', 
                                'is_archived', 'summary', 'tags']
                
                for field in allowed_fields:
                    if field in kwargs:
                        updates.append(f"{field} = ?")
                        if field == 'tags':
                            params.append(json.dumps(kwargs[field]))
                        else:
                            params.append(kwargs[field])
                
                if updates:
                    updates.append("updated_at = ?")
                    params.append(datetime.now().isoformat())
                    params.append(session_id)
                    
                    query = f"UPDATE chat_sessions SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(query, params)
                    conn.commit()
                    
                    return cursor.rowcount > 0
                
                return False
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first
                cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
                
                # Delete metadata
                cursor.execute('DELETE FROM chat_metadata WHERE session_id = ?', (session_id,))
                
                # Delete session
                cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    def auto_generate_title(self, session_id: str, first_message: str) -> str:
        """Auto-generate a title based on the first message"""
        # Simple title generation - take first 50 chars
        title = first_message[:50].strip()
        if len(first_message) > 50:
            title += "..."
        
        # Remove any newlines
        title = title.replace('\n', ' ')
        
        # Update the session
        self.update_session(session_id, title=title)
        
        return title
    
    def search_sessions(self, query: str) -> List[Dict]:
        """Search through chat sessions and messages"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Search in session titles and messages
                cursor.execute('''
                    SELECT DISTINCT s.*
                    FROM chat_sessions s
                    LEFT JOIN conversations c ON s.id = c.session_id
                    WHERE s.title LIKE ? 
                       OR c.content LIKE ?
                       OR s.summary LIKE ?
                    ORDER BY s.updated_at DESC
                    LIMIT 20
                ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
                
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    sessions.append({
                        'id': row[0],
                        'title': row[1],
                        'model': row[2],
                        'created_at': row[3],
                        'updated_at': row[4],
                        'is_starred': bool(row[6]),
                        'summary': row[8]
                    })
                
                return sessions
        except Exception as e:
            logger.error(f"Failed to search sessions: {e}")
            return []
    
    # Folder management
    def create_folder(self, folder_id: str, name: str, color: str = '#6B7280', 
                     icon: str = '📁', parent_id: str = None) -> Dict:
        """Create a new folder"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO chat_folders (id, name, color, icon, parent_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (folder_id, name, color, icon, parent_id))
                conn.commit()
                
                return {
                    'id': folder_id,
                    'name': name,
                    'color': color,
                    'icon': icon,
                    'parent_id': parent_id
                }
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return None
    
    def get_folders(self) -> List[Dict]:
        """Get all folders"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM chat_folders
                    ORDER BY sort_order, name
                ''')
                
                rows = cursor.fetchall()
                folders = []
                
                for row in rows:
                    folders.append({
                        'id': row[0],
                        'name': row[1],
                        'color': row[2],
                        'icon': row[3],
                        'created_at': row[4],
                        'parent_id': row[5],
                        'sort_order': row[6]
                    })
                
                return folders
        except Exception as e:
            logger.error(f"Failed to get folders: {e}")
            return []
    
    def update_message_count(self, session_id: str) -> None:
        """Update the message count for a session"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE chat_sessions 
                    SET message_count = (
                        SELECT COUNT(*) FROM conversations 
                        WHERE session_id = ?
                    ),
                    updated_at = ?
                    WHERE id = ?
                ''', (session_id, datetime.now().isoformat(), session_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update message count: {e}")
    
    def get_session_stats(self) -> Dict:
        """Get overall chat statistics"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total sessions
                cursor.execute('SELECT COUNT(*) FROM chat_sessions')
                stats['total_sessions'] = cursor.fetchone()[0]
                
                # Total messages
                cursor.execute('SELECT COUNT(*) FROM conversations')
                stats['total_messages'] = cursor.fetchone()[0]
                
                # Sessions by model
                cursor.execute('''
                    SELECT model, COUNT(*) 
                    FROM chat_sessions 
                    GROUP BY model
                ''')
                stats['sessions_by_model'] = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute('''
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM chat_sessions
                    WHERE created_at > datetime('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                ''')
                stats['recent_activity'] = [
                    {'date': row[0], 'count': row[1]} 
                    for row in cursor.fetchall()
                ]
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}