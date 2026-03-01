# test_gemini.py — Quick Gemini API test
import os
import google.generativeai as genai

key = os.environ.get("GEMINI_API_KEY", "")
if not key:
    print("ERROR: Set GEMINI_API_KEY environment variable first")
    exit(1)

genai.configure(api_key=key)
model = genai.GenerativeModel("gemini-pro")
response = model.generate_content("What is the capital of France? One word answer.")
print(f"Response: {response.text}")
print("Gemini API is working!")
