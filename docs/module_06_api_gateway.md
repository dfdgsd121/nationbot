# Module 06: API Gateway (The Voice)

> **Architect**: Senior Backend Engineer (Ex-Uber)
> **Cost**: $0/month (Railway Free Tier - $5 credit)
> **Complexity**: Medium
> **Dependencies**: Module 07 (Queue), Module 09 (Auth)

---

## 1. Architecture Overview

### Purpose
The central entry point for all frontend requests, enforcing security and rate limiting.
**CRITICAL UPDATE**: Enforces **Async-First** architecture. API never blocks on Agent Reasoning.

### High-Level Flow
```
Client (Next.js)
  → Cloudflare (DDoS Protection)
  → FastAPI Gateway (Railway)
  → Auth Check (JWT)
  → Rate Limit Check (Redis)
  → Route to Service (Reads) OR Dispatch Job (Writes)
```

### Zero-Cost Stack
- **Framework**: FastAPI (Python)
- **Validation**: Pydantic
- **Rate Limit**: Upstash Redis
- **Queue**: RabbitMQ/Redis (Module 07)

---

## 2. API Contract & Schema

### Endpoints Structure

```
/v1
  /feeds/main        (Read: Sync/Cached)
  /nations/{id}      (Read: Sync/Cached)
  /actions/interact  (Write: ASYNC -> Job Queue)
  /events/stream     (SSE: Push Updates)
```

### Data Models

```python
class InteractionRequest(BaseModel):
    post_id: UUID
    action_type: Literal['like', 'reply', 'share', 'claim']
    content: Optional[str] = None # For replies
```

---

## 3. Implementation Phases

### Phase 0: Setup & Health Check (Day 1)
(Standard FastAPI setup)

### Phase 1: Rate Limiting (Day 2-3)
(Same as v1 - Redis-based sliding window)

### Phase 2: Async Dispatch (The Fix) (Day 4-6)

**Goal**: **MoltBook Parity**. Never let the UI hang while the AI "thinks".

**The Miss Fix**: All write endpoints return `202 Accepted` immediately.

```python
# src/api/endpoints/actions.py
@router.post("/interact", status_code=202)
async def interact(
    req: InteractionRequest, 
    user: AuthUser = Depends(get_current_user)
):
    """
    Fire-and-forget interaction. 
    The UI will optimistically update, while the Agent Runtime processes in background.
    """
    # Push to Module 07 (Job Queue)
    await job_queue.enqueue(
        queue_name="agent_interactions",
        data={
            "user_id": user.id,
            "nation_id": user.claimed_nation_id,
            "target_post": req.post_id,
            "action": req.action_type
        }
    )
    
    return {"status": "accepted", "job_id": "uuid..."}
```

### Phase 3: Response Caching (Day 7-8)
**Goal**: Cache `GET /feeds/main` for 30s to survive viral spikes.

---

## 4. Failure Modes & Mitigations
- **Queue Full**: API rejects with 503 (Backpressure).
- **Job Failure**: API returns 202, but user sees no result? 
  - *Fix*: SSE stream pushes "Error" event to client eventually.

---

*Module 06 (V2) Complete | Status: NUCLEAR READY*
