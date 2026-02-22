# src/monetization/wiretap.py
import json
import logging
import asyncio
from typing import Dict, Any
from redis import asyncio as aioredis
from datetime import datetime

logger = logging.getLogger("monetization.wiretap")

class WiretapEngine:
    """
    Captures and broadcasts the AI's internal reasoning process.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis = None

    async def get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self.redis

    async def broadcast_thought(self, nation_id: str, step: str, details: Dict[str, Any]):
        """
        Publishes a single 'thought' to the wiretap channel.
        """
        channel = f"wiretap:{nation_id}"
        
        payload = {
            "type": "THOUGHT_STREAM",
            "nation_id": nation_id,
            "step_name": step,  # e.g., "SENTIMENT_ANALYSIS"
            "content": details, # e.g., {"anger": 0.8, "targets": ["US"]}
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            redis = await self.get_redis()
            await redis.publish(channel, json.dumps(payload))
            logger.debug(f"📡 Wiretap broadcast for {nation_id}: {step}")
        except Exception as e:
            logger.error(f"Wiretap broadcast failed: {e}")

    # Decorator-like usage simulation
    async def trace_agent_decision(self, nation_id: str, decision_process: callable):
        """
        Wraps an agent's Mock decision process and logs steps.
        """
        await self.broadcast_thought(nation_id, "INIT", {"status": "Waking up..."})
        
        # Simulate steps (In real usage, the agent code would call broadcast_thought directly)
        await asyncio.sleep(0.1)
        await self.broadcast_thought(nation_id, "CONTEXT_RETRIEVAL", {
            "query": "history with US",
            "found_docs": 3
        })
        
        await asyncio.sleep(0.1)
        await self.broadcast_thought(nation_id, "EMOTIONAL_STATE", {
            "current_mood": "Hostile",
            "intensity": 85
        })
        
        # Run the actual function
        result = await decision_process()
        
        await self.broadcast_thought(nation_id, "FINAL_DECISION", {
            "action": "POST",
            "draft_id": "draft_999"
        })
        
        return result
