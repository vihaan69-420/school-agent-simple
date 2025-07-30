#!/usr/bin/env python3
"""
Dynamic website scraper that fetches real-time content for any query
"""

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

logger = logging.getLogger(__name__)

class DynamicWebScraper:
    def __init__(self, base_url: str = "https://everestmanila.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\-.,;:!?()\[\]{}@#$%&*+=<>/\\|`~\'"₱]', ' ', text)
        return text.strip()
    
    def extract_structured_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract structured content including headings, lists, and links"""
        content_structure = {
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'links': [],
            'forms': [],
            'steps': []
        }
        
        # Extract headings with hierarchy
        for i, tag in enumerate(['h1', 'h2', 'h3', 'h4']):
            for heading in soup.find_all(tag):
                text = self.clean_text(heading.get_text())
                if text:
                    content_structure['headings'].append({
                        'level': int(tag[1]),
                        'text': text,
                        'order': i
                    })
        
        # Extract paragraphs
        for p in soup.find_all('p'):
            text = self.clean_text(p.get_text())
            if text and len(text) > 20:
                content_structure['paragraphs'].append(text)
        
        # Extract lists (often contain steps or requirements)
        for list_tag in soup.find_all(['ul', 'ol']):
            list_items = []
            for li in list_tag.find_all('li'):
                text = self.clean_text(li.get_text())
                if text:
                    list_items.append(text)
            if list_items:
                content_structure['lists'].append({
                    'type': 'ordered' if list_tag.name == 'ol' else 'unordered',
                    'items': list_items
                })
        
        # Extract links with context
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = self.clean_text(link.get_text())
            if href and text:
                full_url = urljoin(url, href)
                if self._is_valid_url(full_url):
                    content_structure['links'].append({
                        'url': full_url,
                        'text': text,
                        'context': self._get_link_context(link)
                    })
        
        # Extract forms (for application processes)
        for form in soup.find_all('form'):
            form_info = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': []
            }
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                if input_tag.get('name'):
                    form_info['inputs'].append({
                        'name': input_tag.get('name'),
                        'type': input_tag.get('type', 'text'),
                        'required': input_tag.get('required') is not None
                    })
            if form_info['inputs']:
                content_structure['forms'].append(form_info)
        
        # Try to identify step-by-step instructions
        content_structure['steps'] = self._extract_steps(soup)
        
        return content_structure
    
    def _extract_steps(self, soup: BeautifulSoup) -> List[str]:
        """Extract step-by-step instructions from content"""
        steps = []
        
        # Look for numbered lists or step indicators
        step_patterns = [
            r'(?i)step\s*\d+',
            r'^\d+\.',
            r'(?i)first|second|third|then|next|finally'
        ]
        
        for element in soup.find_all(['li', 'p', 'div']):
            text = self.clean_text(element.get_text())
            if any(re.search(pattern, text) for pattern in step_patterns):
                steps.append(text)
        
        return steps
    
    def _get_link_context(self, link_element) -> str:
        """Get surrounding context for a link"""
        parent = link_element.parent
        if parent:
            context = self.clean_text(parent.get_text())
            return context[:200] if len(context) > 200 else context
        return ""
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and from the same domain"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(self.base_url)
            return parsed.netloc == base_parsed.netloc or parsed.netloc == f"www.{base_parsed.netloc}"
        except:
            return False
    
    def scrape_url_with_context(self, url: str, query: str = "") -> Optional[Dict]:
        """Scrape a specific URL and extract relevant content based on query"""
        try:
            logger.info(f"Scraping {url} for query: {query}")
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove non-content elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # Extract title and meta
            title = soup.find('title')
            page_title = self.clean_text(title.get_text()) if title else ""
            
            meta_desc = soup.find('meta', {'name': 'description'})
            description = self.clean_text(meta_desc.get('content', '')) if meta_desc else ""
            
            # Extract structured content
            structured_content = self.extract_structured_content(soup, url)
            
            # Build comprehensive content
            result = {
                'url': url,
                'title': page_title,
                'description': description,
                'structured_content': structured_content,
                'full_text': self._build_full_text(structured_content),
                'relevance_score': self._calculate_relevance(structured_content, query),
                'scraped_at': time.time()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _build_full_text(self, structured_content: Dict) -> str:
        """Build full text from structured content"""
        parts = []
        
        # Add headings
        for heading in sorted(structured_content['headings'], key=lambda x: (x['order'], x['level'])):
            parts.append(heading['text'])
        
        # Add paragraphs
        parts.extend(structured_content['paragraphs'])
        
        # Add lists
        for lst in structured_content['lists']:
            if lst['type'] == 'ordered':
                for i, item in enumerate(lst['items'], 1):
                    parts.append(f"{i}. {item}")
            else:
                for item in lst['items']:
                    parts.append(f"• {item}")
        
        # Add steps if found
        if structured_content['steps']:
            parts.append("\nSteps found:")
            parts.extend(structured_content['steps'])
        
        return "\n".join(parts)
    
    def _calculate_relevance(self, content: Dict, query: str) -> float:
        """Calculate relevance score based on query"""
        if not query:
            return 1.0
        
        query_words = query.lower().split()
        score = 0.0
        
        # Check different content areas with weights
        weights = {
            'title': 5.0,
            'headings': 3.0,
            'steps': 4.0,
            'paragraphs': 1.0,
            'lists': 2.0
        }
        
        full_text = self._build_full_text(content).lower()
        
        for word in query_words:
            if word in full_text:
                score += full_text.count(word)
        
        return score
    
    def find_relevant_urls(self, query: str, max_depth: int = 2) -> List[str]:
        """Find relevant URLs by crawling the website"""
        relevant_urls = []
        visited = set()
        to_visit = [(self.base_url, 0)]
        
        # Keywords to prioritize
        query_words = query.lower().split()
        
        while to_visit and len(relevant_urls) < 10:
            url, depth = to_visit.pop(0)
            
            if url in visited or depth > max_depth:
                continue
            
            visited.add(url)
            
            try:
                response = self.session.get(url, timeout=3)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check if current page is relevant
                page_text = soup.get_text().lower()
                if any(word in page_text for word in query_words):
                    relevant_urls.append(url)
                
                # Find more URLs to visit
                if depth < max_depth:
                    for link in soup.find_all('a', href=True):
                        href = urljoin(url, link['href'])
                        link_text = self.clean_text(link.get_text()).lower()
                        
                        if self._is_valid_url(href) and href not in visited:
                            # Prioritize links with query words
                            if any(word in link_text or word in href.lower() for word in query_words):
                                to_visit.insert(0, (href, depth + 1))
                            else:
                                to_visit.append((href, depth + 1))
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
            
            time.sleep(0.1)  # Be respectful
        
        return relevant_urls
    
    def scrape_for_query(self, query: str, max_pages: int = 5) -> List[Dict]:
        """Main method to scrape relevant content for a query"""
        logger.info(f"Starting dynamic scraping for query: {query}")
        
        # Find relevant URLs
        relevant_urls = self.find_relevant_urls(query, max_depth=2)
        logger.info(f"Found {len(relevant_urls)} relevant URLs")
        
        # Scrape URLs concurrently for speed
        scraped_data = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {
                executor.submit(self.scrape_url_with_context, url, query): url 
                for url in relevant_urls[:max_pages]
            }
            
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    scraped_data.append(result)
        
        # Sort by relevance
        scraped_data.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scraped_data
    
    def format_for_context(self, scraped_data: List[Dict], query: str) -> str:
        """Format scraped data for LLM context with deduplication"""
        if not scraped_data:
            return ""
        
        # Track seen URLs to avoid duplicates
        seen_urls = set()
        
        context_parts = ["=== LIVE WEBSITE CONTENT ==="]
        context_parts.append(f"Query: {query}")
        context_parts.append(f"Found {len(scraped_data)} relevant pages:\n")
        
        for data in scraped_data:
            # Skip if we've already seen this URL
            if data['url'] in seen_urls:
                continue
            seen_urls.add(data['url'])
            
            context_parts.append(f"\n[Page: {data['title']}]")
            context_parts.append(f"(Source: {data['url']})")
            
            if data['description']:
                context_parts.append(f"Description: {data['description']}")
            
            # Add structured content
            structured = data['structured_content']
            
            # Add steps if found
            if structured['steps'] and len(structured['steps']) > 0:
                context_parts.append("\nStep-by-step instructions:")
                for i, step in enumerate(structured['steps'][:5], 1):  # Limit to 5 steps
                    context_parts.append(f"{i}. {step}")
            
            # Add only the most relevant list
            for lst in structured['lists'][:2]:  # Max 2 lists
                if any(word in str(lst).lower() for word in query.lower().split()):
                    context_parts.append(f"\n{lst['type'].title()} list:")
                    for item in lst['items'][:3]:  # Max 3 items
                        context_parts.append(f"- {item}")
                    break
            
            # Add relevant links (deduplicated)
            link_urls_seen = set()
            relevant_links = []
            for link in structured['links']:
                if link['url'] not in link_urls_seen and link['url'] not in seen_urls:
                    if any(word in link['text'].lower() or word in link['url'].lower() 
                          for word in query.lower().split()):
                        relevant_links.append(link)
                        link_urls_seen.add(link['url'])
            
            if relevant_links:
                context_parts.append("\nRelated pages:")
                for link in relevant_links[:3]:  # Max 3 links
                    context_parts.append(f"- {link['text']}: {link['url']}")
                    seen_urls.add(link['url'])
            
            # Add brief content snippet
            content_snippet = data['full_text'][:300]  # Reduced from 500
            if content_snippet:
                context_parts.append(f"\nBrief excerpt: {content_snippet}...")
            
            context_parts.append("\n---")
        
        context_parts.append("\n=== END LIVE WEBSITE CONTENT ===")
        return "\n".join(context_parts)


# Cache to avoid repeated scraping
class ScrapingCache:
    def __init__(self, ttl: int = 900):  # 15 minutes TTL
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[List[Dict]]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: List[Dict]):
        self.cache[key] = (data, time.time())
    
    def clear_old(self):
        current_time = time.time()
        to_delete = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.ttl
        ]
        for key in to_delete:
            del self.cache[key]


# Global cache instance
scraping_cache = ScrapingCache()


def get_dynamic_content_for_query(query: str, base_url: str = "https://everestmanila.com") -> str:
    """Optimized function to get dynamic content for a query"""
    # Check cache first
    cache_key = f"{base_url}:{query}"
    cached_data = scraping_cache.get(cache_key)
    
    if cached_data:
        logger.info(f"Using cached data for query: {query}")
        scraper = DynamicWebScraper(base_url)
        return scraper.format_for_context(cached_data, query)
    
    # Scrape fresh data with reduced pages for speed
    scraper = DynamicWebScraper(base_url)
    scraped_data = scraper.scrape_for_query(query, max_pages=3)  # Reduced from 5
    
    # Cache the results
    scraping_cache.set(cache_key, scraped_data)
    
    # Clear old cache entries
    scraping_cache.clear_old()
    
    return scraper.format_for_context(scraped_data, query)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the dynamic scraper
    test_query = "admission application process"
    content = get_dynamic_content_for_query(test_query)
    print(content)