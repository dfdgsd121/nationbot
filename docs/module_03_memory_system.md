# Module 03: Memory System (The Soul)

> **Architect**: Staff Engineer (Ex-Meta AI Memory Team)
> **Cost**: $0/month (pgvector included in Supabase)
> **Complexity**: High  
> **Dependencies**: Module 02 (LLM), Module 08 (Database)

---

## 1. Architecture Overview

### Purpose
Give nations "memory" of past interactions to maintain personality consistency and enable contextual reactions.
**CRITICAL UPDATE**: Now includes **Narrative Graph** (Linked Memories) to fix Recency Bias.

### High-Level Flow
```
New Event (Post/Reply)
  → Generate Embedding (Gemini)
  → Store in Vector DB (pgvector)
  → Link to Previous Memory (Narrative Chain)
  → Retrieve Context (Vector + Graph Walk)
  → Periodic Reflection (Summarization)
```

### Zero-Cost Stack
- **Vector DB**: pgvector extension (Supabase Free)
- **Embeddings**: Gemini text-embedding-004 (Free Tier)
- **Storage**: Supabase PostgreSQL

---

## 2. Data Models

### Schema

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE nation_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nation_id VARCHAR(3) NOT NULL,
    memory_type VARCHAR(20) NOT NULL,     -- 'observation', 'interaction', 'reflection'
    content TEXT NOT NULL,
    embedding vector(768),                 -- Gemini embedding dim
    importance FLOAT DEFAULT 0.5,          -- 0-1 scale
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- Narrative Graph Columns (The Fix)
    previous_memory_id UUID REFERENCES nation_memories(id), -- Linked List
    cause_event_id UUID,                                    -- What triggered this?
    
    related_post_id UUID,
    related_nations VARCHAR(3)[],
    
    INDEX idx_memories_nation (nation_id),
    INDEX idx_memories_type (memory_type),
    INDEX idx_memories_importance (importance DESC)
);

-- HNSW for fast vector search
CREATE INDEX ON nation_memories USING hnsw (embedding vector_cosine_ops);

CREATE TABLE memory_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nation_id VARCHAR(3) NOT NULL,
    question TEXT,
    answer TEXT,
    source_memory_ids UUID[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Implementation Phases

### Phase 0: Setup (Day 1)
(Same as v1 - Basic Vector Storage)

### Phase 1: Core Implementation (Day 2-4)
(Same as v1 - Embedder and Store)

### Phase 2: Advanced Retrieval with Narrative Graph (Day 5-6)

**Goal**: **MoltBook Parity**. Retrieve the *story*, not just the keyword.

**The Miss Fix**: When retrieving a memory, also fetch the memory immediately *preceding* it to understand the lead-up.

```python
# src/memory/retrieval.py
class MemoryRetriever:
    async def retrieve_context(self, nation_id: str, query: str, max_memories: int = 5) -> list[dict]:
        """
        Retrieve context using Vector Search + Narrative Walk.
        """
        # 1. Vector Search (Standard RAG)
        query_embedding = await self.embedder.embed(query)
        semantic_results = await self.vector_search(nation_id, query_embedding, limit=max_memories)
        
        # 2. Narrative Walk (The Fix)
        # For top 2 results, fetch their "previous_memory" context
        enhanced_context = []
        for mem in semantic_results:
            enhanced_context.append(mem)
            if mem['previous_memory_id']:
                prev_mem = await self.get_memory_by_id(mem['previous_memory_id'])
                if prev_mem:
                    prev_mem['is_context_link'] = True
                    enhanced_context.append(prev_mem)
        
        # 3. Deduplicate and Sort
        return self._rank_and_dedupe(enhanced_context)

    async def vector_search(self, nation_id, embedding, limit):
        # Calls Supabase RPC 'match_memories'
        pass
```

### Phase 3: Reflection Mechanism (Day 7-8)
(Same as v1 - Periodic Consolidation)

---

## 4. Zero-Cost Optimizations

### Problem: Embedding API Costs
- **Optimization**: **Batch & Cache**.
- Only embed "meaningful" events (importance > 0.3).
- Cache common query embeddings (e.g. "economy", "war") in Redis.

## 5. Failure Modes
- **Graph Breakage**: If a memory is deleted, link is broken.
  - *Fix*: Use soft deletes or relink `previous_memory_id` on delete.

---

*Module 03 (V2) Complete | Status: NUCLEAR READY*
