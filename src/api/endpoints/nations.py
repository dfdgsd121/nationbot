# src/api/endpoints/nations.py
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any
from ..models import ServiceResponse
import random # Mock data generation

router = APIRouter()

VALID_NATIONS = ["USA", "CHN", "FRA", "DEU", "RUS", "GBR"]

@router.get("/{nation_id}/profile", response_model=ServiceResponse)
async def get_nation_profile(
    nation_id: str = Path(..., min_length=3, max_length=3, description="ISO-3 Country Code")
):
    """
    Get public profile and current mood of a nation.
    """
    nid = nation_id.upper()
    if nid not in VALID_NATIONS:
        raise HTTPException(status_code=404, detail="Nation not found")
        
    # Mock Data (In prod: Fetch from NationState DB)
    return ServiceResponse(
        status="success",
        data={
            "id": nid,
            "name": f"Nation of {nid}",
            "mood": random.choice(["aggressive", "diplomatic", "happy", "cautious"]),
            "avatar_url": f"https://avatars.nationbot.io/{nid}.png",
            "bio": "A global superpower managing its debt ceiling and ego.",
            "joined_at": "2025-01-01T00:00:00Z"
        }
    )

@router.get("/{nation_id}/stats", response_model=ServiceResponse)
async def get_nation_stats(
    nation_id: str = Path(..., min_length=3, max_length=3)
):
    """
    Get live game stats (Leaderboard metrics).
    """
    nid = nation_id.upper()
    if nid not in VALID_NATIONS:
        raise HTTPException(status_code=404, detail="Nation not found")

    return ServiceResponse(
        status="success",
        data={
            "gdp": random.randint(20000, 80000),
            "stability": random.randint(10, 100),
            "influence_score": random.randint(1000, 9999),
            "rank": random.randint(1, 10)
        }
    )
