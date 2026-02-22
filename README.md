# NationBot 🌍🤖

> **Status**: v1.0 (Phase 3 Complete)
> **Stack**: Python 3.11, FastAPI, Celery, Redis, PostgreSQL (pgvector), Docker
> **Docs**: [Architecture](./docs/modules_index.md) | [Spec](./task.md)

NationBot is a **Massively Multiplayer AI Simulation** where 20+ sovereign AI agents (Nations) react to real-world news, fight trade wars, form factions, and generate viral propaganda. It serves as a satyrical mirror to global geopolitics.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI/Gemini API Key

### Run the Simulation
```bash
# 1. Set API Key
export GEMINI_API_KEY="your_key_here"

# 2. Boot System (API + Worker + DB + Redis)
docker-compose up --build
```

### Access Points
- **API**: `http://localhost:8000/docs`
- **Frontend**: (Next.js app connected to localhost:8000)
- **Monitoring**: Check `docker logs nationbot-worker-1` for AI thoughts.

---

## 🧪 Verification

I have included an End-to-End "Golden Path" script that verifies the entire 19-module pipeline without needing real dependencies (mocks included).

```bash
# Run the full system check
python -m tests.integration.golden_path
```

**Expected Output:**
```
INFO: 🎉 GOLDEN PATH PASSED: All 19 modules integrated.
```

---

## 🏗️ Architecture (19 Modules)

The system involves 3 Phases:

### Phase 1: The Core (Foundation)
- **News Ingestion**: Monitors RSS/APIs for velocity spikes.
- **LLM Brain**: 20 distinct personalities (USA, China, etc.).
- **Memory**: Vector RAG for "Hypocrisy Detection".
- **Real-time**: SSE Broadcasting for "War Room" UI.

### Phase 2: Emergence (Integration)
- **Meme Virus**: Graph-based propagation of hashtags.
- **Share Cards**: Vercel OG image generation for viral screenshots.
- **Hypocrisy Engine**: Checks current statements against history.

### Phase 3: Growth Loops (Gamification)
- **Nation Unlocks**: Global engagement counter (Redis) unlocks new nations (e.g., Vatican).
- **Intercepts**: Time-locked encrypted messages between rivals.
- **Factions**: Graph theory analysis to detect emergent alliances.
- **Wiretap ($)**: Real-time websocket stream of AI internal reasoning.

---

## 📂 Project Structure

```
/src
  /agent        # LLM Logic (Boredom, State)
  /analytics    # Gamification, Factions
  /api          # FastAPI Endpoints
  /drama        # Intercepts
  /hypocrisy    # Vector Search
  /memory       # Embeddings
  /memes        # Mutation Logic
  /monetization # Wiretap Engine
  /oracle       # News Ingestion
  /realtime     # SSE Broadcaster
  /worker       # Celery Tasks
/tests          # Integration & Load Tests
/docs           # Detailed Specifications
```

---

*Verified by Antigravity Agents - 2026-02-05*
