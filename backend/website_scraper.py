#!/usr/bin/env python3
"""
Website scraper for Everest Academy Manila
Scrapes content from everestmanila.com and structures it for the knowledge base
"""

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import time
import re

logger = logging.getLogger(__name__)

class EverestWebsiteScraper:
    def __init__(self, base_url: str = "https://everestmanila.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.scraped_data = []
        self.visited_urls = set()
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to everestmanila.com domain"""
        parsed = urlparse(url)
        return parsed.netloc in ['everestmanila.com', 'www.everestmanila.com']
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters that might break formatting
        text = re.sub(r'[^\w\s\-.,;:!?()\[\]{}@#$%&*+=<>/\\|`~\'"₱]', ' ', text)
        return text.strip()
    
    def extract_page_content(self, url: str) -> Dict:
        """Extract content from a single page"""
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            page_title = self.clean_text(title.get_text()) if title else url.split('/')[-1]
            
            # Extract main content
            content_areas = []
            
            # Look for main content containers
            main_selectors = [
                'main', '[role="main"]', '.main-content', '.content',
                '.page-content', '.entry-content', 'article'
            ]
            
            main_content = None
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            if main_content:
                # Extract headings and paragraphs
                for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li']):
                    text = self.clean_text(element.get_text())
                    if text and len(text) > 10:  # Only meaningful content
                        content_areas.append(text)
            
            # Extract meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            description = ""
            if meta_desc:
                description = self.clean_text(meta_desc.get('content', ''))
            
            # Combine all content
            full_content = ' '.join(content_areas)
            
            # Extract links for further crawling
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                        links.append(full_url)
            
            return {
                'url': url,
                'title': page_title,
                'description': description,
                'content': full_content,
                'links': links,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def scrape_website(self, max_pages: int = 8) -> List[Dict]:
        """Scrape the entire website up to max_pages"""
        # Start with verified working URLs
        urls_to_visit = [
            self.base_url,
            "https://everestmanila.com/about/contact",
            "https://everestmanila.com/about/welcome",
            "https://everestmanila.com/who-we-are"
        ]
        self.visited_urls = set()
        self.scraped_data = []
        
        while urls_to_visit and len(self.scraped_data) < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
                
            self.visited_urls.add(url)
            
            page_data = self.extract_page_content(url)
            if page_data and page_data['content']:
                self.scraped_data.append(page_data)
                
                # Add new links to visit (prioritize key pages)
                priority_keywords = ['admission', 'academic', 'tuition', 'fee', 'contact', 'about']
                priority_links = []
                regular_links = []
                
                for link in page_data['links'][:3]:  # Reduce links per page
                    if link not in self.visited_urls and link not in urls_to_visit:
                        if any(keyword in link.lower() for keyword in priority_keywords):
                            priority_links.append(link)
                        else:
                            regular_links.append(link)
                
                # Add priority links first
                for link in priority_links[:2]:
                    urls_to_visit.append(link)
                for link in regular_links[:1]:
                    urls_to_visit.append(link)
            
            # Be respectful - minimal delay for speed
            time.sleep(0.1)
        
        logger.info(f"Scraped {len(self.scraped_data)} pages from {self.base_url}")
        return self.scraped_data
    
    def format_for_knowledge_base(self) -> List[Dict]:
        """Format scraped data for knowledge base integration"""
        formatted_data = []
        
        for page in self.scraped_data:
            # Determine category based on URL and title
            url_path = urlparse(page['url']).path.lower()
            title = page['title'].lower()
            
            category = "Website Content"
            if any(term in url_path or term in title for term in ['admission', 'apply', 'enroll']):
                category = "Admissions"
            elif any(term in url_path or term in title for term in ['academic', 'curriculum', 'program']):
                category = "Academics"
            elif any(term in url_path or term in title for term in ['about', 'overview', 'mission']):
                category = "About"
            elif any(term in url_path or term in title for term in ['contact', 'location', 'address']):
                category = "Contact"
            elif any(term in url_path or term in title for term in ['news', 'event', 'announcement']):
                category = "News & Events"
            elif any(term in url_path or term in title for term in ['tuition', 'fee', 'cost', 'payment']):
                category = "Fees & Tuition"
            
            formatted_entry = {
                'category': category,
                'title': f"{page['title']} (Website)",
                'content': f"{page['description']}\n\n{page['content']}" if page['description'] else page['content'],
                'tags': ['website', 'live_content', url_path.split('/')[-1] if url_path else 'home'],
                'source_url': page['url'],
                'scraped_at': page['scraped_at']
            }
            
            formatted_data.append(formatted_entry)
        
        return formatted_data

def scrape_everest_website() -> List[Dict]:
    """Main function to scrape Everest Academy website"""
    scraper = EverestWebsiteScraper()
    scraper.scrape_website(max_pages=8)  # Limit to 8 pages for speed
    return scraper.format_for_knowledge_base()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = scrape_everest_website()
    print(f"Scraped {len(data)} pages")
    for item in data[:3]:  # Show first 3 items
        print(f"- {item['title']}: {len(item['content'])} chars")