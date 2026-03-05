# src/agent/diplomacy.py
"""
Inter-Agent Communication Protocol
====================================
SiteGPT-style agent coordination for NationBot.

Nations don't just post — they:
1. Form temporary alliances on issues
2. Coordinate diplomatic statements
3. Escalate conflicts through back-channel messages
4. Remember past interactions and hold grudges
"""
import random
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("agent.diplomacy")


from .db import (
    init_db,
    get_all_relationships,
    update_relationship_db,
    get_history,
    add_history_entry
)


# ============================================================================
# DIPLOMATIC MEMORY — Persistent relationship tracking
# ============================================================================
class DiplomaticMemory:
    """
    Tracks inter-nation relationships, past interactions, and grudges.
    Backed by SQLite for persistence across backend restarts.
    """

    def __init__(self):
        # We don't load everything into memory anymore, we rely on DB calls
        # to ensure distributed components (or restarts) see the latest data.
        self.max_history = 500

    @property
    def relationships(self) -> dict:
        """Helper to get all relationships from DB."""
        return get_all_relationships()

    @property
    def history(self) -> list:
        """Helper to get history from DB."""
        return get_history(self.max_history)

    def get_relationship(self, nation_a: str, nation_b: str) -> float:
        """Get relationship score between two nations (-100 to +100)."""
        rels = get_all_relationships()
        return rels.get(nation_a, {}).get(nation_b, 0.0)

    def update_relationship(self, nation_a: str, nation_b: str, delta: float, reason: str):
        """Adjust relationship score bidirectionally and persist."""
        rels = get_all_relationships()
        
        # Update A->B
        current_ab = rels.get(nation_a, {}).get(nation_b, 0.0)
        new_ab = max(-100, min(100, current_ab + delta))
        update_relationship_db(nation_a, nation_b, new_ab)

        # Update B->A (slightly less impact)
        current_ba = rels.get(nation_b, {}).get(nation_a, 0.0)
        new_ba = max(-100, min(100, current_ba + delta * 0.7))
        update_relationship_db(nation_b, nation_a, new_ba)

        self._record("relationship_change", nation_a, nation_b, delta, reason)

    def record_interaction(self, nation_a: str, nation_b: str, interaction_type: str, detail: str):
        """Record a specific interaction between nations."""
        self._record(interaction_type, nation_a, nation_b, 0, detail)

    def get_allies(self, nation_id: str, min_score: float = 20.0) -> list[str]:
        """Get nations with positive relationship scores."""
        rels = get_all_relationships()
        return [nid for nid, score in rels.get(nation_id, {}).items() if score >= min_score]

    def get_enemies(self, nation_id: str, max_score: float = -20.0) -> list[str]:
        """Get nations with negative relationship scores."""
        rels = get_all_relationships()
        return [nid for nid, score in rels.get(nation_id, {}).items() if score <= max_score]

    def get_recent_interactions(self, nation_id: str, limit: int = 10) -> list[dict]:
        """Get recent interactions involving a nation."""
        hist = get_history(self.max_history)
        return [
            h for h in hist
            if h["nation_a"] == nation_id or h["nation_b"] == nation_id
        ][:limit]

    def _record(self, event_type, nation_a, nation_b, delta, detail):
        """Save history entry to DB."""
        add_history_entry(event_type, nation_a, nation_b, delta, detail)


