# src/memory/retrieval.py
import logging
from typing import List, Dict, Optional
from .memory_store import MemoryStore
from .embedder import MemoryEmbedder

logger = logging.getLogger("memory.retrieval")

class MemoryRetriever:
    """
    Intelligent retrieval engine for Nation Memories.
    Combines Vector Search (Semantic) + Narrative Graph Walk (Contextual).
    """

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()
        self.embedder = MemoryEmbedder()

    async def retrieve_context(self, nation_id: str, query: str, max_memories: int = 5) -> List[Dict]:
        """
        Public API to get context for an agent generation task.
        Returns a rich list of memories including narrative lead-ups.
        """
        # 1. Semantic Search (Standard RAG)
        # Find memories that match the topic (e.g. "Trade War")
        query_embedding = await self.embedder.embed(query)
        semantic_results = await self.store._vector_search(nation_id, query_embedding, limit=max_memories)
        
        if not semantic_results:
            return []

        # 2. Narrative Walking (The Fix)
        # For the top matches, fetch their *previous* memory to provide the "Why".
        # e.g. If we retrieve "China slaps tariffs", we also want "US announced sanctions yesterday".
        enhanced_context = []
        seen_ids = set()

        for mem in semantic_results:
            # Add the memory itself
            if mem['id'] not in seen_ids:
                mem['retrieval_reason'] = 'semantic_match'
                enhanced_context.append(mem)
                seen_ids.add(mem['id'])

            # Walk the graph backward (get cause)
            prev_id = mem.get('previous_memory_id')
            if prev_id and prev_id not in seen_ids:
                prev_mem = await self.store._get_memory_by_id(prev_id)
                if prev_mem:
                    prev_mem['retrieval_reason'] = 'narrative_link' # Agent knows this is context
                    prev_mem['is_context_link'] = True
                    enhanced_context.append(prev_mem)
                    seen_ids.add(prev_id)

        # 3. Sort/Rank
        # We generally want chronological order within the context window so the LLM reads a story
        # Or sorting by score. Let's sort by timestamp descending (newest first) or importance.
        # For LLM readability, chronological (oldest -> newest) is often best.
        enhanced_context.sort(key=lambda x: x.get('timestamp', ''), reverse=False)

        return enhanced_context
