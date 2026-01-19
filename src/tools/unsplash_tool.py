import os
import requests

class UnsplashTool:
    def __init__(self):
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.base_url = "https://api.unsplash.com"

    def search_images(self, query, count=4):
        """
        Search for images on Unsplash.
        """
        if not self.access_key:
            print("Unsplash Access Key not found.")
            return []

        headers = {
            "Authorization": f"Client-ID {self.access_key}"
        }
        
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape"
        }

        try:
            response = requests.get(f"{self.base_url}/search/photos", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            images = []
            for item in data.get("results", []):
                images.append({
                    "id": item["id"],
                    "url": item["urls"]["regular"],
                    "thumb": item["urls"]["thumb"],
                    "download_url": item["links"]["download_location"], # Important for attribution tracking
                    "author": item["user"]["name"],
                    "author_url": item["user"]["links"]["html"],
                    "alt_description": item["alt_description"] or query
                })
            
            return images
            
        except Exception as e:
            print(f"Error searching Unsplash: {e}")
            return []

if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    tool = UnsplashTool()
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    print(f"Key loaded: {bool(key)}")
    results = tool.search_images("laziness")
    print(f"Found {len(results)} images.")
    if results:
        print(results[1]["thumb"])
