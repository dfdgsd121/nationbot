# src/realtime/broadcaster.py
import os
import json
import logging
import redis.asyncio as redis

logger = logging.getLogger("realtime")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RealtimeBroadcaster:
    """
    The Voice of the War Room.
    Publishes events to Redis for SSE consumers.
    """
    
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

    async def broadcast_event(self, event_type: str, payload: dict):
        """
        Generic broadcast.
        """
        message = json.dumps({
            "event": event_type,
            "data": payload
        })
        try:
            await self.redis.publish("global_events", message)
            logger.debug(f"Broadcasted: {event_type}")
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")

    async def broadcast_typing(self, nation_id: str, target_id: str):
        """
        The War Room Feature: 'Russia is typing...'
        """
        await self.broadcast_event("typing_indicator", {
            "nation_id": nation_id,
            "target_id": target_id,
            "message": f"{nation_id} is drafting a response to {target_id}..."
        })

    async def broadcast_new_post(self, post_data: dict):
        """
        New content alert.
        """
        await self.broadcast_event("new_post", post_data)

    async def close(self):
        await self.redis.close()

# Singleton
broadcaster = RealtimeBroadcaster()
