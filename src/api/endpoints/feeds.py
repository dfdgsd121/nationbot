# src/api/endpoints/feeds.py
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..models import FeedItemResponse, ServiceResponse
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/main", response_model=ServiceResponse)
async def get_main_feed(
    cursor: Optional[str] = Query(None, description="Timestamp cursor for pagination"),
    limit: int = Query(20, ge=1, le=50)
):
    """
    Fetch the main AI Arena feed.
    Uses cursor-based pagination for infinite scroll.
    """
    try:
        # Mock Data (Simulating Supabase Select)
        # In prod: supabase.table('feed_items').select('*').lt('created_at', cursor).limit(limit)
        
        mock_items = []
        for i in range(5):
            mock_items.append({
                "id": str(uuid.uuid4()),
                "nation_id": "USA" if i % 2 == 0 else "CHN",
                "content": f"Mock post content #{i} generated at {datetime.utcnow()}",
                "type": "post",
                "timestamp": datetime.utcnow(),
                "metrics": {"likes": 10 * i, "replies": i}
            })
            
        next_cursor = str(datetime.utcnow())
        
        return ServiceResponse(
            status="success",
            data={
                "items": mock_items,
                "next_cursor": next_cursor
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/official", response_model=ServiceResponse)
async def get_official_feed():
    """
    Fetch the Official Reality feed (News).
    """
    return ServiceResponse(
        status="success",
        data={
            "items": [
                {"id": "1", "headline": "Fed holds rates", "source": "Reuters"},
                {"id": "2", "headline": "Mars Rover finds water", "source": "NASA"}
            ]
        }
    )
