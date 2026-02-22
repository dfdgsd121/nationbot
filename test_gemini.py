# test_gemini.py - Run this to verify Gemini API works
import os

# Set your API key
os.environ["GEMINI_API_KEY"] = "AIzaSyDIoVI-HKKZi7I9YEuqBPW0QFKepuNpgf0"

print("Testing Gemini API...")
print(f"API Key: {os.environ['GEMINI_API_KEY'][:15]}...")

try:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = """You are the United States personified as a social media user.
Your personality: Loud, confident, uses exclamation points. Always mentions freedom and being #1.

Generate a short, punchy social media post about current world events.
Be dramatic, sarcastic, and entertaining. Include 1-2 relevant emojis.
Max 280 characters. No hashtags."""

    print("\nSending to Gemini...")
    response = model.generate_content(prompt)
    
    print("\n✅ SUCCESS! Gemini responded:")
    print("-" * 40)
    print(response.text)
    print("-" * 40)
    
except ImportError:
    print("❌ ERROR: google-generativeai not installed")
    print("Run: pip install google-generativeai")
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
