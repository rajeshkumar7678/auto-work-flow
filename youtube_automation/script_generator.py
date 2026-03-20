import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def detect_topic_type(topic):
    topic = topic.lower()
    if "joke" in topic or "jokes" in topic or "funny" in topic:
        return "jokes"
    if "fact" in topic or "facts" in topic or "did you know" in topic:
        return "facts"
    if "psychology" in topic or "mind" in topic:
        return "psychology"
    if "devotional" in topic or "spiritual" in topic or "faith" in topic or "god" in topic:
        return "devotional"
    return "general"

def get_specialized_prompt(topic, topic_type, language, duration):
    hook_instruction = "IMPORTANT: Start with a high-energy, high-impact HOOK in the first 3 seconds (e.g., 'Stop scrolling!', '99% of people don't know this...', 'This will change your life...')."
    word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 130 and 150 words total to ensure a duration of 45-60 seconds. Do not exceed 150 words."
    
    if topic_type == "jokes":
        return f"""
        Create a hilarious YouTube Shorts script in {language}.
        Topic: {topic}
        Requirements:
        - {hook_instruction}
        - {word_count_instruction}
        - Provide exactly 3-5 short, punchy jokes.
        - End with: "If you laughed, like and subscribe for more!"
        Return ONLY the spoken narration.
        """
    elif topic_type == "facts":
        return f"""
        Create an interesting YouTube Shorts script in {language}.
        Topic: {topic}
        Requirements:
        - {hook_instruction}
        - {word_count_instruction}
        - Provide 5 mind-blowing facts about the topic.
        - Use "Did you know?" style.
        - End with: "Subscribe for more amazing facts!"
        Return ONLY the spoken narration.
        """
    elif topic_type == "psychology":
        return f"""
        Create a fascinating YouTube Shorts script in {language}.
        Topic: {topic}
        Requirements:
        - {hook_instruction}
        - {word_count_instruction}
        - Explain 3-5 psychology tricks or facts.
        - Focus on dark psychology or human behavior.
        - End with: "Like and subscribe to master your mind."
        Return ONLY the spoken narration.
        """
    elif topic_type == "devotional":
        return f"""
        Create a peaceful and inspiring YouTube Shorts script in {language}.
        Topic: {topic}
        Requirements:
        - {hook_instruction}
        - {word_count_instruction}
        - Provide an inspiring spiritual message or lesson.
        - Tone should be calm, wise, and encouraging.
        - End with: "Subscribe for your daily dose of peace."
        Return ONLY the spoken narration.
        """
    else:
        return f"""
        Write a viral YouTube Shorts script IN {language}.
        Topic: {topic}
        Requirements:
        - {hook_instruction}
        - {word_count_instruction}
        - Numbered points and fast pacing.
        - End with: "If you enjoyed this, like and subscribe for more!"
        Return ONLY the spoken narration.
        """

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
