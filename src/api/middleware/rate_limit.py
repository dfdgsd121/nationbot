# src/api/middleware/rate_limit.py
import time
from fastapi import Request, HTTPException
import redis.asyncio as redis
import os

# Connect to Redis (Upstash)
# In prod, UPSTASH_REDIS_REST_URL is used
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class RateLimitMiddleware:
    """
    Zero-Cost Rate Limiter using Redis.
    Limits requests per IP to protect Free Tier resources.
    """
    
    RATE_LIMIT_PER_MINUTE = 60 # 1 req/sec per IP
    
    async def __call__(self, request: Request, call_next):
        # 1. Identify Client
        client_ip = request.client.host if request.client else "unknown"
        
        # 2. Key Construction
        # rate_limit:127.0.0.1:17000000 (minute bucket)
        current_minute = int(time.time() // 60)
        key = f"rate_limit:{client_ip}:{current_minute}"
        
        # 3. Check & Increment (Atomic)
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, 90) # Expire slightly after minute ends
            results = await pipe.execute()
            
        request_count = results[0]
        
        # 4. Enforce Limit
        if request_count > self.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Slow down your diplomacy."
            )
            
        # 5. Process Request
        response = await call_next(request)
        
        # Add headers for visibility
        response.headers["X-RateLimit-Limit"] = str(self.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.RATE_LIMIT_PER_MINUTE - request_count))
        
        return response
