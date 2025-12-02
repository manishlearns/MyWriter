import yaml
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.tools.youtube_tool import YouTubeTool

class Researcher:
    def __init__(self):
        self.youtube_tool = YouTubeTool()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.config = self.load_config()

    def load_config(self):
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)

    def research(self):
        self.config = self.load_config() # Reload config to pick up changes
        channels = self.config.get("youtube_channels", [])
        interests = self.config.get("interests", [])
        
        found_topics = []
        
        for channel_id in channels:
            print(f"Checking channel: {channel_id}")
            videos = self.youtube_tool.get_latest_videos(channel_id)
            print(f"Found {len(videos)} videos.")
            
            # MOCK DATA FOR TESTING IF NO VIDEOS FOUND (e.g. no API key)
            if not videos and not self.youtube_tool.api_key:
                print("Using mock data for research...")
                videos = [{
                    "video_id": "mock_vid_1",
                    "title": "The Future of Agentic AI",
                    "description": "How agents are changing coding.",
                    "published_at": "2023-10-27T00:00:00Z"
                }]
            
            for video in videos:
                transcript = self.youtube_tool.get_transcript(video["video_id"])
                
                
                print(f"Analyzing video: {video['title']}")
                # Analyze relevance
                # Mock analysis if no API key or dummy key
                api_key = os.getenv("OPENAI_API_KEY")
                if not self.youtube_tool.api_key or not api_key or api_key == "dummy":
                    analysis = {
                        "is_relevant": True,
                        "summary": "A video about Agentic AI.",
                        "key_points": ["Agents are the future", "They can plan", "They execute tasks"],
                        "relevance_score": 9
                    }
                else:
                    analysis = self.analyze_video(video, transcript, interests)

                if analysis.get("is_relevant"):
                    print(f"Video is relevant: {video['title']}")
                    found_topics.append({
                        "video_title": video["title"],
                        "video_id": video["video_id"],
                        "summary": analysis.get("summary"),
                        "key_points": analysis.get("key_points"),
                        "transcript_snippet": (transcript[:2000] if transcript else "") # Pass a chunk for context
                    })
                else:
                    print(f"Video NOT relevant: {video['title']}")
        
        return found_topics

    def analyze_video(self, video, transcript, interests):
        if not transcript:
            print(f"Skipping analysis for {video['title']} due to missing transcript.")
            return {"is_relevant": False}

        prompt = ChatPromptTemplate.from_template("""
        You are a content researcher. Analyze the following video transcript and determine if it matches the user's interests.
        
        User Interests: {interests}
        
        Video Title: {title}
        Transcript: {transcript}
        
        Return a JSON object with the following fields:
        - is_relevant: boolean
        - summary: string (brief summary of the topic)
        - key_points: list of strings (3-5 key takeaways)
        - relevance_score: number (1-10)
        """)
        
        chain = prompt | self.llm | JsonOutputParser()
        
        # Truncate transcript to avoid token limits
        truncated_transcript = transcript[:10000]
        
        try:
            result = chain.invoke({
                "interests": ", ".join(interests),
                "title": video["title"],
                "transcript": truncated_transcript
            })
            return result
        except Exception as e:
            print(f"Error analyzing video {video['title']}: {e}")
            return {"is_relevant": False}

if __name__ == "__main__":
    # Test the researcher (requires API key and valid channel ID in config)
    researcher = Researcher()
    # Mocking for test if no API key
    if not researcher.youtube_tool.api_key:
        print("No YouTube API Key found. Skipping live test.")
    else:
        results = researcher.research()
        print(f"Found {len(results)} relevant topics.")
