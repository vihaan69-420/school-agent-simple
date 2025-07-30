#!/usr/bin/env python3
"""
General web assistant that can scrape and provide information from any website
"""

import re
from urllib.parse import urlparse
from dynamic_scraper import DynamicWebScraper, scraping_cache
import logging

logger = logging.getLogger(__name__)

def extract_url_from_query(query: str) -> tuple[str, str]:
    """Extract URL from query and return (url, cleaned_query)"""
    # Common URL patterns
    url_pattern = r'https?://[^\s]+'
    
    urls = re.findall(url_pattern, query)
    if urls:
        url = urls[0]
        # Remove URL from query to get the actual question
        cleaned_query = re.sub(url_pattern, '', query).strip()
        return url, cleaned_query
    
    # Check for domain mentions without protocol
    domain_pattern = r'(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)'
    domains = re.findall(domain_pattern, query)
    
    if domains:
        domain = domains[0]
        # Try with https
        url = f"https://{domain}"
        cleaned_query = query.replace(domain, '').strip()
        return url, cleaned_query
    
    return None, query

def get_base_url(url: str) -> str:
    """Extract base URL from a full URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def analyze_query_intent(query: str) -> dict:
    """Analyze what the user is looking for"""
    intent = {
        'needs_instructions': False,
        'needs_urls': False,
        'needs_form_help': False,
        'needs_navigation': False,
        'specific_info': []
    }
    
    # Instruction indicators
    instruction_keywords = ['how to', 'steps', 'process', 'guide', 'tutorial', 
                          'procedure', 'instructions', 'apply', 'fill', 'submit']
    intent['needs_instructions'] = any(kw in query.lower() for kw in instruction_keywords)
    
    # URL/navigation indicators
    url_keywords = ['url', 'link', 'page', 'where', 'find', 'locate', 'navigate', 'access']
    intent['needs_urls'] = any(kw in query.lower() for kw in url_keywords)
    
    # Form-related
    form_keywords = ['form', 'application', 'registration', 'submit', 'fill out', 'apply']
    intent['needs_form_help'] = any(kw in query.lower() for kw in form_keywords)
    
    # Navigation help
    nav_keywords = ['navigate', 'find', 'where is', 'location of', 'how to get to']
    intent['needs_navigation'] = any(kw in query.lower() for kw in nav_keywords)
    
    # Extract specific topics
    topic_patterns = [
        r'about\s+(\w+)',
        r'information\s+on\s+(\w+)',
        r'details\s+(?:on|about)\s+(\w+)',
        r'(\w+)\s+(?:process|procedure|form|application)'
    ]
    
    for pattern in topic_patterns:
        matches = re.findall(pattern, query.lower())
        intent['specific_info'].extend(matches)
    
    return intent

def get_context_for_any_website(query: str) -> tuple[str, str]:
    """Get context for any website mentioned in the query"""
    # Extract URL from query
    url, cleaned_query = extract_url_from_query(query)
    
    if not url:
        return "", query
    
    # Get base URL
    base_url = get_base_url(url)
    
    # Analyze what user needs
    intent = analyze_query_intent(cleaned_query)
    
    # Create enhanced query for scraping
    scraping_query = cleaned_query
    if intent['needs_instructions']:
        scraping_query += " instructions steps process"
    if intent['needs_urls']:
        scraping_query += " links pages navigation"
    if intent['needs_form_help']:
        scraping_query += " form application submit"
    
    # Check cache
    cache_key = f"{base_url}:{scraping_query}"
    cached_data = scraping_cache.get(cache_key)
    
    if cached_data:
        logger.info(f"Using cached data for {base_url}")
        scraper = DynamicWebScraper(base_url)
        formatted = scraper.format_for_context(cached_data, scraping_query)
    else:
        # Scrape the website
        try:
            logger.info(f"Scraping {base_url} for: {scraping_query}")
            scraper = DynamicWebScraper(base_url)
            
            # If specific URL provided, start with that
            if url != base_url:
                # Scrape the specific page first
                specific_data = scraper.scrape_url_with_context(url, scraping_query)
                if specific_data:
                    scraped_data = [specific_data]
                    # Then find related pages
                    related = scraper.scrape_for_query(scraping_query, max_pages=3)
                    scraped_data.extend(related)
                else:
                    scraped_data = scraper.scrape_for_query(scraping_query, max_pages=5)
            else:
                scraped_data = scraper.scrape_for_query(scraping_query, max_pages=5)
            
            # Cache results
            scraping_cache.set(cache_key, scraped_data)
            
            formatted = scraper.format_for_context(scraped_data, scraping_query)
            
        except Exception as e:
            logger.error(f"Failed to scrape {base_url}: {e}")
            formatted = f"Unable to retrieve content from {base_url}. Error: {str(e)}"
    
    # Add intent-specific guidance
    guidance = f"\n\nUser Query Analysis:\n"
    guidance += f"- Website: {base_url}\n"
    guidance += f"- Question: {cleaned_query}\n"
    
    if intent['needs_instructions']:
        guidance += "- User needs step-by-step instructions\n"
    if intent['needs_urls']:
        guidance += "- User needs specific URLs/links\n"
    if intent['needs_form_help']:
        guidance += "- User needs help with forms/applications\n"
    if intent['specific_info']:
        guidance += f"- Specific topics: {', '.join(intent['specific_info'])}\n"
    
    return formatted + guidance, cleaned_query

def enhance_query_with_website_context(original_query: str) -> dict:
    """Enhance a query with website context if URL is mentioned"""
    context, cleaned_query = get_context_for_any_website(original_query)
    
    return {
        'original_query': original_query,
        'cleaned_query': cleaned_query,
        'has_website_context': bool(context),
        'website_context': context,
        'enhanced_prompt': f"{context}\n\nUser Question: {cleaned_query}" if context else original_query
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test queries
    test_queries = [
        "how to apply for admission at https://everestmanila.com",
        "tell me about the application process on everestmanila.com",
        "where can I find the tuition fees on https://www.example-school.com",
        "how to fill out the registration form at example.edu"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = enhance_query_with_website_context(query)
        print(f"Has context: {result['has_website_context']}")
        print(f"Cleaned query: {result['cleaned_query']}")
        if result['has_website_context']:
            print(f"Context preview: {result['website_context'][:200]}...")