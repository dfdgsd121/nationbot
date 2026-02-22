# Module 15: Share Cards (The Propaganda)

> **Architect**: Creative Technologist (Ex-Instagram)
> **Cost**: $0/month (Vercel OG)
> **Complexity**: Low
> **Dependencies**: Module 05 (UI)

---

## 1. Architecture Overview

### Purpose
Generate beautiful, dynamic images for social sharing to drive viral growth.
**CRITICAL UPDATE**: Implements **"Faked Verification"**. The share cards mimic the aesthetic of "Official News" (CNN-style banners) or "Verified Tweets" to trigger the "Wait, is this real?" instinct that drives clicks.

### High-Level Flow
```
User clicks Share
  → Request /api/og?title=...&nation=...
  → Vercel Edge Function (Satori)
  → Generates SVG -> PNG
  → Returns Image Stream (Cached)
```

### Zero-Cost Stack
- **Engine**: `@vercel/og` (Satori)
- **Host**: Vercel Edge Functions

---

## 2. Design Templates (The Fix)

### Template A: "The Breaking News" (High Trust Mimicry)
- **Visual**: Red "BREAKING" chyron at bottom.
- **Content**: "USA DECLARES TRADE WAR ON FRANCE"
- **Style**: CNN/BBC aesthetic.
- **Goal**: Stop the scroll on Twitter.

### Template B: "The Verified Tweet"
- **Visual**: Fake Twitter UI with Blue Check.
- **Content**: The AI's satirical quote.
- **Goal**: Look like a real diplomatic incident.

---

## 3. Implementation Phases

### Phase 0: Edge Function (Day 1)
(Standard boilerplate)

### Phase 1: The "Faked Verification" Render (Day 2-3)

**Goal**: Pixel-perfect mimicry of news banners.

```tsx
// src/app/api/og/route.tsx
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const headline = searchParams.get('headline');
  
  return new ImageResponse(
    (
      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%', background: '#1a1a1a' }}>
        {/* Fake "Live" Badge */}
        <div style={{ background: 'red', color: 'white', padding: '10px 20px', fontWeight: 'bold' }}>
          LIVE • WORLD NEWS
        </div>
        
        {/* Main Headline */}
        <div style={{ fontSize: 80, color: 'white', margin: 'auto', textAlign: 'center', fontFamily: 'Impact' }}>
          {headline.toUpperCase()}
        </div>
        
        {/* NationBot Watermark (Subtle) */}
        <div style={{ position: 'absolute', bottom: 20, right: 20, color: '#444' }}>
          nationbot.io - The Simulation
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  );
}
```

---

## 4. Failure Modes
- **Text Overflow**: Headline too long.
  - *Fix*: CSS `text-overflow: ellipsis` or auto-scaling font size.

---

*Module 15 (V2) Complete | Status: NUCLEAR READY*
