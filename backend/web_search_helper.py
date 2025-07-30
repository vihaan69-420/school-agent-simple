#!/usr/bin/env python3
"""
Web search helper for General Assistant to get current information
"""

import requests
import logging
from typing import List, Dict, Optional
from urllib.parse import quote
import json
import re

logger = logging.getLogger(__name__)

class WebSearchHelper:
    """Provides web search capability for current information"""
    
    def __init__(self):
        # We'll use DuckDuckGo's instant answer API (no API key needed)
        self.ddg_api = "https://api.duckduckgo.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_web(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search the web for current information"""
        try:
            # DuckDuckGo instant answer API
            params = {
                'q': query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(self.ddg_api, params=params, headers=self.headers, timeout=5)
            data = response.json()
            
            results = []
            
            # Extract instant answer if available
            if data.get('AbstractText'):
                results.append({
                    'type': 'instant_answer',
                    'title': data.get('Heading', 'Web Result'),
                    'content': data['AbstractText'],
                    'source': data.get('AbstractSource', 'Web'),
                    'url': data.get('AbstractURL', '')
                })
            
            # Extract answer if available (for calculations, facts, etc.)
            if data.get('Answer'):
                results.append({
                    'type': 'direct_answer',
                    'title': 'Direct Answer',
                    'content': data['Answer'],
                    'source': data.get('AnswerType', 'Calculation'),
                    'url': ''
                })
            
            # Extract definition if available
            if data.get('Definition'):
                results.append({
                    'type': 'definition',
                    'title': 'Definition',
                    'content': data['Definition'],
                    'source': data.get('DefinitionSource', 'Dictionary'),
                    'url': data.get('DefinitionURL', '')
                })
            
            # Extract related topics
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'type': 'related',
                        'title': topic.get('Text', '').split(' - ')[0][:50],
                        'content': topic.get('Text', ''),
                        'source': 'Related Topic',
                        'url': topic.get('FirstURL', '')
                    })
            
            # If no results, try a simpler search approach
            if not results:
                results.append({
                    'type': 'search_needed',
                    'title': 'Web Search Required',
                    'content': f"I couldn't find specific information about '{query}'. This may require a more detailed web search.",
                    'source': 'Search Status',
                    'url': ''
                })
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []
    
    def needs_web_search(self, query: str) -> bool:
        """Determine if a query needs web search for current information"""
        # Keywords that indicate need for current information
        current_indicators = [
            'today', 'current', 'latest', 'now', 'recent',
            'news', 'update', 'price', 'weather', 'score',
            'president', 'election', 'stock', 'covid',
            'ukraine', 'ai news', 'openai', 'anthropic',
            'this year', 'this month', 'this week',
            '2024', '2025', 'happening'
        ]
        
        query_lower = query.lower()
        
        # Check for date-specific queries
        if any(word in query_lower for word in ['when', 'what time', 'what date']):
            return False  # We handle dates internally
        
        # Check for current information needs
        return any(indicator in query_lower for indicator in current_indicators)
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for inclusion in response"""
        if not results:
            return ""
        
        formatted_parts = ["\n[Web Search Results]"]
        
        for result in results:
            if result['type'] == 'search_needed':
                continue
                
            formatted_parts.append(f"\n• {result['title']}")
            if result['content']:
                # Truncate long content
                content = result['content']
                if len(content) > 200:
                    content = content[:200] + "..."
                formatted_parts.append(f"  {content}")
            if result['source']:
                formatted_parts.append(f"  Source: {result['source']}")
        
        return "\n".join(formatted_parts)
    
    def extract_facts_for_query(self, query: str, search_results: List[Dict]) -> str:
        """Extract relevant facts from search results"""
        if not search_results:
            return ""
        
        facts = []
        for result in search_results:
            if result['type'] in ['instant_answer', 'direct_answer', 'definition']:
                facts.append(result['content'])
        
        if facts:
            return "\n".join(facts[:2])  # Limit to 2 facts
        
        return ""

# Global instance
web_search_helper = WebSearchHelper()

def enhance_response_with_web_search(query: str) -> Dict[str, any]:
    """Main function to enhance responses with web search"""
    if not web_search_helper.needs_web_search(query):
        return {
            'needs_search': False,
            'search_results': [],
            'facts': '',
            'formatted_results': ''
        }
    
    # Perform web search
    results = web_search_helper.search_web(query)
    
    return {
        'needs_search': True,
        'search_results': results,
        'facts': web_search_helper.extract_facts_for_query(query, results),
        'formatted_results': web_search_helper.format_search_results(results)
    }

if __name__ == "__main__":
    # Test the web search
    test_queries = [
        "current US president",
        "latest AI news",
        "weather in New York",
        "Python programming"
    ]
    
    for query in test_queries:
        print(f"\nTesting: {query}")
        result = enhance_response_with_web_search(query)
        print(f"Needs search: {result['needs_search']}")
        if result['needs_search']:
            print(f"Results: {result['formatted_results']}")