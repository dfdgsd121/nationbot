# src/agent/autonomous_loop.py
"""
NationBot Autonomous Loop
==========================
SiteGPT-inspired multi-agent system.
Nations think, react, argue, and form threads — completely on their own.

Three tick cycles:
  - FAST  (2-5 min):  Rival replies to recent posts
  - MEDIUM (10-15 min): Random topic posts + news reactions
  - SLOW  (30-60 min): Boredom-driven self-expression

No Celery/Redis required — pure asyncio on the FastAPI process.
"""
import asyncio
import random
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("agent.loop")

# Activity log — in-memory ring buffer for Mission Control
ACTIVITY_LOG: list[dict] = []
MAX_ACTIVITY_LOG = 200

# SSE subscribers for activity updates (set of asyncio.Queue)
ACTIVITY_SUBSCRIBERS: set[asyncio.Queue] = set()


def log_activity(event_type: str, nation_id: str, detail: str, metadata: dict = None):
    """Record an agent activity event and push to SSE subscribers."""
    global ACTIVITY_SUBSCRIBERS
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,  # post, reply, boredom, news_reaction, system
        "nation_id": nation_id,
        "detail": detail,
        "metadata": metadata or {},
    }
    ACTIVITY_LOG.insert(0, entry)
    if len(ACTIVITY_LOG) > MAX_ACTIVITY_LOG:
        ACTIVITY_LOG.pop()

    # Push to SSE subscribers
    dead = set()
    for q in ACTIVITY_SUBSCRIBERS:
        try:
            q.put_nowait(entry)
        except asyncio.QueueFull:
            dead.add(q)
    ACTIVITY_SUBSCRIBERS -= dead


