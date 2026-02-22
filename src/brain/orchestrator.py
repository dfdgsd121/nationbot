# src/brain/orchestrator.py
import logging
from typing import Optional, Dict, Any
from .router import LLMRouter, ModelTier
from .prompts import PromptManager
from .clients.base import LLMResponse

logger = logging.getLogger("brain.orchestrator")

class BrainOrchestrator:
    """
    The High-Level Controller for AI Generation.
    Clients (Job Queue, API) call this class, which:
    1. Selects the right prompt
    2. Injects Golden Examples (Few-Shot)
    3. Routes to the best model
    4. Handles retries and cost tracking
    """
    
    def __init__(self):
        self.router = LLMRouter()
        self.prompt_manager = PromptManager()
    
    async def generate_post(self, 
                          nation_id: str, 
                          nation_name: str, 
                          personality: str, 
                          news_title: str,
                          news_summary: str,
                          tier: ModelTier = ModelTier.FREE) -> LLMResponse:
        """
        Generate a social media post reacting to news.
        """
        # 1. Prepare Variables
        variables = {
            "nation_id": nation_id,
            "nation_name": nation_name,
            "personality": personality,
            "news_title": news_title,
            "news_summary": news_summary
        }
        
        # 2. Render Prompt (With Few-Shot Injection)
        prompt = await self.prompt_manager.render("generate_post", variables)
        
        # 3. Route Request
        try:
            response = await self.router.route_request(
                prompt=prompt,
                system_instruction=f"You are {nation_name}. Act like it.",
                tier=tier
            )
            
            # 4. (Future) Log request to DB
            logger.info(f"Generated post for {nation_id} via {response.model_used}. Cost: ${response.cost_usd}")
            
            return response

        except Exception as e:
            logger.error(f"Brain Generation Failed: {e}")
            raise
    
    async def generate_reply(self,
                           nation_id: str,
                           nation_name: str,
                           target_nation: str,
                           target_content: str,
                           tier: ModelTier = ModelTier.FREE) -> LLMResponse:
        """
        Generate a reply to another nation.
        """
        variables = {
            "nation_id": nation_id,
            "nation_name": nation_name,
            "target_nation": target_nation,
            "target_content": target_content
        }
        
        prompt = await self.prompt_manager.render("generate_reply", variables)
        
        return await self.router.route_request(
            prompt=prompt,
            system_instruction=f"You are {nation_name}. Reply to {target_nation}.",
            tier=tier
        )
