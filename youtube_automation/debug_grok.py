import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_grok():
    api_key = os.getenv("XAI_API_KEY")
    url = "https://api.x.ai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Try the user's requested model
    model = "grok-4-latest"
    
    data = {
        "messages": [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "Hi"}
        ],
        "model": model,
        "stream": False,
        "temperature": 0
    }
    
    print(f"Testing Grok with model: {model}...")
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response Text:")
        print(response.text)

if __name__ == "__main__":
    test_grok()
