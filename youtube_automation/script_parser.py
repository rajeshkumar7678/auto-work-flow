import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def parse_script_to_scenes(script):
    """
    Uses LLM to break a script into logical scenes and 
    extract search keywords for each scene.
    Returns a list of dictionaries with 'text' and 'keyword'.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = "gpt-4o-mini"
    elif provider == "grok" or provider == "groq":
        key = os.getenv("XAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if key and key.startswith("gsk_"):
            client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
            model = "llama-3.3-70b-versatile"
        else:
            client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
            model = "grok-4-latest"
    else:
        # Fallback: simple sentence split with generic keywords
        sentences = [s.strip() for s in script.split(".") if s.strip()]
        return [{"text": s, "scene_description": s, "emotion": "dramatic", "keywords": ["cinematic"]} for s in sentences]

    prompt = f"""
    Break this YouTube script into 15-20 highly granular visual scenes. 
    Each scene should only last 2-4 seconds to maintain a high-paced "Pattern Interrupt" style.
    
    For each scene, provide a detailed dictionary with:
    1. "text": The exact phrase or segment of the script this visual corresponds to.
    2. "scene_description": A highly descriptive, cinematic, and detailed description of the visual scene (perfect for generating a rich AI image).
    3. "emotion": The core emotional tone (e.g., sad, happy, suspenseful, mysterious, billionaire mindset, dramatic, shocking).
    4. "keywords": A list of 3-4 highly relevant search terms to find stock videos on Pexels/Pixabay (ordered from most specific to generic). Avoid copyrighted words.
    
    Script:
    {script}
    
    Format your response as a JSON list of objects:
    [
      {{
        "text": "phrase from script",
        "scene_description": "poor child walking in rain",
        "emotion": "sad",
        "keywords": ["rain", "child", "street", "cinematic"]
      }},
      ...
    ]
    """


    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" } if provider == "openai" else None
        )
        content = response.choices[0].message.content
        
        # In case the LLM adds markdown or other text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        # If the LLM returns an object with a list inside, handle it
        if isinstance(data, dict):
            for key in ["scenes", "data", "list"]:
                if key in data:
                    return data[key]
        return data if isinstance(data, list) else []
        
    except Exception as e:
        print(f"⚠️  Script parsing failed: {e}. Falling back to simple split.")
        sentences = [s.strip() for s in script.split(".") if s.strip()]
        return [{"text": s, "scene_description": s, "emotion": "dramatic", "keywords": ["cinematic"]} for s in sentences]

if __name__ == "__main__":
    test_script = "Ever wondered why you forget names instantly? It is because your brain does not think they are important. Try this: repeat the name three times. You will never forget again."
    scenes = parse_script_to_scenes(test_script)
    print(json.dumps(scenes, indent=2))
