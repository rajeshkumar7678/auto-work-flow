import os
import subprocess
import shutil
import json

def _get_duration(ffprobe_bin, path):
    """Return media duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            ffprobe_bin, "-v", "quiet",
            "-print_format", "json",
            "-show_format", path,
        ],
        capture_output=True, text=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def build_final_video(video_paths, audio_path, srt_path, output_path="output/final_video.mp4", durations=None):
    """
    Assembles the final video using ONE or MULTIPLE input clips.
    If 'durations' is provided, each clip is trimmed to match its specific share of the audio.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    ffmpeg_bin = shutil.which("ffmpeg")
    ffprobe_bin = shutil.which("ffprobe")
    if not ffmpeg_bin:
        raise FileNotFoundError("ffmpeg not found.")

    audio_path = os.path.abspath(audio_path)
    srt_path = os.path.abspath(srt_path)
    output_path = os.path.abspath(output_path)
    
    audio_duration = _get_duration(ffprobe_bin, audio_path)
    print(f"🎵 Audio duration: {audio_duration:.1f}s")

    if isinstance(video_paths, str):
        video_paths = [video_paths]
    video_paths = [os.path.abspath(p) for p in video_paths]
    
    srt_filter = srt_path.replace("\\", "/").replace(":", "\\:")

    # Caption Style: Larger, Bold, and safe MarginV
    CAPTION_STYLE = "FontSize=34,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Bold=1,MarginV=150"

    if len(video_paths) == 1:
        # Loop single clip
        cmd = [
            ffmpeg_bin,
            "-stream_loop", "-1",
            "-i", video_paths[0],
            "-i", audio_path,
            "-t", str(audio_duration),
            "-vf", (
                f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
                f"subtitles='{srt_filter}':force_style='{CAPTION_STYLE}'"
            ),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            output_path,
        ]
    else:
        # Build complex filter for multi-clip concat with trimming
        inputs = []
        filter_parts = []
        
        for i, path in enumerate(video_paths):
            inputs.extend(["-i", path])
            
            # Use specific duration if provided, else default to equal share
            clip_dur = durations[i] if (durations and i < len(durations)) else (audio_duration / len(video_paths))
            
            # Scale, Crop, and Trim
            # We use trim=0:duration to take the first X seconds of the clip
            filter_parts.append(
                f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
                f"trim=0:{clip_dur:.2f},setpts=PTS-STARTPTS[v{i}];"
            )
        
        # Concatenate the trimmed clips
        concat_filter = "".join([f"[v{i}]" for i in range(len(video_paths))])
        concat_filter += f"concat=n={len(video_paths)}:v=1:a=0[basev];"
        
        # Add subtitles
        subtitle_filter = f"[basev]subtitles='{srt_filter}':force_style='{CAPTION_STYLE}'[finalv]"
        
        full_filter = "".join(filter_parts) + concat_filter + subtitle_filter

        cmd = [
            ffmpeg_bin,
            *inputs,
            "-i", audio_path,
            "-filter_complex", full_filter,
            "-map", "[finalv]",
            "-map", f"{len(video_paths)}:a", 
            "-t", str(audio_duration), 
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            output_path,
        ]

    print(f"⚙️  Building final video with {len(video_paths)} clips and precision trimming...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FFmpeg stderr:\n{result.stderr[-3000:]}")
        raise RuntimeError("FFmpeg failed to build video")

    print(f"✅ Final video: {output_path}")
    return output_path

if __name__ == "__main__":
    v_path = "assets/video.mp4"
    a_path = "assets/voice.mp3"
    s_path = "assets/captions.srt"
    
    # Ensure assets exist for testing
    if not os.path.exists(v_path):
        print("Test failed: assets/video.mp4 not found. Run video_fetcher.py first.")
    elif not os.path.exists(a_path):
        print("Test failed: assets/voice.mp3 not found. Run voice_generator.py (or create dummy) first.")
    elif not os.path.exists(s_path):
        print("Test failed: assets/captions.srt not found. Run caption_generator.py first.")
    else:
        print("Building final video...")
        try:
            out = build_final_video(v_path, a_path, s_path)
            print(f"Final video created at: {out}")
        except Exception as e:
            print(f"Error: {e}")
