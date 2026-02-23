# tests/test_e2e_autonomous.py
"""
End-to-End Validation: NationBot Autonomous Multi-Agent System
==============================================================
Tests every component against the SiteGPT reference architecture:

SiteGPT Component          | NationBot Equivalent         | Test
---------------------------|------------------------------|------
Jarvis (Orchestrator)      | AutonomousLoop               | test_loop_lifecycle
Specialist Agents          | 25 Nation Agents              | test_nation_generation
15-min Polling             | Tick cycles                   | test_tick_generation
Mission Control            | /v1/admin/* endpoints         | test_admin_*
Squad Chat                 | Feed + SSE                    | test_feed_*
Human Handoff              | Crisis Injection              | test_crisis_injection
"""
import requests
import time
import json
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0
RESULTS = []


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        RESULTS.append(f"  [PASS] {name}")
    else:
        FAIL += 1
        RESULTS.append(f"  [FAIL] {name} -- {detail}")


def section(title):
    RESULTS.append(f"\n{'='*60}")
    RESULTS.append(f"  {title}")
    RESULTS.append(f"{'='*60}")


# ===================================================================
# 1. HEALTH CHECK
# ===================================================================
section("1. API Health Check")
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    test("GET /health returns 200", r.status_code == 200)
    data = r.json()
    test("Health response has status=online", data.get("status") == "online")
    test("Health response has version", "version" in data)
except Exception as e:
    test("Backend reachable", False, str(e))

# ===================================================================
# 2. AUTONOMOUS LOOP (SiteGPT: Jarvis Orchestrator)
# ===================================================================
section("2. Autonomous Loop (Jarvis Orchestrator)")
try:
    r = requests.get(f"{BASE}/v1/admin/status", timeout=5)
    test("GET /v1/admin/status returns 200", r.status_code == 200)
    data = r.json()
    test("Loop is running", data.get("running") == True)
    test("Loop is not paused", data.get("paused") == False)
    test("Has stats object", "stats" in data)
    test("Has tick intervals", "fast_interval" in data)
    test("Has recent_activity", "recent_activity" in data)
    test("Activity log exists", isinstance(data.get("recent_activity"), list))
except Exception as e:
    test("Admin status endpoint", False, str(e))

# ===================================================================
# 3. ADMIN CONTROLS (SiteGPT: Mission Control)  
# ===================================================================
section("3. Admin Controls (Mission Control)")

# Test pause
try:
    r = requests.post(f"{BASE}/v1/admin/pause", timeout=5)
    test("POST /v1/admin/pause returns 200", r.status_code == 200)
    data = r.json()
    test("Pause response has status", "status" in data)

    # Verify paused
    r = requests.get(f"{BASE}/v1/admin/status", timeout=5)
    data = r.json()
    test("Loop is paused after pause command", data.get("paused") == True)
except Exception as e:
    test("Pause control", False, str(e))

# Test resume
try:
    r = requests.post(f"{BASE}/v1/admin/resume", timeout=5)
    test("POST /v1/admin/resume returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/v1/admin/status", timeout=5)
    data = r.json()
    test("Loop is running after resume", data.get("running") == True and data.get("paused") == False)
except Exception as e:
    test("Resume control", False, str(e))

# Test speed adjustment
try:
    r = requests.post(f"{BASE}/v1/admin/speed", timeout=5,
                      json={"fast_interval": 60, "medium_interval": 300})
    test("POST /v1/admin/speed returns 200", r.status_code == 200)
    data = r.json()
    test("Speed updated — fast_interval=60", data.get("fast_interval") == 60)
    test("Speed updated — medium_interval=300", data.get("medium_interval") == 300)

    # Reset to defaults
    requests.post(f"{BASE}/v1/admin/speed",
                  json={"fast_interval": 120, "medium_interval": 600})
except Exception as e:
    test("Speed control", False, str(e))

# ===================================================================
# 4. NATION GENERATION (SiteGPT: Specialist Agents)
# ===================================================================
section("4. Nation Post Generation (Specialist Agents)")
try:
    r = requests.post(f"{BASE}/v1/generate/nation-post", timeout=10,
                      json={"nation_id": "US", "topic": "trade negotiations"})
    test("POST /nation-post US returns 200", r.status_code == 200)
    data = r.json()
    test("Response has post object", "post" in data)
    post = data.get("post", {})
    test("Post has id", "id" in post)
    test("Post has nation_id=US", post.get("nation_id") == "US")
    test("Post has content", len(post.get("content", "")) > 10)
    test("Post has timestamp", "timestamp" in post)
    test("Post has flag 🇺🇸", post.get("flag") == "🇺🇸")
    test("Post has rep_score", "rep_score" in post)
except Exception as e:
    test("US nation post", False, str(e))

# Test multiple nations
for nid in ["CN", "RU", "IN", "JP", "UK"]:
    try:
        r = requests.post(f"{BASE}/v1/generate/nation-post", timeout=10,
                          json={"nation_id": nid, "topic": "sanctions"})
        test(f"POST /nation-post {nid} returns 200", r.status_code == 200)
    except Exception as e:
        test(f"POST /nation-post {nid}", False, str(e))

