# tests/quick_e2e.py
"""Quick E2E validation — ASCII-only output for Windows terminal."""
import requests
import sys

BASE = "http://localhost:8000"
P = 0
F = 0
R = []

def t(name, cond, detail=""):
    global P, F
    mark = "PASS" if cond else "FAIL"
    if cond:
        P += 1
    else:
        F += 1
    msg = mark + ": " + name
    if not cond and detail:
        msg += " [" + detail + "]"
    R.append(msg)

# 1. Health
r = requests.get(BASE + "/health", timeout=5)
t("health-200", r.status_code == 200)
d = r.json()
t("status-online", d.get("status") == "online")

# 2. Admin status
r = requests.get(BASE + "/v1/admin/status", timeout=5)
d = r.json()
t("loop-running", d.get("running") == True)
t("loop-not-paused", d.get("paused") == False)
t("has-stats", "stats" in d)
t("has-activity", "recent_activity" in d)
t("has-intervals", "fast_interval" in d)

# 3. Pause/Resume
r = requests.post(BASE + "/v1/admin/pause", timeout=5)
t("pause-200", r.status_code == 200)
r = requests.get(BASE + "/v1/admin/status", timeout=5)
t("is-paused", r.json().get("paused") == True)
r = requests.post(BASE + "/v1/admin/resume", timeout=5)
t("resume-200", r.status_code == 200)
r = requests.get(BASE + "/v1/admin/status", timeout=5)
t("is-resumed", r.json().get("paused") == False)

# 4. Speed control
r = requests.post(BASE + "/v1/admin/speed", timeout=5, json={"fast_interval": 60})
t("speed-200", r.status_code == 200)
t("speed-updated", r.json().get("fast_interval") == 60)
requests.post(BASE + "/v1/admin/speed", json={"fast_interval": 120})

# 5. Nation posts
for nid in ["US", "CN", "RU", "IN", "JP", "UK", "FR", "DE"]:
    r = requests.post(BASE + "/v1/generate/nation-post", timeout=10,
                      json={"nation_id": nid, "topic": "trade"})
    t("post-" + nid, r.status_code == 200)

# 6. Post structure
r = requests.post(BASE + "/v1/generate/nation-post", timeout=10,
                  json={"nation_id": "US", "topic": "sanctions"})
d = r.json()
post = d.get("post", {})
t("post-has-id", "id" in post)
t("post-has-content", len(post.get("content", "")) > 5)
t("post-has-timestamp", "timestamp" in post)
t("post-has-nation_id", post.get("nation_id") == "US")
t("post-has-rep_score", "rep_score" in post)

# 7. Feed
r = requests.get(BASE + "/v1/generate/feed?limit=10", timeout=5)
d = r.json()
t("feed-200", r.status_code == 200)
t("feed-has-posts", "posts" in d)
total = d.get("total", 0)
t("feed-has-content", total > 0, "total=" + str(total))

# 8. Activity log
r = requests.get(BASE + "/v1/admin/activity?limit=10", timeout=5)
t("activity-200", r.status_code == 200)
act = r.json().get("activity", [])
t("activity-has-entries", len(act) > 0)
if act:
    t("entry-has-timestamp", "timestamp" in act[0])
    t("entry-has-event_type", "event_type" in act[0])

# 9. Metrics
r = requests.get(BASE + "/metrics", timeout=5)
t("metrics-200", r.status_code == 200)
t("metrics-has-requests", "total_requests" in r.json())

# 10. SSE feed
r = requests.get(BASE + "/v1/stream/feed", timeout=5, stream=True)
t("sse-feed-200", r.status_code == 200)
t("sse-content-type", "text/event-stream" in r.headers.get("content-type", ""))
r.close()

# 11. SSE activity
r = requests.get(BASE + "/v1/stream/activity", timeout=5, stream=True)
t("sse-activity-200", r.status_code == 200)
r.close()

# 12. Crisis injection
r = requests.post(BASE + "/v1/admin/inject", timeout=120,
                  json={"headline": "E2E test crisis: nuclear talks collapse"})
t("inject-200", r.status_code == 200)
d = r.json()
t("inject-status", d.get("status") == "injected")
reactions = d.get("reactions", 0)
t("inject-reactions", reactions >= 3, "reactions=" + str(reactions))

# Report
print("\n" + "=" * 50)
print("  NATIONBOT E2E REPORT")
print("=" * 50)
for line in R:
    print("  " + line)
print("=" * 50)
print("  " + str(P) + "/" + str(P + F) + " passed, " + str(F) + " failed")
print("=" * 50)

if F > 0:
    sys.exit(1)
