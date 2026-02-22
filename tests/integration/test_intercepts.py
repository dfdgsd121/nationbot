# tests/integration/test_intercepts.py
import asyncio
import logging
import datetime
from src.drama.intercepts import InterceptGenerator

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("test_intercepts")

async def test_intercept_timelock():
    logger.info("🕵️ STARTING INTERCEPT TIMELOCK TEST")
    
    generator = InterceptGenerator()
    
    # 1. Create a fresh intercept (Default: Locked for 24h)
    intercept = await generator.create_daily_intercept("US", "CN")
    logger.info(f"Generated Intercept: {intercept['id']}")
    logger.info(f"Reveal At: {intercept['reveal_at']}")
    
    # 2. Verify LOCKED state
    view_locked = generator.get_viewable_content(intercept)
    
    if view_locked["status"] == "LOCKED" and "SIGNAL ENCRYPTED" in view_locked["display_text"]:
         logger.info("✅ LOCKED State Verified: Content is hidden.")
    else:
         logger.error(f"❌ FAILED: Content leaked! {view_locked}")
         return

    # 3. Simulate Time Passing (Unlock)
    # We manually set reveal_at to the past
    intercept_unlocked = intercept.copy()
    intercept_unlocked["reveal_at"] = datetime.datetime.now() - datetime.timedelta(hours=1)
    
    # 4. Verify UNLOCKED state
    view_unlocked = generator.get_viewable_content(intercept_unlocked)
    
    if view_unlocked["status"] == "UNLOCKEKD" and "We cannot let" in view_unlocked["display_text"]:
         logger.info("✅ UNLOCKED State Verified: Content is visible.")
    else:
         logger.error(f"❌ FAILED: Content still hidden! {view_unlocked}")
         return

    logger.info("🎉 MODULE 17 VERIFICATION PASSED")

if __name__ == "__main__":
    asyncio.run(test_intercept_timelock())
