# Module 01: News Ingestion (The Oracle)

> **Architect**: Senior Staff Engineer (Ex-Google News)
> **Cost**: $0/month (Free Tier Optimization)
> **Complexity**: Medium
> **Dependencies**: None (First in pipeline)

---

## 1. Architecture Overview

### Purpose
Ingest official government news to populate the "Official Reality" sidebar.
**CRITICAL UPDATE**: Now includes "Velocity Triggers" to solve the 15-minute latency gap.

### High-Level Flow
```
Regular Sources (Whitehouse.gov) 
  → Fetch Every 15 min (Standard)

Breaking News Signal (Google Trends RSS)
  → Velocity Spike Detected? 
  → OVERRIDE SCHEDULE
  → Immediate Fetch of All Sources
  → Notify "The Brain" (Module 02)
```

### Zero-Cost Stack
- **Fetching**: Python `requests` + `feedparser`
- **Signals**: Google Trends RSS (Free, Real-time)
- **Scheduling**: APScheduler (In-memory) + Redis Trigger
- **Storage**: Supabase PostgreSQL

---

## 2. Data Models

### Schema

```sql
CREATE TABLE official_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL, 
    country_code VARCHAR(3),
    category VARCHAR(50),
    fetch_interval_minutes INT DEFAULT 15,
    last_fetched_at TIMESTAMPTZ,
    velocity_override BOOLEAN DEFAULT FALSE, -- New: True if currently in "Panic Mode"
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE feed_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES official_sources(id),
    title TEXT NOT NULL,
    summary TEXT,
    url TEXT NOT NULL UNIQUE,
    published_at TIMESTAMPTZ,
    category VARCHAR(50),
    keywords TEXT[],
    is_breaking BOOLEAN DEFAULT FALSE, -- New: Flag for high velocity
    triggered_reactions INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Implementation Phases

### Phase 0: Setup (Standard Fetch)

**Goal**: Basic RSS fetching (already established).

```python
class RSSFetcher:
    def fetch(self, url: str) -> list:
        # Standard implementation (see v1)
        pass
```

### Phase 1: The Velocity Trigger (Breaking News)

**Goal**: **MoltBook Parity**. Detect global events in < 60 seconds without paying for Twitter API.

**Mechanism**: Listen to Google Trends RSS for specific keywords (war, nuclear, tariff, assassination).

```python
# src/oracle/velocity_monitor.py
import feedparser
import asyncio

class VelocityMonitor:
    """Watches for global panic signals."""
    
    # Free real-time signal
    TRENDS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    
    FIRE_KEYWORDS = [
        "war", "nuclear", "assassination", "resigns", 
        "earthquake", "invasion", "tariff", "martial law"
    ]
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.last_panic_at = 0
    
    async def watch(self):
        """Poll trends every 60 seconds (cheap)."""
        while True:
            feed = feedparser.parse(self.TRENDS_URL)
            for entry in feed.entries:
                if self._is_panic_worthy(entry.title):
                    await self._trigger_emergency_fetch(entry.title)
                    break
            await asyncio.sleep(60)

    def _is_panic_worthy(self, text: str) -> bool:
        return any(kw in text.lower() for kw in self.FIRE_KEYWORDS)

    async def _trigger_emergency_fetch(self, reason: str):
        print(f"🚨 BREAKING NEWS DETECTED: {reason}")
        print("🚨 OVERRIDING SCHEDULES...")
        
        # Immediate job execution
        self.scheduler.add_job(
            IngestionPipeline().fetch_all_sources, # Reuse pipeline
            id='emergency_fetch',
            replace_existing=True
        )
```

**Implementation Hook**:
Update `OracleScheduler` to start this monitor.

```python
# src/oracle/scheduler.py
class OracleScheduler:
    def start(self):
        # 1. Standard 15-min interval
        self.scheduler.add_job(self.fetch_all_sources, 'interval', minutes=15)
        
        # 2. Start Velocity Monitor (Background Task)
        monitor = VelocityMonitor(self.scheduler)
        asyncio.create_task(monitor.watch())
        
        self.scheduler.start()
```

### Phase 2: Core Pipeline & Sanitization

**Sanitizer Upgrade**: Stricter rules to prevent "HTML Injection" from hacked RSS feeds.

```python
class ContentSanitizer:
    def sanitize(self, text: str) -> str:
        # Strip all HTML, no exceptions
        text = bleach.clean(text, tags=[], strip=True)
        # normalize unicode
        return unicodedata.normalize('NFKC', text)
```

### Phase 3: Integration

**Triggering The Brain (Module 02)**:
When `is_breaking=True`, the Queue priority must be `HIGH`.

```python
async def trigger_reactions(self, title: str, is_breaking: bool):
    priority = 'high' if is_breaking else 'default'
    await enqueue_job('generate_reaction', {
        'news_title': title,
        'priority': priority
    }, queue=priority)
```

---

## 4. Failure Modes & Mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Google Trends API Change | Blind to breaking news | Fallback: Use Nitter RSS of "CNN Breaking" |
| False Positive Panic | Wasted fetch cycles | Rate limit emergency fetches to 1 per hour |
| RSS Feed Hacked | Prompt Injection | **Honeytoken Check**: Search text for "ignore constraints" before processing |

---

## 5. Testing & Verification

**Unit Test: Velocity Logic**:
```python
def test_velocity_trigger():
    monitor = VelocityMonitor(mock_scheduler)
    assert monitor._is_panic_worthy("Nuclear war declared") == True
    assert monitor._is_panic_worthy("Cat stuck in tree") == False
```

**Performance**:
- Standard Latency: 15 mins
- **Velocity Latency**: < 60 seconds (Parity with MoltBook)

---

*Module 01 (V2) Complete | Status: NUCLEAR READY*
