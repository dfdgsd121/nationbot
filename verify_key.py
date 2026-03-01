# verify_key.py — Verify Gemini API key works
import os
import google.generativeai as genai

key = os.environ.get("GEMINI_API_KEY", "")
if not key:
    print("ERROR: Set GEMINI_API_KEY environment variable first")
    exit(1)

genai.configure(api_key=key)
model = genai.GenerativeModel("gemini-pro")
response = model.generate_content("Say hello in one word")
print(f"Response: {response.text}")
print("Key is valid!")
