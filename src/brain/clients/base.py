# src/brain/clients/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, Any, Optional

class LLMResponse(BaseModel):
    content: str
    model_used: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: int

class BaseLLMClient(ABC):
    """
    Abstract base class for all LLM providers.
    Ensures interchangeable usage by the router.
    """
    
    @abstractmethod
    async def generate(self, prompt: str, system_instruction: Optional[str] = None, **kwargs) -> LLMResponse:
        """
        Generate text from a prompt.
        """
        pass
    
    @abstractmethod
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate cost for this specific provider.
        """
        pass
