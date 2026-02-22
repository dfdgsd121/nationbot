import google.generativeai as genai
import os

key = "AIzaSyDD6CF07J9BPgGvsMTn2Q5mhfMtlq8Svt4"

print(f"Testing key: {key[:10]}...")

try:
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Hello")
    print("✅ Key Works! Response:", response.text)
except Exception as e:
    print("❌ Key Failed:", e)
