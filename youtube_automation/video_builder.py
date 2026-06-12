import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

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
    if result.returncode != 0:
        return 0
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def rename_user_music():
    """Renames specific uploaded music files to clean names."""
    base = "static_assets"
    if not os.path.exists(base):
        return
        
    mappings = {
        "alexgrohl-dark-mystery-trailer-taking-our-time-131566.mp3": "Tension Build-Up.mp3",
        "jonasblakewood-emotional-46-sec-527469.mp3": "Emotional Cinematic.mp3",
        "nastelbom-suspense-487702.mp3": "Suspense Ambient.mp3"
    }
    
    for old_name, new_name in mappings.items():
        old_path = os.path.join(base, old_name)
        new_path = os.path.join(base, new_name)
        if os.path.exists(old_path) and not os.path.exists(new_path):
            try:
                os.rename(old_path, new_path)
                print(f"🎵 Renamed music: '{old_name}' -> '{new_name}'")
            except Exception as e:
                print(f"⚠️ Failed to rename '{old_name}': {e}")


def build_final_video(video_paths, audio_path, srt_path, output_path="output/final_video.mp4", durations=None, thumbnail_path=None, mood="cinematic_story"):
    """
    Assembles the final video using ONE or MULTIPLE input clips.
    Includes viral hacks:
    - Prepends thumbnail for 0.2s (Hook Frame)
    - Ken Burns Effect: Continuous 1.0x to 1.15x zoom for every clip.
    - Multi-track Audio: Voice + Looping Background Music + Transition SFX.
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
    print(f"Audio duration: {audio_duration:.1f}s")

    if isinstance(video_paths, str):
        video_paths = [video_paths]
    video_paths = [os.path.abspath(p) for p in video_paths]
    
    # Caption Style: Properly scaled for Shorts (384x288 internal ASS resolution)
    CAPTION_STYLE = "FontSize=24,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Bold=1,MarginV=70"

    # --- Viral Hack: Ken Burns (Smooth Constant Zoom) ---
    # We use scale + zoompan. 
    # Logic: Scale to a larger size first, then zoom in slowly based on 'on' (frame number).
    # d='clip_frames' ensures the zoom spans the entire clip duration.
    # We target 25-30fps. 1.0 to 1.15 zoom over duration.
    def get_zoom_filter(dur_sec, is_image):
        fps = 30
        total_frames = int(dur_sec * fps)
        total_frames = max(1, total_frames)
        d_val = total_frames if is_image else 1
        return f"scale=1280:2275,zoompan=z='min(zoom+0.0005,1.15)':d={d_val}:s=1080x1920:fps={fps},unsharp=5:5:1.5:5:5:0.0,format=yuv420p"

    inputs = []
    filter_parts = []
    
    # 1. Handle Thumbnail Prepend (0.2s)
    if thumbnail_path and os.path.exists(thumbnail_path):
        inputs.extend(["-loop", "1", "-t", "0.2", "-i", os.path.abspath(thumbnail_path)])
        filter_parts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p[v_thumb];")
        input_offset = 1
    else:
        input_offset = 0

    # 2. Add Background Video Inputs
    for i, path in enumerate(video_paths):
        clip_dur = durations[i] if (durations and i < len(durations)) else (audio_duration / len(video_paths))
        is_img = path.lower().endswith((".png", ".jpg", ".jpeg"))
        
        if is_img:
            inputs.extend(["-loop", "1", "-t", str(clip_dur + 1), "-i", path])
        else:
            inputs.extend(["-i", path])
        
        idx = i + input_offset
        zoom_filter = get_zoom_filter(clip_dur, is_img)
        
        # Step: Basic scaling, then the Ken Burns zoompan, then ensure yuv420p
        # We ensure pix_fmt is consistent for concatenation
        filter_parts.append(
            f"[{idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
            f"trim=0:{clip_dur:.2f},setpts=PTS-STARTPTS,{zoom_filter}[v{idx}];"
        )
    
    # 3. Concatenate all streams
    concat_list = []
    if input_offset > 0:
        concat_list.append("[v_thumb]")
    for i in range(len(video_paths)):
        concat_list.append(f"[v{i + input_offset}]")
        
    concat_filter = "".join(concat_list) + f"concat=n={len(concat_list)}:v=1:a=0[basev];"
    
    # 4. Add Subtitles
    try:
        rel_srt_path = os.path.relpath(srt_path, start=os.getcwd()).replace("\\", "/")
    except:
        rel_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")
        
    subtitle_filter = f"[basev]subtitles='{rel_srt_path}':force_style='{CAPTION_STYLE}'[finalv]"

    # --- Audio Layering Assets (Permanent Static Assets) ---
    rename_user_music()
    
    # Select background music based on the video mood
    music_filename = "background_viral.mp3" # default fallback
    
    if mood == "emotional" or mood == "karma":
        music_filename = "Emotional Cinematic.mp3"
    elif mood == "mystery" or mood == "shocking_facts":
        music_filename = "Suspense Ambient.mp3"
    elif mood == "billionaire":
        music_filename = "Tension Build-Up.mp3"
        
    music_path = os.path.join("static_assets", music_filename)
    whoosh_path = "static_assets/whoosh.mp3"
    
    # If the targeted mood track doesn't exist, try default background_viral.mp3
    if not os.path.exists(music_path):
        music_path = "static_assets/background_viral.mp3"
        
    # If background_viral.mp3 also doesn't exist, pick ANY mp3 file in static_assets
    if not os.path.exists(music_path):
        for f in os.listdir("static_assets") if os.path.exists("static_assets") else []:
            if f.endswith(".mp3") and f != "whoosh.mp3":
                music_path = os.path.join("static_assets", f)
                break
                
    if os.path.exists(music_path):
        print(f"🎵 Using Background Track: '{os.path.basename(music_path)}' (Mapped to mood: '{mood}')")
        
    # Track the audio input stream indices
    voice_idx = input_offset + len(video_paths)
    inputs.extend(["-i", audio_path])
    
    audio_filters = []
    audio_filters.append(f"[{voice_idx}:a]volume=1.0[voice_a];")
    mix_sources = ["[voice_a]"]
    
    # Next available input index starts after 'voice_idx + 1'
    next_input_idx = voice_idx + 1

    if os.path.exists(music_path):
        music_idx = next_input_idx
        inputs.extend(["-stream_loop", "-1", "-i", os.path.abspath(music_path)])
        audio_filters.append(f"[{music_idx}:a]volume=0.12,atrim=0:{audio_duration + 1}[bg_music];")
        mix_sources.append("[bg_music]")
        next_input_idx += 1

    if os.path.exists(whoosh_path):
        sfx_names = []
        whoosh_idx = next_input_idx
        inputs.extend(["-i", os.path.abspath(whoosh_path)])
        
        current_time = 0.2 if input_offset > 0 else 0
        for i in range(len(video_paths)):
            if i > 0:
                sfx_name = f"sfx{i}"
                delay_ms = int(current_time * 1000)
                audio_filters.append(f"[{whoosh_idx}:a]atrim=0:1,adelay={delay_ms}|{delay_ms},volume=0.8[{sfx_name}];")
                sfx_names.append(f"[{sfx_name}]")
            
            clip_dur = durations[i] if (durations and i < len(durations)) else (audio_duration / len(video_paths))
            current_time += clip_dur
            
        if sfx_names:
            if len(sfx_names) > 1:
                audio_filters.append(f"{''.join(sfx_names)}amix=inputs={len(sfx_names)}:dropout_transition=999[all_sfx];")
            else:
                audio_filters.append(f"{sfx_names[0]}anull[all_sfx];")
            mix_sources.append("[all_sfx]")

    if len(mix_sources) > 1:
        amix_filter = f"{''.join(mix_sources)}amix=inputs={len(mix_sources)}:duration=first:dropout_transition=999[final_a]"
    else:
        amix_filter = f"{mix_sources[0]}anull[final_a]"
    
    full_filter_complex = "".join(filter_parts) + concat_filter + subtitle_filter + ";" + "".join(audio_filters) + amix_filter

    cmd = [
        ffmpeg_bin,
        *inputs,
        "-filter_complex", full_filter_complex,
        "-map", "[finalv]",
        "-map", "[final_a]",
        "-t", str(audio_duration + (0.2 if input_offset > 0 else 0)), 
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-y",
        output_path,
    ]

    print(f"⚙️  Building premium viral video (Ken Burns Zoom + Multi-track Audio + Visual Hooks)...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FFmpeg stderr:\n{result.stderr[-3000:]}")
        raise RuntimeError("FFmpeg failed to build video")

    print(f"✅ Final video: {output_path}")
    return output_path

if __name__ == "__main__":
    print("Video Builder Ken Burns Engine Ready.")