# ===================================================================
# 5. FEED (SiteGPT: Squad Chat)
# ===================================================================
section("5. Feed Endpoint (Squad Chat)")
try:
    r = requests.get(f"{BASE}/v1/generate/feed?limit=10", timeout=5)
    test("GET /feed returns 200", r.status_code == 200)
    data = r.json()
    test("Feed has posts array", "posts" in data)
    test("Feed has total count", "total" in data)
    posts = data.get("posts", [])
    test("Feed has posts", len(posts) > 0)
    if posts:
        test("First post has content", len(posts[0].get("content", "")) > 0)
        test("First post has nation_id", "nation_id" in posts[0])
except Exception as e:
    test("Feed endpoint", False, str(e))

# ===================================================================
# 6. CRISIS INJECTION (SiteGPT: Human Handoff / Event Trigger)
# ===================================================================
section("6. Crisis Injection (Human Handoff)")
try:
    r = requests.post(f"{BASE}/v1/admin/inject", timeout=60,
                      json={"headline": "Russia launches cyber attack on NATO"})
    test("POST /admin/inject returns 200", r.status_code == 200)
    data = r.json()
    test("Injection status=injected", data.get("status") == "injected")
    test("Multiple nations reacted", data.get("reactions", 0) >= 3)
    test("Headline echoed back", "Russia" in data.get("headline", ""))
    reactions_count = data.get("reactions", 0)
    test(f"Reaction count reasonable ({reactions_count})", 3 <= reactions_count <= 12)
except Exception as e:
    test("Crisis injection", False, str(e))

# ===================================================================
# 7. ACTIVITY LOG (SiteGPT: Mission Control Dashboard Data)
# ===================================================================
section("7. Activity Log (Dashboard Data)")
try:
    r = requests.get(f"{BASE}/v1/admin/activity?limit=20", timeout=5)
    test("GET /admin/activity returns 200", r.status_code == 200)
    data = r.json()
    test("Activity has entries", len(data.get("activity", [])) > 0)
    if data.get("activity"):
        entry = data["activity"][0]
        test("Entry has timestamp", "timestamp" in entry)
        test("Entry has event_type", "event_type" in entry)
        test("Entry has nation_id", "nation_id" in entry)
        test("Entry has detail", "detail" in entry)
except Exception as e:
    test("Activity log", False, str(e))

# ===================================================================
# 8. METRICS & OBSERVABILITY
# ===================================================================
section("8. Metrics & Observability")
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    test("GET /metrics returns 200", r.status_code == 200)
    data = r.json()
    test("Has total_requests", "total_requests" in data)
    test("Has latency stats", "latency" in data)
except Exception as e:
    test("Metrics endpoint", False, str(e))

# ===================================================================
# 9. SSE STREAM CONNECTIVITY
# ===================================================================
section("9. SSE Streams")
try:
    r = requests.get(f"{BASE}/v1/stream/feed", timeout=5, stream=True)
    test("GET /stream/feed returns 200", r.status_code == 200)
    test("Stream content type is event-stream",
         "text/event-stream" in r.headers.get("content-type", ""))
    # Read first event
    for line in r.iter_lines(decode_unicode=True):
        if line and "connected" in line:
            test("Feed SSE sends connected event", True)
            break
    r.close()
except Exception as e:
    test("Feed SSE stream", False, str(e))

try:
    r = requests.get(f"{BASE}/v1/stream/activity", timeout=5, stream=True)
    test("GET /stream/activity returns 200", r.status_code == 200)
    for line in r.iter_lines(decode_unicode=True):
        if line and "connected" in line:
            test("Activity SSE sends connected event", True)
            break
    r.close()
except Exception as e:
    test("Activity SSE stream", False, str(e))

# ===================================================================
# 10. AUTONOMOUS GENERATION VERIFICATION
# ===================================================================
section("10. Autonomous Generation (Wait for Tick)")
try:
    # Get current stats
    r = requests.get(f"{BASE}/v1/admin/status", timeout=5)
    initial_stats = r.json().get("stats", {})
    initial_total = (initial_stats.get("posts_generated", 0) +
                     initial_stats.get("replies_generated", 0) +
                     initial_stats.get("news_reactions", 0))

    # Check feed count
    r = requests.get(f"{BASE}/v1/generate/feed?limit=50", timeout=5)
    feed_total = r.json().get("total", 0)
    test(f"Feed has accumulated posts (total={feed_total})", feed_total > 0)
    test(f"Autonomous stats show activity (total={initial_total})", initial_total > 0)
except Exception as e:
    test("Autonomous generation check", False, str(e))

# ===================================================================
# FINAL REPORT
# ===================================================================
report_lines = []
report_lines.append("\n" + "="*60)
report_lines.append("  NATIONBOT E2E VERIFICATION REPORT")
report_lines.append("="*60)
report_lines.extend(RESULTS)
report_lines.append(f"\n{'='*60}")
report_lines.append(f"  TOTAL: {PASS + FAIL} tests | PASSED: {PASS} | FAILED: {FAIL}")
report_lines.append(f"{'='*60}")

report = "\n".join(report_lines)

# Write to file (reliable)
with open("test_report.txt", "w", encoding="utf-8") as f:
    f.write(report)

# Also try stdout
try:
    print(report)
except Exception:
    pass

if FAIL > 0:
    sys.exit(1)

