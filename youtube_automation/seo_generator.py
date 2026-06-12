import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_seo(topic, research_data=None):
    """
    Generates YouTube SEO metadata using the configured LLM provider.
    Accepts optional research_data for sports/football-specific metadata generation.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower().strip()

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
        raise ValueError(f"Unsupported LLM provider: {provider}")

    # Build context block from research data if available
    if research_data:
        facts_str = "\n".join([f"- {f}" for f in research_data.get("facts", [])])
        stats_str = "\n".join([f"- {s}" for s in research_data.get("stats", [])])
        records_str = "\n".join([f"- {r}" for r in research_data.get("records", [])])
        summary_str = research_data.get("summary", "")

        prompt = f"""
    You are a viral YouTube sports channel SEO expert.
    Generate high-impact YouTube SEO metadata for a Shorts video about: {topic}

    Use these REAL researched facts to craft highly specific, accurate metadata:

    Facts:
{facts_str}

    Stats:
{stats_str}

    Records:
{records_str}

    Summary:
{summary_str}

    Rules:
    1. TITLE must reference a specific REAL fact, stat, or record from the research above (max 100 chars).
       Formats that work great for sports:
       - "[Player] just broke THIS record at the World Cup 🔥"
       - "Nobody expected THIS at the 2026 FIFA World Cup..."
       - "The moment that SHOCKED 84,000 fans at the World Cup"
       - "This World Cup goal broke the internet"
       Make the title specific and grounded in the REAL data. DO NOT be generic.
    2. Description MUST start with a hook referencing the real stats, include relevant keywords naturally,
       and end with a strong Subscribe/Like CTA.
    3. Provide exactly 10 relevant football/sports hashtags (starting with #).
    4. Provide exactly 10 SEO-optimized tags mixing specific (player/match names) and broad ("football", "soccer") terms.

    Format your response EXACTLY as:
    TITLE: [Your Title]
    DESCRIPTION: [Your Description]
    HASHTAGS: [Your Hashtags]
    TAGS: [Your Tags]
    """
    else:
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
