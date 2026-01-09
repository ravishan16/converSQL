
import os
import sys
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

print("--- AI Service Debug ---")

# Check Gemini
print("\n--- Checking Gemini Models ---")

import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY or GEMINI_API_KEY not found.")
else:
    genai.configure(api_key=api_key)
    print("Available Gemini Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

print("\n--- Debug Complete ---")
