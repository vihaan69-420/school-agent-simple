#!/usr/bin/env python3
"""Test the web search functionality directly"""

import sys
sys.path.append('.')

from web_search import WebSearcher, enhance_with_web_search
import logging

logging.basicConfig(level=logging.INFO)

def test_web_search():
    searcher = WebSearcher()
    
    print("Testing Web Search Module")
    print("=" * 50)
    
    # Test 1: Weather query
    print("\n1. Testing weather search:")
    query = "What is the weather in New York?"
    if searcher.should_search_web(query):
        print(f"   Query needs web search: YES")
        weather_info = searcher.get_weather_info("New York")
        print(f"   Weather info:\n{weather_info}")
    else:
        print(f"   Query needs web search: NO")
    
    # Test 2: News query
    print("\n2. Testing news search:")
    query = "Latest news about technology"
    if searcher.should_search_web(query):
        print(f"   Query needs web search: YES")
        news = searcher.get_news_headlines("technology")
        print(f"   News headlines:\n{news[:500]}...")
    else:
        print(f"   Query needs web search: NO")
    
    # Test 3: General search
    print("\n3. Testing general search:")
    query = "Current stock price of Apple"
    if searcher.should_search_web(query):
        print(f"   Query needs web search: YES")
        results = searcher.search_for_current_info(query)
        print(f"   Search results:\n{results[:500]}...")
    else:
        print(f"   Query needs web search: NO")
    
    # Test 4: Enhance with web search
    print("\n4. Testing enhance_with_web_search:")
    query = "What is the weather today in San Francisco?"
    enhanced = enhance_with_web_search(query)
    print(f"   Needs search: {enhanced['needs_search']}")
    if enhanced['search_results']:
        print(f"   Results:\n{enhanced['search_results'][:500]}...")

if __name__ == "__main__":
    test_web_search()