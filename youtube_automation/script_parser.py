import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def parse_script_to_scenes(script, content_mode=None):
    """
    Uses LLM to break a script into logical scenes and 
    extract search keywords for each scene.
    Returns a list of dictionaries with 'text' and 'keyword'.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower().strip()
    if content_mode is None:
        content_mode = os.getenv("CONTENT_MODE", "general").strip().lower()

    # --- LLM Client Initialization ---
    if provider == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = "gpt-4o-mini"
    elif provider in ["grok", "groq"]:
        key = os.getenv("XAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if key and key.startswith("gsk_"):
            client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
            model = "llama-3.3-70b-versatile"
        else:
            client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
            model = "grok-4-latest"
    elif provider == "deepseek":
        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        model = "deepseek-chat"
    else:
        # Fallback: simple sentence split with generic keywords
        sentences = [s.strip() for s in script.split(".") if s.strip()]
        return [{"text": s, "scene_description": s, "emotion": "dramatic", "keywords": ["cinematic"]} for s in sentences]

    # --- Visual Keyword Style by Mode ---
    if content_mode == "football":
        visual_style_instruction = (
            "\"scene_description\": (MUST BE IN ENGLISH) A highly descriptive, cinematic description of the visual sports/football scene, focusing on player action, team logos, stadium atmosphere, or country flags. For example: 'A close-up of a football player kick in slow motion on a lush green stadium pitch during sunset, cinematic lighting'.\n"
            "    3. \"keywords\": (MUST BE IN ENGLISH) A list of 3-4 sports/football terms to search on Pexels/Pixabay (ordered from most specific to generic). DO NOT use copyrighted names like FIFA, World Cup, or specific team/player names in Pexels/Pixabay searches. Use generic terms like 'soccer player', 'stadium crowd', 'football goal', 'soccer match'."
        )
    else:
        visual_style_instruction = (
            "\"scene_description\": (MUST BE IN ENGLISH) A highly descriptive, cinematic, and detailed description of the visual scene (perfect for generating a rich AI image). For example, 'Elderly Indian man with glasses smiling, historical sepia photo, Mahatma Gandhi portrait style'.\n"
            "    3. \"keywords\": (MUST BE IN ENGLISH) A list of 3-4 highly relevant search terms to find stock videos on Pexels/Pixabay (ordered from most specific to generic). Avoid copyrighted words."
        )

    prompt = f"""
    Break this YouTube script into highly granular visual scenes. 
    For longer videos (like 2 or 5 minutes), ensure you break it down into 15-30 sequential scenes.
    For standard Shorts (45-60s), aim for 8-12 scenes.
    Each scene should only last 2-4 seconds to maintain a high-paced "Pattern Interrupt" style.
    
    CRITICAL RULE: The keys "scene_description", "emotion", and "keywords" MUST be written strictly in ENGLISH. 
    This is because they are sent to English-only search APIs (Pexels, Pixabay) and AI image generators.
    Only the "text" field should contain the original script segment (which will be in Hindi or English).

    For each scene, provide a detailed dictionary with:
    1. "text": The exact phrase or segment of the script this visual corresponds to (in its original language).
    2. {visual_style_instruction}
    4. "emotion": (MUST BE IN ENGLISH) The core emotional tone (e.g., sad, happy, suspenseful, mysterious, dramatic, shocking).
    
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
