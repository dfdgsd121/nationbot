# src/api/endpoints/stream.py
"""
REAL-TIME SSE ENDPOINT
Streams live posts to connected clients
"""
import asyncio
import json
import logging
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as aioredis
import os

router = APIRouter()
logger = logging.getLogger("api.stream")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@router.get("/feed")
async def stream_feed():
    """SSE endpoint for real-time feed updates"""
    
    async def event_generator():
        redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        pubsub = redis.pubsub()
        await pubsub.subscribe("nationbot:feed")
        
        # Send initial connection message
        yield {
            "event": "connected",
            "data": json.dumps({"status": "connected", "channel": "nationbot:feed"})
        }
        
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    yield {
                        "event": "new_post",
                        "data": message["data"]
                    }
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            await pubsub.unsubscribe("nationbot:feed")
            await redis.close()
            raise
    
    return EventSourceResponse(event_generator())
