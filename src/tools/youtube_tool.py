import os
import requests
import http.cookiejar
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api.proxies import GenericProxyConfig

class YouTubeTool:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if self.api_key:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)
        else:
            self.youtube = None

    def get_latest_videos(self, channel_id, max_results=5):
        if not self.youtube:
            return []
        
        try:
            # 1. Get Uploads Playlist ID
            channel_response = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()
            
            print(f"DEBUG: Channel Response for {channel_id}: {channel_response}")

            if not channel_response.get("items"):
                print(f"Channel ID lookup failed for {channel_id}. Trying search fallback...")
                # Fallback: Search for the channel
                search_response = self.youtube.search().list(
                    part="snippet",
                    q=channel_id,
                    type="channel",
                    maxResults=1
                ).execute()
                
                if not search_response.get("items"):
                    print(f"Channel not found via search either: {channel_id}")
                    return []
                
                # Use the ID found from search
                new_channel_id = search_response["items"][0]["snippet"]["channelId"]
                print(f"Found channel via search: {new_channel_id}")
                
                # Retry getting content details with new ID
                channel_response = self.youtube.channels().list(
                    part="contentDetails",
                    id=new_channel_id
                ).execute()
                
                if not channel_response.get("items"):
                     return []

            uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # 2. Get Videos from Playlist
            playlist_response = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in playlist_response.get("items", []):
                videos.append({
                    "video_id": item["snippet"]["resourceId"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"]
                })
            return videos
        except Exception as e:
            print(f"Error fetching videos for {channel_id}: {e}")
            if hasattr(e, 'content'):
                 print(f"Error content: {e.content}")
            return []

    def get_transcript_via_official_api(self, video_id):
        """
        Try to get transcript using YouTube's official Captions API.
        This doesn't get blocked but only works for videos with available captions.
        """
        if not self.youtube:
            return None
            
        try:
            # List available captions
            captions_response = self.youtube.captions().list(
                part="snippet",
                videoId=video_id
            ).execute()
            
            if not captions_response.get("items"):
                print(f"No captions available via official API for {video_id}")
                return None
            
            # Find English caption track
            english_caption = None
            for item in captions_response["items"]:
                lang = item["snippet"]["language"]
                if lang in ["en", "en-US", "en-GB"]:
                    english_caption = item
                    break
            
            if not english_caption:
                # Try any caption and note it's not English
                print("No English captions found, trying first available...")
                english_caption = captions_response["items"][0]
            
            # Download the caption track
            # Note: This requires OAuth2 authorization, not just API key
            # So this method is limited - it works for your own videos
            caption_id = english_caption["id"]
            
            # For public videos, we can't download directly without OAuth
            # But we can use the timedtext endpoint as a workaround
            caption_url = f"https://www.youtube.com/api/timedtext?lang=en&v={video_id}"
            response = requests.get(caption_url)
            
            if response.status_code == 200 and response.text:
                # Parse the XML response
                import re
                # Remove XML tags and extract text
                text = re.sub(r'<[^>]+>', ' ', response.text)
                text = ' '.join(text.split())  # Clean up whitespace
                return text
            
            return None
            
        except Exception as e:
            print(f"Official Captions API failed for {video_id}: {e}")
            return None

    def get_transcript_via_rapidapi(self, video_id):
        """
        Get transcript using RapidAPI YouTube Transcripts service.
        This bypasses YouTube's IP blocking since requests go through RapidAPI.
        """
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if not rapidapi_key:
            print("RAPIDAPI_KEY not set in environment")
            return None
        
        try:
            print(f"Fetching transcript via RapidAPI for {video_id}...")
            
            url = "https://youtube-transcripts.p.rapidapi.com/youtube/transcript"
            headers = {
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": "youtube-transcripts.p.rapidapi.com"
            }
            params = {
                "videoId": video_id,
                "lang": "en"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            print(f"RapidAPI response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response - extract text from content array
                if isinstance(data, dict) and "content" in data:
                    content = data["content"]
                    if isinstance(content, list):
                        transcript = " ".join([
                            item.get("text", "") 
                            for item in content if isinstance(item, dict)
                        ])
                        if transcript.strip():
                            return transcript
                    elif isinstance(content, str):
                        return content
                
                # Fallback: try other common fields
                if isinstance(data, list):
                    transcript = " ".join([
                        item.get("text", "") for item in data 
                        if isinstance(item, dict)
                    ])
                    if transcript.strip():
                        return transcript
                        
                elif isinstance(data, dict):
                    for field in ["transcript", "transcription", "text"]:
                        if field in data and data[field]:
                            return str(data[field])
            
            print(f"RapidAPI failed - Status: {response.status_code}, Response: {response.text[:500]}")
            return None
            
        except Exception as e:
            print(f"RapidAPI error: {e}")
            return None

    def get_transcript(self, video_id):
        """
        Get transcript - uses RapidAPI if configured, otherwise falls back to direct method.
        """
        # Try RapidAPI first (works on cloud without blocking)
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if rapidapi_key:
            transcript = self.get_transcript_via_rapidapi(video_id)
            if transcript:
                print("✅ Got transcript via RapidAPI")
                return transcript
            print("RapidAPI failed, trying fallback methods...")
        
        # Fallback: Try official API
        print(f"Attempting official captions API for {video_id}...")
        official_transcript = self.get_transcript_via_official_api(video_id)
        if official_transcript:
            print("Successfully fetched transcript via official API!")
            return official_transcript
        
        # Fallback: Try direct youtube-transcript-api
        print("Official API failed, trying youtube-transcript-api...")
        
        try:
            http_client = None
            if os.path.exists("cookies.txt"):
                try:
                    cookie_jar = http.cookiejar.MozillaCookieJar("cookies.txt")
                    cookie_jar.load()
                    http_client = requests.Session()
                    http_client.cookies = cookie_jar
                except Exception as e:
                    print(f"Warning: Failed to load cookies.txt: {e}")
            
            proxy_config = None
            proxy_url = os.getenv("YOUTUBE_PROXY")
            if proxy_url:
                proxy_config = GenericProxyConfig(
                    http_url=proxy_url,
                    https_url=proxy_url
                )

            if http_client or proxy_config:
                transcript_api = YouTubeTranscriptApi(http_client=http_client, proxy_config=proxy_config)
                transcript_list = transcript_api.list(video_id)
            else:
                transcript_api = YouTubeTranscriptApi()
                transcript_list = transcript_api.list(video_id)
            
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            transcript_data = transcript.fetch()
            
            formatter = TextFormatter()
            return formatter.format_transcript(transcript_data)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching transcript for {video_id}: {error_msg}")
            if "blocking requests" in error_msg or "Sign in to confirm you're not a bot" in error_msg:
                print("\n!!! YOUTUBE IP BLOCK DETECTED !!!")
                print("If you are running on Streamlit Cloud, you MUST use a proxy or RapidAPI.")
                print("1. Get a residential proxy and add it to Streamlit Secrets as 'YOUTUBE_PROXY'.")
                print("2. OR set 'RAPIDAPI_KEY' in your environment to bypass this.")
                print("\nAlternatively for local use, check README_COOKIES.md.\n")
            return None
