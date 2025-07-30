#!/usr/bin/env python3
"""
Web search module for getting current information
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class WebSearcher:
    """Handles web search functionality for current information"""
    
    def __init__(self):
        # We'll use DuckDuckGo's instant answer API (no API key required)
        self.ddg_api_url = "https://api.duckduckgo.com/"
        
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search the web for current information
        Returns a list of search results
        """
        try:
            # Use DuckDuckGo instant answer API
            params = {
                'q': query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(self.ddg_api_url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Extract instant answer if available
            if data.get('Answer'):
                results.append({
                    'title': 'Direct Answer',
                    'snippet': data['Answer'],
                    'source': data.get('AnswerType', 'DuckDuckGo'),
                    'url': data.get('AbstractURL', '')
                })
            
            # Extract abstract if available
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Summary'),
                    'snippet': data['Abstract'],
                    'source': data.get('AbstractSource', 'Unknown'),
                    'url': data.get('AbstractURL', '')
                })
            
            # Extract related topics
            for topic in data.get('RelatedTopics', [])[:3]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic['Text'],
                        'source': 'DuckDuckGo',
                        'url': topic.get('FirstURL', '')
                    })
            
            # If no structured results, try a different approach
            if not results:
                # Use Google's Custom Search JSON API alternative
                results = self._search_with_serpapi_alternative(query, num_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _search_with_serpapi_alternative(self, query: str, num_results: int) -> List[Dict]:
        """
        Alternative search using a free search API
        """
        try:
            # Use a simple web scraping approach for search results
            # This is a fallback when DuckDuckGo doesn't provide good results
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            # Simple regex to extract search results
            results = []
            
            # Extract result snippets (simplified)
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', response.text, re.DOTALL)
            titles = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', response.text, re.DOTALL)
            
            for i, (title, snippet) in enumerate(zip(titles[:num_results], snippets[:num_results])):
                # Clean HTML tags
                title = re.sub(r'<[^>]+>', '', title).strip()
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                
                if title and snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'source': 'Web Search',
                        'url': ''
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Alternative search error: {e}")
            return []
    
    def search_for_current_info(self, query: str) -> str:
        """
        Search for current information and format it for the LLM
        """
        # Enhance query with current date/time context
        current_date = datetime.now().strftime("%B %d, %Y")
        enhanced_query = f"{query} {current_date}"
        
        # Perform search
        results = self.search(enhanced_query)
        
        if not results:
            return "No current information found for this query."
        
        # Format results for context
        formatted = f"Current Information (searched on {current_date}):\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            if result.get('url'):
                formatted += f"   Source: {result['url']}\n"
            formatted += "\n"
        
        return formatted
    
    def get_weather_info(self, location: str) -> str:
        """
        Get weather information for a specific location
        """
        # Use wttr.in API for weather (no API key required)
        try:
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                weather_info = f"Weather in {location}:\n"
                weather_info += f"- Temperature: {current['temp_C']}°C ({current['temp_F']}°F)\n"
                weather_info += f"- Feels like: {current['FeelsLikeC']}°C ({current['FeelsLikeF']}°F)\n"
                weather_info += f"- Condition: {current['weatherDesc'][0]['value']}\n"
                weather_info += f"- Humidity: {current['humidity']}%\n"
                weather_info += f"- Wind: {current['windspeedKmph']} km/h {current['winddir16Point']}\n"
                weather_info += f"- UV Index: {current['uvIndex']}\n"
                
                return weather_info
            else:
                return f"Could not fetch weather data for {location}"
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return f"Error fetching weather information: {str(e)}"
    
    def get_news_headlines(self, topic: str = "latest") -> str:
        """
        Get current news headlines
        """
        try:
            # Search for news
            news_query = f"{topic} news today {datetime.now().strftime('%B %Y')}"
            results = self.search(news_query, num_results=5)
            
            if not results:
                return "No current news found."
            
            formatted = f"Latest News ({datetime.now().strftime('%B %d, %Y')}):\n\n"
            for i, result in enumerate(results, 1):
                formatted += f"{i}. {result['title']}\n"
                formatted += f"   {result['snippet'][:200]}...\n\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"News search error: {e}")
            return "Error fetching news headlines."
    
    def should_search_web(self, query: str) -> bool:
        """
        Determine if a query needs web search
        """
        # Keywords that indicate need for current information
        current_info_keywords = [
            'today', 'current', 'latest', 'now', 'weather', 'news',
            'price', 'stock', 'score', 'result', 'update', 'recent',
            'happening', 'temperature', 'forecast', 'trending',
            'live', 'real-time', 'at the moment', 'right now'
        ]
        
        # Check if query contains time-sensitive keywords
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in current_info_keywords)


# Global instance
web_searcher = WebSearcher()


def enhance_with_web_search(query: str) -> dict:
    """
    Enhance a query with web search results if needed
    """
    result = {
        'needs_search': False,
        'search_results': '',
        'enhanced_context': ''
    }
    
    # Check if web search is needed
    if web_searcher.should_search_web(query):
        result['needs_search'] = True
        
        # Check for specific information types
        query_lower = query.lower()
        
        if 'weather' in query_lower:
            # Extract location - more flexible patterns
            location_patterns = [
                r'weather\s+(?:today\s+)?(?:in|for|at|of)\s+([^?.,]+)',
                r'(?:in|at)\s+([^?.,]+?)\s*(?:weather|temperature)',
                r'([^?.,]+?)\s+weather',
                r'weather.*?(?:in|at|for)\s+([^?.,]+)'
            ]
            
            location = None
            for pattern in location_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    location = match.group(1).strip()
                    # Clean up common words
                    location = location.replace('the ', '').replace('today', '').strip()
                    if location and len(location) > 2:
                        break
            
            if location:
                result['search_results'] = web_searcher.get_weather_info(location)
            else:
                # Try to extract any proper noun as location
                proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
                if proper_nouns:
                    location = proper_nouns[0]
                    result['search_results'] = web_searcher.get_weather_info(location)
                else:
                    result['search_results'] = "Please specify a location for weather information."
        
        elif 'news' in query_lower:
            # Extract topic if specified
            topic_match = re.search(r'news\s+(?:about|on|regarding)\s+([^?.,]+)', query_lower)
            topic = topic_match.group(1).strip() if topic_match else "latest"
            result['search_results'] = web_searcher.get_news_headlines(topic)
        
        else:
            # General web search
            result['search_results'] = web_searcher.search_for_current_info(query)
        
        # Create enhanced context
        if result['search_results']:
            result['enhanced_context'] = f"""Web Search Results:
{result['search_results']}

Based on the above current information, here's my response:"""
    
    return result


if __name__ == "__main__":
    # Test the web search functionality
    logging.basicConfig(level=logging.INFO)
    
    test_queries = [
        "What is the weather today in San Francisco?",
        "Latest news about AI",
        "Current stock price of Apple",
        "Who won the game last night?"
    ]
    
    searcher = WebSearcher()
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        if searcher.should_search_web(query):
            print("Web search needed!")
            results = enhance_with_web_search(query)
            print(results['search_results'])
        else:
            print("No web search needed.")