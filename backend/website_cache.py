#!/usr/bin/env python3
"""
Website cache manager for session-based content caching
"""

import time
import logging
from typing import Dict, List, Optional
from threading import Lock
from website_scraper import scrape_everest_website

logger = logging.getLogger(__name__)

class WebsiteCache:
    def __init__(self, cache_duration: int = 14400):  # 4 hours default for better performance
        self.cache_duration = cache_duration
        self.global_cache = None
        self.global_cache_timestamp = 0
        self.lock = Lock()
    
    def _is_cache_expired(self, timestamp: float) -> bool:
        """Check if cache has expired"""
        return time.time() - timestamp > self.cache_duration
    
    def get_website_content_for_session(self, session_id: str) -> List[Dict]:
        """Get website content with global caching (no session-specific caching)"""
        with self.lock:
            current_time = time.time()
            
            # Check if we have fresh global cache
            if (self.global_cache is not None and 
                not self._is_cache_expired(self.global_cache_timestamp)):
                logger.debug(f"Using existing global cache (age: {current_time - self.global_cache_timestamp:.1f}s)")
                return self.global_cache
            
            # Need to scrape fresh content
            logger.info("Scraping fresh website content (global cache expired)")
            try:
                website_content = scrape_everest_website()
                
                # Update global cache
                self.global_cache = website_content
                self.global_cache_timestamp = current_time
                
                logger.info(f"Updated global cache with {len(website_content)} website pages")
                return website_content
                
            except Exception as e:
                logger.error(f"Failed to scrape website: {e}")
                # Return cached content even if expired, or empty list
                return self.global_cache if self.global_cache else []
    
    def invalidate_cache(self):
        """Invalidate global cache"""
        with self.lock:
            self.global_cache = None
            self.global_cache_timestamp = 0
            logger.info("Invalidated global cache")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            return {
                'global_cache_age': time.time() - self.global_cache_timestamp if self.global_cache else None,
                'global_cache_expired': self._is_cache_expired(self.global_cache_timestamp) if self.global_cache else True,
                'cache_duration': self.cache_duration
            }

# Global cache instance
website_cache = WebsiteCache()

def get_website_content(session_id: str) -> List[Dict]:
    """Get website content with caching"""
    return website_cache.get_website_content_for_session(session_id)

def invalidate_website_cache():
    """Invalidate website cache"""
    website_cache.invalidate_cache()