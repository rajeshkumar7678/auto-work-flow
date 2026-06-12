import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    for m in data.get("models", []):
        print(f"- {m['name']} (supports: {m.get('supportedGenerationMethods')})")
except Exception as e:
    print(f"Error: {e}")
