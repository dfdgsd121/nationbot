# src/api/endpoints/stream.py
"""
REAL-TIME SSE ENDPOINTS
Streams live posts and admin activity to connected clients.
Works WITHOUT Redis — uses in-memory asyncio queues as fallback.
"""
import asyncio
import json
import logging
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter()
logger = logging.getLogger("api.stream")

# ── In-memory feed subscribers (no Redis required) ────────────────────
FEED_SUBSCRIBERS: set[asyncio.Queue] = set()


def push_to_feed(post: dict):
    """Push a post to all SSE subscribers (called from broadcast_post)."""
    global FEED_SUBSCRIBERS
    dead = set()
    for q in FEED_SUBSCRIBERS:
        try:
            q.put_nowait(post)
        except asyncio.QueueFull:
            dead.add(q)
    FEED_SUBSCRIBERS -= dead


@router.get("/feed")
async def stream_feed():
    """SSE endpoint for real-time feed updates."""

    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        FEED_SUBSCRIBERS.add(queue)

        # Send initial connection message
        yield {
            "event": "connected",
            "data": json.dumps({"status": "connected", "channel": "nationbot:feed"})
        }

        try:
            while True:
                try:
                    post = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": "new_post",
                        "data": json.dumps(post)
                    }
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {
                        "event": "keepalive",
                        "data": json.dumps({"ts": __import__("datetime").datetime.utcnow().isoformat()})
                    }
        except asyncio.CancelledError:
            FEED_SUBSCRIBERS.discard(queue)
            raise

    return EventSourceResponse(event_generator())


@router.get("/activity")
async def stream_activity():
    """SSE endpoint for Mission Control — agent activity events."""
    from src.agent.autonomous_loop import ACTIVITY_SUBSCRIBERS

    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        ACTIVITY_SUBSCRIBERS.add(queue)

        yield {
            "event": "connected",
            "data": json.dumps({"status": "connected", "channel": "nationbot:activity"})
        }

        try:
            while True:
                try:
                    entry = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": "activity",
                        "data": json.dumps(entry)
                    }
                except asyncio.TimeoutError:
                    yield {
                        "event": "keepalive",
                        "data": json.dumps({"ts": __import__("datetime").datetime.utcnow().isoformat()})
                    }
        except asyncio.CancelledError:
            ACTIVITY_SUBSCRIBERS.discard(queue)
            raise

    return EventSourceResponse(event_generator())
