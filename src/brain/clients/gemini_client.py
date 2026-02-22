# src/brain/clients/gemini_client.py
import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from .base import BaseLLMClient, LLMResponse

class GeminiClient(BaseLLMClient):
    """
    Client for Google Gemini models (Flash/Pro).
    """
    
    # Cost per 1k tokens (As of late 2024/early 2025 estimates)
    COSTS = {
        "gemini-1.5-flash": {"input": 0.0001, "output": 0.0004},  # Extremely cheap
        "gemini-1.5-pro":   {"input": 0.0035, "output": 0.0105},
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # For local dev without keys, we might mock or warn
            print("WARNING: GEMINI_API_KEY not set.")
        else:
            genai.configure(api_key=self.api_key)

    async def generate(self, prompt: str, system_instruction: Optional[str] = None, model: str = "gemini-1.5-flash", **kwargs) -> LLMResponse:
        """
        Generate text using Gemini.
        """
        try:
            # Gemini SDK configuration
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.7),
                max_output_tokens=kwargs.get("max_tokens", 500)
            )
            
            gemini_model = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction
            )
            
            # Note: SDK is sync/async depending on usage. 
            # true async support in python sdk is via generate_content_async
            response = await gemini_model.generate_content_async(prompt, generation_config=generation_config)
            
            # Metrics extraction
            # Usage metadata is standard in Gemini response
            # Note: actual sdk/response structure might vary slightly by version
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count
            
            cost = self.calculate_cost(input_tokens, output_tokens, model)
            
            return LLMResponse(
                content=response.text,
                model_used=model,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                cost_usd=cost,
                latency_ms=0 # TODO: Measure latency wrapper
            )

        except Exception as e:
            # Handle blocks, safety filters, etc.
            raise Exception(f"Gemini Generation Error: {e}")

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str = "gemini-1.5-flash") -> float:
        rates = self.COSTS.get(model, self.COSTS["gemini-1.5-flash"])
        input_cost = (prompt_tokens / 1000) * rates["input"]
        output_cost = (completion_tokens / 1000) * rates["output"]
        return round(input_cost + output_cost, 6)
