import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from src.graph import app

def main():
    print("Starting LinkedIn Article Automation System...")
    
    # Initial State
    initial_state = {
        "messages": [],
        "style_persona": None,
        "research_results": [],
        "selected_topic": None,
        "draft": None
    }
    
    # Run the graph until the interrupt
    print("Running workflow...")
    thread = {"configurable": {"thread_id": "1"}}
    
    for output in app.stream(initial_state, config=thread):
        for key, value in output.items():
            print(f"Finished node: {key}")

    


    # Check current state
    current_state = app.get_state(thread)
    
    # Handle Topic Selection (Interrupt before 'writer')
    if current_state.next and current_state.next[0] == "writer":
        print("\n--- Topic Selection Required ---")
        results = current_state.values.get("research_results")
        
        if results:
            print("Select a topic from the following:")
            for i, topic in enumerate(results):
                print(f"{i+1}. {topic['video_title']}")
            
            while True:
                try:
                    user_input = input("\nEnter the number of your choice: ")
                    selected_index = int(user_input) - 1
                    if 0 <= selected_index < len(results):
                        selected_topic = results[selected_index]
                        print(f"Selected: {selected_topic['video_title']}")
                        
                        # Update state with selected topic
                        app.update_state(thread, {"selected_topic": selected_topic})
                        
                        # Resume the graph
                        print("Resuming workflow...")
                        for output in app.stream(None, config=thread):
                            for key, value in output.items():
                                print(f"Finished node: {key}")
                        break
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        else:
            print("No research results found. Exiting.")
            return

    # Check current state again (for Publisher interrupt)
    current_state = app.get_state(thread)
    if current_state.next and current_state.next[0] == "publisher":
        print("\n--- Human Review Required ---")
        print("The system has paused before publishing.")
        
        draft = current_state.values.get("final_draft")
        print("\nGenerated Draft:\n")
        print("="*40)
        print(draft)
        print("="*40)
        
        user_input = input("\nDo you approve this draft? (yes/no): ")
        
        if user_input.lower() == "yes":
            print("Approving and resuming...")
            # Resume the graph
            for output in app.stream(None, config=thread):
                 for key, value in output.items():
                    print(f"Finished node: {key}")
        else:
            print("Draft rejected. Exiting.")
    elif not current_state.next:
        print("Workflow completed without interruption.")

if __name__ == "__main__":
    main()