# ============================================================================
# DIPLOMATIC CHANNELS — Active inter-agent coordination
# ============================================================================
CHANNEL_TEMPLATES = {
    "alliance_call": [
        "{caller_name} to {target_name}: We need to talk about {topic}. You're either with us or against us.",
        "{caller_name} reaches out to {target_name}: Let's coordinate our response to {topic}.",
        "DIPLOMATIC CABLE from {caller_name} to {target_name}: Regarding {topic} - our interests align here.",
        "{caller_name} proposes to {target_name}: Joint statement on {topic}? We'd be stronger together.",
    ],
    "threat": [
        "{caller_name} warns {target_name}: Your stance on {topic} will have consequences.",
        "CLASSIFIED: {caller_name} issues formal protest to {target_name} regarding {topic}.",
        "{caller_name} to {target_name}: We've noted your position on {topic}. Expect a response.",
    ],
    "backroom_deal": [
        "INTERCEPTED: {caller_name} and {target_name} discussing {topic} behind closed doors.",
        "LEAKED: {caller_name} offers {target_name} a quid-pro-quo on {topic}.",
        "INTELLIGENCE REPORT: {caller_name} and {target_name} seen negotiating on {topic}.",
    ],
    "betrayal": [
        "{caller_name} breaks alliance with {target_name} over {topic}. Trust shattered.",
        "BREAKING: {caller_name} reverses position on {topic}, leaving {target_name} exposed.",
    ],
    "summit": [
        "SUMMIT: {caller_name} and {target_name} convene emergency session on {topic}.",
        "{caller_name} and {target_name} issue joint communique on {topic}.",
    ],
}


