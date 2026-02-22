# src/memory/embedder.py
import os
import logging
from typing import List
import google.generativeai as genai

logger = logging.getLogger("memory.embedder")

class MemoryEmbedder:
    """
    Client for generating vector embeddings using Gemini (text-embedding-004).
    Optimized for cost (batching).
    """
    
    MODEL_NAME = "models/text-embedding-004"
    DIMENSION = 768

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logger.warning("GEMINI_API_KEY not set. Embedding will fail.")

    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single string.
        """
        try:
            result = await genai.embed_content_async(
                model=self.MODEL_NAME,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            # Return zero vector in worst case to prevent crash, or raise
            return [0.0] * self.DIMENSION

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Batch embedding for efficiency.
        Gemini supports up to 100/call.
        """
        if not texts:
            return []
            
        try:
            # Note: SDK batch syntax might vary slightly
            result = await genai.embed_content_async(
                model=self.MODEL_NAME,
                content=texts,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [ [0.0]*self.DIMENSION for _ in texts ]
