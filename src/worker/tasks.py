# src/worker/tasks.py
import logging
import asyncio
from .celery_app import app

# Mock connections for now - in prod would duplicate instantiation or use shared singleton
# from src.agent.graph import NationAgent
# from src.oracle.models import FeedItem 

logger = logging.getLogger("worker.tasks")

@app.task(queue='default', bind=True, max_retries=3)
def generate_reaction(self, news_item_id: str, nation_id_list: list):
    """
    Background Task: React to a news item.
    Queue: 'default' (Slower SLA is fine)
    """
    logger.info(f"Processing News Reaction: {news_item_id} for {len(nation_id_list)} nations")
    
    try:
        # In prod:
        # 1. Fetch news item content
        # 2. For each nation in list:
        #    agent.run(nation_id, news_content, type='news')
        
        # Mocking delay to simulate LLM work
        import time
        time.sleep(2) 
        
        logger.info(f"Reaction Generated for {news_item_id}")
        return {"status": "success", "generated_count": len(nation_id_list)}
        
    except Exception as exc:
        logger.error(f"Failed to generate reaction: {exc}")
        # Exponential backoff: 2s, 4s, 8s...
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@app.task(queue='high_priority', bind=True, max_retries=2)
def process_user_interaction(self, user_id: str, nation_id: str, target_post: str, action: str):
    """
    High Priority Task: Respond to a user.
    Queue: 'high_priority' (Must be < 2s)
    """
    logger.info(f"🔥 Processing User Interaction: {action} from {user_id}")
    
    try:
        # 1. Load Agent
        # agent = NationAgent(...)
        
        # 2. Run with 'reply' context
        # result = asyncio.run(agent.run(nation_id, f"Reply to post {target_post}", type='reply'))
        
        logger.info(f"Interaction Processed: {action}")
        return {"status": "success", "reply_id": "mock_uuid"}
        
    except Exception as exc:
        logger.error(f"Interaction failed: {exc}")
        raise self.retry(exc=exc, countdown=1) # Fast retry for user actions
