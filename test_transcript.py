from youtube_transcript_api import YouTubeTranscriptApi

def test_transcript():
    print("Testing YouTubeTranscriptApi...")
    print(f"Available attributes: {dir(YouTubeTranscriptApi)}")
    
    try:
        # Try fetching a known video transcript (Google Developers)
        video_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw" # Wait, this is a channel ID. Let's use a video ID.
        # Video: "Google I/O 2023 in under 10 minutes" -> "cNfINi5CNbY"
        video_id = "cNfINi5CNbY" 
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print("Success! Transcript fetched.")
        print(transcript[:2])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_transcript()
