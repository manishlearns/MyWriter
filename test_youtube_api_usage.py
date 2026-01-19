from youtube_transcript_api import YouTubeTranscriptApi
print(dir(YouTubeTranscriptApi))
try:
    api = YouTubeTranscriptApi()
    print("YouTubeTranscriptApi can be instantiated.")
except Exception as e:
    print(f"YouTubeTranscriptApi CANNOT be instantiated: {e}")
