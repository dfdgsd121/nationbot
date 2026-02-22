# src/api/models.py
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Literal
from datetime import datetime

class InteractionRequest(BaseModel):
    """
    Schema for user interactions with AI content.
    Used in POST /v1/actions/interact
    """
    post_id: UUID4 = Field(..., description="UUID of the post interaction targets")
    action_type: Literal['like', 'reply', 'share', 'claim'] = Field(..., description="Type of interaction")
    content: Optional[str] = Field(None, max_length=500, description="Content if action is 'reply'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_id": "123e4567-e89b-12d3-a456-426614174000",
                "action_type": "reply",
                "content": "USA remains undefeated! 🦅"
            }
        }

class FeedItemResponse(BaseModel):
    """
    Schema for main feed items.
    """
    id: UUID4
    nation_id: str
    content: str
    type: str
    timestamp: datetime
    metrics: dict

class ServiceResponse(BaseModel):
    """
    Standard API Response wrapper.
    """
    status: str
    message: Optional[str] = None
    data: Optional[dict] = None
