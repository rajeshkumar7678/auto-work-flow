import os
import shutil
from video_builder import build_final_video

# Use the actual conversation directory for testing
test_dir = r"d:\Projects\auto-work-flow\youtube_automation"
clips_dir = os.path.join(test_dir, "assets", "clips")

if os.path.exists(clips_dir):
    clips = [os.path.join(clips_dir, f) for f in os.listdir(clips_dir) if f.endswith(".mp4")]
else:
    clips = []

voice = os.path.join(test_dir, "assets", "voice.mp3")
srt = os.path.join(test_dir, "assets", "captions.srt")
output = os.path.join(test_dir, "output", "test_build_final.mp4")

if not clips:
    print(f"Error: No clips found in {clips_dir}")
elif not os.path.exists(voice):
    print(f"Error: Voice file not found at {voice}")
elif not os.path.exists(srt):
    print(f"Error: SRT file not found at {srt}")
else:
    print(f"Testing build with {len(clips)} clips...")
    try:
        build_final_video(clips[:3], voice, srt, output)
        print("Test build successful!")
    except Exception as e:
        print(f"Test build failed: {e}")
