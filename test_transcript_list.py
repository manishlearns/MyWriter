from youtube_transcript_api import YouTubeTranscriptApi

def test_transcript_list():
    print("Testing YouTubeTranscriptApi.list_transcripts...")
    video_id = "cNfINi5CNbY" 
    
    try:
        # Try 'list_transcripts' if it exists, or 'list' based on dir() output
        if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            print("Calling list_transcripts...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for t in transcript_list:
                print(f"Found transcript: {t.language} ({t.language_code})")
                print(t.fetch()[:2])
                break
        # Try instantiating
        print("Instantiating YouTubeTranscriptApi...")
        api = YouTubeTranscriptApi()
        if hasattr(api, 'get_transcript'):
            print("Calling instance.get_transcript...")
            transcript = api.get_transcript(video_id)
            print(transcript[:2])
        elif hasattr(api, 'list'):
            print("Calling instance.list...")
            # Note: 'list' might return a list of transcripts or be a method to list them
            # Let's assume it returns something iterable or print it
            transcript = api.list(video_id)
            print(f"Result type: {type(transcript)}")
            print(transcript)
        else:
            print("Instance has neither get_transcript nor list.")


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_transcript_list()
