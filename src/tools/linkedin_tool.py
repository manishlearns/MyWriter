import os
import requests
import json

class LinkedInTool:
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.person_urn = os.getenv("LINKEDIN_PERSON_URN") # e.g., urn:li:person:12345
        self.api_url = "https://api.linkedin.com/v2/ugcPosts"

    def post_article(self, text, visibility="PUBLIC"):
        if not self.access_token or not self.person_urn:
            print("LinkedIn credentials not found.")
            return None

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        post_data = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=post_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error posting to LinkedIn: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)
            return None
