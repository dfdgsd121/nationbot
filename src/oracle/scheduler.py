# src/oracle/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import logging
from typing import Optional

from .pipeline import IngestionPipeline
from .velocity_monitor import VelocityMonitor

logger = logging.getLogger("oracle.scheduler")

class OracleScheduler:
    """
    Manages the heartbeat of the News Ingestion system (Module 01).
    Orchestrates standard periodic fetches and emergency velocity triggers.
    """

    def __init__(self, db_engine=None):
        self.scheduler = AsyncIOScheduler()
        self.pipeline = IngestionPipeline(db_engine)
        self.velocity_monitor: Optional[VelocityMonitor] = None

    def start(self):
        """
        Start the scheduler and velocity monitor.
        Blocks the loop if run directly, or can be awaited if integrated into a larger app.
        """
        logger.info("Starting Oracle Scheduler services...")

        # 1. Standard Schedule: Fetch all active sources every 15 minutes
        self.scheduler.add_job(
            self.pipeline.fetch_all_sources,
            trigger=IntervalTrigger(minutes=15),
            id='standard_fetch_all',
            replace_existing=True
        )
        logger.info("Scheduled: Standard fetch every 15 minutes.")

        # 2. Start Velocity Monitor (Background Task)
        # This closes the 15-minute gap by watching for Breaking News signatures.
        self.velocity_monitor = VelocityMonitor(trigger_callback=self._handle_emergency_trigger)
        
        # Add the monitor's watch loop to the event loop
        # Note: In production, this might be a separate service or daemon.
        if self.scheduler.running:
             asyncio.create_task(self.velocity_monitor.watch())
        else:
            # If scheduler hasn't started, we'll start it now
            self.scheduler.start()
            asyncio.create_task(self.velocity_monitor.watch())

    async def _handle_emergency_trigger(self, trigger_reason: str):
        """
        Callback for when VelocityMonitor detects a panic event.
        Overrides the schedule to fetch immediately.
        """
        logger.critical(f"🚨 EMERGENCY TRIGGER RECEIVED: {trigger_reason}")
        logger.critical("🚨 Initiating immediate full fetch sequence...")
        
        # Execute the pipeline immediately
        # We use add_job with 'date' trigger (run once, now) or just await directly
        # Awaiting directly ensures we don't pile up jobs if the system is overloaded,
        # but using the scheduler allows for better job tracking.
        # Here we await directly for immediate priority execution.
        try:
            await self.pipeline.fetch_all_sources()
            logger.info("✅ Emergency fetch sequence completed.")
        except Exception as e:
            logger.error(f"❌ Emergency fetch failed: {e}")

    def stop(self):
        """Graceful shutdown."""
        if self.velocity_monitor:
            self.velocity_monitor.stop()
        self.scheduler.shutdown()
        logger.info("Oracle Scheduler stopped.")
