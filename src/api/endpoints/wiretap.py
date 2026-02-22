# src/api/endpoints/wiretap.py
import logging
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from redis import asyncio as aioredis
import os

router = APIRouter()
logger = logging.getLogger("api.wiretap")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@router.websocket("/{nation_id}")
async def wiretap_stream(websocket: WebSocket, nation_id: str, token: str = "guest"):
    """
    PREMIUM FEATURE: Streams the internal monologue of a nation.
    """
    # 1. Monetization Gate
    if token != "premium_secret":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Premium Subscription Required")
        return
        
    await websocket.accept()
    
    # 2. Redis Subscription
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()
    channel = f"wiretap:{nation_id}"
    await pubsub.subscribe(channel)

    try:
        # Welcome message
        await websocket.send_json({
            "type": "SYSTEM",
            "message": f"🔒 WIRETAP ESTABLISHED: {nation_id} SITUATION ROOM"
        })
        
        while True:
            # Wait for message from Redis
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            
            if message:
                # Forward to Websocket
                # Redis returns string data, we assume it is valid JSON from WiretapEngine
                data = json.loads(message['data'])
                await websocket.send_json(data)
                
            await asyncio.sleep(0.01)
            
    except WebSocketDisconnect:
        logger.info(f"Wiretap disconnected for {nation_id}")
    except Exception as e:
        logger.error(f"Wiretap error: {e}")
        await websocket.close()
    finally:
        await pubsub.unsubscribe(channel)
        await redis.close()
