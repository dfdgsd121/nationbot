# src/analytics/factions.py
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger("analytics.factions")

class FactionEngine:
    """
    Analyzes the social graph to detect emergent factions.
    """
    
    def __init__(self, repository=None, llm_client=None):
        self.repo = repository
        self.llm = llm_client

    async def build_relationship_graph(self) -> nx.Graph:
        """
        Fetches relationship scores and builds a NetworkX graph.
        """
        G = nx.Graph()
        
        # In prod, fetch from DB: await self.repo.get_all_relationships()
        # Mocking data for this implementation phase
        relationships = [
            ("US", "GB", 90), ("US", "FR", 80), ("GB", "FR", 85),  # Western Bloc
            ("RU", "CN", 85), ("RU", "IR", 80), ("CN", "IR", 75),  # Eastern Bloc
            ("BR", "IN", 60), ("IN", "ZA", 60), ("BR", "ZA", 65)   # BRICS-ish
        ]
        
        for n1, n2, score in relationships:
            # Only consider strong bonds for alliances
            if score > 50:
                G.add_edge(n1, n2, weight=score)
                
        return G

    async def detect_factions(self) -> List[Dict]:
        """
        Runs community detection to find factions.
        """
        G = await self.build_relationship_graph()
        
        # Detect communities using Modularity
        # Returns list of frozensets: [frozenset({'US', 'GB', 'FR'}), ...]
        communities = list(greedy_modularity_communities(G))
        
        factions = []
        for i, community in enumerate(communities):
            members = list(community)
            
            # Filter: A faction needs at least 3 members
            if len(members) >= 3:
                faction_name = await self._generate_faction_name(members)
                factions.append({
                    "id": f"faction_{i}",
                    "name": faction_name,
                    "members": members,
                    "type": "emergent_alliance"
                })
                
        logger.info(f"✅ Detected {len(factions)} factions: {[f['name'] for f in factions]}")
        return factions

    async def _generate_faction_name(self, members: List[str]) -> str:
        """
        Uses LLM (or mock) to name the faction based on members.
        """
        # Mock Logic for V1
        s = set(members)
        if {"US", "GB", "FR"}.issubset(s):
            return "The Western Core"
        if {"RU", "CN", "IR"}.issubset(s):
            return "The Axis of Resistance"
        if {"BR", "IN", "ZA"}.issubset(s):
            return "The Global South"
            
        return f"Alliance of {', '.join(members)}"
