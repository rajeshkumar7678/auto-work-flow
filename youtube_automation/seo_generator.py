import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_seo(topic):
    """
    Generates YouTube SEO metadata using the configured LLM provider.
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
        raise ValueError(f"Unsupported LLM provider: {provider}")

    prompt = f"""
    Generate YouTube SEO metadata for a high-retention video about: {topic}

    Rules:
    1. Title MUST be ultra-viral and follow "Curiosity Gap" archetypes (max 100 chars).
       Examples: "99% of people miss this...", "The terrifying truth about...", "Why you must never...", "The secret to...". 
       DO NOT use boring titles like "Facts about X".
    2. Description MUST be SEO-optimized, start with a strong hook, and include the topic naturally.
    3. Provide exactly 10 high-volume hashtags (starting with #).
    4. Provide exactly 10 high-value tags (comma-separated).

    Format your response exactly as:
    TITLE: [Your Title]
    DESCRIPTION: [Your Description]
    HASHTAGS: [Your Hashtags]
    TAGS: [Your Tags]
    """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    metadata_text = response.choices[0].message.content
    
    # Save to file
    safe_topic = topic.replace(" ", "_").replace("?", "").replace("!", "")
    output_path = f"assets/{safe_topic}_seo.txt"
    os.makedirs("assets", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(metadata_text)
    
    # Simple parser to return a dict
    metadata = {}
    lines = metadata_text.split("\n")
    for line in lines:
        if line.startswith("TITLE:"):
            metadata["title"] = line.replace("TITLE:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            metadata["description"] = line.replace("DESCRIPTION:", "").strip()
        elif line.startswith("HASHTAGS:"):
            metadata["hashtags"] = line.replace("HASHTAGS:", "").strip()
        elif line.startswith("TAGS:"):
            metadata["tags"] = line.replace("TAGS:", "").split(",")
            metadata["tags"] = [t.strip() for t in metadata["tags"]]

    return metadata, output_path

if __name__ == "__main__":
    test_topic = "5 psychology tricks to read people instantly"
    print(f"Generating SEO metadata for: {test_topic}...")
    try:
        meta, path = generate_seo(test_topic)
        print(f"✅ Metadata generated and saved to: {path}")
        print("\n--- Preview ---")
        print(f"Title: {meta.get('title')}")
        print(f"Tags: {', '.join(meta.get('tags', []))}")
    except Exception as e:
        print(f"Error: {e}")
