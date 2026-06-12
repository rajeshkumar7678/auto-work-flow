import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

import random
from core_pipeline import run_youtube_pipeline
from trending_topics import get_trending_topics

def run_autonomous_mode():
    """
    Runs a fully automated cycle:
    1. Pick a trending topic (automatic)
    2. Run the full pipeline including upload
    """
    print("\n" + "!" * 40)
    print("   🤖 YouTube Autonomous Agent Active")
    print("!" * 40)

    mode = os.getenv("CONTENT_MODE", "general").strip().lower()

    if mode == "football":
        print("⚽ Content Mode: Football/World Cup Real-time Trends")
        from football_trends import FootballTrendScout
        scout = FootballTrendScout()
        trends = scout.get_football_trends()
        topics = [t["topic"] for t in trends] if trends else []
        if not topics:
            print("❌ No trending football topics found. Agent hibernating.")
            return
        target_topic = topics[0]
    else:
        print("💼 Content Mode: General Niche Trends")
        # 1. Pick a niche randomly or use a favorite (High US CPM)
        niches = ["psychology tricks", "AI tools", "productivity hacks", "money habits", "tech secrets"]
        chosen_niche = random.choice(niches)
        print(f"🔍 Digging into niche: {chosen_niche}")

        # 2. Get trending topics (auto-fetch)
        topics = get_trending_topics(keywords=[chosen_niche])
        if not topics:
            print("❌ No trending topics found. Agent hibernating.")
            return
        # 3. Pick the #1 trending topic
        target_topic = topics[0]

    print(f"🔥 Target acquired: '{target_topic}'")


    # 4. Run the full pipeline with auto-upload enabled
    try:
        video_id, info = run_youtube_pipeline(
            topic=target_topic,
            language="English", # Default for autonomous
            duration="45-60 seconds", # Best for viral growth
            auto_upload=True
        )
        print(f"✅ Autonomous cycle complete! Video live at: https://youtu.be/{video_id}")
    except Exception as e:
        print(f"❌ Autonomous cycle failed: {e}")

if __name__ == "__main__":
    run_autonomous_mode()
