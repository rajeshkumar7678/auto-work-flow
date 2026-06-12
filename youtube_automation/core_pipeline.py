import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

import shutil

from script_generator import generate_script, detect_topic_type
from voice_generator import generate_voice
from video_fetcher import fetch_background_video
from caption_generator import generate_srt
from video_builder import build_final_video, _get_duration
from seo_generator import generate_seo
from upload_video import upload_video
from trending_topics import get_trending_topics
from cleanup_utils import cleanup_assets, cleanup_old_outputs

def run_youtube_pipeline(topic, language="English", duration="45-60 seconds", auto_upload=False, content_mode=None):
    """
    Core pipeline logic that can be called by main.py (manual) 
    or autonomous_pipeline.py (automatic).
    """
    if content_mode is None:
        content_mode = os.getenv("CONTENT_MODE", "general").strip().lower()

    # [NEW] Pre-run cleanup: Delete outputs older than 2 days
    cleanup_old_outputs(days=2)

    print(f"\n🚀 Starting Pipeline for: '{topic}'")

    print(f"   Language: {language} | Duration: {duration} | Auto-upload: {auto_upload} | Mode: {content_mode}")
    print("-" * 40)

    try:
        # Step 1: Script Generation
        print(f"\n[1/7] Generating script in {language}...")
        
        research_data = None
        if content_mode == "football":
            from content_researcher import ContentResearcher
            researcher = ContentResearcher()
            research_data = researcher.research_topic(topic)
            
        script = generate_script(topic, duration=duration, language=language, research_data=research_data)
        print("Script generated successfully.")

        
        # Step 2: Voice Generation
        print("\n[2/7] Generating voice...")
        voice_path = generate_voice(script, language=language)
        print(f"Voice saved to: {voice_path}")
        
        # Get actual audio duration for caption sync
        ffprobe_bin = shutil.which("ffprobe")
        audio_duration = _get_duration(ffprobe_bin, voice_path)
        
        # Step 3: Multi-Clip Visual Matching (Step 11 Upgrade)
        from script_parser import parse_script_to_scenes
        from video_fetcher import fetch_multi_video_clips
        
        print("\n[3/7] Matching visual scenes (Multi-clip)...")
        scenes = parse_script_to_scenes(script, content_mode=content_mode)

        
        # Ensure scenes list is not empty
        if not scenes:
            scenes = [{"text": script, "scene_description": topic, "emotion": "dramatic", "keywords": [topic]}]

        # Calculate durations for each scene to ensure perfect visual sync
        total_words = len(script.split())
        scene_durations = []
        for scene in scenes:
            scene_word_count = len(scene.get('text', '').split())
            # Calculate duration proportion
            proportion = scene_word_count / total_words if total_words > 0 else (1.0 / len(scenes))
            scene_durations.append(audio_duration * proportion)

            
        video_paths = fetch_multi_video_clips(scenes)
        if not video_paths:
            print("⚠️  No specific clips found, falling back to general search.")
            video_paths = [fetch_background_video(topic, min_duration=audio_duration)]
            scene_durations = [audio_duration]
        
        # Step 4: Caption Generation
        print("\n[4/7] Generating captions...")
        srt_path = generate_srt(text=script, audio_duration=audio_duration, audio_path=voice_path)
        print(f"Captions saved to: {srt_path}")
        
        # Step 5: Video Building
        print("\n[5/7] Building final video...")
        
        # Sanitize topic for filename (remove illegal characters like : | / \ ? * < > ")
        import re
        safe_topic = re.sub(r'[<>:"/\\|?*]', '', topic).replace(' ', '_')
        output_name = f"{safe_topic}_final.mp4"
        output_path = f"output/{output_name}"
        
        topic_type = detect_topic_type(topic)
        final_video = build_final_video(video_paths, voice_path, srt_path, output_path, durations=scene_durations, mood=topic_type)

        
        # Step 6: SEO Metadata Generation
        print("\n[6/7] Generating SEO metadata...")
        seo_meta, seo_path = generate_seo(topic, research_data=research_data)
        print(f"SEO metadata saved to: {seo_path}")
        print(f"Viral Title: {seo_meta.get('title')}")

        # Step 7: Upload
        if auto_upload:
            print("\n[7/7] Auto-uploading to YouTube...")
            video_id = upload_video(
                video_file=final_video,
                title=seo_meta.get("title", topic),
                description=seo_meta.get("description", ""),
                tags=seo_meta.get("tags", [])
            )
            print(f"✅ Success! Video ID: {video_id}")
            cleanup_assets() # Clean up all temp assets after successful upload
            return video_id, seo_meta
        else:
            print("\n[7/7] Skipping upload (manual mode).")
            cleanup_assets() # Optional: also clean assets in manual mode if desired
            return final_video, seo_meta


    except Exception as e:
        print(f"\n❌ ERROR in pipeline: {e}")
        raise e
