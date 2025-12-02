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

    def get_transcript(self, video_id):
        try:
            # Setup cookies if available
            http_client = None
            if os.path.exists("cookies.txt"):
                print("Loading cookies from cookies.txt...")
                try:
                    cookie_jar = http.cookiejar.MozillaCookieJar("cookies.txt")
                    cookie_jar.load()
                    http_client = requests.Session()
                    http_client.cookies = cookie_jar
                except Exception as e:
                    print(f"Warning: Failed to load cookies.txt: {e}")
            
            # Setup proxy if available
            proxy_config = None
            proxy_url = os.getenv("YOUTUBE_PROXY")
            if proxy_url:
                print(f"Using proxy: {proxy_url}")
                proxy_config = GenericProxyConfig(
                    http_url=proxy_url,
                    https_url=proxy_url
                )

            # Instantiate the API with cookies and/or proxy
            if http_client or proxy_config:
                # If we have custom config, we must instantiate
                transcript_api = YouTubeTranscriptApi(http_client=http_client, proxy_config=proxy_config)
                transcript_list = transcript_api.list(video_id)
            else:
                # Default usage
                transcript_api = YouTubeTranscriptApi()
                transcript_list = transcript_api.list(video_id)
            
            # Try to find English transcript (manual or generated)
            # find_transcript takes a list of language codes
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            
            # Fetch the actual data
            transcript_data = transcript.fetch()
            
            # Format it
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_data)
            return transcript_text
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching transcript for {video_id}: {error_msg}")
            if "blocking requests" in error_msg or "Sign in to confirm you're not a bot" in error_msg:
                print("\n!!! YOUTUBE IP BLOCK DETECTED !!!")
                print("Please follow the instructions in README_COOKIES.md to fix this.")
                print("You need to export your browser cookies to a 'cookies.txt' file in the project root.\n")
            return None
