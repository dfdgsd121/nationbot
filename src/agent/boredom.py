# src/agent/boredom.py
import logging
import random
from datetime import datetime
from typing import Optional, Callable
from .state_manager import StateManager

logger = logging.getLogger("agent.boredom")

class BoredomEngine:
    """
    Simulates internal drive for Nation Agents.
    If an agent is ignored (no news/replies), it gets 'bored' and acts out.
    """

    # How much boredom increases per hour of inactivity
    BOREDOM_RATE_PER_HOUR = 10 
    
    def __init__(self, state_manager: StateManager, trigger_callback: Callable):
        self.state_manager = state_manager
        self.trigger_callback = trigger_callback # Function to call to start an agent run

    async def check_boredom(self, nation_id: str):
        """
        Evaluate if a nation is bored and needs to post.
        Run this via cron every hour.
        """
        state = self.state_manager.get_state(nation_id)
        
        # 1. Calculate Inactivity
        if not state.last_active_at:
            state.last_active_at = datetime.utcnow()
            
        delta = datetime.utcnow() - state.last_active_at
        hours_inactive = delta.total_seconds() / 3600
        
        # 2. Update Score
        # Linear growth: 4 hours = +40 boredom
        new_boredom = min(100, int(hours_inactive * self.BOREDOM_RATE_PER_HOUR))
        
        logger.info(f"Nation {nation_id}: Inactive {hours_inactive:.1f}h. Boredom: {new_boredom}/{state.boredom_threshold}")

        # 3. Trigger?
        if new_boredom > state.boredom_threshold:
            logger.info(f"🚨 BOREDOM TRIGGER: {nation_id} is acting out!")
            
            # Reset boredom slightly to avoid spamming every minute if run fails
            # Ideally reset fully ONLY after successful run
            self.state_manager.update_boredom(nation_id, 0) 
            
            await self._trigger_self_expression(nation_id)
        else:
            self.state_manager.update_boredom(nation_id, new_boredom)

    async def _trigger_self_expression(self, nation_id: str):
        """
        Initiate a self-driven thought/post.
        """
        # Pick a random internal topic
        topics = [
            "past_glory", 
            "economic_anxiety", 
            "random_fact", 
            "cultural_superiority",
            "provoke_rival"
        ]
        topic = random.choice(topics)
        
        # Trigger the agent with a special 'internal' input type
        # The Soul Loop will see this not as 'news' but as an 'urge'
        await self.trigger_callback(
            nation_id=nation_id,
            input_text=f"INTERNAL_URGE: thinking about {topic}",
            input_type="boredom_drive"
        )
