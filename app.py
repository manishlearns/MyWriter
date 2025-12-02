
import streamlit as st
import os
# Load secrets from Streamlit Cloud if available
#if hasattr(st, "secrets"):
#    for key, value in st.secrets.items():
#        os.environ[key] = str(value)

from src.graph import app as graph_app
from langchain_core.messages import HumanMessage

# Page Config
st.set_page_config(page_title="LinkedIn Article Automation", layout="wide")

# Title
st.title("LinkedIn Article Automation System")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    
    # YouTube Channels
    default_channels = "@MelRobbins"
    channels_input = st.text_input("YouTube Channels (comma-separated)", value=default_channels)
    channels = [c.strip() for c in channels_input.split(",") if c.strip()]
    
    # Interests
    default_interests = "Personal Development, Productivity, Career Advice"
    interests_input = st.text_area("Interests (comma-separated)", value=default_interests)
    interests = [i.strip() for i in interests_input.split(",") if i.strip()]
    
    # Buttons
    start_btn = st.button("Start Workflow", type="primary")
    reset_btn = st.button("Reset State")

# Session State Initialization
if "thread_id" not in st.session_state:
    import uuid
    st.session_state.thread_id = str(uuid.uuid4())

if "graph_state" not in st.session_state:
    st.session_state.graph_state = None

if "workflow_running" not in st.session_state:
    st.session_state.workflow_running = False

# Reset Logic
if reset_btn:
    import uuid
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.graph_state = None
    st.session_state.workflow_running = False
    st.rerun()

# Main Area
status_container = st.container()
content_container = st.container()

def run_workflow():
    thread = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # Initial State
    # We need to pass config to the graph via the state or just rely on the agents reading config.yaml
    # But wait, the agents read config.yaml. 
    # We should probably update the config.yaml OR pass these inputs to the graph state if the nodes support it.
    # Looking at src/graph.py:
    # researcher.research() reads from self.config which loads config.yaml.
    # So the UI inputs won't affect the agents unless we:
    # 1. Update config.yaml
    # 2. Or modify agents to accept inputs from state.
    
    # For now, let's assume we need to update config.yaml or just mock it.
    # Actually, the best way is to update config.yaml since the agents are designed to read it.
    
    # Update config.yaml with UI inputs
    import yaml
    config_data = {
        "youtube_channels": channels,
        "interests": interests
    }
    with open("config.yaml", "w") as f:
        yaml.dump(config_data, f)
    
    st.session_state.workflow_running = True
    
    with status_container:
        st.info("Workflow Started...")
        
        # Run the graph
        # We use stream() to get updates
        # The graph expects an initial state.
        initial_state = {
            "messages": [HumanMessage(content="Start processing")],
            "style_persona": None,
            "research_results": [],
            "selected_topic": None,
            "draft": None,
            "final_draft": None
        }
        
        # We need to handle the stream loop carefully in Streamlit
        # Because Streamlit reruns on interaction, we can't just have a long running loop blocking everything
        # unless we use st.spinner or similar.
        
        try:
            # If we are resuming (e.g. after edit), we shouldn't pass initial_state again?
            # Actually app.stream(None, config) resumes if state exists.
            
            input_to_stream = initial_state if not st.session_state.graph_state else None
            
            for event in graph_app.stream(input_to_stream, config=thread):
                # event is a dict of node_name -> state_update
                for node_name, state_update in event.items():
                    st.write(f"**Step Completed:** {node_name}")
                    # Update our local view of state
                    # Note: state_update is just the delta. We might want the full state.
                    # But for now let's just log.
                    if "messages" in state_update:
                        st.caption(state_update["messages"][-1])
                        
            st.success("Workflow Paused or Completed!")
            
        except Exception as e:
            st.error(f"Error running workflow: {e}")

if start_btn:
    run_workflow()

