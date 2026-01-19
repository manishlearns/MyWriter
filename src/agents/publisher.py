from src.tools.linkedin_tool import LinkedInTool

class Publisher:
    def __init__(self):
        self.linkedin_tool = LinkedInTool()

    def publish(self, draft_text, scheduled_time=None, image_url=None):
        if scheduled_time:
            from src.database import add_post
            try:
                print(f"Persisting scheduled post for {scheduled_time}...")
                post_id = add_post(draft_text, scheduled_time, image_url)
                if post_id:
                    print(f"✅ Scheduling successful! Saved to DB with ID: {post_id}")
                    return {"status": "scheduled", "scheduled_time": scheduled_time, "db_id": post_id}
                else:
                    print("❌ Failed to save schedule to DB.")
                    return None
            except Exception as e:
                print(f"Error scheduling post: {e}")
                return None

        print("Publishing article to LinkedIn...")
        result = self.linkedin_tool.post_article(draft_text, image_url=image_url)
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
