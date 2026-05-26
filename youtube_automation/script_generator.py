import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def detect_topic_type(topic):
    topic = topic.lower()
    if "karma" in topic or "revenge" in topic or "justice" in topic:
        return "karma"
    if "mystery" in topic or "disappear" in topic or "unexplained" in topic or "secret" in topic:
        return "mystery"
    if "mindset" in topic or "billionaire" in topic or "success" in topic or "rich" in topic:
        return "billionaire"
    if "life lesson" in topic or "moral" in topic or "sad" in topic or "emotional" in topic:
        return "emotional"
    if "fact" in topic or "shocking" in topic or "crazy" in topic:
        return "shocking_facts"
    return "cinematic_story"

def get_specialized_prompt(topic, topic_type, language, duration):
    hook_instruction = "IMPORTANT: Start with a high-energy, high-impact HOOK in the first 3 seconds (e.g., 'Nobody believed him until...', 'This terrifying secret was just exposed...', 'A homeless man did this, and then...')."
    word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 75 and 90 words total to ensure a fast-paced duration of 25-40 seconds."
    story_instruction = "Focus on ONE emotional micro-story, ONE twist, and ONE emotional payoff. NO robotic lists. Make it feel cinematic."
    
    base_prompt = f"""
    Create a highly viral, fast-paced YouTube Shorts story in {language}.
    Topic/Vibe: {topic}
    Requirements:
    - {hook_instruction}
    - {word_count_instruction}
    - {story_instruction}
    """
    
    if topic_type == "karma":
        return base_prompt + "\nStyle: Karma Story. Someone does something bad or good, and they get exactly what they deserve at the end in a shocking way."
    elif topic_type == "mystery":
        return base_prompt + "\nStyle: Mystery. Build suspense rapidly. Reveal a shocking, terrifying, or unbelievable truth at the very end."
    elif topic_type == "billionaire":
        return base_prompt + "\nStyle: Motivational Cinematic. A story of extreme doubt or struggle that ends in massive success or a brilliant mindset shift."
    elif topic_type == "emotional":
        return base_prompt + "\nStyle: Emotional Micro-Story. Touch the viewer's heart. A story of sacrifice, love, or a deep life lesson with a twist."
    elif topic_type == "shocking_facts":
        return base_prompt + "\nStyle: Shocking Story. Tell a cohesive story about a crazy historical event or unbelievable occurrence, not just a list of facts."
    else:
        return base_prompt + "\nStyle: Cinematic AI Story. Dark, moody, or inspiring narrative with a massive plot twist at the end."

def generate_script(topic, duration="45-60 seconds", language="English"):
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
        raise ValueError(f"Unsupported LLM provider: {provider}")

    topic_type = detect_topic_type(topic)
    prompt = get_specialized_prompt(topic, topic_type, language, duration)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a viral YouTube content creator."},
            {"role": "user", "content": prompt}
        ]
    )

    script = response.choices[0].message.content
    
    # Sanitize: Remove markdown bolding/italics that TTS reads as "asterisk asterisk"
    script = script.replace("**", "").replace("*", "")
    
    # Save to file
    os.makedirs("assets", exist_ok=True)
    with open("assets/script.txt", "w", encoding="utf-8") as f:
        f.write(script)
    
    return script

if __name__ == "__main__":
    test_topic = "Why your brain makes decisions before you do"
    print(f"Generating script for: {test_topic} using {os.getenv('LLM_PROVIDER')}...")
    try:
        result = generate_script(test_topic)
        print("Script generated successfully!")
        print("-" * 30)
        print(result)
        print("-" * 30)
    except Exception as e:
        print(f"Error: {e}")
