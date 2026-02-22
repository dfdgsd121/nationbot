# src/oracle/pipeline.py
import asyncio
from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import OfficialSource, FeedItem
from .fetcher import RSSFetcher
from .sanitizer import ContentSanitizer
# from src.queue import enqueue_job  # Forward reference for Module 07

logger = logging.getLogger("oracle.pipeline")

class IngestionPipeline:
    """
    Coordinates the fetching, sanitizing, and storing of news items.
    Ties together the components of Module 01.
    """

    def __init__(self, db_engine=None):
        self.fetcher = RSSFetcher()
        self.sanitizer = ContentSanitizer()
        
        # In a real app, engine is passed or configured globally
        if db_engine:
            self.Session = sessionmaker(bind=db_engine)
        else:
            # Placeholder for testing without actual DB connection
            self.Session = None

    async def fetch_all_sources(self):
        """
        Main entry point for scheduled jobs.
        Fetches all active sources.
        """
        logger.info("Starting batch fetch of all official sources.")
        # Logic to fetch active sources from DB would go here
        # sources = session.query(OfficialSource).filter_by(is_active=True).all()
        # For now, we simulate with a hardcoded list for MVP structure
        
        mock_sources = [
            {"id": "uuid-1", "url": "https://www.whitehouse.gov/feed/", "country": "USA"},
            {"id": "uuid-2", "url": "https://www.gov.uk/government/feed.atom", "country": "GBR"}
        ]
        
        for source in mock_sources:
            await self.process_source(source)

    async def process_source(self, source_dict: dict):
        """
        Process a single source: Fetch -> Sanitize -> Dedup -> Store -> Trigger.
        """
        items = self.fetcher.fetch(source_dict['url'])
        
        new_items_count = 0
        for item in items:
            try:
                # 1. Sanitize
                clean_title = self.sanitizer.sanitize(item['title'])
                clean_summary = self.sanitizer.sanitize(item['summary'])
                
                if not clean_title:
                   logger.warning(f"Skipping item with invalid/safety-blocked title from {source_dict['url']}")
                   continue

                # 2. Store (Mock DB logic)
                # item_model = FeedItem(...)
                # session.add(item_model)
                # session.commit()
                
                # 3. Trigger Downstream (Mock Module 07)
                await self._trigger_reaction(clean_title, source_dict['country'])
                new_items_count += 1
                
            except Exception as e:
                logger.error(f"Error processing item: {e}")

        logger.info(f"Processed {source_dict['url']}: {new_items_count} new items.")

    async def _trigger_reaction(self, title: str, country: str):
        """
        Enqueues a job for the Agent Runtime (Module 04).
        """
        # This will eventually connect to Redis/Celery (Module 07)
        logger.info(f"⚡ TRIGGERING REACTION: {country} should react to '{title}'")
        # await enqueue_job('generate_reaction', {'title': title, 'nation': country})
