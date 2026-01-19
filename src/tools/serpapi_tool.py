from serpapi import GoogleSearch


class SerpApiTool:
    def __init__(self):
        self.api_key = "fd6da3fcd03592b026c86fa2d7570a2201098d53a2c4d4e8b930fb33b7aef98e"
    
    def search(self, query):
        params = {
            "q": query,
            "engine": "google_images",
            "ijn": "0",
            "api_key": self.api_key
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        images_results = results["images_results"]
        return images_results

if __name__ == "__main__":
    tool = SerpApiTool()
    images_list = []
    image_dict = {}

    for i in tool.search("Apple"):
        #image_dict = {}
        images_list.append({'thumb': i['thumbnail'], 'author': i['source'], 'url': i['original']})
    
    print(images_list[:6])