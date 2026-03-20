import os
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_background_video(query, output_path="assets/video.mp4", min_duration=30):
    """
    Fetch a portrait-oriented stock video from Pexels with randomization.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    import random

    headers = {"Authorization": api_key}
    page = random.randint(1, 10)

    # Fetch with a random page
    search_url = (
        f"https://api.pexels.com/videos/search"
        f"?query={query}&per_page=15&orientation=portrait&page={page}"
    )

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        # Fallback to page 1 if random page fails
        search_url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait&page=1"
        response = requests.get(search_url, headers=headers)

    data = response.json()
    videos = data.get("videos", [])
    if not videos:
        print(f"No videos found for query: {query}")
        return None

    # Pick a random one from the top results for variety
    selected = random.choice(videos[:5])
    
    # Prefer HD portrait file
    video_files = selected.get("video_files", [])
    if not video_files:
        print(f"No video files in result for {query}.")
        return None

    # Pick the highest quality portrait file
    portrait_files = [f for f in video_files if (f.get("width") or 0) < (f.get("height") or 1)]
    best = sorted(portrait_files or video_files, key=lambda f: (f.get("width") or 0), reverse=True)[0]
    video_url = best["link"]

    print(f"Downloading video from: {video_url}")
    video_response = requests.get(video_url, stream=True)
    video_response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in video_response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return output_path

def fetch_multi_video_clips(queries, output_dir="assets/clips", min_clip_duration=5):
    """
    Downloads multiple clips based on a list of queries.
    Clears the output_dir first to ensure no old clips are reused.
    """
    import shutil
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    clip_paths = []
    
    # Header for Pexels
    api_key = os.getenv("PEXELS_API_KEY")
    headers = {"Authorization": api_key}
    
    print(f"🎬 Fetching {len(queries)} clips for retention upgrade (Randomized)...")
    
    import random
    
    for i, query in enumerate(queries):
        try:
            filename = f"clip_{i}_{query.replace(' ', '_')[:20]}.mp4"
            target_path = os.path.join(output_dir, filename)
            
            # Search Pexels with a random page for variety
            page = random.randint(1, 5) 
            search_url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait&page={page}"
            resp = requests.get(search_url, headers=headers)
            resp.raise_for_status()
            
            videos = resp.json().get("videos", [])
            if not videos:
                # If random page returns nothing, try page 1
                search_url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait&page=1"
                resp = requests.get(search_url, headers=headers)
                videos = resp.json().get("videos", [])
                
            if not videos:
                print(f"⚠️  No clips found for '{query}', skipping.")
                continue
                
            # Pick a random clip from the results for even more variety
            selected = random.choice(videos[:5])
            
            # Get video file URL
            video_files = selected.get("video_files", [])
            portrait_files = [f for f in video_files if f.get("width", 0) < f.get("height", 1)]
            best = sorted(portrait_files or video_files, key=lambda f: f.get("width", 0), reverse=True)[0]
            video_url = best["link"]
            
            # Download
            print(f"   [{i+1}/{len(queries)}] Downloading clip (page {page}): {query}...")
            v_resp = requests.get(video_url, stream=True)
            with open(target_path, "wb") as f:
                for chunk in v_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            clip_paths.append(target_path)
            
        except Exception as e:
            print(f"   ❌ Failed to fetch clip for '{query}': {e}")
            
    return clip_paths


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    test_query = "mind psychology"
    print(f"Fetching video for: '{test_query}'...")
    try:
        path = fetch_background_video(test_query)
        if path:
            print(f"Video saved to: {path}")
    except Exception as e:
        print(f"Error: {e}")
