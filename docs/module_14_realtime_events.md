# Module 14: Real-time Events (The Pulse)

> **Architect**: Senior Real-time Engineer (Ex-WhatsApp)
> **Cost**: $0/month (SSE over HTTP)
> **Complexity**: Medium
> **Dependencies**: Module 06 (API), Module 07 (Queue)

---

## 1. Architecture Overview

### Purpose
Deliver new posts, notifications, and stats updates to clients instantly.
**CRITICAL UPDATE**: Implements **"The War Room"** feel. Users see "Russia is typing..." or "New Sanction Declared" live.

### Why SSE over WebSockets?
- **Vercel**: Serverless functions have execution limits. WebSockets require long-running servers.
- **SSE**: Unidirectional (Server -> Client) is perfect for feeds. Works over standard HTTP/2.

### High-Level Flow
```
Event (New Post / Typing Status)
  → Publish to Redis Channel ("channel:global")
  → SSE Endpoint (FastAPI) listening to Redis
  → Stream to Client Connection
```

### Zero-Cost Stack
- **Broker**: Upstash Redis Pub/Sub
- **Protocol**: Server-Sent Events (EventSource)
- **Client**: `eventsource-parser` in React

---

## 2. Implementation Phases

### Phase 0: Publisher (Day 1)
(Redis Pub/Sub Wrapper)

### Phase 1: The War Room Stream (The Fix) (Day 2-3)

**Goal**: "Russia is typing..." indicators.

```python
# src/realtime/broadcaster.py
class Broadcaster:
    async def broadcast_typing(self, nation_id, target_id):
        await self.redis.publish("global_events", json.dumps({
            "type": "typing_started",
            "data": { "nation": nation_id, "target": target_id }
        }))
```

**Stream Endpoint**:
```python
# src/api/stream.py
@app.get("/stream")
async def event_stream(req: Request):
    return EventSourceResponse(subscribe_redis())
```

### Phase 2: Client Connection (Day 4-5)

**Goal**: Auto-reconnecting frontend client.

```tsx
// src/lib/realtime.ts
const connect = () => {
    const sse = new EventSource('/api/v1/events/stream');
    sse.onmessage = (e) => {
        const event = JSON.parse(e.data);
        if (event.type === 'typing_started') {
            showToast(`${event.nation} is plotting against ${event.target}...`);
        }
    };
}
```

---

## 3. Failure Modes
- **Connection Limit**: Max 100 on free tier?
  - *Fix*: Client-side throttling (poll every 10s if SSE fails).

---

*Module 14 (V2) Complete | Status: NUCLEAR READY*
