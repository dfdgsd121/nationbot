# src/analytics/tracker.py
import os
import logging
from posthog import Posthog

logger = logging.getLogger("analytics")

# Zero-Cost Analytics Stack
# PostHog (Free: 1M events/mo)
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "phc_your_key_here")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")

class AnalyticsTracker:
    """
    Server-side Event Tracker.
    Proxies critical events to PostHog to bypass AdBlockers.
    Tracks 'Viral Metrics' (TTFL, Hook Rate).
    """

    def __init__(self):
        self.client = Posthog(project_api_key=POSTHOG_API_KEY, host=POSTHOG_HOST)
        # Disable geoip to save latency if needed
        self.client.disable_geoip() 

    def track_event(self, user_id: str, event_name: str, properties: dict = None):
        """
        Generic track wrapper.
        """
        if not properties:
            properties = {}
            
        try:
            self.client.capture(
                distinct_id=user_id,
                event=event_name,
                properties=properties
            )
        except Exception as e:
            logger.error(f"Analytics capture failed: {e}")

    def track_viral_metric(self, user_id: str, metric_type: str, value: float, context: dict):
        """
        Track specific MoltBook-style viral metrics.
        """
        # 1. Time To First Laugh (TTFL)
        if metric_type == "ttfl":
            # Value = seconds
            self.track_event(user_id, "viral_ttfl", {
                "seconds": value,
                "is_good": value < 15,
                **context
            })
            
        # 2. Hook Rate (Scroll Velocity Drop)
        elif metric_type == "hook_stop":
            # Value = duration of pause in ms
            self.track_event(user_id, "viral_hook_stop", {
                "duration_ms": value,
                "post_id": context.get('post_id'),
                "trigger_word": context.get('trigger_word')
            })

    def shutdown(self):
        self.client.shutdown()

# Singleton
tracker = AnalyticsTracker()