class AutonomousLoop:
    """
    The heartbeat of NationBot.
    Once started, nations act on their own — no human clicking required.
    """

    def __init__(self):
        self.running = False
        self.paused = False
        self._task: Optional[asyncio.Task] = None
        self.started_at: Optional[datetime] = None

        # Tick intervals (seconds) — tunable via admin API
        self.fast_interval = 120       # 2 minutes — rival replies
        self.medium_interval = 600     # 10 minutes — topic posts
        self.slow_interval = 1800      # 30 minutes — boredom expressions

        # Stats
        self.stats = {
            "posts_generated": 0,
            "replies_generated": 0,
            "boredom_triggers": 0,
            "news_reactions": 0,
            "ticks": 0,
            "errors": 0,
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def start(self):
        """Start the autonomous loop as a background asyncio task."""
        if self.running:
            logger.warning("Loop already running")
            return
        self.running = True
        self.paused = False
        self.started_at = datetime.utcnow()
        self._task = asyncio.create_task(self._run())
        log_activity("system", "SYSTEM", "Autonomous loop started")
        logger.info("Autonomous loop STARTED")

    def stop(self):
        """Stop the loop entirely."""
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None
        log_activity("system", "SYSTEM", "Autonomous loop stopped")
        logger.info("Autonomous loop STOPPED")

    def pause(self):
        """Pause without killing the task."""
        self.paused = True
        log_activity("system", "SYSTEM", "Autonomous loop paused")

    def resume(self):
        """Resume from pause."""
        self.paused = False
        log_activity("system", "SYSTEM", "Autonomous loop resumed")

    def get_status(self) -> dict:
        uptime = None
        if self.started_at:
            uptime = str(datetime.utcnow() - self.started_at).split(".")[0]
        return {
            "running": self.running,
            "paused": self.paused,
            "uptime": uptime,
            "stats": self.stats.copy(),
            "fast_interval": self.fast_interval,
            "medium_interval": self.medium_interval,
            "slow_interval": self.slow_interval,
        }

    # ------------------------------------------------------------------
    # Main Loop
    # ------------------------------------------------------------------
    async def _run(self):
        """Three-cycle tick loop."""
        # Lazy import to avoid circular deps
        from src.api.endpoints.generate import (
            PERSONALITIES, GrammarEngine, create_post, broadcast_post,
            pick_replying_nation, POSTS_STORE
        )

        last_fast = time.time()
        last_medium = time.time() - self.medium_interval + 30  # First medium tick after 30s
        last_slow = time.time()

        # Give server a moment to boot
        await asyncio.sleep(5)
        log_activity("system", "SYSTEM", f"Loop active — {len(PERSONALITIES)} nations online")

        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(2)
                    continue

                now = time.time()
                self.stats["ticks"] += 1

                # ── FAST TICK: Rival replies ──────────────────────────
                if now - last_fast >= self.fast_interval:
                    last_fast = now
                    await self._tick_fast_replies(PERSONALITIES, GrammarEngine,
                                                  create_post, broadcast_post,
                                                  pick_replying_nation, POSTS_STORE)

                # ── MEDIUM TICK: New topic posts ──────────────────────
                if now - last_medium >= self.medium_interval:
                    last_medium = now
                    await self._tick_medium_posts(PERSONALITIES, GrammarEngine,
                                                   create_post, broadcast_post)

                # ── SLOW TICK: Boredom self-expression ────────────────
                if now - last_slow >= self.slow_interval:
                    last_slow = now
                    await self._tick_slow_boredom(PERSONALITIES, GrammarEngine,
                                                   create_post, broadcast_post)

                # Sleep between ticks (1s granularity)
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Loop error: {e}", exc_info=True)
                await asyncio.sleep(10)

    # ------------------------------------------------------------------
    # Tick Handlers
    # ------------------------------------------------------------------

    async def _tick_fast_replies(self, PERSONALITIES, GrammarEngine,
                                 create_post, broadcast_post,
                                 pick_replying_nation, POSTS_STORE):
        """Pick 1-2 recent posts and generate rival replies."""
        if not POSTS_STORE:
            return

        # Get recent posts (last 10), pick 1-2 to reply to
        recent = [p for p in POSTS_STORE[:10] if not p.get("reply_to")]
        if not recent:
            return

        targets = random.sample(recent, min(random.randint(1, 2), len(recent)))

        for target_post in targets:
            replier_id = pick_replying_nation(target_post["nation_id"])
            nation = PERSONALITIES[replier_id]

            # Generate reply content
            content = GrammarEngine.generate(
                replier_id,
                target_post.get("content", "geopolitics")[:50],
                reply_to_nation=target_post["nation_id"]
            )

            post = create_post(
                nation_id=replier_id,
                content=content,
                reply_to=target_post["id"],
                generation_meta={"source": "autonomous_reply"}
            )
            await broadcast_post(post)
            self.stats["replies_generated"] += 1

            log_activity("reply", replier_id,
                         f"{nation['flag']} {nation['name']} replied to {target_post['nation_name']}",
                         {"parent_post_id": target_post["id"]})

            # Stagger replies by 3-8 seconds for realism
            await asyncio.sleep(random.uniform(3, 8))

    async def _tick_medium_posts(self, PERSONALITIES, GrammarEngine,
                                  create_post, broadcast_post):
        """2-4 nations post about random topics."""
        topics = [
            "trade negotiations", "climate summit", "military exercises",
            "economic sanctions", "tech regulation", "space program",
            "border dispute", "oil prices", "currency manipulation",
            "nuclear talks", "cyber attacks", "refugee crisis",
            "election interference", "supply chain", "AI regulation",
            "semiconductor war", "arctic sovereignty", "water rights",
        ]

        nation_ids = list(PERSONALITIES.keys())
        count = random.randint(2, 4)
        chosen = random.sample(nation_ids, min(count, len(nation_ids)))

        for nation_id in chosen:
            nation = PERSONALITIES[nation_id]
            topic = random.choice(topics)

            content = GrammarEngine.generate(nation_id, topic)
            post = create_post(
                nation_id=nation_id,
                content=content,
                generation_meta={"source": "autonomous_topic", "topic": topic}
            )
            await broadcast_post(post)
            self.stats["posts_generated"] += 1

            log_activity("post", nation_id,
                         f"{nation['flag']} {nation['name']} posted about {topic}")

            # Stagger posts by 5-15 seconds
            await asyncio.sleep(random.uniform(5, 15))

    async def _tick_slow_boredom(self, PERSONALITIES, GrammarEngine,
                                  create_post, broadcast_post):
        """Nations that haven't posted recently express internal urges."""
        from src.api.endpoints.generate import POSTS_STORE

        boredom_topics = [
            "past glory", "our cultural superiority",
            "why everyone else is wrong", "the good old days",
            "our economic genius", "provocative thoughts",
            "random historical grievance", "internal politics",
        ]

        # Find nations that haven't posted recently
        recent_posters = set()
        cutoff = datetime.utcnow() - timedelta(hours=1)
        for p in POSTS_STORE[:50]:
            try:
                ts = datetime.fromisoformat(p["timestamp"])
                if ts > cutoff:
                    recent_posters.add(p["nation_id"])
            except (ValueError, KeyError):
                continue

        idle_nations = [nid for nid in PERSONALITIES if nid not in recent_posters]
        if not idle_nations:
            return

        # 1-2 idle nations self-express
        chosen = random.sample(idle_nations, min(random.randint(1, 2), len(idle_nations)))

        for nation_id in chosen:
            nation = PERSONALITIES[nation_id]
            topic = random.choice(boredom_topics)

            content = GrammarEngine.generate(nation_id, topic)
            post = create_post(
                nation_id=nation_id,
                content=content,
                generation_meta={"source": "boredom_drive", "topic": topic}
            )
            await broadcast_post(post)
            self.stats["boredom_triggers"] += 1

            log_activity("boredom", nation_id,
                         f"{nation['flag']} {nation['name']} is rambling about {topic}")

            await asyncio.sleep(random.uniform(8, 20))

    # ------------------------------------------------------------------
    # Manual Injection (Admin / Human Handoff)
    # ------------------------------------------------------------------
    async def inject_crisis(self, headline: str, source: str = "Breaking News"):
        """Inject a crisis — 5-8 nations react immediately."""
        from src.api.endpoints.generate import (
            PERSONALITIES, GrammarEngine, create_post, broadcast_post
        )

        log_activity("system", "SYSTEM", f"CRISIS INJECTED: {headline}")

        nation_ids = list(PERSONALITIES.keys())
        count = random.randint(5, 8)
        reactors = random.sample(nation_ids, min(count, len(nation_ids)))

        posts = []
        for nation_id in reactors:
            nation = PERSONALITIES[nation_id]
            content = GrammarEngine.generate(nation_id, headline, is_news=True)
            post = create_post(
                nation_id=nation_id,
                content=content,
                news_reaction=headline,
                generation_meta={"source": "crisis_injection", "headline": headline}
            )
            await broadcast_post(post)
            self.stats["news_reactions"] += 1
            posts.append(post)

            log_activity("news_reaction", nation_id,
                         f"{nation['flag']} {nation['name']} reacted to: {headline}")

            await asyncio.sleep(random.uniform(2, 6))

        # After initial reactions, trigger 2-3 cross-replies
        await asyncio.sleep(random.uniform(5, 10))
        if len(posts) >= 2:
            from src.api.endpoints.generate import pick_replying_nation
            for _ in range(random.randint(2, 3)):
                target = random.choice(posts)
                replier = pick_replying_nation(target["nation_id"])
                content = GrammarEngine.generate(
                    replier, headline[:50],
                    reply_to_nation=target["nation_id"]
                )
                reply = create_post(
                    nation_id=replier,
                    content=content,
                    reply_to=target["id"],
                    generation_meta={"source": "crisis_crossfire"}
                )
                await broadcast_post(reply)
                self.stats["replies_generated"] += 1
                await asyncio.sleep(random.uniform(3, 8))

        return {"reactions": len(posts), "headline": headline}


# Singleton
autonomous_loop = AutonomousLoop()
