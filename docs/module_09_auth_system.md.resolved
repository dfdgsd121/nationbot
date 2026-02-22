# Module 09: Auth System (The Gatekeeper)

> **Architect**: Senior Security Engineer (Ex-Auth0)
> **Cost**: $0/month (Supabase Auth - 50K MAU free)
> **Complexity**: Medium
> **Dependencies**: Module 05 (UI), Module 06 (API)

---

## 1. Architecture Overview

### Purpose
Manage user identity, sessions, and permissions.
**CRITICAL UPDATE**: Implements **"Lazy Auth"** (Guest Mode). Users can Vote/Like/Reply *without* logging in (actions stored in LocalStorage/Session). Login is only forced for "claiming" a nation or after 3 interactions to "Save Progress".

### High-Level Flow
```
User (Guest)
  → Click "Like" 
  → UI Optimistically Updates (Store in LocalStorage)
  → API Accepts (Rate Limited by IP)
  
User (Guest) -> 3rd Action
  → "Sign up to save your influence!" Modal
  → Convert Guest -> User (Supabase Auth)
  → Sync Local Actions to DB
```

### Zero-Cost Stack
- **Provider**: Supabase Auth (GoTrue)
- **Methods**: Email/Password + OAuth (Google, GitHub)
- **Session**: JWT (Stateless)

---

## 2. Implementation Phases

### Phase 0: Setup (Day 1)
(Standard Supabase Config - Email/Google)

### Phase 1: The "Lazy Auth" Backend (The Fix) (Day 2-3)

**Goal**: Allow unauthenticated requests for low-stakes actions.

**API Dependency**:
```python
# src/api/auth.py
async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        # Return Guest User (Identified by IP/Fingerprint in real app, or just None)
        return GuestUser(is_authenticated=False)
        
    # Validation logic...
    return AuthenticatedUser(...)
```

**Endpoint Logic**:
```python
@router.post("/interact")
async def interact(req: InteractionRequest, user = Depends(get_optional_user)):
    if not user.is_authenticated and req.action_type == 'claim':
         raise HTTPException(401, "Login required to claim nations.")
         
    # Allow Likes/Replies for guests (Rate limited elsewhere)
    dispatch_job(...)
```

### Phase 2: Frontend "Soft Wall" (Day 4-5)

**Goal**: Track local actions and prompt login at threshold.

**Client Logic**:
```typescript
// useGuestActions.ts
const performAction = (action) => {
   if (!user) {
      const actions = getLocalActions();
      if (actions.length >= 3) {
          triggerLoginModal("You're on fire! Sign up to make it count.");
          return;
      }
      saveLocalAction(action);
   }
   api.send(action);
}
```

---

## 4. Failure Modes & Mitigations
- **Guest Spam**: Botnet mimics guests.
  - *Fix*: Strict IP rate limiting (Module 06).
- **Sync Fail**: User logs in, local actions lost.
  - *Fix*: Send local history array on `POST /auth/sync`.

---

*Module 09 (V2) Complete | Status: NUCLEAR READY*
