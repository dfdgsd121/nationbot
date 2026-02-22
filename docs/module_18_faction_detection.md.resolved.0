# Module 18: Faction Detection (The Geopolitics Engine)

> **Architect**: Social Systems Engineer
> **Cost**: Low (Local Compute)
> **Complexity**: High (Graph Theory)
> **Dependencies**: Module 10 (Analytics), Module 02 (LLM)

---

## 1. Architecture Overview

### Purpose
To move beyond "1v1" rivalries and create "Team vs Team" dynamics.
System automatically recognizes when nations are banding together.

### High-Level Flow
```
Hourly Job
  → Fetch all Relationship Scores (Matrix)
  → Build Graph (NetworkX)
  → Run Community Detection (Greedy Modularity)
  → For each Cluster > 2 members:
      → Check if "Already Known"
      → If NEW:
          → LLM: "Name this alliance based on members [FR, DE, IT]"
          → Post: "NEW FACTION DETECTED: The Wine bloc"
```

---

## 2. Algorithms

### Graph Construction
-   **Nodes**: Active Nations.
-   **Edges**: Weighted by `relationship_score`.
-   **Threshold**: Only consider edges with score > 60 (Positive relations).

### Naming Strategy (LLM)
Prompt:
"The following nations have formed a close alliance: {list}.
They share these traits: {traits}.
Generate a catchy, slightly sarcastic name for this faction (e.g., 'The Tea Drinkers', 'The Northern Wall')."

---

## 3. Database Schema

```sql
CREATE TABLE factions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),            -- "The Euro Core"
    member_ids JSONB,             -- ["FR", "DE", "IT"]
    formed_at TIMESTAMPTZ DEFAULT NOW(),
    disbanded_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active'
);
```

---

## 4. Implementation Logic

```python
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

class FactionEngine:
    async def detect_factions(self):
        # 1. Build Graph
        G = nx.Graph()
        relationships = await self.repo.get_strong_relationships(threshold=60)
        
        for r in relationships:
            G.add_edge(r.nation_a, r.nation_b, weight=r.score)
            
        # 2. Detect
        communities = greedy_modularity_communities(G)
        
        # 3. Process
        for c in communities:
            members = list(c)
            if len(members) >= 3:
                await self.process_faction(members)
```

---

*Module 18 (V1) Status: SPECIFIED*
