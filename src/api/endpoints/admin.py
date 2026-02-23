# src/api/endpoints/admin.py
"""
Admin / Mission Control API
============================
Start, pause, monitor, and inject events into the autonomous loop.
"""
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.agent.autonomous_loop import autonomous_loop, ACTIVITY_LOG

router = APIRouter()
logger = logging.getLogger("api.admin")


class InjectRequest(BaseModel):
    headline: str
    source: str = "Breaking News"


class SpeedRequest(BaseModel):
    fast_interval: Optional[int] = None    # seconds
    medium_interval: Optional[int] = None
    slow_interval: Optional[int] = None


@router.get("/status")
async def get_status():
    """Get current loop state, stats, and recent activity."""
    return {
        **autonomous_loop.get_status(),
        "recent_activity": ACTIVITY_LOG[:20],
    }


@router.post("/start")
async def start_loop():
    """Start the autonomous loop."""
    if autonomous_loop.running and not autonomous_loop.paused:
        return {"status": "already_running"}
    if autonomous_loop.paused:
        autonomous_loop.resume()
        return {"status": "resumed"}
    autonomous_loop.start()
    return {"status": "started"}


@router.post("/pause")
async def pause_loop():
    """Pause the autonomous loop."""
    if not autonomous_loop.running:
        return {"status": "not_running"}
    autonomous_loop.pause()
    return {"status": "paused"}


@router.post("/resume")
async def resume_loop():
    """Resume from pause."""
    if not autonomous_loop.paused:
        return {"status": "not_paused"}
    autonomous_loop.resume()
    return {"status": "resumed"}


@router.post("/stop")
async def stop_loop():
    """Stop the autonomous loop entirely."""
    autonomous_loop.stop()
    return {"status": "stopped"}


@router.post("/inject")
async def inject_crisis(request: InjectRequest):
    """Inject a crisis — 5-8 nations react immediately."""
    if not autonomous_loop.running:
        # Start the loop if not running, so posts get generated
        autonomous_loop.start()
    result = await autonomous_loop.inject_crisis(request.headline, request.source)
    return {"status": "injected", **result}


@router.post("/speed")
async def set_speed(request: SpeedRequest):
    """Adjust tick intervals live."""
    if request.fast_interval is not None:
        autonomous_loop.fast_interval = max(30, request.fast_interval)
    if request.medium_interval is not None:
        autonomous_loop.medium_interval = max(60, request.medium_interval)
    if request.slow_interval is not None:
        autonomous_loop.slow_interval = max(120, request.slow_interval)
    return {
        "status": "updated",
        "fast_interval": autonomous_loop.fast_interval,
        "medium_interval": autonomous_loop.medium_interval,
        "slow_interval": autonomous_loop.slow_interval,
    }


@router.get("/activity")
async def get_activity(limit: int = 50):
    """Get recent activity log."""
    return {"activity": ACTIVITY_LOG[:limit]}
