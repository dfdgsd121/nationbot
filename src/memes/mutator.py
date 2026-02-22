# src/memes/mutator.py
import logging
import random
import re
from typing import List

logger = logging.getLogger("memes")

class MemeMutator:
    """
    The Virus.
    Allows slang and inside jokes to spread across the graph.
    """
    
    def __init__(self):
        # In prod: self.graph_store = RedisGraph()
        # In prod: self.agent_repo = AgentRepository()
        pass

    def extract_catchphrases(self, content: str) -> List[str]:
        """
        Identify potential memes (short, punchy phrases).
        """
        # HACK: Simple heuristic for MVP. 
        # In prod: Use TF-IDF or specific N-gram analysis.
        
        # 1. Quoted text: "Oil?"
        quotes = re.findall(r'"([^"]*)"', content)
        if quotes:
            return [q for q in quotes if len(q.split()) < 5]
            
        # 2. Short sentences (Twitter style)
        sentences = [s.strip() for s in content.split('.') if s]
        short_sentences = [s for s in sentences if len(s.split()) < 6]
        
        return short_sentences[:1]

    async def get_allies(self, nation_id: str) -> List[str]:
        """
        Mock Graph Query: Who is influenced by this nation?
        """
        # Static mock graph
        alliances = {
            "USA": ["UK", "Canada", "Israel", "Japan"],
            "Russia": ["China", "Iran", "Belarus", "Syria"],
            "China": ["Russia", "Pakistan", "North Korea"],
            "UK": ["USA", "France", "Germany"],
            "France": ["Germany", "UK", "Italy"]
        }
        return alliances.get(nation_id, [])

    async def infect_network(self, nation_id: str, content: str, viral_score: float):
        """
        Propagate the virus.
        """
        if viral_score < 0.5:
             # Not viral enough to mutate culture
             return
             
        phrases = self.extract_catchphrases(content)
        if not phrases:
            return
            
        meme = phrases[0]
        allies = await self.get_allies(nation_id)
        
        for ally in allies:
            # Infection Probability
            # Higher viral score -> Higher infection chance
            chance = 0.2 + (viral_score * 0.1) 
            
            if random.random() < chance:
                logger.info(f"🦠 MEME INFECTION: {ally} caught '{meme}' from {nation_id}")
                # await self.agent_repo.add_catchphrase(ally, meme)
                # await self.notify_infection(ally, meme)

    async def process_post(self, post_data: dict):
        """
        Main entry point called by Job Queue worker.
        """
        # Calculate simplistic viral score based on quick reaction
        # In prod: Use Redis ZSCORE
        viral_score = random.random() # Mock
        
        await self.infect_network(
            post_data['nation_id'], 
            post_data['content'], 
            viral_score
        )
