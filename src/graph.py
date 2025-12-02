from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated, Optional
import operator

from src.agents.stylist import StyleAnalyzer
from src.agents.researcher import Researcher
from src.agents.writer import Writer
from src.agents.publisher import Publisher
from src.agents.reviewer import Reviewer

# Define the State
class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    style_persona: Optional[str]
    research_results: Optional[List[dict]]
    selected_topic: Optional[dict]
    draft: Optional[str]
    final_draft: Optional[str]

# Initialize Agents
stylist = StyleAnalyzer()
researcher = Researcher()
writer = Writer()
publisher = Publisher()

# Define Nodes
def analyze_style_node(state: AgentState):
    print("--- Analyzing Style ---")
    persona = stylist.analyze_style()
    return {"style_persona": persona, "messages": ["Style analyzed"]}

def research_node(state: AgentState):
    print("--- Researching Topics ---")
    results = researcher.research()
    if not results:
        return {"research_results": [], "messages": ["No topics found"]}
    
    # For simplicity, pick the first topic. In a real app, user might select.
    # selected = results[0]
    return {"research_results": results, "messages": ["Research completed, waiting for topic selection"]}



from pathlib import Path

# ... (existing imports)

# ...

def write_node(state: AgentState):
    print("--- Writing Draft ---")
    topic = state.get("selected_topic")
    style = state.get("style_persona")
    
    if not topic or not style:
        return {"messages": ["Missing topic or style"]}
    
    # Load sample draft
    try:
        sample_draft_path = Path(__file__).parent.parent / "data" / "style_examples" / "sample5.txt"
        with open(sample_draft_path, "r") as f:
            sample_draft = f.read()
    except Exception as e:
        print(f"Error loading sample draft: {e}")
        # Fallback to empty string or handle appropriately
        sample_draft = ""

    draft = writer.write_draft(topic, style, sample_draft)
    print(f"DEBUG: Draft generated. Length: {len(draft) if draft else 'None'}")
    return {"draft": draft, "messages": ["Draft created"]}

def review_node(state: AgentState):
    print("--- Revisting draft ---")
    draft = state['draft']

    reviewer = Reviewer()
    final_draft = reviewer.review(draft)
    return {"final_draft": final_draft, "messages": ["Draft reviewed"]}





def publish_node(state: AgentState):
    print("--- Publishing ---")
    draft = state.get("final_draft")
    if not draft:
        return {"messages": ["No draft to publish"]}
    
    publisher.publish(draft)
    return {"messages": ["Published to LinkedIn"]}

# Define the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("stylist", analyze_style_node)
workflow.add_node("researcher", research_node)
workflow.add_node("writer", write_node)
workflow.add_node("publisher", publish_node)
workflow.add_node("review_node", review_node )




# Add Edges
workflow.set_entry_point("stylist")
workflow.add_edge("stylist", "researcher")

def check_topics(state):
    if state.get("research_results"):
        return "writer"
    return END

workflow.add_conditional_edges(
    "researcher",
    check_topics,
    {
        "writer": "writer",
        END: END
    }
)

#workflow.add_edge("writer", "publisher")
workflow.add_edge("writer", "review_node")
workflow.add_edge("review_node", "publisher")
workflow.add_edge("publisher", END)

from langgraph.checkpoint.memory import MemorySaver

# Compile the Graph with Interrupt and Checkpointer
# We interrupt BEFORE the publisher node to allow human review
checkpointer = MemorySaver()
# Adding interrupt_after to ensure we stop after review
app = workflow.compile(
    interrupt_before=["writer", "publisher"], 
    interrupt_after=["review_node"],
    checkpointer=checkpointer
)





