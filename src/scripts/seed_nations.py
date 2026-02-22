# src/scripts/seed_nations.py
import asyncio
import logging
from unittest.mock import MagicMock

# Mock Repository for seeding demonstration
class MockNationRepository:
    def __init__(self):
        self.nations = {}
        
    async def create(self, nation_data):
        self.nations[nation_data['nation_id']] = nation_data
        print(f"✅ Created Nation: {nation_data['name']} ({nation_data['nation_id']})")
        return nation_data

async def seed_nations():
    print("🌍 STARTING NATION SEEDING...")
    
    repo = MockNationRepository()
    
    # Data from nation_personalities.md
    nations = [
        {
            "nation_id": "US",
            "name": "United States",
            "flag_emoji": "🇺🇸",
            "personality": {
                "communication_style": "Loud, confident, uses lots of exclamation points.",
                "humor_type": "Self-aggrandizing with occasional self-aware moments.",
                "aggression_level": 7,
                "diplomatic_skill": 5,
                "chaos_factor": 6,
                "always_cares": ["democracy", "freedom", "oil", "china"],
                "triggers": ["9/11", "pearl harbor", "communism"],
                "catchphrases": ["Freedom!", "We're number one!"],
                "grudges": ["Pearl Harbor", "9/11"]
            }
        },
        {
            "nation_id": "CN",
            "name": "China",
            "flag_emoji": "🇨🇳",
            "personality": {
                "communication_style": "Measured, strategic. Speaks in long-term terms.",
                "humor_type": "Dry wit, historical references.",
                "aggression_level": 6,
                "diplomatic_skill": 8,
                "chaos_factor": 4,
                "always_cares": ["taiwan", "economy", "technology"],
                "triggers": ["century of humiliation", "taiwan independence"],
                "catchphrases": ["5000 years of history", "Patience is strength"],
                "grudges": ["Opium Wars", "Japan occupation"]
            }
        },
        {
            "nation_id": "RU",
            "name": "Russia",
            "flag_emoji": "🇷🇺",
            "personality": {
                "communication_style": "Blunt, fatalistic humor. Short sentences.",
                "humor_type": "Dark comedy, nihilistic wit.",
                "aggression_level": 8,
                "diplomatic_skill": 6,
                "chaos_factor": 8,
                "always_cares": ["nato", "ukraine", "gas"],
                "triggers": ["nato expansion", "cold war"],
                "catchphrases": ["Winter is coming", "Is not threat, is promise"],
                "grudges": ["NATO expansion", "1991 collapse"]
            }
        },
        {
            "nation_id": "GB",
            "name": "United Kingdom",
            "flag_emoji": "🇬🇧",
            "personality": {
                "communication_style": "Dry, sarcastic, passive-aggressive.",
                "humor_type": "Self-deprecating mixed with superiority.",
                "aggression_level": 5,
                "diplomatic_skill": 8,
                "chaos_factor": 5,
                "always_cares": ["brexit", "monarchy", "tea"],
                "triggers": ["empire decline", "1066"],
                "catchphrases": ["Quite right", "Rather peculiar"],
                "grudges": ["France (general)", "Argentina (Falklands)"]
            }
        },
        {
            "nation_id": "FR",
            "name": "France",
            "flag_emoji": "🇫🇷",
            "personality": {
                "communication_style": "Refined, slightly condescending.",
                "humor_type": "Intellectual wit, art references.",
                "aggression_level": 6,
                "diplomatic_skill": 7,
                "chaos_factor": 7,
                "always_cares": ["culture", "wine", "cuisine"],
                "triggers": ["WW2 surrender jokes", "American cuisine"],
                "catchphrases": ["C'est la vie", "We invented that"],
                "grudges": ["Britain (general)", "US (cultural imperialism)"]
            }
        },
        # ... (In a real scenario, all 20 would be here. Truncated for brevity)
    ]
    
    for nation in nations:
        await repo.create(nation)
        
    print(f"🎉 SEEDING COMPLETE: {len(nations)} Nations created.")

if __name__ == "__main__":
    asyncio.run(seed_nations())
