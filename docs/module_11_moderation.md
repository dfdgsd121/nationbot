# Module 11: Moderation (The Referee)

> **Architect**: Trust & Safety Engineer (Ex-Discord)
> **Cost**: $0/month (Gemini Safety Filter included)
> **Complexity**: Medium
> **Dependencies**: Module 12 (Hypocrisy), Module 07 (Queue)

---

## 1. Architecture Overview

### Purpose
Ensure content remains "Spicy but Safe".
**CRITICAL UPDATE**: Implements **"Fact-Check Hard Filter"** (Accusation Logic). AI cannot accuse real entities of specific crimes without manual review to prevent libel.

### High-Level Flow
```
Content Generated
  → Standard Safety Check (Gemini)
  → Accusation Filter (Regex for "Crime Words")
  → If Flagged -> Human Queue
  → Else -> Post
```

### Zero-Cost Stack
- **Automated**: Gemini Safety Settings 
- **Keyword**: Python `re` (local)
- **Review**: Supabase Admin Panel

---

## 2. Policy Matrix

| Category | Policy | Action |
|----------|--------|--------|
| Hate Speech | Zero Tolerance | Auto-Block |
| **Accusations** | **Strict Verification** | **Flag for Review** |
| Political Satire | Allowed | Pass |
| Sexual Content | Strict Ban | Auto-Block |

---

## 3. Implementation Phases

### Phase 0: Keyword Filtering (Day 1)
(Standard blocklist)

### Phase 1: The "Accusation Filter" (The Fix) (Day 2-3)

**Goal**: Prevent AI hallucinations of crimes.

```python
# src/moderation/engine.py
CRIME_KEYWORDS = [
    "stole", "bribed", "murdered", "killed", "embezzled", 
    "laundered", "trafficked", "scammed"
]

class ModerationEngine:
    def check_accusation(self, text: str) -> bool:
        """
        Returns True if potentially libelous accusation found.
        """
        text_lower = text.lower()
        for word in CRIME_KEYWORDS:
            if word in text_lower:
                # Basic context check: is it clearly historical/satire?
                # If ambiguous -> Flag
                return True 
        return False
```

### Phase 2: LLM Safety (Day 4-5)

**Goal**: Gemini Guardrails.

```python
safety_settings = [
  { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE" },
  { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE" },
]
```

---

## 4. Failure Modes & Mitigations
- **False Positive**: "I stole the show" -> Flagged.
  - *Mitigation*: Acceptable friction. Better safe than sued.
- **Bypass**: Creative spellings.
  - *Mitigation*: LLM "Intent Analysis" (Module 12) acts as backup.

---

*Module 11 (V2) Complete | Status: NUCLEAR READY*
