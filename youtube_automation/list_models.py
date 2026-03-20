import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROK_API_KEY")
url = "https://api.x.ai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    models = response.json()
    print("Available models:")
    for model in models.get("data", []):
        print(f"- {model['id']}")
else:
    print(f"Failed to fetch models: {response.status_code}")
    print(response.text)
