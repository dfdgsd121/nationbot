# src/worker/celery_app.py
import os
from celery import Celery
from kombu import Queue, Exchange

# Default to localhost Redis if not set (for dev)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery('nationbot_worker', broker=REDIS_URL, backend=REDIS_URL)

# 1. Zero-Cost Concurrency Optimization
# Use gevent (Greenlets) to handle many I/O bound tasks (LLM calls) 
# without the RAM overhead of prefork processes.
# This allows running ~20-50 concurrent tasks on a 512MB Railway container.
# usage command: celery -A src.worker.celery_app worker -P gevent -c 20

# 2. Priority Lanes Configuration (The Fix for 'Priority Inversion')
# Explicitly define queues so High Priority tasks don't get stuck behind 500 news items.
app.conf.task_queues = (
    Queue('high_priority',  routing_key='high.#'), # User actions (Reply, Like, Claim)
    Queue('default',        routing_key='default.#'), # News reactions, Boredom
    Queue('low_priority',   routing_key='low.#'),     # Analytics, Cleanup
)

app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default.misc'

# 3. Robustness & DLQ Strategy (The Fix for 'Queue Rot')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Reliability: Don't lose tasks if worker crashes mid-process
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Prefetch: Don't hoard tasks. 1 at a time ensures fair distribution 
    # if we scale to multiple workers later.
    worker_prefetch_multiplier=1,
    
    # Time limits to prevent hung tasks (LLM timeouts)
    task_soft_time_limit=300, # 5 minutes
    task_time_limit=310,      # Kill after 310s
)

# Auto-discover tasks in this directory
app.autodiscover_tasks(['src.worker'])

if __name__ == '__main__':
    app.start()
