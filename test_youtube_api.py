import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def test_api():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in .env")
        return

    print(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")
    youtube = build("youtube", "v3", developerKey=api_key)

    # 1. Test with a KNOWN valid channel (Google Developers)
    known_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    print(f"\n--- Testing Known Channel ({known_id}) ---")
    try:
        response = youtube.channels().list(part="snippet", id=known_id).execute()
        if response.get("items"):
            print("SUCCESS: Found Google Developers channel.")
            print(f"Title: {response['items'][0]['snippet']['title']}")
        else:
            print("FAILURE: Could not find Google Developers channel. API Key might be invalid or quota exceeded.")
            print(f"Response: {response}")
    except Exception as e:
        print(f"ERROR: {e}")

    # 2. Test with User's Channel
    user_id = "UCNYx1hR78bT5M0wSpOcILBw" # The one failing
    print(f"\n--- Testing User Channel ({user_id}) ---")
    try:
        response = youtube.channels().list(part="snippet", id=user_id).execute()
        if response.get("items"):
            print(f"SUCCESS: Found channel.")
            print(f"Title: {response['items'][0]['snippet']['title']}")
        else:
            print("FAILURE: Channel ID not found.")
            print(f"Response: {response}")
            
            # Try search
            print("Trying search fallback...")
            search_response = youtube.search().list(part="snippet", q=user_id, type="channel").execute()
            print(f"Search Response: {search_response}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_api()
