"""
Isolated database management for multi-user support
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class IsolatedDatabase:
    """Database manager with user isolation"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db_path = self._get_user_db_path()
        self._init_db()
    
    def _get_user_db_path(self) -> str:
        """Get isolated database path for user"""
        # Create user directory if it doesn't exist
        user_dir = f"data/users/{self.user_id}"
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, "chat.db")
    
    def _init_db(self):
        """Initialize user's database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_starred BOOLEAN DEFAULT 0,
                folder_id TEXT
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                model TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Create folders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                parent_id TEXT
            )
        ''')
        
        # Create user settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_sessions(self, limit: int = 50) -> List[Dict]:
        """Get user's chat sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, s.title, s.model, s.created_at, s.updated_at, s.is_starred,
                   COUNT(m.id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            LIMIT ?
        ''', (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'title': row[1],
                'model': row[2],
                'created_at': row[3],
                'updated_at': row[4],
                'is_starred': bool(row[5]),
                'message_count': row[6]
            })
        
        conn.close()
        return sessions
    
    def create_session(self, session_id: str, title: str, model: str) -> Dict:
        """Create a new session for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (id, title, model)
            VALUES (?, ?, ?)
        ''', (session_id, title, model))
        
        conn.commit()
        conn.close()
        
        return {
            'id': session_id,
            'title': title,
            'model': model,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def add_message(self, session_id: str, role: str, content: str, 
                   model: str = None, metadata: Dict = None):
        """Add message to user's session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if session exists, create if not
        cursor.execute('SELECT id FROM sessions WHERE id = ?', (session_id,))
        if not cursor.fetchone():
            # Auto-create session
            title = content[:50] + "..." if len(content) > 50 else content
            cursor.execute('''
                INSERT INTO sessions (id, title, model)
                VALUES (?, ?, ?)
            ''', (session_id, title, model or 'general'))
        
        # Insert message
        metadata_str = json.dumps(metadata) if metadata else None
        cursor.execute('''
            INSERT INTO messages (session_id, role, content, model, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, role, content, model, metadata_str))
        
        # Update session timestamp
        cursor.execute('''
            UPDATE sessions 
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_messages(self, session_id: str) -> List[Dict]:
        """Get messages for a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, model, timestamp, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            message = {
                'role': row[0],
                'content': row[1],
                'model': row[2],
                'timestamp': row[3]
            }
            if row[4]:
                message['metadata'] = json.loads(row[4])
            messages.append(message)
        
        conn.close()
        return messages
    
    def delete_session(self, session_id: str):
        """Delete a session and its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages first
        cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        # Delete session
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_messages = cursor.fetchone()[0]
        
        # Model usage
        cursor.execute('''
            SELECT model, COUNT(*) as count
            FROM sessions
            GROUP BY model
        ''')
        model_usage = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'model_usage': model_usage,
            'user_id': self.user_id
        }

# Factory function
def get_user_database(user_id: str) -> IsolatedDatabase:
    """Get database instance for a specific user"""
    return IsolatedDatabase(user_id)