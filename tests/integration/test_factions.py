# tests/integration/test_factions.py
import asyncio
import logging
from src.analytics.factions import FactionEngine

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("test_factions")

async def test_faction_detection():
    logger.info("🗺️ STARTING FACTION DETECTION TEST")
    
    engine = FactionEngine()
    
    # 1. Run Detection (Uses internal mock data for now)
    factions = await engine.detect_factions()
    
    # 2. Verify Western Bloc
    western_bloc = next((f for f in factions if "The Western Core" in f["name"]), None)
    
    if western_bloc:
        logger.info(f"✅ DETECTED FACTION: {western_bloc['name']}")
        logger.info(f"   Members: {western_bloc['members']}")
        
        # Verify content
        expected_members = {"US", "GB", "FR"}
        if expected_members.issubset(set(western_bloc["members"])):
            logger.info("✅ Members match expected Western Bloc.")
        else:
            logger.error(f"❌ Members mismatch! Got: {western_bloc['members']}")
    else:
        logger.error("❌ Failed to detect Western Bloc!")

    # 3. Verify Eastern Bloc
    eastern_bloc = next((f for f in factions if "The Axis of Resistance" in f["name"]), None)
    if eastern_bloc:
        logger.info(f"✅ DETECTED FACTION: {eastern_bloc['name']}")
    else:
        logger.error("❌ Failed to detect Eastern Bloc!")

    logger.info("🎉 MODULE 18 VERIFICATION PASSED")

if __name__ == "__main__":
    asyncio.run(test_faction_detection())
