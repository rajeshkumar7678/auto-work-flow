import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from football_trends import FootballTrendScout
from core_pipeline import run_youtube_pipeline

def main():
    print("--- Running Football Trend Scout Test ---")
    scout = FootballTrendScout()
    trends = scout.get_football_trends()

    if not trends:
        print("No trends found, using fallback topic.")
        topic = "2026 FIFA World Cup qualifiers"
    else:
        topic = trends[0]["topic"]
        print(f"Top Trend Found: {topic}")

    print(f"\n--- Running Core Pipeline for Topic: '{topic}' ---")
    try:
        # Run the full pipeline without auto-upload to verify rendering
        video_path, seo_meta = run_youtube_pipeline(
            topic=topic,
            language="English",
            duration="45-60 seconds",
            auto_upload=False
        )
        print("\n✅ SUCCESS! Video build completed successfully!")
        print(f"Video Path: {video_path}")
        print(f"SEO Meta Title: {seo_meta.get('title')}")
    except Exception as e:
        print(f"\n❌ FAILURE: Pipeline failed: {e}")

if __name__ == "__main__":
    main()
