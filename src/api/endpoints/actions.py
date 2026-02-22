# src/api/endpoints/actions.py
import logging
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from ..models import InteractionRequest, ServiceResponse

logger = logging.getLogger("api.actions")
router = APIRouter()

# Mock Job Queue Interface (Module 07 Placeholder)
async def enqueue_agent_job(job_type: str, payload: dict):
    """
    Placeholder for Module 07 RabbitMQ/Redis producer.
    In prod, this pushes to the queue.
    """
    job_id = str(uuid.uuid4())
    logger.info(f"Checking Job Queue... [MOCK] Enqueued {job_type}: {job_id}")
    return job_id

@router.post("/interact", status_code=status.HTTP_202_ACCEPTED, response_model=ServiceResponse)
async def interact(
    request: InteractionRequest,
    background_tasks: BackgroundTasks
):
    """
    Handle user interactions (Like, Reply, Claim).
    NON-BLOCKING: Returns 202 Accepted immediately.
    """
    try:
        # Validate logic (e.g. valid post_id) would happen here or in middleware
        
        # Dispatch to Job Queue (Async)
        # We use BackgroundTasks for simple in-process async or the proper Queue wrapper
        # Here we simulate the Queue dispatch
        job_id = await enqueue_agent_job(
            job_type="process_interaction",
            payload={
                "post_id": str(request.post_id),
                "action": request.action_type,
                "content": request.content,
                "timestamp": str(uuid.uuid1()) # Mock time
            }
        )
        
        # --- MODULE 16: GAMIFICATION TRIGGER ---
        from src.analytics.gamification import GamificationEngine
        game_engine = GamificationEngine()
        # Fire and forget counter increment
        background_tasks.add_task(game_engine.increment_global_counter)
        # ---------------------------------------
        
        return ServiceResponse(
            status="accepted",
            message="Interaction queued for agent processing.",
            data={"job_id": job_id}
        )
        
    except Exception as e:
        logger.error(f"Interaction failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Dispatch Error")
