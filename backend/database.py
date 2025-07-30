import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "chatbot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Knowledge base table
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
                
                # Conversation history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_base(tags)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # Knowledge Base Methods
    def add_knowledge(self, category: str, title: str, content: str, tags: Optional[List[str]] = None) -> int:
        """Add a new knowledge entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                tags_str = json.dumps(tags) if tags else None
                
                cursor.execute('''
                    INSERT INTO knowledge_base (category, title, content, tags)
                    VALUES (?, ?, ?, ?)
                ''', (category, title, content, tags_str))
                
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add knowledge: {e}")
            raise
    
    def get_knowledge_by_id(self, knowledge_id: int) -> Optional[Dict]:
        """Get knowledge entry by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM knowledge_base WHERE id = ?
                ''', (knowledge_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'category': row[1],
                        'title': row[2],
                        'content': row[3],
                        'tags': json.loads(row[4]) if row[4] else [],
                        'created_at': row[5],
                        'updated_at': row[6]
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get knowledge by ID: {e}")
            raise
    
    def search_knowledge(self, query: str = None, category: str = None, tags: List[str] = None) -> List[Dict]:
        """Search knowledge base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                sql = "SELECT * FROM knowledge_base WHERE 1=1"
                params = []
                
                if query:
                    sql += " AND (title LIKE ? OR content LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])
                
                if category:
                    sql += " AND category = ?"
                    params.append(category)
                
                if tags:
                    # Search for any of the provided tags
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{tag}%")
                    sql += f" AND ({' OR '.join(tag_conditions)})"
                
                sql += " ORDER BY updated_at DESC"
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'id': row[0],
                        'category': row[1],
                        'title': row[2],
                        'content': row[3],
                        'tags': json.loads(row[4]) if row[4] else [],
                        'created_at': row[5],
                        'updated_at': row[6]
                    })
                
                return results
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            raise
    
    def update_knowledge(self, knowledge_id: int, category: str = None, title: str = None, 
                        content: str = None, tags: List[str] = None) -> bool:
        """Update knowledge entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if category:
                    updates.append("category = ?")
                    params.append(category)
                
                if title:
                    updates.append("title = ?")
                    params.append(title)
                
                if content:
                    updates.append("content = ?")
                    params.append(content)
                
                if tags is not None:
                    updates.append("tags = ?")
                    params.append(json.dumps(tags))
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(knowledge_id)
                    
                    sql = f"UPDATE knowledge_base SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(sql, params)
                    conn.commit()
                    
                    return cursor.rowcount > 0
                
                return False
        except Exception as e:
            logger.error(f"Failed to update knowledge: {e}")
            raise
    
    def delete_knowledge(self, knowledge_id: int) -> bool:
        """Delete knowledge entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM knowledge_base WHERE id = ?', (knowledge_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete knowledge: {e}")
            raise
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT category FROM knowledge_base ORDER BY category')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            raise
    
    # Conversation History Methods
    def save_conversation(self, session_id: str, role: str, content: str) -> int:
        """Save a conversation message"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (session_id, role, content)
                    VALUES (?, ?, ?)
                ''', (session_id, role, content))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            raise
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT role, content, timestamp 
                    FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                ''', (session_id, limit))
                
                rows = cursor.fetchall()
                return [
                    {
                        'role': row[0],
                        'content': row[1],
                        'timestamp': row[2]
                    }
                    for row in reversed(rows)  # Reverse to get chronological order
                ]
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise
    
    def clear_conversation_history(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to clear conversation history: {e}")
            raise
    
    def get_relevant_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """Get relevant knowledge based on query similarity"""
        try:
            # Simple relevance scoring based on keyword matching
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Split query into keywords
                keywords = query.lower().split()
                
                # Build relevance score query
                relevance_parts = []
                params = []
                
                for keyword in keywords:
                    relevance_parts.append('''
                        (CASE WHEN LOWER(title) LIKE ? THEN 10 ELSE 0 END) +
                        (CASE WHEN LOWER(content) LIKE ? THEN 5 ELSE 0 END) +
                        (CASE WHEN LOWER(category) LIKE ? THEN 3 ELSE 0 END)
                    ''')
                    params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
                
                relevance_score = " + ".join(relevance_parts)
                
                # Double the params for the WHERE clause
                where_params = params[:]
                
                sql = f'''
                    SELECT *, ({relevance_score}) as relevance_score
                    FROM knowledge_base
                    WHERE ({relevance_score}) > 0
                    ORDER BY relevance_score DESC, updated_at DESC
                    LIMIT ?
                '''
                
                all_params = params + where_params + [limit]
                cursor.execute(sql, all_params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'id': row[0],
                        'category': row[1],
                        'title': row[2],
                        'content': row[3],
                        'tags': json.loads(row[4]) if row[4] else [],
                        'created_at': row[5],
                        'updated_at': row[6],
                        'relevance_score': row[7]
                    })
                
                return results
        except Exception as e:
            logger.error(f"Failed to get relevant knowledge: {e}")
            raise