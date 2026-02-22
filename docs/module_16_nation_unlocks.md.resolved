# Module 16: Nation Unlocks (The Growth Engine)

> **Architect**: Game Designer (Ex-Supercell)
> **Cost**: $0/month (Redis)
> **Complexity**: Medium
> **Dependencies**: Module 14 (Realtime), Module 10 (Analytics)

---

## 1. Architecture Overview

### Purpose
Gamify the entire platform. Users aren't just reading news; they are "building" the simulation.
**The Loop**: Read Drama -> React (Like/Reply) -> Global Counter Goes Up -> New Nation Unlocked -> More Drama.

### High-Level Flow
```
User Like/Reply
  → Redis INCR "global_interactions"
  → Check Tiers (10k, 50k, 100k)
  → IF Tier Reached:
      → Fire "UNLOCK_EVENT" (Module 14)
      → Update DB `nations.status = 'active'`
      → Post "ARRIVAL" message from new Nation
```

### Zero-Cost Stack
- **State**: Upstash Redis (Counters are atomic & free)
- **Logic**: Celery Worker (Async check)

---

## 2. Unlock Tiers

| Tier | Trigger (Total Actions) | Unlocked Nations | The Narrative Event |
|------|-------------------------|------------------|---------------------|
| **1** | 10,000 | **Vatican City 🇻🇦** | "Divine Intervention: The Pope has entered the chat." |
| | | **Monaco 🇲🇨** | "The billionaires have arrived." |
| **2** | 50,000 | **Texas 🤠** | "Y'all couldn't behave. We're seceding." (Fictional) |
| | | **Catalonia 🟡** | "Independence declared!" |
| **3** | 100,000 | **Roman Empire 🏛️** | "GLITCH IN SIMULATION: History collapsing." |
| **4** | 1,000,000 | **Aliens 👽** | "WE ARE WATCHING." |

---

## 3. Implementation Specs

### A. The Global Counter
We don't query SQL `COUNT(*)` every time (too slow). We use Redis.

```python
# src/analytics/gamification.py
class ValidationEngine:
    TIERS = {
        10000: ["VA", "MC"],
        50000: ["TX", "CA"],
        100000: ["ROM"]
    }

    async def increment_global_counter(self) -> int:
        # Atomic increment
        count = await self.redis.incr("sim_total_interactions")
        await self.check_unlock(count)
        return count
```

### B. The Unlock Ceremony (Realtime)
When a tier is hit, the "War Room" (Module 14) goes huge.

1.  **Freeze Mode**: All chats pause.
2.  **Animation**: "Simulation Upgrading..." overlay via SSE.
3.  **Reveal**: New Nation profile card slams onto screen.
4.  **First Post**: The new nation immediately posts a roast of the top 3 leader.

---

## 4. Database Schema Updates

### Nations Table
Add `status` and `unlock_tier` columns.

```sql
ALTER TABLE nations 
ADD COLUMN status VARCHAR(20) DEFAULT 'locked', -- 'active', 'locked', 'hidden'
ADD COLUMN unlock_tier INT DEFAULT 0;
```

---

## 5. Failure Modes
-   **Race Conditions**: Two users hit 10,000 at same time.
    -   *Fix*: Redis `INCR` returns the NEW value. Only the process that sees exactly `10000` triggers the event.
    -   *Backup*: DB check `IF status == 'locked'`.

---

*Module 16 (V1) Status: SPECIFIED*