# Check current state to display content
# We can fetch the current state from the graph
try:
    thread = {"configurable": {"thread_id": st.session_state.thread_id}}
    current_state = graph_app.get_state(thread)
    
    if current_state and current_state.values:
        state_values = current_state.values
        
        with content_container:
            # Display Style Analysis
            if state_values.get("style_persona"):
                with st.expander("Style Analysis", expanded=False):
                    st.markdown(state_values["style_persona"])

            # Display Research
            if state_values.get("research_results"):
                with st.expander("Research Results", expanded=False):
                    st.json(state_values["research_results"])
            
            # Display Draft
            if state_values.get("draft"):
                with st.expander("Initial Draft", expanded=False):
                    st.markdown(state_values["draft"])
            
            # Display Final Draft & Edit Interface
            # We check if we are at the 'publisher' interrupt
            # The next node should be 'publisher'
            if current_state.next and "writer" in current_state.next:
                st.subheader("Select a Topic")
                results = state_values.get("research_results", [])
                
                if not results:
                    st.warning("No research results found.")
                else:
                    # Create options for selection
                    # Use index to avoid long keys if titles are long, or just title
                    options = {f"{i+1}. {r['video_title']}": r for i, r in enumerate(results)}
                    selected_option = st.radio("Choose a topic to write about:", list(options.keys()))
                    
                    if st.button("Generate Draft"):
                        selected_topic = options[selected_option]
                        # Update state
                        st.info(f"Selected: {selected_topic['video_title']}")
                        graph_app.update_state(thread, {"selected_topic": selected_topic})
                        
                        # Resume graph
                        with status_container:
                            st.info("Resuming workflow to write draft...")
                            for event in graph_app.stream(None, config=thread):
                                 for node_name, state_update in event.items():
                                    st.write(f"**Step Completed:** {node_name}")
                                    if "messages" in state_update:
                                        st.caption(state_update["messages"][-1])
                            st.rerun()

            if current_state.next and "publisher" in current_state.next:
                st.subheader("Review & Edit Final Draft")
                
                final_draft = state_values.get("final_draft", "")
                
                # Editable Text Area
                # Use a form to prevent premature reruns
                with st.form("edit_draft_form"):
                    edited_draft = st.text_area("Edit before publishing:", value=final_draft, height=400)
                    col1, col2 = st.columns(2)
                    with col1:
                        approve_btn = st.form_submit_button("Approve & Publish")
                    with col2:
                        reject_btn = st.form_submit_button("Reject & restart")
                
                if approve_btn:
                    # Update state
                    st.info("Updating draft...")
                    graph_app.update_state(thread, {"final_draft": edited_draft})
                    
                    # Resume graph
                    with status_container:
                        st.info("Resuming workflow to publish...")
                        # Pass None as input to resume
                        for event in graph_app.stream(None, config=thread):
                             for node_name, state_update in event.items():
                                st.write(f"**Step Completed:** {node_name}")
                                if "messages" in state_update:
                                    st.caption(state_update["messages"][-1])
                        
                        st.success("Published Successfully!")
                        st.balloons()
                        st.rerun()
                
                if reject_btn:
                    st.warning("Rejecting draft and starting new workflow...")
                    # Update state to clear draft and selected topic
                    # We want to go back to the state BEFORE 'writer'.
                    # The graph structure is: researcher -> check_topics -> writer.
                    # We want to be at the point where 'researcher' has finished.
                    # We can use update_state with as_node="researcher" to simulate researcher finishing again.
                    # But we need to keep research_results.
                    
                #    current_research = state_values.get("research_results")
                #    graph_app.update_state(thread, {
                #        "selected_topic": None,
                #        "draft": None,
                #        "final_draft": None,
                #        "research_results": current_research # Keep results
                #    }, as_node="researcher")

                # Reset state
                    import uuid
                    st.session_state.thread_id = str(uuid.uuid4())
                    st.rerun()
                

            # Check for completion (no next steps but we have a final draft)
            if not current_state.next and state_values.get("final_draft"):
                st.success("Workflow Completed Successfully!")
                st.subheader("Published Article")
                st.markdown(state_values["final_draft"])
                if st.button("Start New Workflow"):
                    # Reset state
                    import uuid
                    st.session_state.thread_id = str(uuid.uuid4())
                    st.rerun()

except Exception as e:
    # State might not exist yet
    pass
