import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
        self.is_postgres = self.db_url.startswith("postgresql://")
        
        if self.is_postgres:
            # Parse PostgreSQL URL
            result = urlparse(self.db_url)
            self.db_config = {
                'database': result.path[1:],
                'user': result.username,
                'password': result.password,
                'host': result.hostname,
                'port': result.port
            }
        
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        if self.is_postgres:
            return psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)
        else:
            import sqlite3
            conn = sqlite3.connect(self.db_url.replace("sqlite:///", ""))
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                # PostgreSQL schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id SERIAL PRIMARY KEY,
                        category TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)')
            else:
                # SQLite schema (your existing code)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
        finally:
            conn.close()
    
    def save_conversation(self, session_id: str, role: str, content: str) -> int:
        """Save a conversation message"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (session_id, role, content)
                VALUES (%s, %s, %s)
            ''' if self.is_postgres else '''
                INSERT INTO conversations (session_id, role, content)
                VALUES (?, ?, ?)
            ''', (session_id, role, content))
            
            conn.commit()
            return cursor.lastrowid if not self.is_postgres else cursor.fetchone()['id']
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            raise
        finally:
            conn.close()
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT role, content, timestamp 
                FROM conversations 
                WHERE session_id = %s 
                ORDER BY timestamp ASC 
                LIMIT %s
            ''' if self.is_postgres else '''
                SELECT role, content, timestamp 
                FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise
        finally:
            conn.close()
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all unique chat sessions with metadata"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                cursor.execute('''
                    WITH RankedConversations AS (
                        SELECT 
                            session_id,
                            content,
                            timestamp,
                            ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY timestamp ASC) as rn
                        FROM conversations
                        WHERE role = 'user'
                    )
                    SELECT 
                        session_id,
                        MAX(CASE WHEN rn = 1 THEN content END) as title,
                        MAX(timestamp) as timestamp,
                        MAX(CASE WHEN rn = 1 THEN content END) as preview
                    FROM RankedConversations
                    GROUP BY session_id
                    ORDER BY MAX(timestamp) DESC
                ''')
            else:
                cursor.execute('''
                    SELECT 
                        session_id,
                        MIN(content) as title,
                        MAX(timestamp) as timestamp,
                        MIN(content) as preview
                    FROM conversations
                    WHERE role = 'user'
                    GROUP BY session_id
                    ORDER BY timestamp DESC
                ''')
            
            rows = cursor.fetchall()
            sessions = []
            
            for row in rows:
                row_dict = dict(row)
                title = row_dict['title'] or "New Chat"
                if len(title) > 50:
                    title = title[:50] + "..."
                
                sessions.append({
                    'session_id': row_dict['session_id'],
                    'title': title,
                    'timestamp': row_dict['timestamp'],
                    'preview': row_dict['preview'][:100] + "..." if row_dict['preview'] and len(row_dict['preview']) > 100 else row_dict['preview']
                })
            
            return sessions
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            raise
        finally:
            conn.close()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete all messages in a session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'DELETE FROM conversations WHERE session_id = %s' if self.is_postgres else 
                'DELETE FROM conversations WHERE session_id = ?', 
                (session_id,)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise
        finally:
            conn.close()