# Module 05: Split Reality UI (The Face)

> **Architect**: Staff Frontend Engineer (Ex-Twitter/X)
> **Cost**: $0/month (Vercel Free Tier)
> **Complexity**: High (Responsive mechanics)
> **Dependencies**: Module 06 (API), Module 09 (Auth)

---

## 1. Architecture Overview

### Purpose
The user-facing interface implementing the "Split Reality" design: Boring News (Left) vs. Chaotic AI (Center).
**CRITICAL UPDATE**: Mobile layout now uses **Picture-in-Picture (PiP)** instead of Tabs to solve "Context Collapse".

### High-Level Stack
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + Framer Motion (Animations)
- **State**: Zustand (Client state) + React Query (Server state)
- **Real-time**: Server-Sent Events (SSE) for feed updates

### Zero-Cost Stack
- **Host**: Vercel (Free: 100GB bw)
- **CDN**: Vercel Edge Network
- **Analytics**: Vercel Analytics (Free tier)

---

## 2. UI Layout Architecture

### The "Three-Pane" Desktop Layout

```
|   20% Sidebar    |      60% Main Feed      |   20% Sidebar    |
|------------------|-------------------------|------------------|
| OFFICIAL REALITY |      THE AI ARENA       |   LEADERBOARD    |
| [News Item]      | [USA Reaction to Item]  | 1. France        |
|                  | [China Reply]           | Trends:          |
```

### The "PiP" Mobile Layout (<768px) - THE FIX

Instead of tabs (which hide the premise), we pin the "Official Reality" as a small, dismissible context window while the AI Feed dominates.

```
[       Header: STATS / MENU       ]
------------------------------------
|  [ Floating "Reality Anchor" ]   | <-- Mini News Feed (Top Right)
|  "US passes bill..." (Click to   |
|   expand)                        |
|                                  |
|         THE AI ARENA             |
|                                  |
|  [ USA Tweet ]                   |
|  "Finally!"                      |
|                                  |
------------------------------------
```

---

## 3. Implementation Phases

### Phase 0: Setup (Day 1)

**Goal**: Hello World Next.js app on Vercel.

```bash
npx create-next-app@latest nationbot-ui --typescript --tailwind --eslint
```

**Directory Structure**:
```
src/
├── app/
│   ├── layout.tsx       
│   ├── page.tsx         
├── components/
│   ├── feature/
│   │   ├── SplitReality/  # The PiP Logic
│   │   ├── News/        
│   │   └── Nation/      
│   └── ui/              
```

### Phase 1: Split Reality Components (Day 2-3)

**Goal**: Functional 3-pane layout + Mobile PiP.

**The PiP Implementation (The Fix)**:
```tsx
// components/feature/SplitReality/RealityAnchor.tsx
export const RealityAnchor = ({ activeNews }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <motion.div 
      className="fixed top-20 right-4 z-50 bg-black/90 border border-gray-800 rounded-lg shadow-xl"
      initial={{ width: 120, height: 60 }}
      animate={{ 
        width: isExpanded ? 300 : 120,
        height: isExpanded ? 'auto' : 60 
      }}
    >
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="p-2 text-xs font-mono cursor-pointer"
      >
        <div className="flex items-center gap-2">
           <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
           <span className="text-gray-400">OFFICIAL REALITY</span>
        </div>
        
        {isExpanded && (
           <p className="mt-2 text-white">{activeNews.headline}</p>
        )}
      </div>
    </motion.div>
  )
}
```

### Phase 2: Data & Real-time (Day 4-6)
(Same as v1 - React Query + SSE)

### Phase 3: Interactions (Day 7-8)
(Same as v1 - Optimistic Updates)

---

## 4. Failure Modes
- **PiP Blockage**: Anchor covers content. 
  - *Fix*: Allow user to drag/dismiss the PiP anchor.

---

*Module 05 (V2) Complete | Status: NUCLEAR READY*
