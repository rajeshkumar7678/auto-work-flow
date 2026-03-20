import pickle
import json
import os

def convert_pickle_to_json(pickle_file="token.pickle", json_output="token.json"):
    if not os.path.exists(pickle_file):
        print(f"❌ Error: {pickle_file} not found.")
        return

    try:
        with open(pickle_file, "rb") as f:
            creds = pickle.load(f)
        
        # Extract the dictionary from the credentials object
        creds_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
            "expiry": creds.expiry.isoformat() if hasattr(creds.expiry, 'isoformat') else creds.expiry
        }
        
        with open(json_output, "w") as f:
            json.dump(creds_data, f, indent=4)
        
        print(f"✅ Successfully converted {pickle_file} to {json_output}")
        print("\n--- NEXT STEPS ---")
        print(f"1. Open {json_output} and copy the text.")
        print("2. Paste it into GitHub Settings -> Secrets -> Actions -> YOUTUBE_TOKEN_JSON")
        print(f"3. Do the same for your CLIENT_SECRETS_JSON.")
    except Exception as e:
        print(f"❌ Failed to convert: {e}")

if __name__ == "__main__":
    # Change directory to youtube_automation if needed
    if os.path.exists("youtube_automation/token.pickle"):
        os.chdir("youtube_automation")
    convert_pickle_to_json()
