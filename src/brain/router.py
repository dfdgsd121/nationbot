# src/brain/router.py
import logging
from typing import Optional, Dict
from enum import Enum
from .clients.gemini_client import GeminiClient
from .clients.base import LLMResponse

logger = logging.getLogger("brain.router")

class ModelTier(Enum):
    FREE = "free"       # Gemini Flash / Groq
    STANDARD = "standard" # Gemini Pro / GPT-4o-mini
    PREMIUM = "premium"   # GPT-4 / Claude Opus (Rarely used)

class LLMRouter:
    """
    Intelligent router for LLM requests.
    Optimizes for Zero-Cost by default, upgrades only when necessary.
    """
    
    def __init__(self):
        # Initialize clients (Lazy load in real app)
        self.gemini_client = GeminiClient()
        # self.groq_client = GroqClient() # Future
        # self.openai_client = OpenAIClient() # Fallback

    async def route_request(self, 
                          prompt: str, 
                          system_instruction: Optional[str] = None, 
                          tier: ModelTier = ModelTier.FREE,
                          context_length: int = 0) -> LLMResponse:
        """
        Route request to the best model based on tier and context.
        """
        
        # Strategy 1: Free Tier First (The "Zero Cost" Rule)
        if tier == ModelTier.FREE:
            # Prefer Gemini Flash for large context, Groq for speed
            # For now, default to Gemini Flash
            try:
                return await self.gemini_client.generate(
                    prompt, 
                    system_instruction, 
                    model="gemini-1.5-flash"
                )
            except Exception as e:
                logger.warning(f"Primary Free Model failed: {e}. Trying fallback...")
                return await self._fallback_route(prompt, system_instruction)

        # Strategy 2: Complex tasks get better models
        elif tier == ModelTier.STANDARD:
            return await self.gemini_client.generate(
                prompt,
                system_instruction,
                model="gemini-1.5-pro"
            )

        raise ValueError("Invalid Model Tier")

    async def _fallback_route(self, prompt: str, system_instruction: str) -> LLMResponse:
        """
        Emergency fallback if primary model fails.
        """
        # In full implementation, this calls Groq or OpenAI
        # For now, retry Gemini standard as last resort
        logger.info("Routing to Fallback (Gemini Pro)")
        return await self.gemini_client.generate(
            prompt,
            system_instruction,
            model="gemini-1.5-pro"
        )
