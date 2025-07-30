#!/usr/bin/env python3
"""
Helper for getting current, up-to-date information
"""

from datetime import datetime
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class CurrentInfoHelper:
    """Provides current, up-to-date information"""
    
    @staticmethod
    def get_current_context() -> Dict[str, str]:
        """Get current date and contextual information"""
        now = datetime.now()
        
        # Calculate current US president based on date
        current_president = "Joe Biden"
        president_since = "January 20, 2021"
        
        if now.year > 2025 or (now.year == 2025 and now.month > 1) or (now.year == 2025 and now.month == 1 and now.day >= 20):
            current_president = "Donald Trump"
            president_since = "January 20, 2025"
        elif now.year > 2029 or (now.year == 2029 and now.month > 1) or (now.year == 2029 and now.month == 1 and now.day >= 20):
            # This would need updating after 2028 election
            current_president = "Unknown (after 2028 election)"
            president_since = "January 20, 2029"
        
        return {
            "date": now.strftime("%B %d, %Y"),
            "day": now.strftime("%A"),
            "year": str(now.year),
            "month": now.strftime("%B"),
            "time": now.strftime("%I:%M %p"),
            "president": current_president,
            "president_since": president_since,
            "season": get_season(now),
            "quarter": f"Q{(now.month-1)//3 + 1} {now.year}"
        }
    
    @staticmethod
    def needs_current_info(query: str) -> bool:
        """Check if query needs current information"""
        current_info_keywords = [
            'today', 'current', 'now', 'present', 'latest',
            'date', 'time', 'president', 'year', 'month',
            'news', 'recent', 'update', 'happening',
            'what day', 'what time', 'what year'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in current_info_keywords)
    
    @staticmethod
    def get_web_search_context(query: str) -> Optional[str]:
        """Get current information via web search if available"""
        # This is a placeholder - in production you'd use a news API
        # or web search API to get truly current information
        try:
            # For now, return None to use our date-based context
            return None
        except Exception as e:
            logger.error(f"Failed to get web search context: {e}")
            return None

def get_season(date: datetime) -> str:
    """Get the current season based on date"""
    month = date.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall/Autumn"

# Global instance
current_info_helper = CurrentInfoHelper()