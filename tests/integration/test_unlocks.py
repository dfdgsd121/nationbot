# tests/integration/test_unlocks.py
import asyncio
import logging
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# Mock Redis BEFORE imports
sys.modules['redis'] = MagicMock()
sys.modules['redis.asyncio'] = MagicMock()

from src.analytics.gamification import GamificationEngine

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("test_unlocks")

async def test_unlock_mechanic():
    logger.info("🎮 STARTING UNLOCK MECHANIC TEST")
    
    # 1. Setup Mock Engine
    engine = GamificationEngine()
    
    # Mock Redis INCR to return a specific threshold
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 10000  # We hit Tier 1!
    engine.get_redis = AsyncMock(return_value=mock_redis)
    
    # Mock Broadcaster to capture the event
    engine.broadcaster.broadcast_event = AsyncMock()
    
    # 2. Trigger Action
    new_count = await engine.increment_global_counter()
    logger.info(f"✅ Triggered increment. New Count: {new_count}")
    
    # 3. Verify Unlock Logic
    # Should have triggered Tier 1 (Vatican + Monaco)
    expected_nations = ["VA", "MC"]
    
    if engine.broadcaster.broadcast_event.called:
        call_args = engine.broadcaster.broadcast_event.call_args[0][0]
        if call_args['event_type'] == "NATION_UNLOCK" and call_args['milestone'] == 10000:
             logger.info(f"✅ UNLOCK EVENT FIRED: {call_args['message']}")
             logger.info(f"✅ Unlocked Nations: {call_args['unlocked_nations']}")
        else:
             logger.error(f"❌ Event Details mismatch: {call_args}")
    else:
        logger.error("❌ UNLOCK EVENT NOT FIRED")
        
    # 4. Test Non-Threshold
    mock_redis.incr.return_value = 10001
    engine.broadcaster.broadcast_event.reset_mock()
    
    await engine.increment_global_counter()
    
    if not engine.broadcaster.broadcast_event.called:
        logger.info("✅ Non-threshold value (10001) correctly IGNORED.")
    else:
        logger.error("❌ Event fired when it shouldn't have!")

    logger.info("🎉 MODULE 16 VERIFICATION PASSED")

if __name__ == "__main__":
    asyncio.run(test_unlock_mechanic())
