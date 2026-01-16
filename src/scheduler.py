import time
import threading
from src.database import get_due_posts, update_post_status
from src.tools.linkedin_tool import LinkedInTool

class SchedulerService:
    def __init__(self):
        self.linkedin = LinkedInTool()
        self.is_running = False
        self.thread = None
        self._stop_event = threading.Event()

    def start_polling(self, interval=60):
        if self.is_running:
            print("Scheduler is already running.")
            return

        self.is_running = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._poll_loop, args=(interval,), daemon=True)
        self.thread.start()
        print("Scheduler service started.")

    def stop_polling(self):
        if self.is_running:
            self.is_running = False
            self._stop_event.set()
            if self.thread:
                self.thread.join(timeout=1)
            print("Scheduler service stopped.")
    
    def _poll_loop(self, interval):
        print("Scheduler loop active.")
        while not self._stop_event.is_set():
            try:
                self._process_due_posts()
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
            
            # Sleep for interval or until stopped
            # We break sleep into 1s chunks to allow faster stopping
            for _ in range(int(interval)):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def _process_due_posts(self):
        pending = get_due_posts()
        if not pending:
            return

        print(f"Found {len(pending)} due posts. Processing...")
        
        for post in pending:
            post_id = post['id']
            draft = post['draft_text']
            image_url = post['image_url']
            
            print(f"Publishing scheduled post ID {post_id}...")
            
            try:
                result = self.linkedin.post_article(draft, image_url=image_url)
                if result:
                    print(f"Successfully published post {post_id}")
                    update_post_status(post_id, 'PUBLISHED')
                else:
                    print(f"Failed to publish post {post_id}")
                    update_post_status(post_id, 'FAILED', error_msg="LinkedIn tool returned None")
            except Exception as e:
                print(f"Exception publishing post {post_id}: {e}")
                update_post_status(post_id, 'FAILED', error_msg=str(e))

# Singleton instance
scheduler = SchedulerService()
