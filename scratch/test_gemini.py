import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY", "")
print("GEMINI_API_KEY configured:", bool(key and key != "your_gemini_api_key_here"))

try:
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    res = model.generate_content("Hello, respond in one word.")
    print("Success! Gemini response:", res.text.strip())
except Exception as e:
    print("Error calling Gemini API:", e)
