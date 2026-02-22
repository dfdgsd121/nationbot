# src/memory/memory_store.py
from datetime import datetime
import logging
from typing import List, Dict, Optional
import json

# from supabase import create_client (Mocked for logic structure)
from .embedder import MemoryEmbedder

logger = logging.getLogger("memory.store")

class MemoryStore:
    """
    Manages storage and retrieval of nation memories.
    Implements the 'Narrative Graph' logic (Linked List of Memories).
    """

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.embedder = MemoryEmbedder()
        self.last_memory_id_cache = {} # Local cache for narrative linking

    async def add_memory(self, 
                       nation_id: str, 
                       content: str, 
                       memory_type: str = 'observation',
                       importance: float = 0.5,
                       cause_event_id: Optional[str] = None):
        """
        Store a new memory and link it to the previous one (Graph Building).
        """
        # 1. Generate Embedding
        embedding = await self.embedder.embed(content)
        
        # 2. Find Previous Memory ID (for Linked List)
        # In prod, fetch from DB: SELECT id FROM memories WHERE nation_id=x ORDER BY created_at DESC LIMIT 1
        previous_id = self.last_memory_id_cache.get(nation_id)
        
        # 3. Construct Data Payload
        data = {
            "nation_id": nation_id,
            "memory_type": memory_type,
            "content": content,
            "embedding": embedding,
            "importance": importance,
            "previous_memory_id": previous_id, # Link to past
            "cause_event_id": cause_event_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # 4. Insert into Supabase
            if self.supabase:
                response = self.supabase.table('nation_memories').insert(data).execute()
                new_id = response.data[0]['id']
            else:
                # Mock ID for local testing
                new_id = f"mem-{openai_hash(content)}" 
                logger.info(f"Stored Memory [Mock]: {content[:30]}...")

            # 5. Update Head Pointer
            self.last_memory_id_cache[nation_id] = new_id
            return new_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    async def retrieve_context(self, nation_id: str, query: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve context using Vector Search + Narrative Graph Walk.
        """
        query_embedding = await self.embedder.embed(query)
        
        # 1. Vector Search (Semantic)
        semantic_memories = await self._vector_search(nation_id, query_embedding, limit)
        
        # 2. Narrative Walk (Contextual)
        # Fetch the 'previous_memory' for the top match to get the lead-up story
        context_memories = []
        if semantic_memories:
            top_memory = semantic_memories[0]
            if top_memory.get('previous_memory_id'):
                prev_mem = await self._get_memory_by_id(top_memory['previous_memory_id'])
                if prev_mem:
                    prev_mem['is_narrative_context'] = True
                    context_memories.append(prev_mem)
        
        # Combine results
        return context_memories + semantic_memories

    async def _vector_search(self, nation_id, embedding, limit):
        # rpc call to supabase match_memories function
        if not self.supabase: return []
        return []

    async def _get_memory_by_id(self, mem_id):
        # fetch single row
        if not self.supabase: return None
        return None

def openai_hash(s):
    import hashlib
    return hashlib.md5(s.encode()).hexdigest()[:8]
