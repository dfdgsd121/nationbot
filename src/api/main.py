# src/api/main.py
"""
NationBot API Gateway v3 (Hardened)
====================================
FastAPI app with CORS, request timing middleware, and structured routing.
"""
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("nationbot.api")

app = FastAPI(
    title="NationBot API",
    description="The Voice of the System. Geopolitical AI Chaos Simulator.",
    version="3.0.0",
)

import os

# CORS — configurable via CORS_ORIGINS env var (comma-separated)
_cors_env = os.getenv("CORS_ORIGINS", "*")
_cors_origins = ["*"] if _cors_env == "*" else [o.strip() for o in _cors_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MIDDLEWARE: Request Timing + Error Handling
# ============================================================================
REQUEST_METRICS = {
    "total": 0,
    "errors_4xx": 0,
    "errors_5xx": 0,
    "latency_samples": [],
}


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    REQUEST_METRICS["total"] += 1

    try:
        response = await call_next(request)
    except Exception as e:
        REQUEST_METRICS["errors_5xx"] += 1
        logger.error(f"Unhandled error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)},
        )

    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time"] = f"{elapsed_ms:.0f}ms"

    # Track latency (last 200 samples)
    REQUEST_METRICS["latency_samples"].append(elapsed_ms)
    REQUEST_METRICS["latency_samples"] = REQUEST_METRICS["latency_samples"][-200:]

    if response.status_code >= 500:
        REQUEST_METRICS["errors_5xx"] += 1
    elif response.status_code >= 400:
        REQUEST_METRICS["errors_4xx"] += 1

    return response


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": "nationbot-api",
        "version": "3.0.0",
    }


@app.get("/")
async def root():
    return {"message": "NationBot API", "docs": "/docs", "version": "3.0.0"}


@app.get("/metrics")
async def metrics():
    """Expose request-level metrics for observability (Gate E)"""
    samples = REQUEST_METRICS["latency_samples"]
    sorted_samples = sorted(samples) if samples else [0]
    return {
        "total_requests": REQUEST_METRICS["total"],
        "errors_4xx": REQUEST_METRICS["errors_4xx"],
        "errors_5xx": REQUEST_METRICS["errors_5xx"],
        "latency": {
            "p50_ms": sorted_samples[len(sorted_samples) // 2],
            "p95_ms": sorted_samples[int(len(sorted_samples) * 0.95)] if len(sorted_samples) > 1 else sorted_samples[0],
            "p99_ms": sorted_samples[int(len(sorted_samples) * 0.99)] if len(sorted_samples) > 1 else sorted_samples[0],
            "samples": len(samples),
        },
    }


# ============================================================================
# ROUTER REGISTRATION (fail-safe)
# ============================================================================
def _load_router(module_name, prefix, tags):
    try:
        from importlib import import_module
        mod = import_module(f".endpoints.{module_name}", package="src.api")
        app.include_router(mod.router, prefix=prefix, tags=tags)
        logger.info(f"✅ Loaded router: {prefix}")
    except Exception as e:
        logger.warning(f"⚠️ Could not load {module_name}: {e}")


_load_router("generate", "/v1/generate", ["Generate"])
_load_router("stream", "/v1/stream", ["Stream"])
_load_router("intercepts", "/v1/intercepts", ["Intercepts"])
_load_router("actions", "/v1/actions", ["Actions"])
_load_router("auth_endpoints", "/v1/auth", ["Auth"])
_load_router("admin", "/v1/admin", ["Admin"])


# ============================================================================
# LIFECYCLE: Auto-start the autonomous loop
# ============================================================================
@app.on_event("startup")
async def on_startup():
    """Start the autonomous nation loop when the server boots."""
    try:
        from src.agent.db import init_db
        init_db()
        # Load persisted posts into in-memory store
        from src.api.endpoints.generate import _load_posts_from_db
        _load_posts_from_db()
        from src.agent.autonomous_loop import autonomous_loop
        autonomous_loop.start()
        logger.info("🚀 Autonomous loop auto-started")
    except Exception as e:
        logger.warning(f"⚠️ Could not auto-start autonomous loop: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    """Gracefully stop the loop."""
    try:
        from src.agent.autonomous_loop import autonomous_loop
        autonomous_loop.stop()
    except Exception:
        pass

