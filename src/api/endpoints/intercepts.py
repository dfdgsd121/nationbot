# src/api/endpoints/intercepts.py
import logging
from fastapi import APIRouter
from src.drama.intercepts import InterceptGenerator

router = APIRouter()
logger = logging.getLogger("api.intercepts")

# In a real app, we'd inject this dependency
generator = InterceptGenerator()

@router.get("/")
async def get_intercepts():
    """
    Returns the list of active intercepted messages.
    Automatically applies 'Redaction Logic' based on timestamps.
    """
    # Mock retrieving from DB
    # In prod: intercepts = await repository.get_all_active()
    
    # Simulating a mixed list (one active, one revealed)
    mock_intercepts = [
        # Message 1: Still Encrypted
        await generator.create_daily_intercept("US", "CN"),
        
        # Message 2: Revealed (Simulated by hacking the timestamp)
        {
            **(await generator.create_daily_intercept("RU", "GB")),
            # Hack: Reveal happened 1 hour ago
            "reveal_at": (await generator.create_daily_intercept("RU", "GB"))["created_at"]
        }
    ]
    
    # Transform for view
    view_models = [generator.get_viewable_content(msg) for msg in mock_intercepts]
    
    return {
        "status": "success",
        "count": len(view_models),
        "data": view_models
    }
