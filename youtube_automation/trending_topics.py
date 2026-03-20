from pytrends.request import TrendReq
import random
import os
import json
from googleapiclient.discovery import build
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Default niche if nothing is provided
DEFAULT_KEYWORDS = [
    "psychology",
    "mind tricks",
    "body language",
    "self improvement",
    "AI tools",
    "money habits",
    "tech secrets"
]

def get_trending_youtube_topics():
    """Fetches trending YouTube titles in the US."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("⚠️  No YOUTUBE_API_KEY found. Skipping YouTube trends.")
        return []
    
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="US",
            maxResults=20
        )
        response = request.execute()
        return [item["snippet"]["title"] for item in response["items"]]
    except Exception as e:
        print(f"⚠️  YouTube Trends failed: {e}")
        return []

def get_tiktok_trending():
    """
    TikTok scraping is complex. 
    Falling back to an LLM-simulated trend scout for TikTok-viral style topics 
    to ensure we always have high-energy 'TikTok style' trends.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if provider == "openai" else None
    if not client: return []
    
    prompt = "Predict 10 currently viral TikTok-style hooks/topics for the US market (Psychology, AI, Hacks). Return ONLY a list, one per line."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().split("\n")
    except:
        return []

def filter_viral_topics(raw_topics, niche="general"):
    """Uses LLM to pick the top 5 most viral topics relevant to the niche."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if provider == "openai" else None
    if not client: return raw_topics[:10]
    
    prompt = f"""
    Analyze these raw trending topics:
    {raw_topics}
    
    Select the Top 5 that have the highest 'Viral Potential' for a {niche} YouTube Shorts channel.
    Focus on curiosity, shocking facts, or high utility.
    Return ONLY a JSON list of strings.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return list(data.values())[0] if isinstance(data, dict) else data
    except Exception as e:
        print(f"⚠️  Filtering failed: {e}")
        return raw_topics[:5]

def get_trending_topics(keywords=None, timeframe="now 7-d", geo="US", top_n=5):
    """
    Aggregates trends from Google, YouTube, and TikTok style analysis.
    """
    if keywords is None: keywords = DEFAULT_KEYWORDS
    
    print("🚀 Aggregating multi-platform viral trends...")
    
    google_trends = []
    try:
        pytrends = TrendReq(hl="en-US", tz=360) 
        pytrends.build_payload(keywords[:5], timeframe=timeframe, geo=geo)
        related = pytrends.related_queries()
        for key in related:
            top_df = related[key].get("top")
            if top_df is not None and not top_df.empty:
                google_trends += top_df["query"].tolist()
    except: pass

    yt_trends = get_trending_youtube_topics()
    tt_trends = get_tiktok_trending()
    
    all_raw = list(set(google_trends + yt_trends + tt_trends))
    
    if not all_raw:
        print("ℹ️  No external trends found. Generating dynamic ideas...")
        return generate_fallback_topics(keywords)[:top_n]
    
    print(f"✅ Collected {len(all_raw)} raw trends. Selecting best for niche...")
    return filter_viral_topics(all_raw, niche=keywords[0])[:top_n]

def generate_fallback_topics(keywords):
    """Fallback LLM logic..."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Generate 10 viral YouTube Shorts topics for: {', '.join(keywords)}. One per line."
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    return [t.strip("- ").strip("1234567890. ") for t in response.choices[0].message.content.split("\n") if t.strip()]

def pick_trending_topic(keywords=None, interactive=True):
    """Selects a topic from the aggregated list."""
    topics = get_trending_topics(keywords=keywords)
    if not topics: return None

    print("\n🔥 Viral Trends Selected for You:")
    for i, t in enumerate(topics, 1): print(f"  [{i}] {t}")

    if not interactive:
        chosen = random.choice(topics)
        print(f"\n✅ Auto-selected: {chosen}")
        return chosen

    choice = input(f"\nSelect a topic # [1-{len(topics)}] or Enter for #1: ").strip()
    return topics[int(choice)-1] if choice.isdigit() and 1<=int(choice)<=len(topics) else topics[0]

if __name__ == "__main__":
    pick_trending_topic()
