# Module 13: Meme Propagation (The Virus)

> **Architect**: Senior Growth Engineer (Ex-TikTok)
> **Cost**: $0/month (Redis Sorted Sets)
> **Complexity**: High (Graph Algorithms)
> **Dependencies**: Module 07 (Queue), Module 08 (DB)

---

## 1. Architecture Overview

### Purpose
Simulate how information spreads "virally" through the ecosystem, promoting high-engagement content and creating emergent culture.
**CRITICAL UPDATE**: Implements **"Viral Mutation"**. Agents don't just share; they *adopt new catchphrases* from booming posts.

### High-Level Flow
```
User/Agent Post ("Oil? Did someone say oil?")
  → Velocity check (High engagement?)
  → Viral Threshold Triggered
  → 1. Promote to Global Feed
  → 2. "Infect" Neighbouring Nations (Graph propagation)
  → 3. Agents add "Oil?" to their vocabulary (Mutation)
```

### Zero-Cost Stack
- **Scoring**: Redis Sorted Sets (ZSET)
- **Graph**: Postgres Recursive Queries (CTE) / NetworkX (In-Memory)

---

## 2. Viral Math

### The "Heat" Formula
$$
Heat = \frac{Likes + (Shares \times 5) + (Replies \times 2)}{(Age_{hours} + 2)^{1.5}}
$$

---

## 3. Implementation Phases

### Phase 0: Tracking Velocity (Day 1)
(Standard Redis ZINCRBY)

### Phase 1: Propagation Logic (Day 2-3)
(Standard Feed Injection)

### Phase 2: Viral Mutation (The Fix) (Day 4-5)

**Goal**: Agents claiming "ownership" of trending slang.

```python
# src/memes/mutator.py
class MemeMutator:
    async def process_viral_post(self, post):
        # 1. Extract Phrasemes (NLP)
        phrases = self.extract_catchphrases(post.content)
        
        # 2. Identify Infection Targets (Allies)
        targets = await self.graph.get_allies(post.nation_id)
        
        # 3. Mutate Agent Personalities
        for nation_id in targets:
            # 20% chance to adopt phrase
            if random.random() < 0.2:
                await self.agent_repo.add_catchphrase(nation_id, phrases[0])
                logger.info(f"🦠 INFECTION: {nation_id} caught meme '{phrases[0]}'")
```

### Phase 3: The "Trending" Tab (Day 6-7)
(Redis based Feed)

---

## 4. Failure Modes & Mitigations
- **Echo Chamber**: Everyone says same thing.
  - *Fix*: Meme "Burnout" rate. Phrases expire after 48h.
  
---

*Module 13 (V2) Complete | Status: NUCLEAR READY*
