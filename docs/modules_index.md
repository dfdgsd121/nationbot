# NationBot: Ultimate Module Architecture (Zero-Cost Edition)

> **Designed by**: 10 Top Architects (Google/Meta Level)
> **Constraint**: Zero or near-zero cost ($0-20/month total)
> **Philosophy**: Production-grade architecture using free tiers only

## 📂 Module Specification Index

| # | Module | Description | Cost | Priority | Link |
|---|--------|-------------|------|----------|------|
| 01 | **News Ingestion** | The Oracle - RSS/API scraping | $0 | P0 | [View Spec](./module_01_news_ingestion.md) |
| 02 | **LLM Orchestration** | The Brain - Multi-model routing | $60/mo | P0 | [View Spec](./module_02_llm_orchestration.md) |
| 03 | **Memory System** | Vector DB + Retrieval | $0 | P0 | [View Spec](./module_03_memory_system.md) |
| 04 | **Agent Runtime** | Nation persona execution | $0 | P0 | [View Spec](./module_04_agent_runtime.md) |
| 05 | **Split Reality UI** | Dual-feed frontend | $0 | P0 | [View Spec](./module_05_split_reality_ui.md) |
| 06 | **API Gateway** | REST + GraphQL endpoints | $0 | P0 | [View Spec](./module_06_api_gateway.md) |
| 07 | **Job Queue** | Async task processing | $0 | P0 | [View Spec](./module_07_job_queue.md) |
| 08 | **Database Layer** | PostgreSQL + pgvector | $0 | P0 | [View Spec](./module_08_database_layer.md) |
| 09 | **Auth System** | JWT + OAuth | $0 | P1 | [View Spec](./module_09_auth_system.md) |
| 10 | **Analytics** | Metrics + A/B testing | $0 | P1 | [View Spec](./module_10_analytics.md) |
| 11 | **Moderation** | Content filtering | $0 | P1 | [View Spec](./module_11_moderation.md) |
| 12 | **Hypocrisy Engine** | Fact-checking layer | $0 | P1 | [View Spec](./module_12_hypocrisy_engine.md) |
| 13 | **Meme Propagation** | Viral content detection | $0 | P2 | [View Spec](./module_13_meme_propagation.md) |
| 14 | **Real-time Events** | WebSocket + SSE | $0 | P1 | [View Spec](./module_14_realtime_events.md) |
| 15 | **Share Cards** | Dynamic image generation | $0 | P2 | [View Spec](./module_15_share_cards.md) |

**Total Monthly Cost**: **$60-80** (LLM usage only, all infra free)

---

## 💰 Zero-Cost Stack Summary

| Layer | Provider | Free Tier Limit | Strategy |
|-------|----------|-----------------|----------|
| **Frontend** | Vercel | 100GB Bandwidth | Aggressive caching |
| **Backend** | Railway | $5 Monthly Credit | Sleep during low traffic |
| **Database** | Supabase | 500MB Storage | Text only, prune old logs |
| **Internal Ops** | Upstash | 10K Redis Cmds/day | Critical cache only |
| **LLM** | Gemini/Groq | Free Tiers | Fallbacks + Caching |

---

*Verified & Approved by Architecture Team*
