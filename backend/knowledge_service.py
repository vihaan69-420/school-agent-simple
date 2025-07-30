from typing import List, Dict, Optional
import logging
from database import DatabaseManager
from website_cache import get_website_content

logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_knowledge_entry(self, category: str, title: str, content: str, tags: Optional[List[str]] = None) -> int:
        """Add a new knowledge entry"""
        return self.db.add_knowledge(category, title, content, tags)
    
    def get_knowledge_by_id(self, knowledge_id: int) -> Optional[Dict]:
        """Get knowledge entry by ID"""
        return self.db.get_knowledge_by_id(knowledge_id)
    
    def search_knowledge(self, query: str = None, category: str = None, tags: List[str] = None) -> List[Dict]:
        """Search knowledge base"""
        return self.db.search_knowledge(query, category, tags)
    
    def update_knowledge_entry(self, knowledge_id: int, category: str = None, title: str = None, 
                             content: str = None, tags: List[str] = None) -> bool:
        """Update knowledge entry"""
        return self.db.update_knowledge(knowledge_id, category, title, content, tags)
    
    def delete_knowledge_entry(self, knowledge_id: int) -> bool:
        """Delete knowledge entry"""
        return self.db.delete_knowledge(knowledge_id)
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories"""
        return self.db.get_all_categories()
    
    def get_relevant_knowledge_for_query(self, query: str, limit: int = 3, session_id: str = None) -> List[Dict]:
        """Get relevant knowledge entries for a given query, including website content"""
        # Get knowledge from database (reduced limit)
        db_knowledge = self.db.get_relevant_knowledge(query, limit)
        
        # Get website content if session_id provided
        website_knowledge = []
        if session_id:
            try:
                website_content = get_website_content(session_id)
                # Simple text matching for website content
                website_knowledge = self._search_website_content(query, website_content, limit)
            except Exception as e:
                logger.error(f"Error getting website content: {e}")
        
        # Combine and return (prioritize database content, then website)
        combined = db_knowledge + website_knowledge
        return combined[:limit + 2]  # Return limited results for speed
    
    def _search_website_content(self, query: str, website_content: List[Dict], limit: int) -> List[Dict]:
        """Search website content for relevant information"""
        if not website_content or not query:
            return []
        
        query_words = query.lower().split()
        scored_content = []
        
        for content in website_content:
            score = 0
            content_text = (content.get('content', '') + ' ' + content.get('title', '')).lower()
            
            # Score based on query word matches
            for word in query_words:
                if word in content_text:
                    score += content_text.count(word)
            
            if score > 0:
                scored_content.append({
                    **content,
                    'relevance_score': score,
                    'source': 'website'
                })
        
        # Sort by relevance score and return top results
        scored_content.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_content[:limit]
    
    def format_knowledge_for_context(self, knowledge_entries: List[Dict]) -> str:
        """Format knowledge entries for use as context in chat"""
        if not knowledge_entries:
            return ""
        
        context_parts = ["=== KNOWLEDGE BASE CONTEXT ==="]
        
        for entry in knowledge_entries:
            source_info = ""
            if entry.get('source') == 'website':
                source_info = f" (Source: {entry.get('source_url', 'website')})"
            
            context_parts.append(f"\n[{entry['category']}] {entry['title']}{source_info}")
            context_parts.append(f"{entry['content']}")
            if entry.get('tags'):
                context_parts.append(f"Tags: {', '.join(entry['tags'])}")
            context_parts.append("---")
        
        context_parts.append("=== END KNOWLEDGE BASE CONTEXT ===\n")
        
        return "\n".join(context_parts)
    
    def bulk_add_knowledge(self, knowledge_entries: List[Dict]) -> List[int]:
        """Add multiple knowledge entries at once"""
        added_ids = []
        
        for entry in knowledge_entries:
            try:
                knowledge_id = self.add_knowledge_entry(
                    category=entry['category'],
                    title=entry['title'],
                    content=entry['content'],
                    tags=entry.get('tags', [])
                )
                added_ids.append(knowledge_id)
                logger.info(f"Added knowledge entry: {entry['title']}")
            except Exception as e:
                logger.error(f"Failed to add knowledge entry '{entry['title']}': {e}")
        
        return added_ids


class ConversationService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_message(self, session_id: str, role: str, content: str) -> int:
        """Save a conversation message"""
        return self.db.save_conversation(session_id, role, content)
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Get conversation history for a session"""
        return self.db.get_conversation_history(session_id, limit)
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        return self.db.clear_conversation_history(session_id)
    
    def format_conversation_for_context(self, conversation_history: List[Dict]) -> str:
        """Format conversation history for use as context"""
        if not conversation_history:
            return ""
        
        context_parts = ["=== CONVERSATION HISTORY ==="]
        
        for message in conversation_history:
            role = message['role'].upper()
            content = message['content']
            timestamp = message['timestamp']
            context_parts.append(f"[{timestamp}] {role}: {content}")
        
        context_parts.append("=== END CONVERSATION HISTORY ===\n")
        
        return "\n".join(context_parts)
    
    def get_recent_context(self, session_id: str, user_query: str, knowledge_service: KnowledgeService) -> str:
        """Get optimized context with no duplicate sources"""
        # Get minimal conversation history for speed
        conversation_history = self.get_conversation_history(session_id, limit=3)
        conversation_context = self.format_conversation_for_context(conversation_history)
        
        # Get relevant knowledge with reduced limit
        relevant_knowledge = knowledge_service.get_relevant_knowledge_for_query(user_query, limit=2, session_id=session_id)
        
        # Remove duplicate sources before formatting
        seen_urls = set()
        unique_knowledge = []
        for entry in relevant_knowledge:
            source_url = entry.get('source_url', '')
            if source_url and source_url in seen_urls:
                continue
            if source_url:
                seen_urls.add(source_url)
            unique_knowledge.append(entry)
        
        knowledge_context = knowledge_service.format_knowledge_for_context(unique_knowledge)
        
        # Combine contexts
        combined_context = ""
        if knowledge_context:
            combined_context += knowledge_context + "\n"
        if conversation_context:
            combined_context += conversation_context + "\n"
        
        return combined_context