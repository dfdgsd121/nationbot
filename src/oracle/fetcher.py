# src/oracle/fetcher.py
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger("oracle.fetcher")

class RSSFetcher:
    """
    Fetches and parses RSS feeds from official sources.
    Part of Module 01: News Ingestion.
    """
    
    def fetch(self, url: str) -> List[Dict]:
        """
        Fetch items from a single RSS feed URL.
        
        :param url: The RSS feed URL (e.g., whitehouse.gov/feed)
        :return: List of dicts with standardized keys
        """
        try:
            feed = feedparser.parse(url)
            
            if feed.bozo:
                logger.warning(f"Feed {url} parsing error: {feed.bozo_exception}")
                # We often continue as feedparser tries to salvage content
            
            items = []
            for entry in feed.entries:
                # Normalize timestamp
                published_at = None
                if hasattr(entry, 'published_parsed'):
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass
                
                # Basic cleaning
                title = entry.get('title', 'No Title').strip()
                link = entry.get('link', '').strip()
                summary = entry.get('summary', '').strip()
                
                if link:
                    items.append({
                        'title': title,
                        'url': link,
                        'published_at': published_at,
                        'summary': summary
                    })
            
            logger.info(f"Fetched {len(items)} items from {url}")
            return items
            
        except Exception as e:
            logger.error(f"Critical error fetching {url}: {e}")
            return []
