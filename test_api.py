# test_api.py - Test the API endpoint directly
import urllib.request
import json

print("Testing NationBot API...")

# Test health
try:
    req = urllib.request.Request("http://localhost:8000/health")
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read())
        print(f"✅ Health: {data}")
except Exception as e:
    print(f"❌ Health failed: {e}")

# Test debug
try:
    req = urllib.request.Request("http://localhost:8000/v1/generate/debug")
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read())
        print(f"✅ Debug: {data}")
except Exception as e:
    print(f"❌ Debug failed: {e}")

# Test nation post
print("\nTesting nation post generation...")
try:
    data = json.dumps({"nation_id": "US", "topic": "world politics"}).encode('utf-8')
    req = urllib.request.Request(
        "http://localhost:8000/v1/generate/nation-post",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
        print(f"✅ Nation Post Result:")
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Nation post failed: {type(e).__name__}: {e}")

# Test news trigger
print("\nTesting news trigger...")
try:
    data = json.dumps({"headline": "USA bans TikTok"}).encode('utf-8')
    req = urllib.request.Request(
        "http://localhost:8000/v1/generate/trigger-news",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read())
        print(f"✅ News Trigger Result:")
        print(f"   Reactions: {len(result.get('reactions', []))}")
        for r in result.get('reactions', []):
            print(f"   {r['flag']} {r['nation_name']}: {r['content'][:50]}...")
except Exception as e:
    print(f"❌ News trigger failed: {type(e).__name__}: {e}")
