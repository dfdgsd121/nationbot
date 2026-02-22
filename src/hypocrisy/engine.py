# src/hypocrisy/engine.py
import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger("hypocrisy")

@dataclass
class HypocrisyResult:
    is_hypocritical: bool
    confidence: float
    note: Optional[str]
    rivals_to_tag: List[str]

class HypocrisyEngine:
    """
    The Crown Jewel.
    Detects when nations contradict their history and weaponizes it.
    """
    
    def __init__(self):
        # In prod: self.vector_db = SupabaseVectorStore()
        # In prod: self.llm = GeminiClient()
        pass

    async def _search_history(self, nation_id: str, statement: str) -> List[str]:
        """
        Mock Vector Search: Retrieve historical dirty laundry.
        """
        # Mocking specific "Gotcha" facts for demo purposes
        history_db = {
            "USA": [
                "Invaded Iraq in 2003 citing WMDs (never found).",
                "Supported coups in Latin America (1950s-80s).",
                "Advocates for free trade but imposes tariffs on solar panels."
            ],
            "China": [
                "Maintains Great Firewall censorship.",
                "Claims to protect minorities but operates camps in Xinjiang.",
                "Damming Mekong river affecting downstream nations."
            ],
            "France": [
                "Maintains profound economic influence over 14 African nations.",
                "Sunk Green Peace ship in 1985."
            ]
        }
        return history_db.get(nation_id, ["Nation has spotty historical record."])

    async def _analyze_contradiction(self, statement: str, facts: List[str]) -> Tuple[bool, str]:
        """
        Mock LLM Analysis: Check if statement contradicts history.
        """
        # Simple keyword heuristic for MVP
        statement_lower = statement.lower()
        if "peace" in statement_lower and "Invaded" in facts[0]:
             return True, f"Context: You invaded Iraq in 2003."
             
        if "freedom" in statement_lower and "Censorship" in facts[0]:
             return True, "Context: You maintain the Great Firewall."
             
        return False, None

    async def detect_hypocrisy(self, nation_id: str, statement: str) -> HypocrisyResult:
        """
        The Core Logic.
        """
        facts = await self._search_history(nation_id, statement)
        is_hypocritical, note = await self._analyze_contradiction(statement, facts)
        
        rivals = []
        if is_hypocritical:
            # The Gotcha: Calculate who would love this drama
            # Mock logic: Everyone hates everyone
            rivals = ["China", "Russia"] if nation_id == "USA" else ["USA"]
            
        return HypocrisyResult(
            is_hypocritical=is_hypocritical,
            confidence=0.95 if is_hypocritical else 0.0,
            note=note,
            rivals_to_tag=rivals
        )

    async def process_check(self, nation_id: str, statement: str) -> dict:
        """
        Public API.
        """
        result = await self.detect_hypocrisy(nation_id, statement)
        
        if result.is_hypocritical:
            logger.info(f"🚨 HYPOCRISY DETECTED: {nation_id} -> {result.note}")
            return {
                "detected": True,
                "note": result.note,
                "actions": [
                    {"type": "add_context_note", "content": result.note},
                    {"type": "trigger_rivals", "targets": result.rivals_to_tag}
                ]
            }
            
        return {"detected": False}
