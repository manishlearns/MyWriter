import os
import requests
import json

class LinkedInTool:
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.person_urn = os.getenv("LINKEDIN_PERSON_URN") # e.g., urn:li:person:12345
        self.api_url = "https://api.linkedin.com/v2/ugcPosts"

    def _register_upload(self):
        """
        Step 1: Register the image upload to get an upload URL.
        """
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self.person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        response = requests.post(register_url, headers=headers, json=register_data)
        response.raise_for_status()
        data = response.json()
        
        upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_urn = data['value']['asset']
        return upload_url, asset_urn

    def _upload_image_binary(self, upload_url, image_url):
        """
        Step 2: Download image from Unsplash and Upload to LinkedIn.
        """
        # Download image
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        image_data = img_response.content
        
        # Upload to LinkedIn
        headers = {
            "Authorization": f"Bearer {self.access_token}",
             "Content-Type": "application/octet-stream"
        }
        
        upload_response = requests.put(upload_url, headers=headers, data=image_data)
        upload_response.raise_for_status()
        return True

    def post_article(self, text, image_url=None, visibility="PUBLIC"):
        if not self.access_token or not self.person_urn:
            print("LinkedIn credentials not found.")
            return None

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        specific_content = {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        }

        # Handle Image Upload if provided
        if image_url:
            try:
                print(f"Uploading image from {image_url}...")
                upload_url, asset = self._register_upload()
                if self._upload_image_binary(upload_url, image_url):
                    print("Image uploaded successfully.")
                    specific_content["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    specific_content["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "description": {"text": "Article Image"},
                            "media": asset,
                            "title": {"text": "Article Image"}
                        }
                    ]
            except Exception as e:
                print(f"Failed to upload image: {e}")
                print("Proceeding with text-only post.")

        post_data = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": specific_content,
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
