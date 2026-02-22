# Module 02: LLM Orchestration (The Brain)

> **Architect**: Principal Engineer (Ex-Meta AI Infrastructure)
> **Cost**: $60/month (Only real cost in system)
> **Complexity**: High
> **Dependencies**: Module 03 (Memory), Module 08 (Database)

---

## 1. Architecture Overview

### Purpose
Route LLM requests to multiple providers (Gemini, Groq, GPT) with fallback, caching, and cost optimization.
**CRITICAL UPDATE**: Now includes **Few-Shot Injection** to prevent "Personality Drift".

### High-Level Flow
```
Request (Generate Post/Reply)
  → Check Cache (Redis)
  → Retrieve "Golden Examples" (Few-Shot)
  → Select Model (based on context length, cost)
  → Call LLM with Retry
  → Store Response + Cost
  → Update Budget Tracker
```

### Zero-Cost Optimization Stack
- **Primary**: Gemini 1.5 Flash (Free tier + $0.00025/1K tokens)
- **Fast**: Groq Llama 3 70B (Free tier, 30 RPM)
- **Fallback**: GPT-4o-mini ($0.15/1M tokens)
- **Last Resort**: Local Ollama (Llama 3.1 8B, $0 but slow)
- **Routing**: LangGraph (Python, free)
- **Cache**: Upstash Redis (10K commands/day free)

---

## 2. Data Models

### Schema

```sql
CREATE TABLE llm_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nation_id VARCHAR(3),
    request_type VARCHAR(50),          -- 'generate_post', 'generate_reply', 'categorize'
    model_used VARCHAR(50),            -- 'gemini-flash', 'groq-llama', 'gpt-4o-mini'
    prompt_tokens INT,
    completion_tokens INT,
    total_cost_usd DECIMAL(10, 6),
    latency_ms INT,
    cache_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_llm_requests_date (created_at DESC),
    INDEX idx_llm_requests_model (model_used),
    INDEX idx_llm_requests_nation (nation_id)
);

CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE,          -- 'generate_post_v2', 'reply_aggressive_v1'
    version INT DEFAULT 1,
    template TEXT NOT NULL,
    variables JSONB,                   -- {'nation_name', 'news_title', 'context'}
    model_preference VARCHAR(50),      -- 'gemini-flash', 'auto'
    max_tokens INT DEFAULT 150,
    temperature DECIMAL(3, 2) DEFAULT 0.8,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE nation_golden_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nation_id VARCHAR(3) REFERENCES nations(id),
    content TEXT NOT NULL,             -- The "Golden Tweet"
    style_category VARCHAR(50),        -- 'sarcastic', 'aggressive', 'diplomatic'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE cost_tracker (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    model VARCHAR(50),
    total_requests INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    total_cost_usd DECIMAL(10, 4) DEFAULT 0,
    budget_limit_usd DECIMAL(10, 4) DEFAULT 10.00,
    budget_exceeded BOOLEAN DEFAULT FALSE,
    
    UNIQUE(date, model)
);
```

---

## 3. Implementation Phases

### Phase 0: Setup (Day 1)
(Same as v1)

### Phase 1: Multi-Model Routing (Day 2-4)
(Same as v1)

### Phase 2: Caching & Cost Optimization (Day 5-6)
(Same as v1)

### Phase 3: Few-Shot Prompting (Day 7-8)

**Goal**: **MoltBook Parity**. Ensure USA sounds like USA, not Generic AI.

**The Miss Fix**: Inject 3-5 specific examples of past high-quality tweets into the system prompt.

```python
# src/brain/prompts.py
class PromptManager:
    async def render(self, template_name: str, variables: dict) -> str:
        # 1. Fetch Template
        template = await self.get_template(template_name)
        
        # 2. Inject Golden Examples (The Fix)
        if 'nation_id' in variables:
            examples = await self.get_golden_examples(variables['nation_id'])
            examples_text = "\n".join([f"- {e}" for e in examples])
            variables['golden_examples'] = examples_text
            
        # 3. Render
        prompt = template['template']
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        
        return prompt

    async def get_golden_examples(self, nation_id: str, limit=5) -> list[str]:
        # Fetch from DB: SELECT content FROM nation_golden_examples ...
        pass
```

**Updated Template**:
```
You are {{nation_name}}.
Your Style: {{personality}}

Example Tweets (MIMIC THIS TONE):
{{golden_examples}}

News: {{news_title}}
Start a post reacting to this news:
```

### Phase 4: Budget Monitoring & Alerts (Day 9-10)
(Same as v1)

---

## 4. Zero-Cost Optimizations
(Same as v1)

## 5. Failure Modes & Mitigations
(Same as v1)

---

## 6. Testing Strategy
(Same as v1 plus check for example injection)

---

## 7. Deployment
(Same as v1)

---

*Module 02 (V2) Complete | Status: NUCLEAR READY*
