# src/oracle/velocity_monitor.py
import asyncio
import feedparser
import logging
from typing import Callable, List

# Configure logger
logger = logging.getLogger("oracle.velocity")
logging.basicConfig(level=logging.INFO)

class VelocityMonitor:
    """
    Watches for global panic signals to trigger emergency fetch overrides.
    Implements the 'Velocity Trigger' aimed at closing the 15-minute latency gap.
    """
    
    # Free, real-time signal from Google Trends (Daily Trends RSS)
    TRENDS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    
    # Keywords that trigger immediate "Panic Mode"
    # These represent events where 15 minutes of silence is unacceptable.
    FIRE_KEYWORDS = [
        "war declared", "nuclear", "assassination", "president resigns", 
        "earthquake", "invasion", "tariff", "martial law", "cyberattack",
        "market crash", "outbreak", "terrorist"
    ]
    
    def __init__(self, trigger_callback: Callable[[str], None]):
        """
        :param trigger_callback: Async function to call when panic is detected.
        """
        self.trigger_callback = trigger_callback
        self.last_triggered_keywords = set()
        self.is_running = False

    async def watch(self, interval_seconds: int = 60):
        """Poll trends loop."""
        self.is_running = True
        logger.info(f"🔥 VelocityMonitor started. Polling every {interval_seconds}s.")
        
        while self.is_running:
            try:
                await self._check_trends()
            except Exception as e:
                logger.error(f"Error extracting patterns from trends: {e}")
            
            await asyncio.sleep(interval_seconds)

    async def _check_trends(self):
        # feedparser is blocking, so strictly we might want to run in executor
        # but for MVP local loop, direct call is acceptable or use async wrapper
        feed = feedparser.parse(self.TRENDS_URL)
        
        if not feed.entries:
            logger.warning("No entries found in Trends RSS.")
            return

        for entry in feed.entries:
            title = entry.title.lower()
            if self._is_panic_worthy(title):
                if title not in self.last_triggered_keywords:
                    logger.critical(f"🚨 VELOCITY SPIKE DETECTED: '{title}'")
                    self.last_triggered_keywords.add(title)
                    
                    # Trigger the emergency callback
                    if asyncio.iscoroutinefunction(self.trigger_callback):
                        await self.trigger_callback(title)
                    else:
                        self.trigger_callback(title)
                    
                    # Clear cache slightly to allow re-triggering later or use TTL
                    # For now, just break to avoid spamming for the same poll cycle
                    break

    def _is_panic_worthy(self, text: str) -> bool:
        return any(kw in text for kw in self.FIRE_KEYWORDS)

    def stop(self):
        self.is_running = False
