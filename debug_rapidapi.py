import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

def test_rapidapi(video_id):
    api_key = os.getenv("RAPIDAPI_KEY")
    print(f"Testing RapidAPI for Video ID: {video_id}")
    print(f"API Key present: {bool(api_key)}")
    
    url = "https://youtube-transcripts.p.rapidapi.com/youtube/transcript"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "youtube-transcripts.p.rapidapi.com"
    }
    params = {
        "videoId": video_id,
        "lang": "en"
    }
    
    for attempt in range(3):
        print(f"Attempt {attempt + 1}...")
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, params=params, timeout=60)
            elapsed = time.time() - start_time
            print(f"Response (Status: {response.status_code}) took {elapsed:.2f} seconds")
            
            if response.status_code == 200:
                print("Success!")
                print(response.text[:200])
                return
            else:
                print(f"Failed: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"Timed out after {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Exception: {e}")
            
test_rapidapi("x8TAAzTQHmE")
