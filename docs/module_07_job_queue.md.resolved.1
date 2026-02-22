# Module 07: Job Queue (The Muscle)

> **Architect**: Senior Systems Engineer (Ex-Netflix)
> **Cost**: $0/month (Railway Worker + Upstash Redis)
> **Complexity**: High (Async / Reliability)
> **Dependencies**: Module 02 (LLM), Module 04 (Agent)

---

## 1. Architecture Overview

### Purpose
Offload slow, heavy, or scheduled tasks from the API to background workers to ensure UI responsiveness.
**CRITICAL UPDATE**: Implements **Dedicated Priority Lanes** to fix "Priority Inversion" and **Dead Letter Queues (DLQ)** to fix "Queue Rot".

### High-Level Flow
```
API / Scheduler 
  → Enqueue Task (Redis)
     ├─ HIGH: User Interactions (Immediate)
     └─ DEFAULT: News Reactions (Background)
  → Celery Worker (Railway)
  → Execute Logic (Agent/LLM)
  → Update DB / Notify User
```

### Zero-Cost Stack
- **Broker**: Upstash Redis (Free)
- **Worker**: Python Celery on Railway (shared $5 credit)
- **Concurrency**: `gevent` (Greenlets) for valid I/O parallelism on low RAM.

---

## 2. Task Definitions & Priority Lanes

### The Priority Lanes (The Fix)
To prevent "Priority Inversion" (User waiting behind 500 news items):

1.  **HIGH Priority Queue** (`queue='high_priority'`)
    *   **Traffic**: User claims, manual replies, "Like" processing.
    *   **SLA**: < 2 seconds start time.
    *   **Worker Allocation**: 1 dedicated worker process (or 50% capacity).

2.  **DEFAULT Priority Queue** (`queue='default'`)
    *   **Traffic**: Scheduled news ingestion, Boredom self-expression.
    *   **SLA**: < 5 minutes start time.

3.  **LOW Priority Queue** (`queue='low'`)
    *   **Traffic**: Analytics batching, pruning.

### Key Tasks

```python
@app.task(queue='default')
def generate_reaction(news_item_id, nation_id):
    # Calls Module 04 Agent Runtime
    pass

@app.task(queue='high_priority')
def process_user_interaction(user_id, post_id, action):
    # Module 06 -> Module 07 -> Module 04
    pass
```

---

## 3. Implementation Phases

### Phase 0: Setup (Day 1)
(Standard Celery Setup)

### Phase 1: Robustness (Day 2-4)

**Goal**: Retries, Dead Letter Queues (DLQ), and Timeouts.

**DLQ Configuration (The Fix)**:
Failed tasks shouldn't rot in the queue. They go to a DLQ for inspection.

```python
app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue='default',
    task_queues=(
        Queue('high_priority', routing_key='high.#'),
        Queue('default', routing_key='default.#'),
    ),
    # Dead Letter Exchange handling is manual in Redis or 
    # via Max Retries -> Log to DB
)
```

**Retry Logic**:
```python
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def robust_task(self):
    try:
        agent.run(...)
    except LLMTimeoutError as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries) # Exponential backoff
```

### Phase 2: Integration (Day 5-6)
Connect API (Producer) → Worker (Consumer).

### Phase 3: Scaling (Day 7-8)
**Goal**: Concurrency management on limited hardware.
**Strategy**: `gevent` pool.

---

## 4. Failure Modes & Mitigations
- **Worker Memory Leak**: Celery can leak RAM.
  - *Fix**: `worker_max_tasks_per_child=1000` (Restart worker after 1000 tasks).
- **Redis OOM**: Queue grows too large.
  - *Fix**: TTL on task inputs.

---

*Module 07 (V2) Complete | Status: NUCLEAR READY*
