from src.tools.linkedin_tool import LinkedInTool

class Publisher:
    def __init__(self):
        self.linkedin_tool = LinkedInTool()

    def publish(self, draft_text):
        print("Publishing article to LinkedIn...")
        result = self.linkedin_tool.post_article(draft_text)
        if result:
             print(f"Successfully published! Post ID: {result.get('id')}")
             return result
        else:
             print("Failed to publish.")
             return None

if __name__ == "__main__":
    # Test the publisher
    publisher = Publisher()
    # Mocking for test if no API key
    if not publisher.linkedin_tool.access_token:
        print("No LinkedIn Access Token found. Skipping live test.")
    else:
        publisher.publish("This is a test post from my automated agent.")
