# src/agent/state_manager.py
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from .models import NationState

logger = logging.getLogger("agent.state")

class StateManager:
    """
    Manages the persistent state of a Nation Agent.
    Handles mood updates, energy levels, and boredom metrics.
    """
    
    def __init__(self, db_session: Session):
        self.session = db_session

    def get_state(self, nation_id: str) -> NationState:
        """Fetch current state or create if missing."""
        state = self.session.query(NationState).filter_by(nation_id=nation_id).first()
        if not state:
            state = NationState(nation_id=nation_id)
            self.session.add(state)
            self.session.commit()
        return state

    def update_mood(self, nation_id: str, event_sentiment: float):
        """
        Update mood based on external event sentiment (-1.0 to 1.0).
        Aggressive <- Neutral -> Happy
        """
        state = self.get_state(nation_id)
        
        # Simple Mood Logic (Nucleus of the 'Soul')
        if event_sentiment < -0.4:
            state.current_mood = "aggressive"
        elif event_sentiment > 0.4:
            state.current_mood = "happy"
        else:
            # Decay towards neutral
            state.current_mood = "diplomatic"
            
        self.session.commit()
        return state.current_mood

    def update_boredom(self, nation_id: str, new_score: int):
        """Update boredom tracking."""
        state = self.get_state(nation_id)
        state.boredom_score = min(100, max(0, new_score))
        self.session.commit()

    def record_activity(self, nation_id: str):
        """Reset boredom and update last active timestamp."""
        state = self.get_state(nation_id)
        state.last_active_at = datetime.utcnow()
        state.boredom_score = 0
        self.session.commit()
