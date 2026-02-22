# src/analytics/gamification.py
import logging
from typing import List, Optional
from redis import asyncio as aioredis
from src.realtime.broadcaster import RealtimeBroadcaster
import os

logger = logging.getLogger("gamification")

class GamificationEngine:
    """
    Manages global engagement counters and nation unlocks.
    """
    
    # Tier Definitions: Threshold -> [Unlocked Nation IDs]
    UNLOCK_TIERS = {
        10000: ["VA", "MC"],   # Tier 1: Vatican, Monaco
        50000: ["TX", "CA"],   # Tier 2: Texas, Catalonia
        100000: ["ROM"],       # Tier 3: Roman Empire
        1000000: ["ALIEN"]     # Tier 4: Aliens
    }
    
    COUNTER_KEY = "sim_total_interactions"

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = None
        self.broadcaster = RealtimeBroadcaster()

    async def get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self.redis

    async def increment_global_counter(self) -> int:
        """
        Atomically increments the global interaction counter.
        Returns the new value.
        """
        try:
            redis = await self.get_redis()
            # INCR is atomic
            new_count = await redis.incr(self.COUNTER_KEY)
            
            # Async check for unlocks (fire and forget logic could be applied here, 
            # but for safety we await to ensure event fires)
            await self.check_unlocks(new_count)
            
            return new_count
        except Exception as e:
            logger.error(f"Failed to increment gamification counter: {e}")
            return 0

    async def check_unlocks(self, count: int):
        """
        Checks if the current count hits a tier threshold.
        """
        if count in self.UNLOCK_TIERS:
            unlocked_nations = self.UNLOCK_TIERS[count]
            await self.trigger_unlock_event(count, unlocked_nations)

    async def trigger_unlock_event(self, count: int, nation_ids: List[str]):
        """
        Broadcasts the unlock event to the War Room.
        """
        logger.info(f"🔓 UNLOCK TRIGGERED at {count}! Nations: {nation_ids}")
        
        event_payload = {
            "type": "SYSTEM_EVENT",
            "event_type": "NATION_UNLOCK",
            "milestone": count,
            "unlocked_nations": nation_ids,
            "message": f"Global Milestone Reached! {len(nation_ids)} new challengers approaching..."
        }
        
        # Use existing broadcaster to notify all connected clients
        await self.broadcaster.broadcast_event(event_payload)
