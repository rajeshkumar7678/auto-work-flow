import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

import json
from google.oauth2.credentials import Credentials

def get_authenticated_service(client_secrets_file=None):
    creds = None
    
    # 1. Try to load from environment variable (GitHub Actions mode)
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON")
    if token_json:
        print("🔐 Loading YouTube credentials from environment variable...")
        try:
            creds_data = json.loads(token_json)
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        except Exception as e:
            print(f"⚠️ Failed to load YOUTUBE_TOKEN_JSON: {e}")

    # 2. Try to load from local token.pickle (Local mode)
    if not creds and os.path.exists("token.pickle"):
        print("🔐 Loading YouTube credentials from token.pickle...")
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
            
    # 3. If there are no (valid) credentials available, handle refresh or login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            # Local interactive login fallback
            if not client_secrets_file:
                 # Find the client secret file automatically
                files = [f for f in os.listdir(".") if f.startswith("client_secret") and f.endswith(".json")]
                if not files:
                    # Check for env var CLIENT_SECRETS_JSON
                    client_secrets_json = os.environ.get("CLIENT_SECRETS_JSON")
                    if client_secrets_json:
                        print("🔐 Using CLIENT_SECRETS_JSON from environment...")
                        client_secrets_data = json.loads(client_secrets_json)
                        flow = InstalledAppFlow.from_client_config(client_secrets_data, SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        raise FileNotFoundError("No client_secret.json or CLIENT_SECRETS_JSON found.")
                else:
                    client_secrets_file = files[0]
                    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
                    creds = flow.run_local_server(port=0)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
                creds = flow.run_local_server(port=0)

        # Save the credentials locally if not in GHA (or for next run)
        if not os.environ.get("GITHUB_ACTIONS"):
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def upload_video(video_file, title, description, tags, category_id="27"):
    """
    Uploads a video to YouTube.
    category_id "27" is Education.
    """
    # Find the client secret file automatically
    files = [f for f in os.listdir(".") if f.startswith("client_secret") and f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No client_secret.json found in directory.")
    
    client_secrets_file = files[0]
    youtube = get_authenticated_service(client_secrets_file)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",  # Can be "public", "private", or "unlisted"
            "selfDeclaredMadeForKids": False,
        }
    }

    # Call the API's videos().insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
    )

    print(f"🚀 Uploading video: {video_file}...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%...")

    print(f"✅ Video Uploaded Successfully! Video ID: {response['id']}")
    return response["id"]

if __name__ == "__main__":
    # Test script (will require interactive login on first run)
    print("YouTube Uploader Test Mode")
    print("Ensure you have client_secret.json in the same folder.")
    # upload_video("path/to/video.mp4", "Test Title", "Test Desc", ["test", "tags"])