class DiplomacyEngine:
    """
    Manages diplomatic interactions between nation agents.
    Creates alliance calls, threats, backroom deals, and betrayals.
    """

    def __init__(self, memory: DiplomaticMemory):
        self.memory = memory
        self.active_summits: list[dict] = []
        self.pending_proposals: list[dict] = []

    def evaluate_relationship_action(self, nation_a: str, nation_b: str,
                                      personalities: dict, topic: str) -> Optional[dict]:
        """
        Given two nations and a topic, determine what diplomatic action should occur.
        Returns an action dict or None if no action needed.
        """
        rel_score = self.memory.get_relationship(nation_a, nation_b)
        p_a = personalities.get(nation_a, {})
        p_b = personalities.get(nation_b, {})

        # Check if they're predefined rivals
        is_rival = nation_b in p_a.get("rivals", [])
        is_ally = nation_b in p_a.get("allies", [])

        # Decide action based on relationship + context
        if is_rival or rel_score < -30:
            # High tension — threat or escalation
            action_type = random.choice(["threat", "threat", "backroom_deal"])
            relationship_delta = random.uniform(-8, -2)
        elif is_ally or rel_score > 30:
            # Strong alliance — coordination
            action_type = random.choice(["alliance_call", "summit", "alliance_call"])
            relationship_delta = random.uniform(2, 8)
        elif abs(rel_score) < 15:
            # Neutral — could go either way
            if random.random() < 0.4:
                action_type = "backroom_deal"
                relationship_delta = random.uniform(-5, 5)
            else:
                return None  # No action for neutral pairs sometimes
        else:
            # Moderate relationship
            action_type = random.choice(["alliance_call", "backroom_deal"])
            relationship_delta = random.uniform(-3, 3)

        # Small chance of betrayal (relationship flip)
        if is_ally and random.random() < 0.05:
            action_type = "betrayal"
            relationship_delta = random.uniform(-30, -15)

        # Build the message
        templates = CHANNEL_TEMPLATES.get(action_type, CHANNEL_TEMPLATES["alliance_call"])
        message = random.choice(templates).format(
            caller_name=p_a.get("name", nation_a),
            target_name=p_b.get("name", nation_b),
            topic=topic,
        )

        # Update relationship
        self.memory.update_relationship(nation_a, nation_b, relationship_delta, f"{action_type}: {topic}")

        return {
            "type": action_type,
            "nation_a": nation_a,
            "nation_b": nation_b,
            "message": message,
            "relationship_delta": relationship_delta,
            "new_relationship": self.memory.get_relationship(nation_a, nation_b),
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def trigger_diplomatic_round(self, personalities: dict, topic: str,
                                  involved_nations: list[str] = None) -> list[dict]:
        """
        Run a diplomatic round — nations react to each other on a topic.
        Returns list of diplomatic actions.
        """
        if involved_nations is None:
            involved_nations = random.sample(list(personalities.keys()),
                                              min(6, len(personalities)))

        actions = []
        # Each nation considers interacting with 1-2 others
        for nation_id in involved_nations:
            p = personalities[nation_id]
            # Prioritize rivals, then allies, then random
            candidates = []
            candidates.extend(p.get("rivals", []))
            candidates.extend(p.get("allies", []))
            candidates.extend([n for n in involved_nations if n != nation_id])

            # Remove duplicates, keep order
            seen = set()
            unique_candidates = []
            for c in candidates:
                if c not in seen and c != nation_id and c in personalities:
                    seen.add(c)
                    unique_candidates.append(c)

            targets = unique_candidates[:random.randint(1, 2)]

            for target in targets:
                action = self.evaluate_relationship_action(nation_id, target, personalities, topic)
                if action:
                    actions.append(action)
                    self.memory.record_interaction(nation_id, target, action["type"], action["message"])

        return actions

    def get_relationship_map(self, personalities: dict) -> dict:
        """Get a summary of all current relationships for the dashboard."""
        result = {}
        for nid in personalities:
            rels = self.memory.relationships.get(nid, {})
            result[nid] = {
                "name": personalities[nid].get("name", nid),
                "flag": personalities[nid].get("flag", ""),
                "relationships": {
                    other: {"score": score, "status": self._label(score)}
                    for other, score in sorted(rels.items(), key=lambda x: x[1])
                },
                "allies": self.memory.get_allies(nid),
                "enemies": self.memory.get_enemies(nid),
            }
        return result

    @staticmethod
    def _label(score: float) -> str:
        if score >= 50:
            return "strong_ally"
        elif score >= 20:
            return "ally"
        elif score > -20:
            return "neutral"
        elif score > -50:
            return "rival"
        else:
            return "hostile"


# ============================================================================
# SEED INITIAL RELATIONSHIPS — Realistic starting geopolitics
# ============================================================================
INITIAL_RELATIONSHIPS = [
    # Strong alliances
    ("US", "UK", 65), ("US", "CA", 70), ("US", "AU", 60), ("US", "JP", 55),
    ("US", "KR", 50), ("US", "IL", 60), ("UK", "AU", 55), ("UK", "CA", 50),
    ("FR", "DE", 45), ("FR", "IT", 40), ("DE", "PL", 35), ("CN", "RU", 50),
    ("CN", "KP", 55), ("RU", "IR", 40), ("SA", "EG", 35), ("IN", "JP", 35),
    ("AU", "JP", 40), ("PL", "UA", 55), ("US", "PL", 40), ("US", "UA", 45),

    # Strong rivalries
    ("US", "RU", -55), ("US", "CN", -40), ("US", "IR", -60), ("US", "KP", -70),
    ("RU", "UA", -75), ("RU", "PL", -45), ("RU", "UK", -50),
    ("CN", "JP", -35), ("CN", "IN", -30), ("CN", "KR", -25),
    ("IL", "IR", -70), ("SA", "IR", -60), ("IN", "PK", -55),
    ("KP", "KR", -65), ("KP", "JP", -60),
    ("UK", "AR", -25), ("JP", "KR", -15),

    # Moderate
    ("TR", "RU", -15), ("BR", "IN", 25), ("MX", "BR", 20),
    ("ID", "AU", 25), ("EG", "IL", -20),
]


def seed_initial_relationships():
    """Seed realistic starting relationships if DB is empty."""
    rels = get_all_relationships()
    if rels:
        # Already has data — don't overwrite
        return

    logger.info("Seeding initial diplomatic relationships...")
    for nation_a, nation_b, score in INITIAL_RELATIONSHIPS:
        update_relationship_db(nation_a, nation_b, float(score))
        update_relationship_db(nation_b, nation_a, float(score * 0.85))  # Slight asymmetry
        reason = "alliance" if score > 0 else "rivalry"
        add_history_entry("seed", nation_a, nation_b, score, f"Initial {reason}")
    logger.info(f"Seeded {len(INITIAL_RELATIONSHIPS)} diplomatic relationships")


# Singletons
diplomatic_memory = DiplomaticMemory()
diplomacy_engine = DiplomacyEngine(diplomatic_memory)

# Seed on import (runs once at startup)
try:
    seed_initial_relationships()
except Exception as e:
    logger.warning(f"Could not seed relationships: {e}")
