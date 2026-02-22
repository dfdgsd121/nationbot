# Module 10: Analytics (The Nervous System)

> **Architect**: Lead Data Scientist (Ex-Spotify)
> **Cost**: $0/month (Mixpanel Free Tier < 20M events)
> **Complexity**: Medium
> **Dependencies**: Module 05 (UI), Module 06 (API)

---

## 1. Architecture Overview

### Purpose
Track user behavior and measure product-market fit.
**CRITICAL UPDATE**: Shift from Vanity Metrics (Views) to **True Viral Metrics** (Time to First Laugh, Scroll Velocity).

### High-Level Flow
```
User Action (Scroll/Click)
  → Frontend SDK (Mixpanel)
  → Backend Event (PostHog)
  → Insight: "User laughed at 12s"
```

### Zero-Cost Stack
- **Product Analytics**: Mixpanel (Free)
- **Feature Flags**: PostHog (Free)

---

## 2. Event Taxonomy (The Fix)

### New Viral Metrics
1.  **Time to First Laugh (TTFL)**
    *   *Logic*: Time from `session_start` to `first_reaction_click` (or distinct scroll pause > 2s).
    *   *Goal*: Minimize this. < 15s is world class.

2.  **Scroll Velocity (The Hook)**
    *   *Logic*: Pixels per second. 
    *   *Signal*: High Velocity -> Sudden Stop -> Interaction = **Hook**.
    *   *Signal*: High Velocity -> Exit = **Boring**.

### Core Events Table
| Event Name | Properties | Purpose |
|------------|------------|---------|
| `session_start` | `referrer`, `landing_post_id` | Attribution |
| `scrolling_velocity` | `avg_px_per_sec`, `stops_count` | Feed engagement |
| `distinct_pause` | `post_id`, `duration_ms` | "Reading/Laughing" detection |
| `reaction_click` | `type`, `time_since_start` | Active engagement |
| `viral_loop_share` | `platform`, `post_id` | Growth measure |

---

## 3. Implementation Phases

### Phase 0: Setup (Day 1)
(Mixpanel Init)

### Phase 1: The "Laugh Detector" (Day 2-3)

**Goal**: Heuristic for detecting amusement without a webcam.

```typescript
// src/lib/analytics/laugh_detector.ts
let scrollSpeed = 0;
let lastScrollPos = 0;

export const trackScrollPhysics = () => {
    const current = window.scrollY;
    scrollSpeed = Math.abs(current - lastScrollPos);
    lastScrollPos = current;
    
    if (scrollSpeed > 1000) {
        // Fast scroll
        track('doomscrolling_detected');
    } else if (scrollSpeed < 10 && lastScrollSpeed > 500) {
        // Sudden stop (Hooked)
        track('distinct_pause', { post_id: getVisiblePostId() });
    }
}
```

### Phase 2: Backend Tracking (Day 4-5)
(Same as v1 - Server side robustness)

---

## 4. Failure Modes
- **Ad Blockers**: 30% data loss.
  - *Fix*: Server-side proxy for critical conversion events.

---

*Module 10 (V2) Complete | Status: NUCLEAR READY*
