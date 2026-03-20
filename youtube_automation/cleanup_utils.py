import os
import time
import shutil

def cleanup_assets(assets_dir="assets"):
    """Deletes all files in the assets directory."""
    if not os.path.exists(assets_dir):
        return
    
    print(f"🧹 Cleaning up assets in '{assets_dir}'...")
    for filename in os.listdir(assets_dir):
        file_path = os.path.join(assets_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"⚠️ Failed to delete {file_path}. Reason: {e}")

def cleanup_old_outputs(output_dir="output", days=2):
    """Deletes files in the output directory that are older than 'days'."""
    if not os.path.exists(output_dir):
        return
    
    print(f"🧹 Checking for old outputs in '{output_dir}' (older than {days} days)...")
    now = time.time()
    cutoff = now - (days * 86400)
    
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff:
                    print(f"🗑️ Deleting old output: {filename}")
                    os.unlink(file_path)
        except Exception as e:
            print(f"⚠️ Failed to delete {file_path}. Reason: {e}")

if __name__ == "__main__":
    # Test cleanup
    cleanup_assets()
    cleanup_old_outputs()
