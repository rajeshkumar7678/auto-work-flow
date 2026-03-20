import os
from core_pipeline import run_youtube_pipeline
from trending_topics import pick_trending_topic

DURATION_OPTIONS = {
    "1": ("45-60 seconds", "YouTube Shorts"),
    "2": ("2 minutes",     "Standard short video"),
    "3": ("5 minutes",     "Long-form video"),
}

LANGUAGE_OPTIONS = {
    "1": "English",
    "2": "Hindi",
}

def main():
    print("=" * 40)
    print("   🎬 YouTube Automation Tool (Manual Mode)")
    print("=" * 40)

    # --- Language selection ---
    print("\nSelect language:")
    print("  [1] 🇺🇸 English")
    print("  [2] 🇮🇳 Hindi")
    lang_choice = input("Choice [1/2] (default: 1): ").strip() or "1"
    language = LANGUAGE_OPTIONS.get(lang_choice, "English")
    print(f"✅ Language: {language}")

    # --- Topic selection ---
    print("\nHow do you want to pick the topic?")
    print("  [1] 🔥 Auto-fetch from Google Trends")
    print("  [2] ✏️  Enter my own topic")
    src = input("Choice [1/2] (default: 1): ").strip() or "1"

    if src == "1":
        n_input = input("\nEnter your niche (e.g. psychology, tech, fitness) [default: psychology]: ").strip()
        niche = [k.strip() for k in n_input.split(",")] if n_input else None
        
        topic = pick_trending_topic(keywords=niche, interactive=True)
        if not topic:
            topic = input("No trending topics found. Enter topic manually: ").strip()
    else:
        topic = input("Enter the topic for your video: ").strip()

    if not topic:
        print("Topic cannot be empty.")
        return

    # --- Duration selection ---
    print("\nSelect video duration:")
    for key, (dur, label) in DURATION_OPTIONS.items():
        print(f"  [{key}] {dur:<15}  ({label})")
    dur_choice = input("Choice [1/2/3] (default: 1): ").strip() or "1"
    duration, _ = DURATION_OPTIONS.get(dur_choice, DURATION_OPTIONS["1"])
    print(f"\n✅ Duration: {duration}")

    # --- Run Pipeline ---
    try:
        # result is a tuple: (final_video_path, seo_meta)
        video_path, seo_meta = run_youtube_pipeline(
            topic=topic, 
            language=language, 
            duration=duration, 
            auto_upload=False # We ask manually at the end
        )
        
        # Manual Upload Confirmation
        print("\n" + "="*40)
        print("🎬 VIDEO READY FOR UPLOAD!")
        print("="*40)
        
        confirm = input("\nDo you want to upload this video to YouTube now? (y/n): ").strip().lower()
        
        if confirm == 'y':
            from upload_video import upload_video
            print("\n[7/7] Uploading to YouTube...")
            
            # Ensure we have a string path
            actual_path = video_path[0] if isinstance(video_path, tuple) else video_path
            
            video_id = upload_video(
                video_file=actual_path,
                title=seo_meta.get("title", topic),
                description=seo_meta.get("description", ""),
                tags=seo_meta.get("tags", [])
            )
            print(f"\n✨ SUCCESS! Your video is live at: https://youtu.be/{video_id}")
        else:
            print(f"\nSkipping upload. You can find your video here: {video_path}")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")

if __name__ == "__main__":
    main()
