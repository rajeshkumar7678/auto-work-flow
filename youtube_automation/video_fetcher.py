import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

import requests
import random
import shutil
from dotenv import load_dotenv


load_dotenv()

def fetch_ai_image(query, output_path):
    """Generate a cinematic AI image using HuggingFace Flux Schnell."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None
        
    print(f"🎨 Generating AI Image for: '{query}'...")
    api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": f"{query}, cinematic lighting, dark and moody, extremely detailed, highly realistic, 8k, portrait orientation",
        "parameters": {"width": 1024, "height": 1024} # Schnell usually outputs 1024x1024 max via free API
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            print(f"⚠️ HF API Error: {response.status_code}")
    except Exception as e:
        print(f"⚠️ HF API Exception: {e}")
    return None

def fetch_pixabay_video(query, output_path):
    """Fetch video from Pixabay API."""
    api_key = os.getenv("PIXABAY_API_KEY")
    if not api_key:
        return None
        
    print(f"🎥 Fetching Pixabay video for: '{query}'...")
    url = f"https://pixabay.com/api/videos/?key={api_key}&q={requests.utils.quote(query)}&video_type=all&per_page=10"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        hits = data.get("hits", [])
        if not hits:
            return None
            
        selected = random.choice(hits[:5])
        # Find best resolution (prefer portrait if available, but Pixabay often has landscape, video_builder will crop it)
        videos = selected.get("videos", {})
        best = videos.get("large") or videos.get("medium") or videos.get("small")
        if not best or not best.get("url"):
            return None
            
        video_url = best["url"]
        v_resp = requests.get(video_url, stream=True, timeout=10)
        with open(output_path, "wb") as f:
            for chunk in v_resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except Exception as e:
        print(f"⚠️ Pixabay API Exception: {e}")
    return None

def fetch_pexels_video(query, output_path):
    """Fetch video from Pexels API."""
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return None
        
    print(f"🎥 Fetching Pexels video for: '{query}'...")
    headers = {"Authorization": api_key}
    page = random.randint(1, 3)
    search_url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait&page={page}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            search_url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait&page=1"
            response = requests.get(search_url, headers=headers, timeout=10)
            
        videos = response.json().get("videos", [])
        if not videos:
            return None
            
        selected = random.choice(videos[:5])
        video_files = selected.get("video_files", [])
        if not video_files:
            return None
            
        portrait_files = [f for f in video_files if (f.get("width") or 0) < (f.get("height") or 1)]
        best = sorted(portrait_files or video_files, key=lambda f: (f.get("width") or 0), reverse=True)[0]

        
        v_resp = requests.get(best["link"], stream=True, timeout=10)
        with open(output_path, "wb") as f:
            for chunk in v_resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except Exception as e:
        print(f"⚠️ Pexels API Exception: {e}")
    return None

def fetch_background_video(query, output_path="assets/video.mp4", min_duration=30):
    res = fetch_pixabay_video(query, output_path)
    if not res:
        res = fetch_pexels_video(query, output_path)
    return res

def fetch_multi_video_clips(scenes, output_dir="assets/clips", min_clip_duration=5):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    clip_paths = []
    print(f"🎬 Fetching {len(scenes)} clips (Scene-Based AI + Stock Retrieval)...")
    
    for i, scene in enumerate(scenes):
        scene_desc = scene.get("scene_description", "cinematic")
        emotion = scene.get("emotion", "dramatic")
        keywords = scene.get("keywords", ["cinematic"])
        if not isinstance(keywords, list):
            keywords = [keywords] if keywords else ["cinematic"]
            
        # Safe filename base
        safe_keyword = keywords[0] if keywords else "clip"
        filename_base = f"clip_{i}_{safe_keyword.replace(' ', '_')[:15]}"
        
        # 50% chance to generate AI image instead of video (makes it look like a viral slideshow)
        chosen_ai = random.random() < 0.5
        
        res = None
        if chosen_ai:
            target_path = os.path.join(output_dir, f"{filename_base}.png")
            ai_prompt = f"{scene_desc}, emotion: {emotion}"
            res = fetch_ai_image(ai_prompt, target_path)
            
        # If we chose stock video, or if AI generation failed (e.g. API rate limit), try stock videos
        if not res:
            target_path = os.path.join(output_dir, f"{filename_base}.mp4")
            # Try keywords sequentially to maximize chances of getting a specific hit
            for kw in keywords:
                res = fetch_pixabay_video(kw, target_path)
                if not res:
                    res = fetch_pexels_video(kw, target_path)
                if res:
                    break
                    
        # If stock video fails and we didn't try AI yet, try AI as a fallback
        if not res and not chosen_ai:
            target_path = os.path.join(output_dir, f"{filename_base}.png")
            ai_prompt = f"{scene_desc}, emotion: {emotion}"
            res = fetch_ai_image(ai_prompt, target_path)
            
        # Ultimate fallback: generic cinematic stock video
        if not res:
            target_path = os.path.join(output_dir, f"{filename_base}.mp4")
            print(f"⚠️  Both AI Image and keyword stock failed for scene {i}. Fetching general cinematic fallback...")
            res = fetch_pixabay_video("cinematic dramatic", target_path)
            if not res:
                res = fetch_pexels_video("cinematic dramatic", target_path)
                
        if res:
            clip_paths.append(res)
        else:
            print(f"   ❌ Critical error: Failed to fetch ANYTHING for scene {i}")
            
    return clip_paths

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    test_query = "mystery dark forest"
    print(fetch_ai_image(test_query, "assets/test_ai_image.png"))

